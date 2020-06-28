import json

import pytest
import requests

from .book_ride import book_ride 
from .ride_status import ride_status
from .accept_ride import accept_ride
from .update_driver_location import update_driver_location
from .update_rider_location import update_rider_location
from .get_rider_location import get_rider_location
from .get_distance import get_distance

# from .test_get_ride import test_get_ride
# from .accept_ride import accept_ride

value = None

def test_book_sched_algo():
     with open('config.json') as json_data:
        data = json.loads(json_data.read())
        json_data.close()
        
        #Book a ride
        rideId = book_ride()
        print('RideId in Test Suite: ', rideId)
        #Get Ride Status
        ride_status(rideId)
        #Accept a Ride
        assert True == True
        