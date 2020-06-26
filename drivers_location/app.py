import json
import boto3
import os
import redis
from uuid import uuid4

# import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DRIVERS_TABLE'])
redis_endpoint = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], db=0)

def lambda_handler(event, context):
    params = event.get('pathParameters')
    driverId = params.get('driverId')
    requestBody = json.loads(event.get('body'))
    
    driverLocId = None
    
    try:
        driverLocId = table.get_item(
            Key={
                'driver_id': driverId
            },
            ProjectionExpression='location_id'
        )['Item']['location_id']
    except:
        driverLocId = str(uuid4())
        response = table.put_item(
            Item={
                'driver_id': driverId,
                'location_id': driverLocId 
            }
        )
    
    redis_endpoint.geoadd(
        'driversGeo', 
        requestBody['updatedLocation']['N'], 
        requestBody['updatedLocation']['W'], 
        driverId
    )
    
    # result = redis_endpoint.geopos('driversGeo', driverId)
    
    # redis_result_body = {
    #     'N': result[0][0],
    #     'W': result[0][1]
    # }
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "locationId": driverLocId,
            "updatedLocation": requestBody['updatedLocation']
            # "location": ip.text.replace("\n", "")
        }),
    }
