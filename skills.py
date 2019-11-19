""" skills.py =================================================================
This file contains all of our skill handlers. The incoming data is passed to
each handler in linear order (the order in which the handlers have been added to
the skill builder), and the "can_handle" function will check to see if it can
handle the nature of the request. If so, the "handle" function will process the
request and construct a response to send back to the alexa service.
============================================================================ """

# We need to import some stuff
import requests, json, random
from config import logger, settings
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model.services import ServiceException
from utils import ( parse_user_loc, parse_device_loc, get_station_list, get_yelp_results )


# Rough implementation of debug mode. Need to refine.
debugMode = settings['Debug']['debugMode']
loc_debug = settings['Debug']['Lat'], settings['Debug']['Long']

# This is where we'll store our response dialogue strings. This is a bad design.
# We need to move these to a separate file.
WELCOME_MSG = "Welcome to waypoint."

FIRST_TIME = "What kind of car do you drive?"

WELCOME_DEBUG = "Debug mode."

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


# Right now this is a hard-coded filter, but we want to dynamically
# build it from the user's preferences in the future.
station_filter = {'ev_pricing': 'Free',

               'limit': '10'}

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

        slots = eval(str(handler_input.request_envelope.request.intent.slots))
        with open('instance/request.json', 'w') as writer:
            writer.write(str(slots))
        slots = [v['value'] for k,v in slots.items() if v['value'] != None]
        slots = slots[0]
        logger.debug(slots)


        # Feel free to check out the request.json file generated here so you
        # can get a feel for how the alexa data packet is structured.


        # If the user permissions and consent token are not present, then we
        # need to prompt the user to give us permission in order to access data
        # on their device. debugMode will bypass this check.
        if not (req_envelope.context.system.user.permissions and
                req_envelope.context.system.user.permissions.consent_token):
            response_builder.speak(MISSING_PERMISSIONS)
            response_builder.set_card(
                AskForPermissionsConsentCard(permissions=permissions))
            return response_builder.response

        # Check for the user's geolocation data first, then device data, then prompt.
        logger.debug("Fetching user's geo-location...")
        location = parse_user_loc(req_envelope) if not debugMode else loc_debug
        if not location:
            logger.debug("Failed to grab geolocation! Checking device address...")
            location = parse_device_loc(req_envelope, service_client_fact)
            if not location:
                logger.debug("Failed to grab device location! Prompting user...")
                response_builder.reprompt(MISSING_LOCATION).getResponse()

        # Fetch a list of charging station based on user's preferences.
        logger.debug("Fetching station list...")
        station_list = get_station_list(location, station_filter)
        logger.debug("Station list received. Dumping to JSON.")
        if debugMode and station_list:
            with open('instance/stations.json', 'w') as writer:
                writer.write(str(station_list))

        rand_index = random.randint(0,2)
        select_station = station_list['fuel_stations'][rand_index]
        station_address = "{}, {}, {} {}".format(select_station['street_address'],
                                                 select_station['city'],
                                                 select_station['state'],
                                                 select_station['zip'])

        # Pick the top station. We'll have the user do this later.
        logger.debug("Fetching yelp results...")
        yelp_results = get_yelp_results(station_address, slots)
        logger.debug("Yelp results received!")

        # Station Values
        station_distance = select_station['distance']
        st_distance = (round(station_distance) + "miles") if station_distance > 1 else "less than a mile"
        network = select_station["ev_network"] if not "Non" in select_station["ev_network"] else ""
        port_type = ""
        port_val = random.randint(1,4)
        port_max = random.randint(4,9)
        logger.debug("Station values loaded!")

        # Nissan Leaf
        total_range = 200
        total_battery = 60
        curr_battery = 0.5
        # full_charge_time = 25, 11, 0.75
        # charge_time = full_charge_time[port_type] * curr_battery
        logger.debug("Car values loaded!")

        # Yelp Values
        rand_index_yelp = random.randint(0,2)
        top_pick = yelp_results['businesses'][rand_index_yelp]
        name = top_pick['name']
        rating = top_pick['rating']
        yelp_distance = round(top_pick['distance']/84)
        logger.debug("Yelp values loaded!")

        # Variables in dialogue syntax.
        # pay = "Free" if "Free" in select_station['ev_pricing'] else "Paid"
        # hours = "open 24 hours" if "24" in select_station['access_days_time'] else ""

        charge_hours = "{} hours".format(1 + random.randint(1,2))
        logger.debug("Syntax values loaded!")

        RESULT = ( "The nearest {} station is {} away. ".format(network, st_distance) +
                   "{} of the {} ports are currently open. ".format(port_val, port_max) +
                   "It will take about {} of charging to make it home. ".format(charge_hours) +
                   "I found a place called {}. It is a {} minute walk away. ".format(name, yelp_distance) +
                   "Are you interested?")

        logger.debug("Dialogue processed!")

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
