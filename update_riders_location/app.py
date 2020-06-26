import json
import boto3
import os
import redis
from uuid import uuid4

dynamodb = boto3.resource('dynamodb')

ridersTbl = dynamodb.Table(os.environ['RIDERS_TABLE'])
ridesTbl = dynamodb.Table(os.environ['RIDES_TABLE'])
driversTbl = dynamodb.Table(os.environ['DRIVERS_TABLE'])

r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
     charset='utf-8', decode_responses=True, db=0)

def lambda_handler(event, context):
    params = event.get('pathParameters')
    riderId = params.get('riderId')
    requestBody = json.loads(event.get('body'))
    response = { 'message': 'Invalid Input.' }
    
    if requestBody and requestBody.get('updatedLocation'):
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
                    'location_id': driverLocId 
                }
            )
        
        r.geoadd(
            'driversRidersGeo', 
            requestBody['updatedLocation']['W'], 
            requestBody['updatedLocation']['N'], 
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
                    UpdateExpression="set ride_id = :r",
                    ExpressionAttributeValues={
                        ':r': '',
                    },
                )
                
                ridersTbl.update_item(
                    Key={
                        'rider_id': riderId
                    },
                    UpdateExpression="set ride_id = :r",
                    ExpressionAttributeValues={
                        ':r': '',
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