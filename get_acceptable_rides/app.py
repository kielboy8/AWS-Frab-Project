import json
import boto3
import os
import uuid
import datetime
import redis 

dynamodb = boto3.client("dynamodb", os.environ['DEFAULT_REGION'])


def lambda_handler(event, context):
    response = []
    params = event.get("pathParameters")
    rideId = params.get('driverId')

    #Fetch Last Location of Driver
    
    #From Cache
    
    #From DB
    
    #georadius GET os.environ['RIDE_ACCEPTABLE_COUNT']
    
    #return 10
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
