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
rideTable = client.Table(os.environ["RIDES_TABLE"])
driverTable = client.Table(os.environ["DRIVERS_TABLE"])

def validate_coord(coord):
    try:
        if coord.get('W') and coord.get('N') and \
        (float(coord.get('W')) > -180 and float(coord.get('W')) < 180) and \
        (float(coord.get('N')) > -90 and float(coord.get('N')) < 90):
            return True
    except:
        return False
        
def lambda_handler(event, context):
    params = event.get("pathParameters")
    driverId = params.get('driverId')
    rideId = params.get('rideId')
    response = {'message': 'Invalid Input.'}
    body = json.loads(event.get('body'))
    acceptLocation = body['acceptLocation']
    accept_location = str(acceptLocation)

    if bool(driverId and rideId and acceptLocation) and bool(acceptLocation.get('W') and acceptLocation.get('N')) :
        rideRecord = r.hgetall('bookingHash:'+rideId)
        if validate_coord(acceptLocation) == False:
            response = {'message': 'Invalid Coordinates.'}
        else:
            if rideRecord['driverId']:
                response = {'message': 'Ride already has a driver.'}
            else:
                if r.get('driverBooking:'+driverId) == None:
                    dateNow = str(datetime.datetime.now().isoformat())
                    update_ride_table=rideTable.update_item(
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
                            ':al': accept_location
                        },
                        UpdateExpression="SET #RS=:s, #DI=:di ADD #AA :ts, #AL :al",
                    )     
                    
                    update_driver_table=driverTable.update_item(
                        Key={
                                'driver_id': driverId
                            },
                        ExpressionAttributeNames={
                            '#DS': 'driver_status',
                            '#RI': 'ride_id'
                        },
                        ExpressionAttributeValues={
                            ':ds': 'Accepted a ride',
                            ':ri': rideId
                        },
                        UpdateExpression="SET #DS=:ds ADD #RI :ri",
                    )                
                    print("Database has been updated")
                    
                    r.zrem('ridesGeoPending:', rideId)     
                    print("Deleted rideID from ridesGeoPending")
                    r.set('driverBooking:'+driverId, rideId)
                    print("Updated driverBooking")
                    r.hmset('bookingHash:'+rideId, {**rideRecord, 'state': 'accepted','driverId': driverId })
                    print("Updated bookingHash")

                    response = {
                        "rideId": rideId,
                        "acceptLocation": body['acceptLocation'],
                        "createAt": dateNow
                    }
                
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }