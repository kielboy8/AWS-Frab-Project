import json

import pytest
import requests

value = None
value2 = None
data = ''
with open('config.json') as json_data:
    data = json.loads(json_data.read())
    json_data.close()
    
# @pytest.mark.skip(reason="no way of currently testing this")
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
    
# @pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.run(order=2)
def test_ride_status():
    global value
    global data
    r = requests.get(data['api_url']+'/rides/'+value, headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
    rdict = json.loads(r.text)
    print('response in ride status: ', rdict)
    # assert True == True
    assert rdict['state'] == 'pending' 
    
# @pytest.mark.skip(reason="no way of currently testing this")
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
    assert json.dumps(resp['updatedLocation']) == '{"N": "14.558168", "W": "121.054201"}'

# @pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.run(order=4)
def test_acceptable_rides():
    global value
    global data
    r = requests.get(data['api_url']+'/drivers/'+'18c1305e-2a7d-4e6f-9d64-7a37cefd2bd2'+'/rides/acceptable/', 
    headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
    rdict = json.loads(r.text)
    assert rdict[0]['ride_id'] == value   

# @pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.run(order=4)
def test_accept_ride():
    global data
    global value
    #Book Ride
    payload = {
      "acceptLocation": {
        "W": "121.052958",
        "N": "14.549637"
      }
    }
    
    r = requests.put(data['api_url'] + '/drivers/18c1305e-2a7d-4e6f-9d64-7a37cefd2bd2/rides/'+value+'/accept/', 
    json=payload, headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
    respAccept = json.loads(r.text)
    
    r = requests.get(data['api_url']+'/rides/'+value, headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
    rdict = json.loads(r.text)
    assert rdict['state'] == 'accepted' 

# @pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.run(order=5)
def test_if_driver_is_in_bookingLocation():
    global data
    payload = {
      "updatedLocation": {
      "N": "14.553902",
      "W": "121.049565"
      }
    }
    r = requests.put(
      data['api_url']+'/drivers/18c1305e-2a7d-4e6f-9d64-7a37cefd2bd2/locations',
      json=payload,
      headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'}
    )
    resp = json.loads(r.text)
    
    assert json.dumps(resp['updatedLocation']) == json.dumps(payload['updatedLocation'])
    
# @pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.run(order=6)
def test_if_ride_state_is_in_progress():
    global value
    global data
    r = requests.get(data['api_url']+'/rides/'+value, headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
    rdict = json.loads(r.text)
    print('response in ride status: ', rdict)
    # assert True == True
    assert rdict['state'] == 'in_progress' 
    
@pytest.mark.run(order=7)
def test_if_driver_is_in_targetLocation():
    global data
    global value
    payload = {
      "updatedLocation": {
        "N": "14.558168",
        "W": "121.054201"
      }
    }
    
    r = requests.put(
      data['api_url']+'/drivers/'+'18c1305e-2a7d-4e6f-9d64-7a37cefd2bd2'+'/locations',
      json=payload, 
      headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'}
    )
    resp = json.loads(r.text)
    print('resp: ', resp)
    assert json.dumps(resp['updatedLocation']) == json.dumps(payload['updatedLocation'])

@pytest.mark.run(order=8)
def test_check_ride_complete():
    global value
    global data
    # print('value: ', value)
    r = requests.get(data['api_url']+'/rides/'+value, headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
    resp = json.loads(r.text)
    # print('resp: ', resp)
    assert resp['state'] == "complete_success"
    
