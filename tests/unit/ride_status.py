import json

import pytest
import requests

def ride_status(rideId):
    with open('config.json') as json_data:
        data = json.loads(json_data.read())
        json_data.close()
        r = requests(data['api_url'], params={'rideId': rideId})
        rdict = json.loads(r.text)
        assert rdict['ride_status'] == 'Booked' 