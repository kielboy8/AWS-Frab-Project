import json
import boto3
import os
import datetime 
import redis

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key #, Attr

client = boto3.resource(
   'dynamodb',
   region_name=os.environ['DEFAULT_REGION'],
)

r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
            charset='utf-8', decode_responses=True, db=0)
riderTable = client.Table(os.environ["RIDES_TABLE"])
driverTable = client.Table(os.environ["DRIVERS_TABLE"])


def lambda_handler(event, context):
    params = event.get("pathParameters")
    driverId = params.get('driverId')
    rideId = params.get('rideId')
    response = {'message': 'Invalid Input.'}
    body = json.loads(event.get('body'))
    acceptLocation = body['acceptLocation']
    
    print('Before')
    print("acceptLocatio: ", acceptLocation)
    print("Type: ", str(type(acceptLocation)))
    print(bool(driverId and rideId and acceptLocation))
    print(bool(acceptLocation.get('W') and acceptLocation.get('N')))
    print(driverId, rideId)
    
    if bool(driverId and rideId and acceptLocation) and bool(acceptLocation.get('W') and acceptLocation.get('N')):
        print("accept")
        rideRecord = r.hgetall('bookingHash:'+rideId)
        print("Meron rideRecord", rideRecord)
        if rideRecord['driver_id']:
            print("may driver na")
            response = {'message': 'Ride already has a driver.'}
        else:
            print("before update")
            if r.get('driverBooking:'+driverId) == '':
                print("before update table")
                update_ride_table=table.update_item(
                    Key={
                            'ride_id': rideId
                        },
                    ExpressionAttributeNames={
                        '#RS': 'ride_status',
                        '#DI': 'driver_id',
                        '#AA': 'accepted_at',
                        '#AL': 'accept_location'
                    },
                    ExpressionAttributeValues={
                        ':s': 'accepted',
                        ':di': driverId,
                        ':ts': dateNow,
                        ':al': body['acceptLocation']
                    },
                    UpdateExpression="set #RS=:s, #DI=:di, #AA=:ts, #AL=:al",
                )     
                
                update_driver_table=table.update_item(
                    Key={
                            'driver_id': driverId
                        },
                    ExpressionAttributeNames={
                        '#DS': 'driver_status',
                        '#RI': 'ride_id'
                    },
                    ExpressionAttributeValues={
                        ':ds': 'accepted a ride',
                        ':ri': rideId
                    },
                    UpdateExpression="set #DS=:ds, #RI=:ri",
                )                
            
                r.zrem('ridesGeoPending:', rideId)                
                r.set('driverBooking:'+driverId, rideId)
                # bookingRec = {**rideRecord, 'state': 'accepted','driver_id': driverId }
                r.hmset('bookingHash:'+rideId, {**rideRecord, 'state': 'accepted','driver_id': driverId })
                
                response = {
                    "rideId": rideId,
                    "acceptLocation": body['acceptLocation'],
                    "createAt": dateNow
                }
                
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }