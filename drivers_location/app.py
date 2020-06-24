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

    faker = Faker()
    latitude = faker.latitude()
    longitude = faker.longitude()

    response = table.put_item(
        Item={
            'driver_id': driverId,
            'latitude': latitude,
            'longitutde': longitude
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "driverId": driverId,
            "latitude": str(latitude),
            "longitude": str(longitude)
            # "location": ip.text.replace("\n", "")
        }),
    }
