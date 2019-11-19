""" utils.py ==================================================================
This file contains any useful tools that we need to handle requests, but do not
need to be stored in the skills.py file.
=========================================================================== """
from datetime import datetime
from config import logger, settings
import requests, json

def parse_user_loc(req_envelope):
    """ Check if user's alexa device supports geolocation. """
    try:
        if req_envelope.context.system.device.supported_interfaces.geolocation:
            # Grab our geolocation info.
            geo_object = req_envelope.context.geolocation
            req_timestamp = str(req_envelope.request.timestamp)

            # Validate our geodata is accurate and fresh.
            try:
                freshness = (datetime(req_timestamp) - datetime(geo_object.timestamp)) / 1000
                logger.debug(freshness)
            except:
                logger.debug(("Freshness check failed!",
                              req_timestamp, type(req_timestamp),
                              geo_object.timestamp, type(geo_object.timestamp)))
                freshness = 1
            ACCURACY_THRESHOLD = 100 # accuracy of 100 meters required
            if ( geo_object and geo_object.coordinate
                and geo_object.coordinate.accuracy_in_meters < ACCURACY_THRESHOLD
                and freshness < 60 ):
                return (geo_object.coordinate.latitude_in_degrees,
                        geo_object.coordinate.longitude_in_degrees)
            else:
                logger.debug("Geodata validation failed.")
                return False
        else:
            logger.debug("Geodata not available.")
            return False
    except ServiceException:
        logger.debug("ServiceException error.")
        return False,
    except Exception as e:
        raise e


def parse_device_loc(req_envelope, service_client_fact):
    """ Check if user's alexa device supports geolocation. """
    try:
        # Grab the device's registered address.
        device_id = req_envelope.context.system.device.device_id
        device_addr_client = service_client_fact.get_device_address_service()
        addr = device_addr_client.get_full_address(device_id)

        # Check if an address exists and return it.
        if addr.address_line1 and addr.state_or_region:
            address = '{}, {}, {}'.format(addr.address_line1,
                                          addr.state_or_region,
                                          addr.postal_code)
            return convert_to_geo(address)
        else:
            logger.debug("Device address not available.")
            return False
    except ServiceException:
        logger.debug("ServiceException error.")
        return False,
    except Exception as e:
        raise e


def get_station_list(location, station_filter):
    """ Uses the NREL Developer network to fetch a list of charging stations.
        Visit their site for more info: https://developer.nrel.gov/docs/ """

    # Base URL for accessing the NREL API
    URL = settings['NREL']['BASE_URL']

    # Our default parameters to use when querying the API.
    PARAMS = {'api_key': settings['NREL']['API_KEY'],
              'fuel_type': 'ELEC'}

    # Parse out location data and add it to the parameters.
    if type(location) is str:
        PARAMS.update({"location": location})
    else:
        PARAMS.update({"latitude": location[0], "longitude": location[1]})

    # Add our user-specified paramaters.
    PARAMS.update(station_filter)

    # Send GET request and return the response as a JSON object.
    r = requests.get(url = URL, params = PARAMS)
    return r.json()


def get_yelp_results(location, keyword):
    """ """
    logger.debug((location,keyword))
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {'Authorization': 'Bearer 3tndetBH2hPx7pG7GCnkX4ngU20Ubr31oqhQX9z6PEA_zZWKXBsAp0gLRZNj2FzitgEkKwYqsky6GuggN9PgQCEd063T1zZIM8e76604WIEjhe2tWjGOGRw1FQDSXXYx'}

    params = {'term': keyword,
              'location': location,
              'radius': '840'}

    # Send GET request and return the response as a JSON object.
    r = requests.get(url=url, params=params, headers=headers)
    data = r.json()

    return data


def get_distance(point_a, point_b):
    """ Uses the HERE Developer API to gather route information. Visit their
    site for more info: https://developer.here.com/documentation/ """

    # Need to properly format our waypoints before sending them to the API
    waypoint0 = 'geo!{}{}'.format(point_a[0],point_a[1])
    waypoint1 = 'geo!{}{}'.format(point_b[0],point_b[1])

    # Base URL for accessing the HERE API
    URL = settings['HERE']['BASE_URL']
    # Our default parameters to use when querying the API.
    PARAMS = {'app_id': settings['HERE']['APP_ID'],
              'app_code': settings['HERE']['APP_ID'],
              'mode': 'fastest;car;traffic:disabled',
              'waypoint0': waypoint0,
              'waypoint1': waypoint1}

    # Parse out location data and add it to the parameters.
    if location['type'] == 'geo':
        PARAMS.update({"latitude": location['location'][0],
                       "longitude": location['location'][1]})
    else:
        PARAMS.update({"location":location[1]})

    # sending get request and saving the response as response object
    r = requests.get(url = URL, params = PARAMS)
    return r.json()
