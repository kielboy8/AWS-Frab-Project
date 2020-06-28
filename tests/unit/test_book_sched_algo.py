import json

import pytest
import requests

value = None
data = ''
with open('config.json') as json_data:
    data = json.loads(json_data.read())
    json_data.close()

@pytest.mark.run(order=1)
def test_book_ride():
    global data
    global value
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
    resp = json.loads(r.text)
    print('resp: ', resp, str(type(resp)))
    assert r.text and resp['state'] == 'pending'
    value = resp['rideId']

@pytest.mark.run(order=2)
def test_ride_status():
    global value
    global data
    r = requests.get(data['api_url']+'/rides/'+value, headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
    rdict = json.loads(r.text)
    print('response in ride status: ', rdict)
    # assert True == True
    assert rdict['state'] == 'pending' 