import json
import boto3
import os
import datetime 
import redis

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key #, Attr

client = boto3.resource(
   'dynamodb',
   region_name=os.environ['DEFAULT_REGION'],
)

r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
            charset='utf-8', decode_responses=True, db=0)
table = client.Table(os.environ["RIDES_TABLE"])

def lambda_handler(event, context):
    params = event.get("pathParameters")
    driverId = params.get('driverId')
    rideId = params.get('rideId')
    
    body = json.loads(event.get('body'))
    
    acceptLocation = {
        'N': body['acceptLocation']['N'],
        'W': body['acceptLocation']['W']
    }
    
    if driverId and rideId and acceptLocation:
        dateNow = str(datetime.datetime.now().isoformat())
        update_ride_table=table.update_item(
            Key={
                'ride_id': rideId
            },
            ExpressionAttributeNames={
                '#RS': 'ride_status',
                '#DI': 'driver_id',
                '#TS': 'timestamp'
            },
            ExpressionAttributeValues={
                ':s': 'accepted',
                ':di': driverId,
                ':ts': dateNow
            },
            UpdateExpression="set #RS=:s, #DI=:di, #TS=:ts",
        )
        
        record = r.hgetall('bookingHash:'+rideId)
        print(record)
        
        response = {
            "rideId": rideId,
            "acceptLocation": acceptLocation,
            "createAt": dateNow
        }
        
        # r.hmset('bookings:'+item['ride_id'], item)
        # r.hmset('bookingHash:'+rideId, 
        #     {
        #         'state':'accepted', 
        #         'rideId': rideId, 
        #         'driverId': driverId
        #     }
        # )
        # r.zrem('ridesGeoPending:', rideId)
        # r.hset('riderBooking:'+record['userId'], rideId)   
        # r.hset('driverBooking:'+driverId, rideId )
    # else:
    #     response = { 'Error':'Ride not found!' }
        
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }