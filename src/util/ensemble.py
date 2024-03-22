import os
import json
from pathlib import Path
from os.path import join
os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd
import pandas as pd
import numpy as np

from util.files import *
from util.const import *
from util.ddfs import *

def get_base_df(fips):
    '''
    Return a dataframe of structures with all the
    relevant characteristics needed for
    generating our ensemble and estimating losses

    fips: str, county code
    '''

    nsi_struct = gpd.read_file(join(EXP_DIR_I, fips, 'nsi_sf.gpkg'))
    nsi_ref = pd.read_parquet(join(EXP_DIR_I, fips, 'nsi_ref.pqt'))
    nsi_depths = pd.read_parquet(join(EXP_DIR_I, fips, 'nsi_depths.pqt'))
    nsi_fz = pd.read_parquet(join(EXP_DIR_I, fips, 'nsi_fz.pqt'))

    # Filter to properties with > 0 
    depths_df = nsi_depths[nsi_depths.iloc[:,1:].sum(axis=1) > 0].set_index('fd_id')
    depths_df.columns = ['depth_' + x for x in depths_df.columns]

    # Need foundation type, number stories, structure value
    # for our ensemble. Structure value will be the center of 
    # the distribution and will be passed to the loss estimation
    # function. Foundation type will be drawn from the implicit
    # distribution in the NSI data. For each census unit that we choose, 
    # we are going to get the multinomial probabilities of 
    # a building having a certain foundation type & number of stories
    # Ideally, we would do this conditioned on prefirm but the
    # building year column is based on median year built from ACS
    # data
    # From the foundation type that is drawn from the multinomial in 
    # the ensemble, we will get the FFE from the distribution 
    # defined in the code for the Wing et al. 2022 paper
    # The point estimate version will just use default values

    # Start by retaining only relevant columns in nsi_struct
    # Then subset this and nsi_ref to the fd_id in nsi_depths
    keep_cols = ['fd_id', 'occtype', 'val_struct', 'bldgtype',
                'found_type', 'num_story', 'found_ht']
    nsi_res = nsi_struct[keep_cols]

    # We need reference ids for spatially defined distributions
    # for certain characteristics
    nsi_res = nsi_res.merge(nsi_ref, on='fd_id')
    # We're also going to merge in fzs
    nsi_res = nsi_res.merge(nsi_fz[['fd_id', 'fld_zone']], on='fd_id')

    # Split occtype to get the number of stories and basement
    # TODO - only would work for residential properties, I think
    # We only need to keep stories for the purposes
    # of estimating the distribution that stories comes from
    # We will draw basement from the foundation type
    # distribution which also gives us first floor elevation
    structs = nsi_res['occtype'].str.split('-').str[1]
    basements = structs.str[2:]
    stories = structs.str[:2]

    nsi_res = nsi_res.assign(stories=stories)

    # Retain only the rows that correspond to structures
    # that are exposed to flood depths
    nsi_res_f = nsi_res[nsi_res['fd_id'].isin(nsi_depths['fd_id'])].set_index('fd_id')

    # Merge in the depths to the struct df you are working with
    # Also merge in the refs - note that there are inconsistencies
    # with the cbfips column from nsi directly and the
    # block data downloaded from the census webpage
    # You retain more structures if you use the block data we
    # downloaded in UNSAFE
    full_df = (nsi_res_f.join(depths_df)).reset_index()

    # We also need the fld_zone column processed for using hazus ddfs
    # Get the first character of the flood zone and only retain it
    # if it's a V zone. We are going to use A zone for A and outside
    # (if any) flood zone depth exposures
    ve_zone = np.where(full_df['fld_zone'].str[0] == 'V',
                    'V',
                    'A')
    full_df = full_df.assign(fz_ddf = ve_zone)

    return full_df