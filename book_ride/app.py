import json
import boto3
import os
import uuid
import datetime
import redis

dynamodb = boto3.client("dynamodb", os.environ['DEFAULT_REGION'])
r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
            charset='utf-8', decode_responses=True, db=0)


def lambda_handler(event, context):
    body = json.loads(event['body'])
    body['ride_id'] = uuid.uuid4().hex
    body['timestamp'] = str(datetime.datetime.now().isoformat())
    response = {'message':'Invalid Input.'}
    
    if body.get('bookingLocation') and body.get('targetLocation'):
        bookingLocation = body['bookingLocation']
        targetLocation = body['targetLocation']
        if (bookingLocation.get('W') and bookingLocation.get('N')) and \
            (targetLocation.get('W') and targetLocation.get('N')):
            currentRideId = r.get('riderBooking:'+body['userId'])
            if currentRideId:
                currentRide = r.hgetall('bookingHash:'+currentRideId)
                if currentRide and (json.loads(currentRide['bookingLocation']) == bookingLocation) and \
                    (json.loads(currentRide['targetLocation']) == targetLocation):
                        response = {'message':'Identical Booking Exists.'}
            
            if response['message'] != 'Identical Booking Exists.':
                dynamodb.put_item(
                    TableName=os.environ['RIDES_TABLE'],
                    Item={
                        'ride_id': {
                            'S': body['ride_id']
                        },
                        'booking_location': {
                            'S':  str(bookingLocation)
                        },
                        'target_location': {
                            'S': str(targetLocation)
                        },
                        'driver_id': {
                            'S': ''  
                        },
                        'rider_id': {
                            'S': body['userId']
                        },
                        'timestamp': {
                            'S': body['timestamp']
                        },
                        'ride_status': {
                            'S': 'pending'
                        }
                    }
                )
                
                r.geoadd('ridesGeoPending', 
                    float(bookingLocation['W']), 
                    float(bookingLocation['N']), 
                    body['ride_id']) #Lon, Lat
                
                r.hmset('bookingHash:'+body['ride_id'], 
                    {
                        'state':'pending', 
                        'rideId': body['ride_id'], 
                        'driverId': '',
                        'userId': body['userId'],
                        'bookingLocation': str(json.dumps(body['bookingLocation'])),
                        'targetLocation': str(json.dumps(body['targetLocation']))
                    }
                )
        
                r.set('riderBooking:'+body['userId'], body['ride_id'])
                
                response = {
                        'rideId': body['ride_id'],
                        'state': 'pending'
                }
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }