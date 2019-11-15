
""" run.py ====================================================================
The is the setup file responsible for compiling our Alexa skill together and
making it available to get/post requests (using Flask).

When a user interacts with our skill, alexa service will collect a bunch of
data from the user, build it into a .json file, then send it to our server.
We capture that request with Flask, process it using our intent handlers, then
return a formatted response to the alexa service using their skill builder.
============================================================================ """

# All our imports go here.
import logging
from flask import Flask
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from flask_ask_sdk.skill_adapter import SkillAdapter
from skills import (LaunchRequestHandler, GetAddressHandler, HelpIntentHandler,
                    CancelOrStopIntentHandler, FallbackIntentHandler,
                    SessionEndedRequestHandler, GetAddressExceptionHandler,
                    CatchAllExceptionHandler)

# It's always good to log things!
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Setup our file handler to log messages to file.
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Setup our stream handler to also post messages to console.
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Initialize our base skill by invoking CustomSkillBuilder.
sb = CustomSkillBuilder(api_client=DefaultApiClient())

# Register all handlers, interceptors etc. From skills.py.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetAddressHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Don't forget to add our exception handlers as well.
sb.add_exception_handler(GetAddressExceptionHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

# This will be needed when our code is uploaded to Amazon's lambda host service.
# lambda_handler = sb.lambda_handler()

# This is the unique ID of our skill, found in the alexa developer console.
SKILL_ID = 'amzn1.ask.skill.4c1b7b71-b47b-4021-89c2-c216cb82832e'

# Initialize our flask instance, then pass into the skill builder with our ID.
app = Flask(__name__)
skill_response = SkillAdapter(skill=sb.create(), skill_id=SKILL_ID, app=app)
skill_response.register(app=app, route="/")

# Config settings for our flask development server.
if __name__ == '__main__':
    app.run(host="localhost", port=8100, debug=True)
