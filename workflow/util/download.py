# Packages
import os
from os.path import join
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import requests
from util.files import *
from util.const import *

'''
Define our utils
'''
# The fill_url function
# For any URL/API endpoint, we want to replace
# wildcard terms (FIPS, STATE, STATE_ALPHA)
# with the appropriate value from the FIPS, STATE, or
# STATE_ALPHA config values
def fill_url(endpoint, wcard_dict):    
    # Get a list of all the wildcards we need to replace for this endpoint
    wildcards = [wcard for wcard in URL_WILDCARDS if wcard in endpoint]
    # Replace the wildcard with the value stored in a wildcard dictionary
    # Defined in download_data.py
    for wildcard in wildcards:
        endpoint = endpoint.replace(wildcard, wcard_dict[wildcard])
        
    return endpoint
# Example unit test
# Might be worth it to have a unit test file? 
test_endpoint = '{STATE_FIPS}_{STATE_ABBR}'
wcard_dict = {'{STATE_FIPS}': '42',
              '{STATE_ABBR}': 'PA'}
assert fill_url(test_endpoint, wcard_dict) == '42_PA'

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
        filename = file_pre + API_EXT[file_pre]
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

# Helper function to process
# the DOWNLOAD dataframe for use in 
# both the dwnld_out_files function
# and when downloading files
def process_file(file):
    # The name follows format like
    # county_api_exp_nsi
    # which we will use to get 
    # file directories
    name = file[0]
    # The endpoint is what we're going to
    # put into a requests call
    endpoint = file[1]
    # Split name from the 1st indexed token onwards
    # Like api_exp_nsi
    str_tokens = name.split('_')[1:]

    return str_tokens, endpoint

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
        str_tokens, endpoint = process_file(file)
        
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

# The download_url helper function
def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

# The downlload_api helper function
# TODO: it may make sense to have some more
# configuration data about
# downloading from different apis
# so want to split this from the download_url
# function
def download_api(url, save_path):
    r = requests.get(url)
    with open(save_path, 'wb') as fd:
        fd.write(r)

# The download_raw function
# We are going to iterate through our 
# DOWNLOAD dataframe and
# 1) clean the endpoint
# 2) get the out filepath
# 3) download the data
# 4) write it in the out_filepath
def download_raw(files, wcard_dict):
    for file in files.itertuples():
        # Get the str_tokens and endpoint from the dataframe row
        str_tokens, endpoint = process_file(file)
        # Get the out filepath
        out_filepath = get_dir(str_tokens, endpoint)
        # "Clean" the endpoint with the wcard_dict
        endpoint = fill_url(endpoint, wcard_dict)

        # Make sure we can write out data to this filepath
        prepare_saving(out_filepath)

        # Download data with api or url call
        if str_tokens[0] == 'api':
            # If api, call download_api helper function
            download_api(endpoint, out_filepath)
        else:
            # If url, call download_url helper function
            # and write file
            download_url(endpoint, out_filepath)

        # TODO log what is being done
        print('Downloaded from: ' + str(endpoint))
