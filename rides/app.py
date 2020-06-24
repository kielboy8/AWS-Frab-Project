import json
import boto3
import os
import uuid
import datetime
import redis

dynamodb = boto3.client("dynamodb", os.environ['DEFAULT_REGION'])
r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], db=0)


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
            
            r.geoadd('ridesBookLoc', 
                float(bookingLocation['W']), 
                float(bookingLocation['N']), 
                body['ride_id']) #Lon, Lat
            
            r.hmset('bookingHash:'+body['ride_id'], 
                {
                    'state':'pending', 
                    'rideId': body['ride_id'], 
                    'driverId': ''
                }
            )
            
            r.expire('bookingHash:'+body['ride_id'], os.environ['RIDES_TTL'])
            
            response = {
                    "rideId": body['ride_id'],
                    "state": "pending"
            }
        else:
            pass
    else:
        pass
    
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
    

  