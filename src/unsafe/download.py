# Packages
import os
from os.path import join
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import requests
import json
import unsafe.files as unfile
import unsafe.const as unconst 

"""
Define our utils
"""

# The get_dir helper function
# For a list of string tokens, we
# are returning a filepath and filename
# The last string token is most of the filename
# If the first token is api, we need to use the exts dict
# and append it to the last string token
# If the first token is url, we need to use the endpoint
# that is passed here to get the exact ext we are downloading
def get_dir(str_tokens, endpoint, fr, api_ext):
    # Get wildcard (FIPS, STATE_FIPS, NATION)
    wcard_type = str_tokens[0]
    # Replace wcard_type with wcard_name
    # The idea is that we want the directory
    # names to be generic, so that it scales
    # better. In practice this means that
    # instead of writing out a file to
    # a directory like
    # raw/exp/nsi.pqt
    # we would do raw/{FIPS}/exp/nsi.pqt
    # where the script that does downloading
    # or unzipping, etc has FIPS passed
    # in as an argument...
    wcard_name = "{" + wcard_type + "}"

    # Get url or api type
    end_type = str_tokens[1]
    # Get most of the filename
    file_pre = str_tokens[-1]
    # Join the middle tokens as a filepath
    mid_dirs = "/".join(str_tokens[2:-1])

    # Implement the api vs. url processing
    if end_type == "api":
        # For example, file_pre will be something like
        # "nsi" which is also our key in the exts dict
        # for the ext we need to use
        filename = file_pre + api_ext[file_pre]
    else:
        # Ext is after the last '.' character
        url_ext = endpoint.split(".")[-1]
        filename = file_pre + "." + url_ext

    # Now join the raw directory with the
    # wildcard name and mid_dirs
    filepath = join(fr, mid_dirs, wcard_name, filename)

    # Return this directory path and the filename w/ extension
    return filepath


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
    # Split name
    # Like county_api_exp_nsi
    str_tokens = name.split("_")

    return str_tokens, endpoint

# The download_url helper function
def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


# The download_api helper function
# TODO: it may make sense to have some more
# configuration data about
# downloading from different apis
# so want to split this from the download_url
# function
def download_api(url, save_path):
    data = requests.get(url).json()
    with open(save_path, "w") as fd:
        json.dump(data, fd)


# The download_raw function
# We are going to iterate through our
# DOWNLOAD dataframe and
# 1) clean the endpoint
# 2) get the out filepath
# 3) download the data
# 4) write it in the out_filepath
def download_raw(files, wcard_dict, fr, api_ext):
    for file in files.itertuples():
        # Get the str_tokens and endpoint from the dataframe row
        str_tokens, endpoint = process_file(file)
        # Get the out filepath
        # "Clean" it with the wcard_dict
        out_filepath = get_dir(str_tokens, endpoint, fr, api_ext)
        out_filepath = unfile.fill_wcard(out_filepath, wcard_dict)
        # "Clean" the endpoint with the wcard_dict
        endpoint = unfile.fill_wcard(endpoint, wcard_dict)

        # Make sure we can write out data to this filepath
        unfile.prepare_saving(out_filepath)

        # Download data with api or url call
        if str_tokens[1] == "api":
            # If api, call download_api helper function
            download_api(endpoint, out_filepath)
        else:
            # If url, call download_url helper function
            # and write file
            download_url(endpoint, out_filepath)

        # TODO log what is being done
        print("Downloaded from: " + str(endpoint))
