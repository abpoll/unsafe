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


def get_nsi_geo(fips, nsi_crs, exp_dir_r):
    '''
    Finds the raw json data for the county named by 
    the fips argument and returns a geodataframe 
    '''

    nsi_filep = join(exp_dir_r, fips, 'nsi.json')
    with open(nsi_filep, 'r') as fp:
        nsi_full = json.load(fp)

    nsi_df = pd.json_normalize(nsi_full['features'])

    geometry = gpd.points_from_xy(nsi_df['properties.x'],
                                nsi_df['properties.y'])
    nsi_gdf = gpd.GeoDataFrame(nsi_df, geometry=geometry,
                               crs=nsi_crs)

    drop_cols = ['type', 'geometry.type', 'geometry.coordinates']
    nsi_gdf = nsi_gdf.drop(columns=drop_cols)
    col_updates = [x.replace("properties.", "") for x in nsi_gdf.columns]
    nsi_gdf.columns = col_updates

    print('Prepared geodataframe')

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

def clip_ref_files(clip_gdf, fips,
                   ref_dir_uz, ref_dir_i, ref_names_dict):
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
    for path in Path(ref_dir_uz).rglob('*.shp'):
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
        ref_name_out = ref_names_dict[ref_name]

        # Reproject and clip our reference shapefile
        ref_reproj = ref_shp.to_crs(clip_gdf.crs)
        ref_clipped = gpd.clip(ref_reproj, clip_gdf)
        
        # Write file
        ref_out_filep = join(ref_dir_i, fips, ref_name_out + ".gpkg")
        prepare_saving(ref_out_filep)
        ref_clipped.to_file(ref_out_filep,
                            driver='GPKG')

        # Helpful message to track progress
        print("Saved Ref: " + ref_name_out)

def process_national_sovi(sovi_list, fips,
                          vuln_dir_r, ref_dir_i, vuln_dir_i):
    '''
    Process the national social vulnerability data
    that are provided in sovi_list for the provided county.
    sovi_list has the name of the sovi data that need
    to be processed. 
    '''
    root_dir = join(vuln_dir_r, 'social', 'US')

    # Load relevant spatial data (tract, block group)
    tract_filep = join(ref_dir_i, fips, 'tract.gpkg')
    bg_filep = join(ref_dir_i, fips, 'bg.gpkg')
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
        cejst_out_filep = join(vuln_dir_i, 'social', fips, 'cejst.gpkg')
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
        sovi_out_filep = join(vuln_dir_i, 'social', fips, 'sovi.gpkg')
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
        lmi_out_filep = join(vuln_dir_i, 'social', fips, 'lmi.gpkg')
        lmi_f.to_file(lmi_out_filep, driver='GPKG')
        print('Processed low-mod income')

def process_nfhl(fips, unzip_dir, pol_dir_i):
    '''
    Process the raw NFHL data and write it out
    '''
    # We want S_FLD_HAZ_AR 
    fld_haz_fp = join(unzip_dir, 'external', 'pol',
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
    nfhl_out_filep = join(pol_dir_i, fips, 'fld_zones.gpkg')
    prepare_saving(nfhl_out_filep)
    nfhl_f.to_file(nfhl_out_filep,
                driver='GPKG')
    # TODO better logging
    print('Wrote NFHL for county')

def get_ref_ids(nsi_gdf, fips,
                ref_id_names_dict, ref_dir_i, exp_dir_i):
    '''
    Spatially join a gdf representing an administrative
    reference, like census tract, that we want to link
    to  individual structures.
    We project the structures to the CRS of the
    ref_gdf for the merge. 

    nsi_gdf: GeoDataFrame of structures
    var_gdf: GeoDataFrame of a reference file, like census tracts
    '''

    ref_df_list = []
    for ref_name, ref_id in ref_id_names_dict.items():
        # We don't need to process county if it's in REF_ID_NAMES_DICT
        # because NSI is already linked to counties, and counties
        # are our unit of analysis, so we know this
        if ref_name != 'county':
            ref_filep = join(ref_dir_i, fips, ref_name + ".gpkg")
        
            # Load in the ref file
            ref_geo = gpd.read_file(ref_filep)
        
            # Limit the geodataframe to our ref id and 'geometry' column
            keep_col = [ref_id, 'geometry']
            ref_geo_sub = ref_geo[keep_col]
        
            # Limit the NSI to our fd_id and geometry column
            keep_col_nsi = ['fd_id', 'geometry']
            nsi_sub = nsi_gdf[keep_col_nsi]
        
            # Reproj nsi_sub to the reference crs
            nsi_reproj = nsi_sub.to_crs(ref_geo.crs)
        
            # Do a spatial join
            nsi_ref = gpd.sjoin(nsi_reproj, ref_geo_sub, predicate='within')
        
            # Set index to fd_id and just keep the ref_id
            # Rename that column to our ref_name + '_id'
            # Append this to our ref_df_list
            nsi_ref_f = nsi_ref.set_index('fd_id')[[ref_id]]
            nsi_ref_f = nsi_ref_f.rename(columns={ref_id: ref_name + '_id'})
            ref_df_list.append(nsi_ref_f)
        
            # Helpful message
            print('Linked reference to NSI: ' + ref_name + '_id')

    # Can concat and write
    nsi_refs = pd.concat(ref_df_list, axis=1).reset_index()
    ref_filep = join(exp_dir_i, fips, 'nsi_ref.pqt')
    prepare_saving(ref_filep)
    nsi_refs.to_parquet(ref_filep)

def get_spatial_var(nsi_gdf,
                    var_gdf, 
                    var_name,
                    fips,
                    exp_dir_i,
                    var_keep_cols=None):
    '''
    Spatially join a gdf representing features 
    that we want to link to  individual structures.
    We project the structures to the CRS of the
    var_gdf for the merge. 

    nsi_gdf: GeoDataFrame of structures
    var_gdf: GeoDataFrame that contains relavent features
    that we want to link to nsi_gdf
    var_name: str, the name of the attribute(s) source
    fips: str, county code
    var_keep_cols: list, subset of columns to keep after join
    '''

    nsi_reproj = nsi_gdf.to_crs(var_gdf.crs)
    nsi_sub = nsi_reproj[['fd_id', 'geometry']]

    # TODO - could accommodate other kinds of
    # spatial joins, hypothetically
    nsi_joined = gpd.sjoin(nsi_sub,
                           var_gdf,
                           predicate='within')

    # We'll keep fd_id + what is passed in or
    # all the columns in the var_gdf
    keep_cols = ['fd_id']
    if var_keep_cols is not None:
        keep_cols = keep_cols + var_keep_cols
    else:
        keep_cols = keep_cols + var_gdf.columns
    nsi_out = nsi_joined[keep_cols]

    nsi_out_filep = join(exp_dir_i, fips, 'nsi_' + var_name + '.pqt')
    prepare_saving(nsi_out_filep)
    nsi_out.to_parquet(nsi_out_filep)
    print('Wrote out: ' + var_name)

def get_inundations(nsi_gdf, fips, haz_crs, ret_pers, exp_dir_i,
                    haz_dir_uz, haz_filen):
    '''
    Reproject nsi into the hazard CRS and sample the depths
    from each of the depth grids that are provided in the
    external hazard directory. 

    nsi_gdf: GeoDataFrame, all structures with Point geometries
    fips: str, the county code
    '''

    #TODO if UNSAFE ever departs from relying on the NSI, it might
    # be helpful to have a more general inundation sampling procedure
    # for rasterized shapes, too (a point would be a 1 in a 0/1 raster
    # of structure locations)

    nsi_reproj = nsi_gdf.to_crs(haz_crs)

    # For each depth grid, we will sample from the grid
    # by way of a list of coordinates from the reprojected
    # nsi geodataframe (this is the fastest way I know to do it
    # for point based spatial data)
    coords = zip(nsi_reproj['geometry'].x, nsi_reproj['geometry'].y)
    coord_list = [(x, y) for x, y in coords]
    print('Store NSI coordinates in list')

    # We'll store series of fd_id/depth pairs for each depth grid
    # in a list and concat this into a df after iterating
    depth_list = []
    dg_dict = {}

    # Loop through RPs
    # TODO it would be better not to always assume you
    # have depth grids that correspond to return periods. 
    # Right now this code is probably too specific to the case study,
    # but is easily adaptable 
    for rp in ret_pers:
        dg = read_dg(rp, haz_dir_uz, haz_filen)
        print('Read in ' + rp + ' depth grid')

        sampled_depths = [x[0] for x in dg.sample(coord_list)]
        print('Sampled depths from grid')

        depths = pd.Series(sampled_depths,
                           index=nsi_reproj['fd_id'],
                           name=rp)

        depth_list.append(depths)
        print('Added depths to list\n')

    depth_df = pd.concat(depth_list, axis=1)

    # Replace nodata values with 0
    depth_df[depth_df == dg.nodata] = 0

    # Retain only structures with some flood exposure
    depth_df_f = depth_df[depth_df.sum(axis=1) > 0]

    # Multiply by MTR_TO_FT to convert to feet
    # TODO it would be better if this was only done
    # based on the need for a unit conversion, which
    # could potentially be inferred from the CRS
    # of the hazard data
    depth_df_f = depth_df_f*MTR_TO_FT

    
    # TODO right now we process return period based columns
    # in UNSAFE so we can make these reflect the 
    # return period, not the annual exceedance probability.
    # This might not be the best default way to handle
    # the depth grid column names, and might be more of 
    # a case-study by case-study thing to handle. 
    ncol = [str(round(100/float(x.replace('_', '.')))) for x in depth_df_f.columns]
    depth_df_f.columns = ncol

    # Write out dataframe that links fd_id to depths
    # with columns corresponding to ret_per (i.e. 500, 100, 50, 10)
    nsi_depths_out = join(exp_dir_i, fips, 'nsi_depths.pqt')
    prepare_saving(nsi_depths_out)
    # Round to nearest hundredth foot
    # Depth-damage functions don't have nearly the precision
    # to make use of inches differences, but some precision
    # is needed for subtracting first floor elevation before rounding
    depth_df_f.round(2).reset_index().to_parquet(nsi_depths_out)

    print('Wrote depth dataframe')