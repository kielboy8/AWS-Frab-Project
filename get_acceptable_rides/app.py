from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key #, Attr

import json
import boto3
import os
import uuid
import datetime
import redis 

client = boto3.resource(
   'dynamodb',
   region_name=os.environ['DEFAULT_REGION'],
)

table = client.Table(os.environ["DRIVERS_TABLE"])
r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], db=0)

def lambda_handler(event, context):
    response = []
    params = event.get("pathParameters")
    driverId = params.get('driverId')
    
    if driverId:
        #Fetch Last Location on ElastiCache
        result = r.geopos('driversGeo', driverId)
            
        if result:
            result = {
                'W': result[0][1],
                'N': result[0][0]
            }
          
        else:
            result = table.query(
                KeyConditionExpression=Key('driver_id').eq(driverId),
                ProjectionExpression='location_id'
            )
            
            if len(result['Items']) > 0:
                result - json.loads(result['Items'][0]['location_id'])
                result = {
                    'W': float(result['W']),
                    'N': float(result['N'])
                }
            
        acceptable_rides = r.georadius('ridesGeoPending', 
                result['W'], result['N'],  #W, N
                os.environ['SEARCH_RADIUS_VALUE'], 
                unit=os.environ['SEARCH_RADIUS_UNIT'], 
                withdist=True, 
                withcoord=True, 
                withhash=False, 
                count=os.environ['RIDES_ACCEPTABLE_COUNT'], 
                sort='ASC'
            )
            
        response = [{
            'ride_id': ride[0],
            'currentLocation': {
                'N': ride[2][1],
                'W': ride[2][0]
            },
            'distance': ride[1] + 'km.'
        } for ride in acceptable_rides]
    else:
        response = { 'message': 'No driverId Provided.' }
    
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
