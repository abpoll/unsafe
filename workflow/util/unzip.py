# Packages
from os.path import join
from pathlib import Path
import glob
from util.files import *
from util.const import *

# This function searches through our 
# raw directory tree and 
# returns a list of all the paths
# to .zip directories
def zipped_downloads():
    zip_list = []
    for path in Path(FR).rglob("*.zip"):
        # Avoid hidden files and files in directories
        if path.name[0] != ".":
            # Add this path to our list of zip directories
            zip_list.append(str(path))
    return zip_list

# This function gives us all the directory
# paths for unzipped files
def unzipped_dirs():
    # For each *.zip directory
    # we want to get the path relative
    # to raw that the .zip is in
    # We can use this relative path
    # and append it to raw/unzipped/
    # Make this directory 
    # and append to a list of output
    # files
    unzip_list = []
    for path in Path(FR).rglob("*.zip"):
        # Avoid hidden files and files in directories
        if path.name[0] != ".":
            # Get root for the directory this .zip file is in
            zip_root = path.relative_to(FR).parents[0]

            # Get path to interim/zip_root
            zip_to_path = join(UNZIP_DIR, zip_root)

            # Make directory, including parents
            # No need to check if directory exists bc
            # it is only created when this script is run
            Path(zip_to_path).mkdir(parents=True, exist_ok=True)

            # Append
            unzip_list.append(zip_to_path)
    return unzip_list

# This function gives us our 
# structured directory path -
# a unique set of these
def unzipped_downloads():
    unzip_list = unzipped_dirs()
    # We need the unique set for the Snakemake
    return list(set(unzip_list))