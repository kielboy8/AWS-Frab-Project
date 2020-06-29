import json

import pytest
import requests

value = None
value2 = None
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

@pytest.mark.run(order=3)
def test_driver_location():
    global data
    global value
    
    #Update driver location
    payload = {
      "updatedLocation": {
        "N": "14.558168",
        "W": "121.054201"
      }
    }
    
    r = requests.put(
      data['api_url']+'/drivers/'+'18c1305e-2a7d-4e6f-9d64-7a37cefd2bd2'+'/locations/',
      json=payload,
      headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'}
    )
    resp = json.loads(r.text)
    print('resp: ', resp, str(type(resp)))
    assert json.dumps(resp['updatedLocation']) == '{"N": "14.558168", "W": "121.054201"}'


@pytest.mark.run(order=4)
def test_acceptable_rides():
    global value
    global data
    r = requests.get(data['api_url']+'/drivers/'+'18c1305e-2a7d-4e6f-9d64-7a37cefd2bd2'+'/rides/acceptable/', 
    headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
    rdict = json.loads(r.text)
    print('acceptable rides: ', rdict)
    print('type: ', type(rdict))
    print('value: ',)
    assert rdict[0]['ride_id'] == value   
    

@pytest.mark.run(order=5)
def test_get_rider_location():
    global data
    global value
    
    r = requests.get(
      data['api_url']+'/riders/'+'3B0A79F0-8E4E-4523-A335-2EB98305354F',
      headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'}
    )
    resp = json.loads(r.text)
    print('resp: ', resp, str(type(resp)))
    assert json.dumps(resp['currentLocation']) == '{"N": "14.558168","W": "121.054201"}'  
    