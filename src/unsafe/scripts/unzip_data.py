from zipfile import ZipFile
import zipfile_deflate64
import os
from pathlib import Path
# import sys
# sys.path.append('/jumbo/keller-lab/projects/icom/nsi_unc/workflow')
from util.unzip import *

# Call zipped_downloads and unzipped_dirs
# from the util.unzip script
# This gives us a list
# of files to unzip, and the directories
# to unzip them to
to_unzip = zipped_downloads()
unzip_dirs = unzipped_dirs()

for i, filepath in enumerate(to_unzip):
    # Get path version of filepath
    path = Path(filepath)
    # The destination directory
    unzip_path = Path(unzip_dirs[i])
    with ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(unzip_path)
    
    #TODO helpful log message
    print('Unzipped: ' + str(path.name).split('.')[0])