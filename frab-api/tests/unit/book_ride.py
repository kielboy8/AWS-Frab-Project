import json

import pytest
import requests

value = None

def book_ride():
    with open('config.json') as json_data:
        data = json.loads(json_data.read())
        json_data.close()
        
        #Book Ride
        payload = {
            "riderID": "1",
            "pickupPoint": "14.5521547,121.0518483",
            "dropoffPoint": "14.5538455,121.0502196"
        }
        r = requests.post(data['api_url'] + '/rides/', json=payload)
        value = json.loads(r.text)
      
        assert r.text != None
        return value['rideId']