import json

import pytest
import requests

from .test_book_ride import test_book_ride 
from .test_ride_status import test_ride_status
# from .test_get_ride import test_get_ride
# from .accept_ride import accept_ride

value = None

def test_book_sched_algo():
     with open('config.json') as json_data:
        data = json.loads(json_data.read())
        json_data.close()
        value = test_book_ride()
        print('rideId: ' + value)
        assert True == True
        