import json
import boto3
import os
import datetime 

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key #, Attr

client = boto3.resource(
   'dynamodb',
   region_name=os.environ['DEFAULT_REGION'],
)

sqs = boto3.client('sqs', os.environ["BOOKING_QUEUE"])
table = client.Table(os.environ["RIDES_TABLE"])
table2 = client.Table(os.environ["DRIVERS_TABLE"])
table3  = client.Table(os.environ["LOCATIONS_TABLE"])

def lambda_handler(event, context):
    params = event.get("pathParameters")
    driverId = params.get('driverId')
    rideId = params.get('rideId')
    
    body = json.loads(event['body'])
    acceptLocation = json.loads(body['acceptLocation'])
    
    if driverId and rideId and acceptLocation:
        dateNow = str(datetime.datetime.now().isoformat())
        update_ride_table=table.update_item(
            Key={
                'ride_id': rideId
            },
            ExpressionAttributeNames={
                '#RS': 'ride_status',
                '#AA': 'accepted_at',
                '#AL': 'accepted_location'
            },
            ExpressionAttributeValues={
                ':s': 'accepted',
                ':aa': dateNow,
                ':al': str(acceptLocation)
            },
            UpdateExpression="set #RS=:s, #AA=:aa, #AL=:al",
        )
        
        update_driver_table=table2.update_item(
            Key={
                'driver_id': driverId
            },
            ExpressionAttributeNames={
                '#DS': 'current_ride',
                '#CL': 'current_location'
            },
            ExpressionAttributeValues={
                ':s': rideId,
                ':cc': str(acceptLocation),
            },
            UpdateExpression="set #DS=:s",
        )
        
        #Delete Message from Queue
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "rideId": rideId,
            "acceptLocation": str(acceptLocation),
            "rideStatus": 'Found a driver',
        }),
    }