# Packages
import os
from os.path import join
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import pandas as pd

os.environ["USE_PYGEOS"] = "0"

'''
Configuring the main set up for
implementing our utils
'''

# Absolute directory
# The root of the project directory 
# is obtained with the Path(os.getcwd()).parents[1]
# command. parents[0] would take us to workflow/
ABS_DIR = os.path.abspath(Path(os.getcwd()).parents[1])

# From ABS_DIR, we can access our config.yaml file
# for the project
config_filep = join(ABS_DIR, 'config', 'config.yaml')

# We can also specify the filepath to the
# raw data directory
FR = join(ABS_DIR, "data", "raw")

# Open the config file and load
with open(config_filep) as f:
    config = yaml.load(f, Loader=SafeLoader)

# Get our constants
# In the future, when this codebase
# is modified to work for more than one county
# the snakemake rule will use a wildcard or the expand
# function to send in one fips, state, and state_alpha
# from the config file. So, noting this
# code block as a place where logic will need
# to change
# TODO  
FIPS = config['FIPS']
STATE = config['STATE']
STATE_ALPHA = config['STATE_ALPHA']

# Get a dict of these constants
FIPS_DICT = {
    '{FIPS}': FIPS,
    '{STATE}': STATE,
    '{STATE_ALPHA}': STATE_ALPHA
}

# Get the files we need downloaded
# These are specified in the "download" key 
# in the config file
# We transpose because one of the utils
# needs to return a list of the output files
# It is easy to use the .itertuples() command
# and get the information for file directories
# and file names in a row-wise fashion
files = pd.json_normalize(config['download'], sep='_').T
# Get the file extensions for api endpoints
exts = config['api_ext']

'''
Define our utils
'''
# The fill_url function
# For any URL/API endpoint, we want to replace
# wildcard terms (FIPS, STATE, STATE_ALPHA)
# with the appropriate value from the FIPS, STATE, or
# STATE_ALPHA config values
def fill_url(endpoint):    
    # Get a list of all the wildcards we need to replace for this endpoint
    fips_wildcards = [key for key,val in fips_dict.items() if key in endpoint]
    # Loop through this list and replace that string with the value from
    # fips_dict
    for wildcard in fips_wildcards:
        endpoint = endpoint.replace(wildcard, FIPS_DICT[wildcard])
        
    return endpoint
# Example unit test
# Might be worth it to have a unit test file? 
test_endpoint = '{STATE}_{STATE_ALPHA}'
assert fill_url(test_endpoint) == 'PA_42'

# The get_dir helper function
# For a list of string tokens, we
# are returning a filepath and filename
# The last string token is most of the filename
# If the first token is api, we need to use the exts dict
# and append it to the last string token
# If the first token is url, we need to use the endpoint
# that is passed here to get the exact ext we are downloading
def get_dir(str_tokens, endpoint):
    # Get url or api type
    end_type = str_tokens[0]
    # Get most of the filename
    file_pre = str_tokens[-1]
    # Join the middle tokens as a filepath
    mid_dirs = '/'.join(str_tokens[1:-1])

    # Implement the api vs. url processing
    if end_type == 'api':
        # For example, file_pre will be something like
        # "nsi" which is also our key in the exts dict
        # for the ext we need to use
        filename = file_pre + exts[file_pre]
    else:
        # Ext is after the last '.' character
        url_ext = endpoint.split('.')[-1]
        filename = file_pre + '.' + url_ext

    # Now join the raw directory with the mid_dirs
    filepath = join(FR, mid_dirs, filename)
    
    # Return this directory path and the filename w/ extension
    return filepath

# Checking the nsi is correct
# get_dir(['api', 'exp', 'nsi'], 'does not matter')

# Checking something more complex is correct, like
# a social vulnerability file which is in a nested directory
# structure
# get_dir(['url', 'vuln', 'social', 'noaa'],
#          'https://coast.noaa.gov/htdata/SocioEconomic/SoVI2010/SoVI_2010_{STATE}.zip')

# Did visual checks for these. Could create assert statements
# based on the path from the project root

# The dwnld_out_files function
# For each URL/API endpoint, we want to return the output
# version of that file
# This is the function we need for the download_data
# rule output
def dwnld_out_files(files):
    # For each file that needs to be downloaded
    # Get the filepath
    # Return the list of these out files
    out_list = []
    for file in files.itertuples():
        name = file[0]
        endpoint = file[1]
        # In the future, it makes sense to use the county, 
        # state, and national token to do some distributed
        # processing, but we are just doing a one county
        # case study to start. 
        # So, for now we are going to just use
        # the strings from the 1st index onwards
        str_tokens = name.split('_')[1:]
        
        # Helper function to return 
        # our filepath from our str_tokens
        # The last token is our filename
        # Everything after the second token and before this
        # are file directories
        # For API endpoints, we need to access the "ext" element
        # to get the filename (urls include the file ext)
        # We use the exts dict for this
        filepath = get_dir(str_tokens, endpoint)
        
        # Add this filepath to our out_list
        out_list.append(filepath)

    return out_list