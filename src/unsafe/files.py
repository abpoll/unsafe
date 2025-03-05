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


def prepare_saving(filepath):
    """
    Make sure a parent directory exists for a filepath.

    This function creates any directories you need to write out a filepath.

    Parameters
    ----------
    filepath: str
        The string containing your filepath. 
        Example: project_root_dir/new_subdir/filename.csv

    Returns
    -------
    None
        Results are saved to disk at the specified locations

    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)


def fill_wcard(wcard_str, wcard_dict):
    """
    Replace wildcard placeholders in a string with their corresponding values.
    
    This function identifies wildcard terms (e.g., {FIPS}, {STATEFIPS}, {STATEABBR})
    in a string and replaces them with their actual values provided in the wildcard
    dictionary. It's commonly used to customize URLs, API endpoints, or file paths
    with specific geographic identifiers.
    
    Parameters
    ----------
    wcard_str : str
        The string containing wildcard placeholders to be replaced.
        Example: "https://example.com/data/{FIPS}/download.zip"
    
    wcard_dict : dict
        Dictionary mapping wildcard placeholders to their replacement values.
        Keys should include the full placeholder syntax (e.g., "{FIPS}").
        Example: {"{FIPS}": "42101", "{STATEFIPS}": "42", "{STATEABBR}": "PA"}
    
    Returns
    -------
    str
        The input string with all wildcards replaced by their corresponding values.
        Example: "https://example.com/data/42101/download.zip"
    
    Notes
    -----
    - The function only replaces wildcards that are present in both the wcard
      string and the wcard_dict keys.
    - Wildcards not found in wcard_dict will remain unchanged in the output.
    - The replacement is case-sensitive and requires the exact wildcard format.
    
    Examples
    --------
    >>> endpoint = "https://data.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_{STATEFIPS}_tract.zip"
    >>> wcard_dict = {"{STATEFIPS}": "42", "{STATEABBR}": "PA"}
    >>> fill_wcard(endpoint, wcard_dict)
    'https://data.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_42_tract.zip'
    
    >>> filepath = "data/{NATION}/{STATEABBR}/counties.shp"
    >>> wcard_dict = {"{NATION}": "US", "{STATEABBR}": "PA", "{FIPS}": "42101"}
    >>> fill_wcard(filepath, wcard_dict)
    'data/US/PA/counties.shp'
    """

    # Get a list of all the wildcards we need to replace for this string
    wildcards = [wcard for wcard in wcard_dict.keys() if wcard in wcard_str]
    # Replace the wildcard with the value stored in a wildcard dictionary
    for wildcard in wildcards:
        replaced_str = wcard_str.replace(wildcard, wcard_dict[wildcard])

    return replaced_str

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
