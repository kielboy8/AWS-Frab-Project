import json
import boto3
import os

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key #, Attr

client = boto3.resource(
   'dynamodb',
   region_name=os.environ['DEFAULT_REGION'],
)

table = client.Table(os.environ["RIDES_TABLE"])
table2 = client.Table(os.environ["DRIVERS_TABLE"])

def lambda_handler(event, context):
    driverId = event.get('driverId')
    rideId = event.get('rideId')
    
    update_ride_table=table.update_item(
        Key={
            'ride_id': rideId
        },
        ExpressionAttributeNames={
            '#RS': 'ride_status',
        },
        ExpressionAttributeValues={
            ':s': 'Found a driver',
        },
        UpdateExpression="set #RS=:s",
    )
    
    update_driver_table=table2.update_item(
        Key={
            'driver_id': driverId
        },
        ExpressionAttributeNames={
            '#DS': 'driver_status',
        },
        ExpressionAttributeValues={
            ':s': 'Booked to a ride',
        },
        UpdateExpression="set #DS=:s",
    )
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "rideId": rideId,
            "driverId": driverId,
            "rideStatus": 'Found a driver',
        }),
    }