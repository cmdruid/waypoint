""" skills.py =================================================================
This file contains all of our skill handlers. The incoming data is passed to
each handler in linear order (the order in which the handlers have been added to
the skill builder), and the "can_handle" function will check to see if it can
handle the nature of the request. If so, the "handle" function will process the
request and construct a response to send back to the alexa service.
============================================================================ """

# We need to import some stuff
import requests, json

from config import logger, settings
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model.services import ServiceException
from utils import ( parse_user_loc, parse_device_loc, get_station_list,
                    parse_station_list )


# Rough implementation of debug mode. Need to refine.
debugMode = settings['Debug']['debugMode']
loc_debug = settings['Debug']['Lat'], settings['Debug']['Long']

# This is where we'll store our response dialogue strings. This is a bad design.
# We need to move these to a separate file.
WELCOME_MSG = """ Welcome to my charging station skill. You can say things like,
           find me the nearest charging station, or Id like to stop at a
           charging station with coffee nearby. """

WELCOME_DEBUG = "Debug mode enabled."

ASK = "What do you want to ask?"

CONFIRM_CORRECT = "Is that correct?"

MISSING_PERMISSIONS = ("Please enable Location permissions in "
                              "the Amazon Alexa app.")

MISSING_LOCATION = "It looks like I can't find your current location."

ERROR = "Uh Oh. Looks like something went wrong."
LOCATION_FAILURE = ("There was an error with the Device Address API. "
                    "Please try again.")
GOODBYE = "Bye! Thanks for using the Sample Device Address API Skill!"
UNHANDLED = "This skill doesn't support that. Please ask something else"
HELP = ("You can use this skill by asking something like: "
        "whats my address?")

# These are the device permissions we need in order for our skill to work.
# More information can be found at:
# https://developer.amazon.com/docs/custom-skills/device-address-api.html#sample-response-with-permission-card
permissions = ["read::alexa:device:all:address"]


class LaunchRequestHandler(AbstractRequestHandler):
    """ Initial handler for skill launch. """
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        WELCOME = WELCOME_MSG if not debugMode else WELCOME_DEBUG
        handler_input.response_builder.speak(WELCOME).ask(ASK)
        return handler_input.response_builder.response


class GetStationHandler(AbstractRequestHandler):
    """ Handler for getting a list of stations or asking user for
    consent to use their location. """

    # This checks to see which intent was triggered within our voice model.
    def can_handle(self, handler_input):
        return is_intent_name("GetStationIntent")(handler_input)

    # If "can_handle" returns True, then we execute the code block below.
    def handle(self, handler_input):

        # It makes our lives easier to set these variables at the beginning.
        # To better understand these object, please check out this link:
        # https://developer.amazon.com/docs/custom-skills/request-and-response-json-reference.html
        req_envelope = handler_input.request_envelope
        response_builder = handler_input.response_builder
        service_client_fact = handler_input.service_client_factory
        template_factory = handler_input.template_factory

        # Feel free to check out the request.json file generated here so you
        # can get a feel for how the alexa data packet is structured.
        if debugMode and req_envelope:
            with open('instance/request.json', 'w') as writer:
                writer.write(str(req_envelope))

        # If the user permissions and consent token are not present, then we
        # need to prompt the user to give us permission in order to access data
        # on their device. debugMode will bypass this check.
        if not (req_envelope.context.system.user.permissions and
                req_envelope.context.system.user.permissions.consent_token
                and debugMode):
            response_builder.speak(MISSING_PERMISSIONS)
            response_builder.set_card(
                AskForPermissionsConsentCard(permissions=permissions))
            return response_builder.response

        # Check for the user's geolocation data first, then device data, then prompt.
        logger.debug("Fetching user's geo-location...")
        location = parse_geo_loc(req_envelope) if not debugMode else loc_debug
        if not location:
            logger.debug("Failed to grab geolocation! Checking device address...")
            location = parse_device_loc(req_envelope, service_client_fact)
            if not location:
                logger.debug("Failed to grab device location! Prompting user...")
                response_builder.reprompt(MISSING_LOCATION).getResponse()

        # Right now this is a hard-coded filter, but we want to dynamically
        # build it from the user's preferences in the future.
        filter_list = {'ev_network': 'ChargePoint Network',
                       'ev_pricing': 'Free',
                       'radius': '25',
                       'limit': '25'}

        # Fetch a list of charging station based on user's preferences.
        logger.debug("Fetching station list...")
        station_list = get_station_list(location, filter_list)
        logger.debug("Station list received. Dumping to JSON.")
        if debugMode and station_list:
            with open('instance/stations.json', 'w') as writer:
                writer.write(str(station_list))

        # Parse out the junk values that we do not need.
        logger.debug("Cleaning up station list...")
        station_list = parse_station_list(station_list)
        logger.debug("Cleaning complete. Dumping file to disk...")
        if debugMode and station_list:
            with open('instance/station_list.json', 'w') as writer:
                writer.write(str(station_list))

        # Pick the top station. We'll have the user do this later.
        select_station = station_list[1]

        url = "https://api.yelp.com/v3/businesses/search"
        headers = {'Authorization': 'Bearer 3tndetBH2hPx7pG7GCnkX4ngU20Ubr31oqhQX9z6PEA_zZWKXBsAp0gLRZNj2FzitgEkKwYqsky6GuggN9PgQCEd063T1zZIM8e76604WIEjhe2tWjGOGRw1FQDSXXYx'}

        pref = "Stores"
        address = "{}, {}, {} {}".format(select_station['street_address'],
                                      select_station['city'],
                                      select_station['state'],
                                      select_station['zip'])

        params = {'term': '{}'.format(pref),
        'location': '{}'.format(address)}

        # Send GET request and return the response as a JSON object.
        r = requests.get(url=url, params=params, headers=headers)
        data = r.json()

        threshold = 0.3 * 1609.34
        avgRate = 0
        counter = 0
        
        businesses = {}

        #Address, Name, Rating
        for x in data['businesses']:
            if x['distance'] < threshold and x['location']['address1'] != None and x['location']['address1'] != '' :
                print("Name: {} \nRating: {}\nLocation: {}\n\n".format(x['alias'],x['rating'], x['location']['address1']))
                businessses = {x['alias'],x['rating'], x['location']['address1']}
                avgRate += x['rating']
                counter += 1
        avg = avgRate/counter
        print('{}'.format(avg))

        # Speak to user and send to navigation
        distance = select_station['distance']
        distance = round(distance, 2) if distance > 1 else "less than a mile"
        network = select_station["ev_network"]
        pay = "Free" if "Free" in select_station['ev_pricing'] else "Paid"
        hours = "open 24 hours" if "24" in select_station['access_days_time'] else ""

        RESULT = ( "The nearest station is {} away. ".format(distance) +
                   "It is a {} {} station {}. ".format(pay, network, hours) +
                   "The address is {}. ".format(address) + 
                   "Here is some businesses you can check out while you are there:  "+
                   "I'm sending it to your navigation now.")


        response_builder.speak(RESULT).ask("Anything else?")

        if debugMode and response_builder.response:
            with open('instance/response.json', 'w') as writer:
                writer.write(str(response_builder.response))

        return response_builder.response



class SessionEndedRequestHandler(AbstractRequestHandler):
    """ Default handler for Session End """
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """ Default handler for Help Intent """
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.speak(HELP).ask(HELP)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """ Default handler for Cancel and Stop Intent """
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        handler_input.response_builder.speak(GOODBYE)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """ AMAZON.FallbackIntent is only available in en-US locale.
        This handler will not be triggered except in that locale,
        so it is safe to deploy on any locale. """
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.speak(UNHANDLED).ask(HELP)
        return handler_input.response_builder.response


class GetAddressExceptionHandler(AbstractExceptionHandler):
    """ Custom Exception Handler for handling device address API
        call exceptions. """
    def can_handle(self, handler_input, exception):
        return isinstance(exception, ServiceException)

    def handle(self, handler_input, exception):
        if debugMode and exception:
            with open('exception.json', 'w') as writer:
                writer.write(str(exception))
        if exception.status_code == 403:
            handler_input.response_builder.speak(
                NOTIFY_MISSING_PERMISSIONS).set_card(
                AskForPermissionsConsentCard(permissions=permissions))
        else:
            handler_input.response_builder.speak(
                LOCATION_FAILURE).ask(LOCATION_FAILURE)
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """ Default catch-all exception handler. Log exception and
        respond with custom message. """
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print("Encountered following exception: {}".format(exception))

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response
