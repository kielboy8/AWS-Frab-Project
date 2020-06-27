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
    
    if driverId and rideId:
        if validate_coord(acceptLocation) == False:
            response = {'message': 'Invalid Coordinates.'}
        else:
            rideRecord = r.hgetall('bookingHash:'+rideId)
            if rideRecord and rideRecord['driverId']:
                response = {'message': 'Ride already has a driver.'}
            else:
                currentRideId = r.get('driverBooking:'+driverId)
                if currentRideId == None or \
                    currentRideId == '' and rideRecord:
                    dateNow = str(datetime.datetime.now().isoformat())
                    update_ride_table=rideTable.update_item(
                        Key={ 'ride_id': rideId },
                        ExpressionAttributeNames={
                            '#RS': 'ride_status',
                            '#DI': 'driver_id',
                            '#AA': 'accepted_at',
                            '#AL': 'accept_location'
                        },
                        ExpressionAttributeValues={
                            ':rs': 'accepted',
                            ':di': driverId,
                            ':aa': dateNow,
                            ':al': json.dumps(acceptLocation)
                        },
                        UpdateExpression="SET #AA= :aa, #AL= :al, #RS= :rs, #DI=:di",
                    )     
                    
                    update_driver_table=driverTable.update_item(
                        Key={
                                'driver_id': driverId
                            },
                        ExpressionAttributeNames={
                            '#RI': 'ride_id'
                        },
                        ExpressionAttributeValues={
                            ':ri': rideId
                        },
                        UpdateExpression="SET #RI=:ri",
                    )                
                    
                    r.zrem('ridesGeoPending', rideId)     
                    r.set('driverBooking:'+driverId, rideId)
                    r.hmset('bookingHash:'+rideId, {**rideRecord, 'state': 'accepted','driverId': driverId })
          
                    response = {
                        "rideId": rideId,
                        "acceptLocation": body['acceptLocation'],
                        "createdAt": dateNow
                    }
                elif r.get('driverBooking:'+driverId):
                    response = { 'error': 'You have an existing ride.'}
                else:
                    response = { 'error': 'Ride doesn\'t exist.' }
                
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }