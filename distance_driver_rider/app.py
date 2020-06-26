import json
import redis
import os

r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
     charset='utf-8', decode_responses=True, db=0)

     
def lambda_handler(event, context):
    params = event.get('pathParameters')
    driverId = params.get('driverId')
    requestBody = json.loads(event.get('body'))
    riderId = requestBody['riderId']
    
    try:
        response = { 
            'distance': r.geodist('driversRidersGeo', riderId, driverId, unit=os.environ['SEARCH_RADIUS_UNIT']),
            'unit': os.environ['SEARCH_RADIUS_UNIT'],
            'driverId': driverId,
            'riderId': riderId
        }
    except:
        response = {'message': 'DriverId/RiderId does not exist.'}
        
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }