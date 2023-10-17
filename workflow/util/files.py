# Packages
import os
from os.path import join
from pathlib import Path

'''
Set up references for file directories that
are used throughout the workflow
'''

# Absolute directory
# The root of the project directory 
# is obtained with the Path(os.getcwd()).parents[1]
# command. parents[0] would take us to workflow/
ABS_DIR = os.path.abspath(Path(os.getcwd()).parents[1])

# From ABS_DIR, we can access our config.yaml file
# for the project
CONFIG_FILEP = join(ABS_DIR, 'config', 'config.yaml')

# We can also specify the filepath to the
# raw data directory
FR = join(ABS_DIR, "data", "raw")

# And external - where our hazard data should be
FE = join(ABS_DIR, "data", "external")

# Set up interim and results directories as well
# We already use "FR" for raw, we use "FO" 
# because you can also think of results
# as output
FI = join(ABS_DIR, "data", "interim")
FO = join(ABS_DIR, "data", "results")

# Directories for exposure, vulnerability (vuln) and
# administrative reference files
EXP_DIR_R = join(FR, "exp")
VULN_DIR_R = join(FR, "vuln")
REF_DIR_R = join(FR, "ref")
# Haz is for depth grids
HAZ_DIR_R = join(FE, "haz")
# Pol is for NFHL
POL_DIR_R = join(FR, "pol")

# Unzip directory 
UNZIP_DIR_I = join(FI, "unzipped")

# prepare_saving method makes sure
# the parent directories exist
def prepare_saving(filepath):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)