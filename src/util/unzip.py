# Packages
from os.path import join
from pathlib import Path
import glob
from zipfile import ZipFile
import zipfile_deflate64
from collections import Counter
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


# This function calls the other helpfer functions to unzip
# all of the external and raw data in our
# directory. In a many county setting, 
# it probably would make sense for this 
# to work based on state, county, and US 
# arguments to facilitate distributed processing
def unzip_raw():
    # This gives us a list
    # of files to unzip, and the directories
    # to unzip them to
    to_unzip = zipped_downloads()
    unzip_dirs = unzipped_dirs()

    # We're going to loop through the files we need to unzip
    # and extract them into the appropriate directories
    # One thing that will help the directory structure stay organized
    # is to keep track of what the destination parent directory is
    # If the parent directory appears multiple times in unzip_dirs
    # we should also use the name of the file (excluding extension)
    # as a subdirectory
    # We can use the Counter() class from collections for this...
    count = Counter(unzip_dirs)
    need_subdir = [k for k, v in count.items() if v > 1]

    for i, filepath in enumerate(to_unzip):
        path = Path(filepath)

        # If unzip_dirs[i] is in need_subdir
        # we are going to add a subdirectory
        # from str.split('/')[-1][:-4]
        # This gives us cdc from cdc.zip, for example

        out_filedir = unzip_dirs[i]
        if unzip_dirs[i] in need_subdir:
            subdir = filepath.split('/')[-1][:-4]
            out_filedir = join(out_filedir, subdir)
            
        with ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(out_filedir)
        
        #TODO helpful log message
        print('Unzipped: ' + str(path.name).split('.')[0])