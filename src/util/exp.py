import json
import glob
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import shape
import rasterio 
from rasterio.warp import calculate_default_transform, reproject, Resampling
import rasterio.mask
from pyproj import CRS
import os
os.environ['USE_PYGEOS'] = '0'

from util.files import *
from util.const import *


def get_nsi_geo(fips):
    '''
    Finds the raw json data for the county named by 
    the fips argument and returns a geodataframe 
    '''

    nsi_filep = join(EXP_DIR_R, fips, 'nsi.json')
    with open(nsi_filep, 'r') as fp:
        nsi_full = json.load(fp)

    nsi_df = pd.json_normalize(nsi_full['features'])

    geometry = gpd.points_from_xy(nsi_df['properties.x'],
                                nsi_df['properties.y'])
    nsi_gdf = gpd.GeoDataFrame(nsi_df, geometry=geometry,
                            crs=NSI_CRS)

    drop_cols = ['type', 'geometry.type', 'geometry.coordinates']
    nsi_gdf = nsi_gdf.drop(columns=drop_cols)
    col_updates = [x.replace("properties.", "") for x in nsi_gdf.columns]
    nsi_gdf.columns = col_updates

    return nsi_gdf

def get_struct_subset(nsi_gdf,
                      filter=None,
                      occtype_list=None):
    '''
    Return a column subset gdf in terms of columns for
    generating the structure ensemble. Also subset
    in terms of rows if a string is passed to filter. 
    If occtype column is in that filter string, you must
    pass in an occtype_list. The string is passed to pd.query() 
    and currently this function does not send helpful messages
    if you pass an incorrect string, so caveat emptor. 
    '''
    sub_cols = ['fd_id', 'occtype', 'found_type', 'cbfips', 'bldgtype',
                'ftprntsrc', 'found_ht', 'val_struct', 'sqft',
                'val_cont', 'source', 'firmzone', 'ground_elv_m',
                'num_story', 'geometry']
    
    nsi_sub = nsi_gdf.loc[:, sub_cols]

    if filter is not None:
        nsi_sub = nsi_sub.query(filter)
    
    return nsi_sub

def clip_ref_files(clip_gdf, fips):
    '''
    Clip reference files in a clip geometry's 
    CRS and write out the resulting files.
    '''
    #TODO it could be helpful to have the fips code
    # also instruct us about where to read unzipped
    # files from. Innocuous for now, but not scalable
    # to just look at REF_DIR_UZ. Eventually, that
    # will also have to structure files by
    # fips, state, etc.

    # For each .shp file in our unzipped ref directory
    # we are going to reproject & clip, then write out
    for path in Path(REF_DIR_UZ).rglob('*.shp'):
        # Read in the file
        ref_shp = gpd.read_file(path)
        
        # Process the filename to figure out what 
        # reference data this is
        # the files are written out in the form of
        # tl_2022_34_tract.shp, for example
        # so we split the string on '_', take the
        # last element of the array, and ignore
        # the last 4 characters
        ref_name = path.name.split('_')[-1][:-4]
        # Replace the ref name with our ref_name dict values
        ref_name_out = REF_NAMES_DICT[ref_name]

        # Reproject and clip our reference shapefile
        ref_reproj = ref_shp.to_crs(clip_gdf.crs)
        ref_clipped = gpd.clip(ref_reproj, clip_gdf)
        
        # Write file
        ref_out_filep = join(REF_DIR_I, fips, ref_name_out + ".gpkg")
        prepare_saving(ref_out_filep)
        ref_clipped.to_file(ref_out_filep,
                            driver='GPKG')

        # Helpful message to track progress
        print("Saved Ref: " + ref_name_out)

def process_national_sovi(sovi_list, fips):
    '''
    Process the national social vulnerability data
    that are provided in sovi_list for the provided county.
    sovi_list has the name of the sovi data that need
    to be processed. 
    '''
    root_dir = join(VULN_DIR_R, 'social', 'US')

    # Load relevant spatial data (tract, block group)
    tract_filep = join(REF_DIR_I, fips, 'tract.gpkg')
    bg_filep = join(REF_DIR_I, fips, 'bg.gpkg')
    tract_geo = gpd.read_file(tract_filep)
    bg_geo = gpd.read_file(bg_filep)

    if 'cejst' in sovi_list:
        ce_filep = join(root_dir, 'cejst.csv')
        cejst = pd.read_csv(ce_filep, dtype={'Census tract 2010 ID': 'str'})

        # Columns to keep
        # Identified as disadvantaged
        # Census tract 2010 ID
        keep_cols = ['Census tract 2010 ID', 'Identified as disadvantaged']
        cejst_sub = cejst[keep_cols]
        # Rename columns
        cejst_sub.columns = ['GEOID', 'disadvantaged']

        # Merge with tract_geo
        cejst_f = tract_geo[['GEOID', 'geometry']].merge(cejst_sub,
                                                        on='GEOID',
                                                        how='inner')

        # Retain only the disadvantaged 
        cejst_f = cejst_f[cejst_f['disadvantaged'] == True].drop(columns='disadvantaged')

        # Write file
        cejst_out_filep = join(VULN_DIR_I, 'social', fips, 'cejst.gpkg')
        prepare_saving(cejst_out_filep)
        cejst_f.to_file(cejst_out_filep, driver='GPKG')

        print('Processed cejst')

    if 'svi' in sovi_list:
        svi_filename = 'svi.csv'
        svi_filep = join(root_dir, svi_filename)
        svi = pd.read_csv(svi_filep)

        # Subset columns
        # The overall summary ranking variable is RPL_THEMES
        # From https://www.atsdr.cdc.gov/placeandhealth/svi/
        # documentation/SVI_documentation_2020.html
        keep_cols = ['FIPS', 'RPL_THEMES']
        svi_high = svi[keep_cols]

        # Rename FIPS to GEOID
        # Rename RPL_THEMES to sovi
        # GEOID needs to be a str, 11 characters long
        svi_high = svi_high.rename(columns={'FIPS': 'GEOID',
                                            'RPL_THEMES': 'sovi'})
        svi_high['GEOID'] = svi_high['GEOID'].astype(str).str.zfill(11)

        # Subset to tracts in our study area (using the tract_geo geometries)
        svi_f = tract_geo[['GEOID', 'geometry']].merge(svi_high,
                                                    on='GEOID',
                                                    how='inner')

        # Write out file
        sovi_out_filep = join(VULN_DIR_I, 'social', fips, 'sovi.gpkg')
        svi_f.to_file(sovi_out_filep, driver='GPKG')

        print('Processed CDC SVI')
    
    if 'lmi' in sovi_list:
        lmi_filename = 'ACS_2015_lowmod_blockgroup_all.xlsx'
        lmi_filep = join(root_dir, lmi_filename)
        lmi = pd.read_excel(lmi_filep, engine='openpyxl')
        # Get GEOID for merge (last 12 characters is the bg id)
        lmi['GEOID'] = lmi['GEOID'].str[-12:]

        # Retain GEOID and Lowmod_pct
        keep_cols = ['GEOID', 'Lowmod_pct']
        lmi_f = bg_geo[['GEOID', 'geometry']].merge(lmi[keep_cols],
                                                    on='GEOID',
                                                    how='inner')

        # Write file
        lmi_out_filep = join(VULN_DIR_I, 'social', fips, 'lmi.gpkg')
        lmi_f.to_file(lmi_out_filep, driver='GPKG')
        print('Processed low-mod income')

def process_nfhl(fips):
    '''
    Process the raw NFHL data and write it out
    '''
    # We want S_FLD_HAZ_AR 
    fld_haz_fp = join(UNZIP_DIR, 'external', 'pol',
                      fips, 'S_FLD_HAZ_AR.shp')
    nfhl = gpd.read_file(fld_haz_fp)

    # Keep FLD_ZONE, FLD_AR_ID, STATIC_BFE, geometry
    keep_cols = ['FLD_ZONE', 'FLD_AR_ID', 'STATIC_BFE', 'ZONE_SUBTY',
                'geometry']
    nfhl_f = nfhl.loc[:,keep_cols]

    # Adjust .2 pct X zones to X_500
    nfhl_f.loc[nfhl_f['ZONE_SUBTY'] == '0.2 PCT ANNUAL CHANCE FLOOD HAZARD',
            'FLD_ZONE'] = nfhl_f['FLD_ZONE'] + '_500'

    # Update column names
    # Lower case
    nfhl_f.columns = [x.lower() for x in nfhl_f.columns]

    # Drop ZONE_SUBTY
    nfhl_f = nfhl_f.drop(columns=['zone_subty'])

    # Write file
    nfhl_out_filep = join(POL_DIR_I, fips, 'fld_zones.gpkg')
    prepare_saving(nfhl_out_filep)
    nfhl_f.to_file(nfhl_out_filep,
                driver='GPKG')
    # TODO better logging
    print('Wrote NFHL for county')