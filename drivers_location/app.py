import json
import boto3
import os
import redis
from uuid import uuid4

dynamodb = boto3.resource('dynamodb')
driversTbl = dynamodb.Table(os.environ['DRIVERS_TABLE'])
ridesTbl = dynamodb.Table(os.environ['RIDES_TABLE'])
r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
     charset='utf-8', decode_responses=True, db=0)

def lambda_handler(event, context):
    params = event.get('pathParameters')
    driverId = params.get('driverId')
    requestBody = json.loads(event.get('body'))
    
    driverLocId = str(uuid4().hex)
    
    try:
        driverLocId = driversTbl.get_item(
            Key={
                'driver_id': driverId
            },
            ProjectionExpression='location_id'
        )['Item']['location_id']
    except:
        response = driversTbl.put_item(
            Item={
                'driver_id': driverId,
                'location_id': driverLocId 
            }
        )
    
    r.geoadd(
        'driversRidersGeo', 
        requestBody['updatedLocation']['N'], 
        requestBody['updatedLocation']['W'], 
        driverId
    )
    
    #Check if has current ride in cache
    currentRideId = r.get('driverBooking:'+driverId)
    if currentRideId:
        currentRide = r.hgetall('bookingHash:'+currentRideId)
        willExpire = False
        if json.loads(currentRide['bookingLocation']) == requestBody['updatedLocation']:
            if currentRide['state'] == 'accepted':
                #Move to In-Progress
                currentRide['state'] = 'in_progress'
            elif currentRide['state'] == 'in_progress':
                #Finish Ride
                currentRide['state'] == 'complete'
            
            ridesTbl.update_item(
                Key={
                    'ride_id': currentRideId
                },
                UpdateExpression="set ride_status = :r",
                ExpressionAttributeValues={
                    ':r': currentRide['state'],
                },
            )
            
            r.hmset('bookingHash:'+currentRideId, currentRide)
            willExpire and r.expire('bookingHash:'+currentRideId, 120)
        
    return {
        "statusCode": 200,
        "body": json.dumps({
            "locationId": driverLocId,
            "updatedLocation": requestBody['updatedLocation']
        }),
    }
