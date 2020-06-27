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
    response = ''
    
    if riderId:
        riderLocId = str(uuid4().hex)
        
        locationRider = r.hgetall('ridersLoc:'+riderId)
        
        if locationRider.get('location_id'):
            location = r.geopos('driversRidersGeo', riderId)
            print('locationRider: ',locationRider.get('location_id'))
            response = {
                "riderId": riderId,
                "locationId": locationRider['location_id'],
                "currentLocation": str(location),
                "lastActive": locationRider.get('last_location_timestamp')
            }
        else:
            try:
                record = ridersTbl.get_item(
                    Key={
                        'rider_id': riderId
                    },
                    ProjectionExpression='location_id,last_location_timestamp',
                )['Item']
                
                r.hmset('ridersLoc:'+riderId, {
                    'location_id': record.get('location_id'),
                    'last_location_timestamp': record.get('last_location_timestamp')
                })
                
                location = r.geopos('driversRidersGeo', riderId)
                print('location: ', location)
                #Add DB Cache Miss
                response = {
                    "riderId": riderId,
                    "locationId": riderLocId,
                    "currentLocation":'',
                    "lastActive": record.get('last_location_timestamp')
                }
            except:
                response = {'error': 'Rider doesn\'t exist.'}
    else:
        response = {'error': 'RiderId Not Provided.'}
            
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }