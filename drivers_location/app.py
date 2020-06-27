import json
import boto3
import os
import redis
from uuid import uuid4
import datetime 


dynamodb = boto3.resource('dynamodb')
driversTbl = dynamodb.Table(os.environ['DRIVERS_TABLE'])
ridesTbl = dynamodb.Table(os.environ['RIDES_TABLE'])
ridersTbl = dynamodb.Table(os.environ['RIDERS_TABLE'])

r = redis.Redis(host=os.environ['ELASTICACHE_HOST'], port=os.environ['ELASTICACHE_PORT'], 
     charset='utf-8', decode_responses=True, db=0)

def validate_coord(coord):
    try:
        if coord.get('W') and coord.get('N') and \
        (float(coord.get('W')) > -180 and float(coord.get('W')) < 180) and \
        (float(coord.get('N')) > -90 and float(coord.get('N')) < 90):
            return True
    except:
        return False

def lambda_handler(event, context):
    params = event.get('pathParameters')
    driverId = params.get('driverId')
    requestBody = json.loads(event.get('body'))
    response = 'Invalid Input.'
    driverLocId = str(uuid4().hex)
    timestamp = str(datetime.datetime.now().isoformat())
    
    if validate_coord((requestBody['updatedLocation'])):
        try:
            driverLocId = driversTbl.get_item(
                Key={
                    'driver_id': driverId
                },
                ProjectionExpression='location_id'
            )['Item']['location_id']
        except:
            driversTbl.put_item(
                Item={
                    'driver_id': driverId,
                    'location_id': driverLocId,
                    'ride_id': '',
                    'last_location_timestamp': timestamp
                }
            )
        
        r.geoadd(
            'driversRidersGeo', 
            requestBody['updatedLocation']['W'],
            requestBody['updatedLocation']['N'],
            driverId
        )
        
        #Check if has current ride in cache
        currentRideId = r.get('driverBooking:'+driverId)
        if currentRideId:
            currentRide = r.hgetall('bookingHash:'+currentRideId)
            willExpire = False
            #Create approx calculation for destination
            print('isSame: ',  json.loads(currentRide['bookingLocation']) == requestBody['updatedLocation'])
            print( json.loads(currentRide['bookingLocation']), requestBody['updatedLocation'])
            if (json.loads(currentRide['bookingLocation']) == requestBody['updatedLocation']) or \
                (json.loads(currentRide['targetLocation']) == requestBody['updatedLocation']):
                print('SAME!', currentRide)
                if currentRide['state'] == 'accepted':
                    #Move to In-Progress
                    print('Driver picked up the Rider...')
                    currentRide['state'] = 'in_progress'
                elif currentRide['state'] == 'in_progress':
                    #Finish Ride
                    print('ride complete...')
                    currentRide['state'] = 'complete_success'
                    r.set('driverBooking:'+driverId, '')
                    r.set('riderBooking:'+currentRide['riderId'], '')
                    
                    driversTbl.update_item(
                        Key={
                            'driver_id': driverId
                        },
                        UpdateExpression="SET ride_id = :r",
                        ExpressionAttributeValues={
                            ':r': '',
                        },
                    )
                    
                    ridersTbl.update_item(
                        Key={
                            'rider_id': currentRide['riderId']
                        },
                        UpdateExpression="SET ride_id = :r",
                        ExpressionAttributeValues={
                            ':r': '',
                        },
                    )
                
                print('currentRide HERE!: ', currentRideId, currentRide)
                ridesTbl.update_item(
                    Key={
                        'ride_id': currentRideId
                    },
                    UpdateExpression="set ride_status = :r",
                    ExpressionAttributeValues={
                        ':r': currentRide['state'],
                    },
                )
                print('execution hrere...')
                r.hmset('bookingHash:'+currentRideId, {**currentRide, 'state': currentRide['state'] })
                
                willExpire and r.expire('bookingHash:'+currentRideId, 120)
                
        response = {
            "locationId": driverLocId,
            "updatedLocation": requestBody['updatedLocation'],
            "createdAt": timestamp
        }
        
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }