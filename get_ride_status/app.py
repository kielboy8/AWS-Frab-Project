import json
import boto3
import os
import uuid
import datetime as dt

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
            KeyConditionExpression=Key('ride_id').eq(rideId)
        )
        
        if result['Items'][0] and len(result['Items']) > 0:
            datenow = dt.datetime.now()
            # timestamp_obj = dt.datetime.strptime(result['Items'][0]['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            timestamp_obj = dt.datetime.fromisoformat(result['Items'][0]['timestamp'])
            if timestamp_obj + dt.timedelta(seconds=120) < datenow and result['Items'][0]['ride_status'] == 'pending':
                response = 'pending_failure' # driver not found
            else:
                response = result['Items'][0]
        else:
            response = 'Ride Not Found.'
    else:
        response = { 'error': 'Please provide a Ride ID.' }

    return {
        "statusCode": 200,
        "body": json.dumps({
            'rideId': response['ride_id'],
            'state': response['ride_status'],
            'driverId': response['driver_id']
        }),
    }
