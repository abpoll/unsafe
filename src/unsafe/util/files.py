# Packages
import os
from os.path import join
from pathlib import Path
from util.const import *
import rasterio

'''
Set up references for file directories that
are used throughout the workflow
'''

# We can also specify the filepath to the
# raw data directory
FR = join(ABS_DIR, "data", "raw")

# And external - where our hazard data should be
FE = join(FR, "external")

# Set up interim and results directories as well
# We already use "FR" for raw, we use "FO" 
# because you can also think of results
# as output
FI = join(ABS_DIR, "data", "interim")
FO = join(ABS_DIR, "data", "results")

# "Raw" data directories for exposure, vulnerability (vuln) and
# administrative reference files
EXP_DIR_R = join(FR, "exp")
VULN_DIR_R = join(FR, "vuln")
REF_DIR_R = join(FR, "ref")
# Haz is for depth grids
HAZ_DIR_R = join(FE, "haz")
# Pol is for NFHL
POL_DIR_R = join(FR, "pol")

# Unzip directory 
UNZIP_DIR = join(FR, "unzipped")

# Figures directory
FIG_DIR = join(ABS_DIR, "figures")

# We want to process unzipped data and move it
# to the interim directory where we keep
# processed data
# Get the filepaths for unzipped data
HAZ_DIR_UZ = join(UNZIP_DIR, "external", "haz")
POL_DIR_UZ = join(UNZIP_DIR, "pol")
REF_DIR_UZ = join(UNZIP_DIR, "ref")
VULN_DIR_UZ = join(UNZIP_DIR, "vuln")

# "Interim" data directories
EXP_DIR_I = join(FI, "exp")
VULN_DIR_I = join(FI, "vuln")
REF_DIR_I = join(FI, "ref")
# Haz is for depth grids
HAZ_DIR_I = join(FI, "haz")
# Pol is for NFHL
POL_DIR_I = join(FI, "pol")

# prepare_saving method makes sure
# the parent directories exist
def prepare_saving(filepath):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

# Helper function for reading in hazard data
def read_dg(rp, haz_dir):
    # Makes sense we would also have the depth grids stored
    # in directories for different %iles
    # ci5/median/ci95, for example
    # and this could be passed in as an argument
    # and put after HAZ_DIR? Not sure what the other
    # file directory formats will be
    base_dir = join(HAZ_DIR_UZ, haz_dir, HAZ_DIR_SUB, "RP_" + rp)
    rp_filep = join(base_dir, HAZ_FILEP.replace('{RP}', rp))
    depth_grid = rasterio.open(rp_filep)

    return depth_grid