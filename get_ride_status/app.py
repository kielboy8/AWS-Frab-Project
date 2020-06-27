import json
import boto3
import os
import uuid
import datetime as dt
import redis
import dateutil.parser

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key #, Attr

client = boto3.resource(
   'dynamodb',
   region_name=os.environ['DEFAULT_REGION'],
)

ridesTbl = client.Table(os.environ["RIDES_TABLE"])

r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'],
    charset='utf-8', decode_responses=True, db=0)


def lambda_handler(event, context):
    params = event.get("pathParameters")
    rideId = params.get('rideId')
    
    if rideId:
        #check if record exists in the cache
        rideRec = r.hgetall('bookingHash:'+rideId)
        if rideRec:
            response = {
                'state': rideRec['state'],
                'rideId': rideRec['rideId'], 
                'driverId': rideRec['driverId']
            }
        else:
            #look at the dynamodb
            result = ridesTbl.query(
                KeyConditionExpression=Key('ride_id').eq(rideId)
            )
            
            if len(result['Items']) > 0:
                datenow = dt.datetime.now()
                item = result['Items'][0]
                timestamp_obj = dateutil.parser.isoparse(item['timestamp'])
                if timestamp_obj + dt.timedelta(seconds=int(os.environ['RIDES_TTL'])) < datenow \
                    and item['ride_status'] == 'pending' and item['driver_id'] == '':
                    response = {
                        'rideId': rideId,
                        'state': 'pending_failure',
                        'driverId': item['driver_id']
                    } # booking expired
                else:
                    item = result['Items'][0]
                    response = {
                        'rideId': item['ride_id'],
                        'state': item['ride_status'],
                        'driverId': item['driver_id']
                    }
                    r.hmset('bookingHash:'+item['ride_id'], item)
            else:
                response = {'error':'Ride Not Found.'}
    else:
        response = { 'error': 'Please provide a Ride ID.' }

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }