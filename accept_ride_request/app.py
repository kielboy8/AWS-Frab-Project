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
#r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], db=0)
table = client.Table(os.environ["RIDES_TABLE"])

def lambda_handler(event, context):
    params = event.get("pathParameters")
    driverId = params.get('driverId')
    rideId = params.get('rideId')
    
    #body = json.loads(event['body'])
    body = json.loads(event.get('body'))
    #request = json.loads(body['acceptLocation'])
    
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
        
        response = {
            "rideId": rideId,
            "acceptLocation": acceptLocation,
            "createAt": dateNow
        }
<<<<<<< HEAD
        # print(str(r))
        # print(r.get('ridesGeoPending'))
        #     # r.geoadd('ridesGeoPending', 
        #     #     float(bookingLocation['W']), 
        #     #     float(bookingLocation['N']), 
        #     #     body['ride_id']) #Lon, Lat        
        
        #r.get('ridesGeoPending')
        
=======

>>>>>>> 620245dcee079cb465e7c98bd57ae54f8ae984c0
        r.zrem('ridesGeoPending', rideId)
        r.hset('bookings': rideId,
            {
                'state':'accepted', 
                'driverId': driverId
            }
        )
        
        
    # else:
    #     response  = ("Invalid")
        
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }