import json
import boto3
import os
import uuid
import datetime as dt
import redis

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key #, Attr

client = boto3.resource(
   'dynamodb',
   region_name=os.environ['DEFAULT_REGION'],
)

table = client.Table(os.environ["RIDES_TABLE"])

r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], db=0)


def lambda_handler(event, context):
    params = event.get("pathParameters")
    rideId = params.get('rideId')
    
    if rideId:
        #check if record exists in the cache
        rideRec = r.hgetall('bookingHash:'+rideId)
        if rideRec:
            rideRec =  { key.decode(): val.decode() for key, val in rideRec.items() }
            response = {
                'state': rideRec['state'], 
                'rideId': rideRec['ride_id'], 
                'driverId': rideRec['driver_id']
            }
        else:
            #look at the dynamodb
            result = table.query(
                KeyConditionExpression=Key('ride_id').eq(rideId)
            )
            
            if result['Items'][0] and len(result['Items']) > 0:
                datenow = dt.datetime.now()
                timestamp_obj = dt.datetime.fromisoformat(result['Items'][0]['timestamp'])
                if timestamp_obj + dt.timedelta(seconds=120) < datenow \
                    and result['Items'][0]['ride_status'] == 'pending':
                    response = 'pending_failure' # driver not found
                else:
                    item = result['Items'][0]
                    response = {
                        'rideId': item['ride_id'],
                        'state': item['ride_status'],
                        'driverId': item['driver_id']
                    }
                    r.hmset('bookings:'+item['ride_id'], item)
            else:
                response = 'Ride Not Found.'
    else:
        response = { 'error': 'Please provide a Ride ID.' }

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }
