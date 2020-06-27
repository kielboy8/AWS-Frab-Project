import json
import boto3
import os
import uuid
import datetime
import redis

dynamodb = boto3.client("dynamodb", os.environ['DEFAULT_REGION'])
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
    body = json.loads(event['body'])
    body['ride_id'] = uuid.uuid4().hex
    body['timestamp'] = str(datetime.datetime.now().isoformat())
    response = {'message':'Invalid Input.'}
    
    if body.get('bookingLocation') and body.get('targetLocation') and body.get('riderId'):
        bookingLocation = body['bookingLocation']
        targetLocation = body['targetLocation']
        if validate_coord(bookingLocation) and validate_coord(targetLocation):
            currentRideId = r.get('riderBooking:'+body['riderId'])
            if currentRideId:
                currentRide = r.hgetall('bookingHash:'+currentRideId)
                if currentRide and (json.loads(currentRide['bookingLocation']) == bookingLocation) and \
                    (json.loads(currentRide['targetLocation']) == targetLocation):
                        response = {'message':'You already booked for this destination.'}
                else:
                    response = {'message': 'New Booking.'}
                    r.zrem('ridesGeoPending:', currentRideId)    
            
            if response['message'] != 'You already booked for this destination.':
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
                        'accepted_at': {
                            'S': ''
                        },
                        'accept_location': {
                            'S': ''
                        },
                        'rider_id': {
                            'S': body['riderId']
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
                        'riderId': body['riderId'],
                        'bookingLocation': str(json.dumps(body['bookingLocation'])),
                        'targetLocation': str(json.dumps(body['targetLocation']))
                    }
                )
       
                if currentRideId is None:
                    dynamodb.put_item(
                        TableName=os.environ['RIDERS_TABLE'],
                        Item={
                            'rider_id': { 'S': body['riderId'] },
                            'ride_id': {'S': body['ride_id'] },
                            'location_id': { 'S': '' },
                            'last_location_timestamp': { 'S': ''}
                        }
                    )
                    
                r.set('riderBooking:'+body['riderId'], body['ride_id'])
                
                response = {
                        'rideId': body['ride_id'],
                        'state': 'pending'
                }
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }