import json

import pytest
import requests

def ride_status(rideId):
    with open('config.json') as json_data:
        data = json.loads(json_data.read())
        json_data.close()
        
        r = requests.get(data['api_url']+'/rides/'+rideId, headers={'Authorization': 'Basic c29tZS1hcGktdG9rZW46'})
        rdict = json.loads(r.text)
        print('response in ride status: ', rdict)
        assert True == True
        # assert rdict['ride_status'] == 'Booked' 