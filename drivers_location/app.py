import json
import boto3
import os
from faker import Faker

# import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DRIVERS_TABLE'])

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

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
