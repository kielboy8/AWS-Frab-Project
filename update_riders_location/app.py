import json
import boto3
import os
import redis
from uuid import uuid4

# import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['RIDERS_TABLE'])
redis_endpoint = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], db=0)

def lambda_handler(event, context):
    params = event.get('pathParameters')
    riderId = params.get('riderId')
    requestBody = json.loads(event.get('body'))
    
    riderLocId = None
    
    try:
        riderLocId = table.get_item(
            Key={
                'rider_id': riderId
            },
            ProjectionExpression='location_id'
        )['Item']['location_id']
    except:
        riderLocId = str(uuid4())
        response = table.put_item(
            Item={
                'rider_id': riderId,
                'location_id': riderLocId 
            }
        )
    
    redis_endpoint.geoadd(
        'riders', 
        requestBody['updatedLocation']['N'], 
        requestBody['updatedLocation']['W'], 
        riderId
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "locationId": riderLocId,
            "updatedLocation": requestBody['updatedLocation']
        }),
    }
