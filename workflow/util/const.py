'''
Constants that are widely used throughout the
framework
'''
from util.files import *
import yaml
from yaml.loader import SafeLoader
import pandas as pd

# Open the config file and load
with open(CONFIG_FILEP) as f:
    CONFIG = yaml.load(f, Loader=SafeLoader)

# Wildcards for urls
URL_WILDCARDS = CONFIG['url_wildcards']

# Get the file extensions for api endpoints
API_EXT = CONFIG['api_ext']

# Get the files we need downloaded
# These are specified in the "download" key 
# in the config file
# We transpose because one of the utils
# needs to return a list of the output files
# TODO the logic here works for one county, but 
# will need rethinking for generalizability
# I think the way to do it would be to break it
# into DOWNLOAD_FIPS, DOWNLOAD_STATE, etc.
# and these are accessed differently
DOWNLOAD = pd.json_normalize(CONFIG['download'], sep='_').T