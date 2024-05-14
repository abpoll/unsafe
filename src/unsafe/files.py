# Packages
import os
import re
from os.path import join
from pathlib import Path
import rasterio

"""
Set up references for file directories that
are used throughout the workflow
"""


# prepare_saving method makes sure
# the parent directories exist
def prepare_saving(filepath):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)


# Helper function for reading in hazard data
# This may have to be modified on a study-by-study
# basis so long as there is not a standardized
# way to share flood hazard model output data
def read_dg(rp, haz_dir_uz, haz_filen, scen=None):
    # Makes sense we would also have the depth grids stored
    # in directories for different %iles
    # ci5/median/ci95, for example
    # and this could be passed in as an argument
    # and put after HAZ_DIR? Not sure what the other
    # file directory formats will be

    # https://stackoverflow.com/questions/6116978/
    # how-to-replace-multiple-substrings-of-a-string
    if scen is not None:
        rep = {"{scen}": scen, "{rp}": rp}
    else:
        rep = {"{rp}": rp}
    # use these three lines to do the replacement
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    haz_file = pattern.sub(lambda m: rep[re.escape(m.group(0))], haz_filen)

    rp_filep = join(haz_dir_uz, haz_file)
    depth_grid = rasterio.open(rp_filep)

    return depth_grid
