import logging, yaml

# Load our local configuration file.
with open('instance/config.yaml') as f:
    settings = yaml.load(f, Loader=yaml.FullLoader)

# It's always good to log things!
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Setup our file handler to log messages to file.
fh = logging.FileHandler('instance/debug.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Setup our stream handler to also post messages to console.
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
