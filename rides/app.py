import json
import boto3
import os
import uuid
import datetime

dynamodb = boto3.client("dynamodb", os.environ['DEFAULT_REGION'])
sqs = boto3.client('sqs', os.environ['DEFAULT_REGION'])

def lambda_handler(event, context):
    body = json.loads(event['body'])
    body['ride_id'] = uuid.uuid4().hex
    body['timestamp'] = str(datetime.datetime.now())
    
    sqs.send_message(
        QueueUrl=os.environ['BOOKING_QUEUE'],
        MessageBody=str(body),
        MessageGroupId=body['ride_id'] #For Fifo
    )
    
    response = dynamodb.put_item(
        TableName=os.environ['RIDES_TABLE'],
        Item={
            'ride_id': {
                'S': body['ride_id']
            },
            'pickup_point': {
                'S':  body['pickupPoint']  
            },
            'dropoff_point': {
                'S': body['dropoffPoint']
            },
            'rider_id': {
                'S': body['riderID']
            },
            'timestamp': {
                'S': body['timestamp']
            },
            'ride_status': {
                'S': 'Booked'
            }
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            # "bookingSuccessful": True if response else False,
            "rideId": body['ride_id'],
            # "rideStatus": 'Booked'
            # "message": [body, str(type(body))],
        }),
    }
