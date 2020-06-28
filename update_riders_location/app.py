import json
import boto3
import os
import redis
from uuid import uuid4
import datetime

dynamodb = boto3.resource('dynamodb')

ridersTbl = dynamodb.Table(os.environ['RIDERS_TABLE'])
ridesTbl = dynamodb.Table(os.environ['RIDES_TABLE'])
driversTbl = dynamodb.Table(os.environ['DRIVERS_TABLE'])

r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
     charset='utf-8', decode_responses=True, db=0)

def validate_coord(coord):
    try:
        if coord.get('W') and coord.get('N') and \
        (float(coord.get('W')) > -180 and float(coord.get('W')) < 180) and \
        (float(coord.get('N')) > -90 and float(coord.get('N')) < 90):
            return True
    except:
        return False
        
        
def lambda_handler(event, context):
    params = event.get('pathParameters')
    riderId = params.get('riderId')
    requestBody = json.loads(event.get('body'))
    response = {'message':'Invalid Input.'}
    lastTimeStamp =  str(datetime.datetime.now().isoformat())
    
    if validate_coord(requestBody['currentLocation']):
        driverLocId = str(uuid4().hex) 
        try:
            if r.get('riderBooking:'+riderId) is None or \
                r.get('riderBooking:'+riderId) is '':
                driverLocId = ridersTbl.get_item(
                    Key={
                        'rider_id': riderId
                    },
                    ProjectionExpression='location_id'
                )['Item']['location_id']
        except:
            response = ridersTbl.put_item(
                Item={
                    'rider_id': riderId,
                    'ride_id': '',
                    'location_id': driverLocId,
                    'last_location': str(json.dumps(requestBody['currentLocation'])),
                    'last_location_timestamp': lastTimeStamp
                }
            )
        
        r.geoadd(
            'driversRidersGeo', 
            requestBody['currentLocation']['W'], 
            requestBody['currentLocation']['N'], 
            riderId
        )
        
        r.hmset(
            'ridersLoc:'+riderId,
            { 'timestamp': lastTimeStamp, 'location_id': driverLocId }
        )
        
        #Check if has current ride in cache
        currentRideId = r.get('driverBooking:'+riderId)
        
        if currentRideId: 
            currentRide = r.hgetall('bookingHash:'+currentRideId)
            willExpire = False
            print('is same: ', json.loads(currentRide['targetLocation']) == requestBody['currentLocation'])
            print(json.loads(currentRide['targetLocation']), requestBody['currentLocation'])
            if json.loads(currentRide['targetLocation']) == requestBody['currentLocation']:
                print('pumasok here...')
                if currentRide['state'] == 'in_progress':
                    print('pumasok to finish..')
                    currentRide['state'] = 'complete_success'
                    r.set('riderBooking:'+riderId, '')
                    r.set('driverBooking:'+currentRide['driver_id'], '')
                
                ridesTbl.update_item(
                    Key={
                        'ride_id': currentRideId
                    },
                    UpdateExpression="set ride_status = :r",
                    ExpressionAttributeValues={
                        ':r': currentRide['state'],
                    },
                )
                
                driversTbl.update_item(
                    Key={
                        'driver_id': currentRide['driver_id']
                    },
                    UpdateExpression="set ride_id = :r, last_location_timestamp = :lt, last_location = :loc",
                    ExpressionAttributeValues={
                        ':r': '',
                        ':lt': lastTimeStamp,
                        ':loc': str(json.dumps(currentRide['targetLocation']))
                    },
                )
                
                ridersTbl.update_item(
                    Key={
                        'rider_id': riderId
                    },
                    UpdateExpression="set ride_id = :r, last_location_timestamp = :lt, last_location = :loc",
                    ExpressionAttributeValues={
                        ':r': '',
                        ':lt': lastTimeStamp,
                        ':loc': str(json.dumps(currentRide['targetLocation']))
                    },
                )
                
                r.hmset('bookingHash:'+currentRideId, currentRide)
                willExpire and r.expire('bookingHash:'+currentRideId, 120)
        
    return {
        "statusCode": 200,
        "body": json.dumps({
            "locationId": driverLocId,
            "currentLocation": requestBody['currentLocation'],
            "lastActive": lastTimeStamp
        }),
    }