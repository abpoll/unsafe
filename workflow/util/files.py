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

# Set up interim and results directories as well
# We already use "FR" for raw, we use "FO" 
# because you can also think of results
# as output
FI = join(ABS_DIR, "data", "interim")
FO = join(ABS_DIR, "data", "results")

# Directories for exposure, vulnerability (vuln) and
# administrative reference files
EXP_DIR_R = join(FR, "exposure")
VULN_DIR_R = join(FR, "vuln")
REF_DIR_R = join(FR, "ref")
# Haz is for depth grids
HAZ_DIR_R = join(FR, "haz")
# Pol is for NFHL
POL_DIR_R = join(FR, "pol")

# prepare_saving method checks if
# a directory or filepath is sent
# If directory, Path(filepath).mkdir() is called
# with parents=True and exist_ok=True
# If filepath, go to the parent directory and 
# repeat the above
# Can do this recursively
def prepare_saving(filepath):
    if Path(filepath).is_dir():
        Path(filepath).mkdir(parents=True, exist_ok=True)
    else:
        prepare_saving(Path(filepath).parents[0])