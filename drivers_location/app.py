import json
import boto3
import os
from faker import Faker
import redis

# import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DRIVERS_TABLE'])
# redis_endpoint = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], db=0)

def lambda_handler(event, context):
    params = event.get('pathParameters')
    driverId = params.get('driverId')
    requestBody = json.loads(event.get('body'))

    response = table.put_item(
        Item={
            'driver_id': driverId,
            'latitude': requestBody['updatedLocation']['N'],
            'longitude': requestBody['updatedLocation']['W']
        }
    )
    
    # redis_endpoint.geoadd('rides', '121.0463828', '14.5543191', 'Globe Telecom')
    
    # result = redis_endpoint.geopos('rides', 'Globe Telecom')
    
    # redis_result_body = {
    #     'N': result[0][0],
    #     'W': result[0][1]
    # }
    
    responseBody = {
        'N': requestBody['updatedLocation']['N'],
        'W': requestBody['updatedLocation']['W']
    }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "driverId": driverId,
            "updatedLocation": responseBody,
            # "location_response": redis_result_body
            # "location": ip.text.replace("\n", "")
        }),
    }
