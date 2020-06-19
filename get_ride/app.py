import json
import boto3
import os
import uuid
import datetime

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key #, Attr

client = boto3.resource(
   'dynamodb',
   region_name=os.environ['DEFAULT_REGION'],
)

table = client.Table(os.environ["RIDES_TABLE"])

def lambda_handler(event, context):
    params = event.get("pathParameters")
    rideId = params.get('rideId')
    if rideId:
        result = table.query(
            ProjectionExpression='ride_status',
            KeyConditionExpression=Key('ride_id').eq(rideId)
        )
        response = result['Items'][0] if len(result['Items']) > 0 else 'Ride Not Found.'
    else:
        response = { 'error': 'Please provide a Ride ID.' }

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
