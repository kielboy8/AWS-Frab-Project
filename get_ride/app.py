import json
import boto3
import os
import uuid
import datetime

dynamodb = boto3.client("dynamodb", os.environ['DEFAULT_REGION'])
sqs = boto3.client('sqs', os.environ['DEFAULT_REGION'])

def lambda_handler(event, context):
    params = event.get("pathParameters")
    rideId = params.get('driverId')

    response = sqs.receive_message(
        QueueUrl=os.environ['BOOKING_QUEUE'],
        MaxNumberOfMessages=5,
        VisibilityTimeout=0,
        WaitTimeSeconds=1
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "rides": response.get('Messages', None)
        }),
    }
