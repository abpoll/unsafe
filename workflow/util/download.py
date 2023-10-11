# Packages
import requests
import os
from os.path import join
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
from pyproj import CRS

os.environ["USE_PYGEOS"] = "0"

