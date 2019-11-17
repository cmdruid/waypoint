
""" run.py ====================================================================
The is the setup file responsible for compiling our Alexa skill together and
making it available to get/post requests (using Flask).

When a user interacts with our skill, alexa service will collect a bunch of
data from the user, build it into a .json file, then send it to our server.
We capture that request with Flask, process it using our intent handlers, then
return a formatted response to the alexa service using their skill builder.
============================================================================ """

# All our imports go here.
from flask import Flask
from config import logger, settings
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from flask_ask_sdk.skill_adapter import SkillAdapter
# from ask_sdk_core.view_resolvers import FileSystemTemplateLoader
# from ask_sdk_jinja_renderer import JinjaTemplateRenderer
from skills import (LaunchRequestHandler, GetStationHandler, HelpIntentHandler,
                    CancelOrStopIntentHandler, FallbackIntentHandler,
                    SessionEndedRequestHandler, GetAddressExceptionHandler,
                    CatchAllExceptionHandler)


# Initialize our base skill by invoking CustomSkillBuilder.
sb = CustomSkillBuilder(api_client=DefaultApiClient())

# Register all handlers, interceptors etc. From skills.py.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetStationHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Don't forget to add our exception handlers as well.
sb.add_exception_handler(GetAddressExceptionHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

# Load our Jinja response templates from the templates directory.
# sb.add_loaders(FileSystemTemplateLoader(dir_path="templates", encoding='utf-8'))

# Add default jinja renderer on skill builder.
# sb.add_renderer(JinjaTemplateRenderer())

# This will be needed when our code is uploaded to Amazon's lambda host service.
# lambda_handler = sb.lambda_handler()

# This is the unique ID of our skill, found in the alexa developer console.
SKILL_ID = settings['Alexa']['SKILL_ID']

# Initialize our flask instance, then pass into the skill builder with our ID.
app = Flask(__name__)
skill_response = SkillAdapter(skill=sb.create(), skill_id=SKILL_ID, app=app)
skill_response.register(app=app, route="/")

# Config settings for our flask development server.
if __name__ == '__main__':
    app.run(host="localhost", port=8100, debug=True)
