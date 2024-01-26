'''
Constants that are widely used throughout the
framework
'''
import os
from os.path import join
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import pandas as pd

# Absolute directory
# The root of the project directory 
# Path(os.path.realpath(__file__).parents[1]
# would take us to workflow/
ABS_DIR = Path(os.path.realpath(__file__)).parents[2]

# From ABS_DIR, we can access our config.yaml file
# for the project
CONFIG_FILEP = join(ABS_DIR, 'config', 'config.yaml')

# Open the config file and load
with open(CONFIG_FILEP) as f:
    CONFIG = yaml.load(f, Loader=SafeLoader)

# Wildcards for urls
URL_WILDCARDS = CONFIG['url_wildcards']

# Get the file extensions for api endpoints
API_EXT = CONFIG['api_ext']

# Get the CRS constants
NSI_CRS = CONFIG['nsi_crs']

# Dictionary of ref_names
REF_NAMES_DICT = CONFIG['ref_names']

# Dictionary of ref_id_names
REF_ID_NAMES_DICT = CONFIG['ref_id_names']

# Coefficient of variation
# for structure values
COEF_VARIATION = CONFIG['coef_var']

# First floor elevation dictionary
FFE_DICT = CONFIG['ffe_dict']

# MTR_TO_FT constant
MTR_TO_FT = 3.28084

# Number of states of the world
N_SOW = CONFIG['sows']

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