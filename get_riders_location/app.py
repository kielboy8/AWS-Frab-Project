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
    
    try:
        riderLocId = table.get_item(
            Key={
                'rider_id': riderId
            },
            ProjectionExpression='location_id'
        )
        
        result = redis_endpoint.geopos('riders', riderLocId['Item']['location_id'])
        
        redis_result_body = {
            'N': result[0][0],
            'W': result[0][1]
        }
        return {
            "statusCode": 200,
            "body": json.dumps({
                "riderId": riderId,
                "locationId": riderLocId['Item']['location_id'],
                "currentLocation": redis_result_body
                # "location": ip.text.replace("\n", "")
            }),
        }
    except:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID does not exist."
                # "location": ip.text.replace("\n", "")
            }),
        }