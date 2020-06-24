import json
import boto3
import os
from faker import Faker

# import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DRIVERS_TABLE'])

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
    
    responseBody = {
        'N': requestBody['updatedLocation']['N'],
        'W': requestBody['updatedLocation']['W']
    }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "driverId": driverId,
            "updatedLocation": responseBody,
            # "location": ip.text.replace("\n", "")
        }),
    }
