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

table = client.Table(os.environ["RIDES_TABLE"])
table2 = client.Table(os.environ["DRIVERS_TABLE"])

def lambda_handler(event, context):
    params = event.get("pathParameters")
    rideId = params.get('rideId')
    driverId = params.get('driverId')
    request = json.loads(event.get('body'))
    
    acceptLocation = {
        'N': request['acceptLocation']['N'],
        'W': request['acceptLocation']['W']
    }
    
    dateNow=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    createAt=str(dateNow.isoformat())
    
    update_ride_table=table.update_item(
        Key={
            'ride_id': rideId
        },
        ExpressionAttributeNames={
            '#RS': 'ride_status',
            '#TS': 'timestamp',
        },
        ExpressionAttributeValues={
            ':s': 'Accepted',
            ':ts': createAt,
        },
        UpdateExpression="set #RS=:s, #TS=:ts",
    )
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "rideId": rideId,
            "acceptLocation": acceptLocation,
            "createAt": createAt,
        }),
    }