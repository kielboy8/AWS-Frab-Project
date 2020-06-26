import json
import boto3
import os
import redis
from uuid import uuid4

dynamodb = boto3.resource('dynamodb')
ridersTbl = dynamodb.Table(os.environ['DRIVERS_TABLE'])
ridesTbl = dynamodb.Table(os.environ['RIDES_TABLE'])
r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
     charset='utf-8', decode_responses=True, db=0)

def lambda_handler(event, context):
    params = event.get('pathParameters')
    riderId = params.get('riderId')
    requestBody = json.loads(event.get('body'))
    
    driverLocId = str(uuid4().hex)
    
    try:
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
                'location_id': driverLocId 
            }
        )
    
    r.geoadd(
        'driversRidersGeo', 
        requestBody['updatedLocation']['N'], 
        requestBody['updatedLocation']['W'], 
        riderId
    )
    
    #Check if has current ride in cache
    currentRideId = r.get('driverBooking:'+riderId)
    
    if currentRideId: 
        currentRide = r.hgetall('bookingHash:'+currentRideId)
        willExpire = False
        if json.loads(currentRide['targetLocation']) == requestBody['updatedLocation']:
            if currentRide['state'] == 'in_progress':
                currentRide['state'] = 'complete_success'
            
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
