# FindChargingStation
This project is being developed for the Automobility LA 2019 Hackathon. This project aims to assist drivers of electric vehicles, via voice-guided assistance, with navigation and trip-planning when it comes to charging their vehicle.

## Introduction
This project aims to assist drivers of electric vehicles, via voice-guided assistance, with the following tasks:

* Find the nearest charging station to your location, and forward it to your navigation system.
* Find the best charging station along your existing route, and add it as a waypoint.
* Provide a list of nearby charging stations to choose from, and filter them based on your preferences.
* Remember your preferences and save them to a profile, so that future results are curated to your preferences.
* [Roadmap] Assist with booking a reservation at a charging station, if reservations are avaiable.
* [Roadmap] Find a charging station near other activities, such as coffee, shopping, food, etc.
* [Roadmap] Locate a charging station in advance, based on your current route, battery level and driving range.

## Motivations
I currently work with enterprise-class systems for security and and access control, and have experience with building many other types of IT systems over the years. I'm studying software development so that I can hone my skills and tackle even more ambitious projects. I'm also looking for new networking and career opportunities. Shameless plug!

This is my first time participating in a hackathon event and developing a real-world software project. I'm diving into the experience in order to make a lot initial mistakes and learn valuable lessons along the way. Please bear with me as I may have no idea what I'm doing at first! However I'm a quick learner!

In regards to the design motivations of this project, these were my ideal requirements:

* The project should honor the intentions and scope of the hackathon event, as outlined here.
* The functionality should be competitive so that fellow contributors can have a real stake in the contest.
* The software itself should have a real-world application that people will find useful.
* The scope should not be too difficult for myself and other contributors to finish by the dead-line.
* If possible, the project build should be a solid template for others to learn from.

Feel free to give me any criticism or feedback you think may help. I'm grateful for anyone who wishes to contribute to this project and help it grow. If you would like to contribute, please check out the [Contributing](#contributing) section below. You can reach me on slack @cmdruid, or email me slack.cmdruid@erine.email.

## Technologies
This project uses the following:
* [Amazon Alexa Developers Console](https://developer.amazon.com/en-US/alexa)
* [Alexa Skills SDK for Python](https://github.com/alexa/alexa-skills-kit-sdk-for-python)
* [Location Services for Alexa Skills](https://developer.amazon.com/docs/custom-skills/location-services-for-alexa-skills.html)
* [Navigation Management for Alexa Skills](https://developer.amazon.com/docs/custom-skills/navigation-management-for-alexa-skills.html)
* [NREL Developer Network: Alternative Fuel Station Database](https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/)
* [HERE Developer API and SDKs](https://developer.here.com/documentation)

## Getting Started
This section is still in development. 

There are two ways (so far) to deploy this project:

1. You can copy/paste code from this project directly into your developer's console. Amazon will host the code for you using their lambda service. This is by far the easiest solution for deploying code for use in production, however it's not great for development (at least for me) because you're constrained to work within their developer console.

Steps for this require:
* Register an account with Amazon's Alexa Developer website.
* Create your skill in the developer's console.
* Copy/paste the model.json data from this repo into the JSON Editor, under "Build" in your console.
* Copy/paste the code (and file structure) from this repo into the "Code" section of your console. (I need to write a better way to do this, a github script can auto-generate a zip file that you can upload directly to the developer console).
* Register an API account with NREL (or whoever you prefer to use) so you can get an API key to use their service. (right now I'm just including my own API key, but that's not a long-term solution.)

2. Deploy your own development server for receiving skill requests and handling the responses. This requires some more leg-work, but it allows you to develop within your own IDE and tinker around much more.

In addition to the above steps, you will have to:
* Make note of your unique Skill ID (it's in the URL to your skill).
* Configure your skill settings to forward traffic to your development server (instead of their lambda service).
* Generate an SSL certificate for your server and upload it to the developer's console.
* Setup nginx on your server to forward port 80 traffic to 5000 (or whatever your flask server is using). 

Currently my server is setup and running behind a FQDN with a valid SSL certificate from LetsEncrypt. In the future I plan to include instructions on how to use a simpler, self-signed certificate for development instead.

## Tests
Will update this in the future.

## Resources
* [Alexa Skills Kit SDK for Python Documentation](https://developer.amazon.com/docs/alexa-skills-kit-sdk-for-python/overview.html)
* [Alexa Design Guide](https://developer.amazon.com/docs/alexa-design/get-started.html)
* [Best Practices for Designing Alexa Skills for Automotive](https://developer.amazon.com/docs/custom-skills/best-practices-for-designing-alexa-skills-for-automotive.html)
* [GET/POST Requests using Python](https://www.geeksforgeeks.org/get-post-requests-using-python/)

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

This project is still in its infancy. I'd appreciate any help with the following:

#### Documentation
* Writing this readme.md.
* Putting together links and resources.
* Formatting this project as a template for others to learn how to build skills with Alexa.

#### Design
* Put together a feature design doc for the developers to follow.
* Put together an alexa voice interaction model, with basic dialogue and scripts.

#### Development
* Check if user has the requested permissions (location services), and what type (mobile or static).
* If user does not have permissions, request it from user (or guide user to enable them).
* Remember and save user preferences, and store within a (free!) amazon persistent storage instance.
* Query API for charging station (based on user preferences!), and return json response as dict.
* Rate and score station results based on default preferences and user preferences.
* Query nearby places based on type (food, shopping, etc.) using (google maps?) API, and also use it to rate and score.
* Figure out how to query current nav destination, then calculate a point between current location and destination.

#### Presentation
* A basic slide presentation for the hackathon event.
* A basic dialogue script for the presentation.
* A planned outline of the presentation, with cues for slides, dialogue and software demo.

#### Collaboration
* A place for everyone to communicate. (slack?)
* A kanban board or something to keep track of tasks and push them along.
* Someone to keep track of contributors and teams, their progress, and what they need help with.
* Someone to to keep track of issues and roadblocks. Either on github or another kanban board.

## Versioning
I plan to use [SemVer](http://semver.org/) for versioning at some point in the future.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments
Will update this in the future!
