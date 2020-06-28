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
          "riderId": "3B0A79F0-8E4E-4523-A335-2EB98305354F",
          "bookingLocation": {
            "N": "14.553902",
            "W": "121.049565"
          },
          "targetLocation": {
            "N": "14.558168",
            "W": "121.054201"
          }
        }
        #request for a book ride
        r = requests.post(
          data['api_url'] + '/rides/', 
          json=payload, 
          headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'}
        )
        value = json.loads(r.text)
        # print('value: ', value, str(type(value)))
        assert r.text and value['state'] == 'pending'
        return value['rideId']