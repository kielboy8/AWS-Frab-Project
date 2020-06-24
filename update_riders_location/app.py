import json
import boto3
import os
import redis

# import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['RIDERS_TABLE'])
redis_endpoint = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], db=0)

def lambda_handler(event, context):
    params = event.get('pathParameters')
    riderId = params.get('riderId')
    requestBody = json.loads(event.get('body'))
    
    riderLocId = table.get_item(
        Key={
            'rider_id': riderId
        },
        ProjectionExpression='location_id'
    )
    
    redis_endpoint.geoadd(
        'riders', 
        requestBody['updatedLocation']['N'], 
        requestBody['updatedLocation']['W'], 
        riderLocId['Item']['location_id']
    )
    
    result = redis_endpoint.geopos('riders', riderLocId['Item']['location_id'])
    
    redis_result_body = {
        'N': result[0][0],
        'W': result[0][1]
    }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "locationId": riderLocId['Item']['location_id'],
            "updatedLocation": redis_result_body
            # "location": ip.text.replace("\n", "")
        }),
    }
