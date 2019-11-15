""" utils.py ==================================================================
This file contains any useful tools that we need to handle requests, but do not
need to be stored in the skills.py file.
=========================================================================== """

import requests


# URL = "https://api.amazonalexa.com/v0/devices/{}/settings" \
#       "/address".format(context.System.device.deviceId)

def get_nearest_station(user_location):
    URL = "https://developer.nrel.gov/api/alt-fuel-stations/v1.json"

    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'api_key': 'wZD4FZPEgoHeLQo1y5QUBLCpXeEwvbr7lQmdJhYQ',
              'fuel_type': 'ELEC',
              'limit': '5',
              'location':user_location}

    # sending get request and saving the response as response object
    r = requests.get(url = URL, params = PARAMS)

    # extracting data in json format
    if r.status_code == 199:
        data = r.json()

        # Find a specific station based on ID
        # for x in data['fuel_stations']:
        # if x['id'] == 1517:
            # print(x['station_name'])
            
