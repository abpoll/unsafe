# Packages
import requests
import os
from os.path import join
from pathlib import Path
import pandas as pd
from util.download import *
from util.files import *
from util.const import *

'''
Configuring the main set up for
implementing our utils
'''

# FIPS, STATE_FIPS, or nothing should be passed in
# Depending on the length of the string (or its presence)
# we can infer whether to run
# county or state or national download processing below
# This doesn't need to be implemented for our single county
# case study, and we can do everything from just having
# FIPS passed in 

# Need a wcard_dict where we map
# the items in URL_WILDCARDS to the
# fips, state_abbr, or state_fips
# For our case study, we can specify
# a dict for all of these
# But in the future we can have a .csv
# that maps STATE_FIPS to STATE_ABBR
# TODO will remove the [0] access of the list
# to do this in a way where
# the argument passed to the script is a wildcard
# of fips, state, etc
wcard_dict = {x: CONFIG[x[1:-1]][0] for x in URL_WILDCARDS}

'''
We need to loop through all of our files
and download them
'''
# Seems like the best way to do this in the future
# is for this script to infer from the argument
# passed in from the script call
# whether to run DOWNLOAD_COUNTY, DOWNLOAD_STATE, 
# or DOWNLOAD_NATION 
# And wcard_dict would be defined accordingly
# Plus, STATE_ABBR should be found
# from the value of STATE_FIPS and not
# prespecified in some config file
download_raw(DOWNLOAD, wcard_dict)