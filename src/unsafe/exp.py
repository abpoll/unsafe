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
from os.path import join
import warnings

os.environ["USE_PYGEOS"] = "0"
import unsafe.download as undown
import unsafe.files as unfile
import unsafe.const as uncnst


def get_nsi_geo(fips, nsi_crs, exp_dir_r):
    """
    Finds the raw json data for the county named by
    the fips argument and returns a geodataframe
    """

    nsi_filep = join(exp_dir_r, fips, "nsi.json")
    with open(nsi_filep, "r") as fp:
        nsi_full = json.load(fp)

    nsi_df = pd.json_normalize(nsi_full["features"])

    geometry = gpd.points_from_xy(nsi_df["properties.x"], nsi_df["properties.y"])
    nsi_gdf = gpd.GeoDataFrame(nsi_df, geometry=geometry, crs=nsi_crs)

    drop_cols = ["type", "geometry.type", "geometry.coordinates"]
    nsi_gdf = nsi_gdf.drop(columns=drop_cols)
    col_updates = [x.replace("properties.", "") for x in nsi_gdf.columns]
    nsi_gdf.columns = col_updates

    print("Prepared geodataframe")

    return nsi_gdf


def get_struct_subset(nsi_gdf, filter=None, occtype_list=None):
    """
    Return a column subset gdf in terms of columns for
    generating the structure ensemble. Also subset
    in terms of rows if a string is passed to filter.
    If occtype column is in that filter string, you must
    pass in an occtype_list. The string is passed to pd.query()
    and currently this function does not send helpful messages
    if you pass an incorrect string, so caveat emptor.
    """
    sub_cols = [
        "fd_id",
        "occtype",
        "found_type",
        "cbfips",
        "bldgtype",
        "ftprntsrc",
        "found_ht",
        "val_struct",
        "sqft",
        "val_cont",
        "source",
        "firmzone",
        "ground_elv_m",
        "num_story",
        "geometry",
    ]

    nsi_sub = nsi_gdf.loc[:, sub_cols]

    if filter is not None:
        nsi_sub = nsi_sub.query(filter)

    return nsi_sub


def clip_ref_files(clip_gdf, clip_str, fips_args, ref_downloads,
                   wcard_dict, ref_dir_uz, ref_dir_i):
    """
    Clip reference shapefiles to a specified geometry and save the results.
    
    This function processes geographic reference files (census tracts, block groups, etc.)
    by clipping them to a specified boundary (typically a county or study area) and 
    saving the clipped files with standardized names to the interim directory.
    
    Parameters
    ----------
    clip_gdf : geopandas.GeoDataFrame
        GeoDataFrame containing the geometry to clip the reference files to.
        Typically represents a county or study area boundary.
    
    clip_str : str
        Used to organize output files in the directory structure. Often
        the FIPS code for the county or area being processed. Can also be
        the name of a catchment area or other unit that may overlap with
        several counties. 

    fips_args: dict
        A dictionary of the FIPS, STATEFIPS, and NATION key/value pairs for
        a specific call of this function. 
    
    ref_downloads: pd.DataFrame
        A subset of the DOWNLOADS dataframe, subset to 
        those for ref files, which we use to efficiently find
        the .shp files for clipping. 
    
    wcard_dict: dict
        A dictionary of the form wildcard strings take (e.g., {FIPS}) to the
        value of those keys for a specific call of this function. 

    ref_dir_uz : str or Path
        Path to the directory containing unzipped reference shapefiles.
        Expected structure is ref_dir_uz/[NATION]/[TYPE]/tl_YYYY_[FIPS]_[TYPE].shp
        Example: "data/raw/unzipped/ref/US/county/tl_2022_us_county.shp"
    
    ref_dir_i : str or Path
        Path to the interim directory where clipped files will be saved.
        Files will be saved as ref_dir_i/[FIPS]/[STANDARDIZED_NAME].gpkg
    
    Returns
    -------
    None
        Results are saved to disk at the specified locations
    
    Notes
    -----
    - All reference files are reprojected to match the CRS of clip_gdf before clipping
    - Output files are saved in GeoPackage (.gpkg) format for better performance
    """
    print("Processing reference files...")
    
    # Find all shapefiles in the reference directory
    for ref_dwnld in ref_downloads.itertuples():
        str_tokens, endpoint = undown.process_file(ref_dwnld)
        if any(wcard in endpoint for wcard in wcard_dict.keys()):
            filled_url = unfile.fill_wcard(endpoint, wcard_dict)
        else:
            filled_url = endpoint
        ref_filename = filled_url.split('/')[-1][:-4] + '.shp'
        ref_name_out = str_tokens[-1]
        ref_filep = '/'.join([ref_dir_uz , fips_args[str_tokens[0]][0], 
                              ref_name_out, ref_filename])
      
        print("Found shapefile: " + ref_name_out)

        # Read in the file
        ref_shp = gpd.read_file(ref_filep)
        print("Read reference")

        # Reproject and clip our reference shapefile
        ref_reproj = ref_shp.to_crs(clip_gdf.crs)
        ref_clipped = gpd.clip(ref_reproj, clip_gdf)
        print("Reprojected and clipped")

        # Write file
        ref_out_filep = join(ref_dir_i, clip_str, ref_name_out + ".gpkg")
        unfile.prepare_saving(ref_out_filep)
        ref_clipped.to_file(ref_out_filep, driver="GPKG")

        # Helpful message to track progress
        print("Saved Ref: " + ref_name_out)


def process_national_sovi(sovi_list, fips, vuln_dir_r, ref_dir_i, vuln_dir_i):
    """
    Process the national social vulnerability data
    that are provided in sovi_list for the provided county.
    sovi_list has the name of the sovi data that need
    to be processed.
    """
    root_dir = join(vuln_dir_r, "social", "US")

    # Load relevant spatial data (tract, block group)
    tract_filep = join(ref_dir_i, fips, "tract.gpkg")
    bg_filep = join(ref_dir_i, fips, "bg.gpkg")
    tract_geo = gpd.read_file(tract_filep)
    bg_geo = gpd.read_file(bg_filep)

    if "cejst" in sovi_list:
        ce_filep = join(root_dir, "cejst.csv")
        cejst = pd.read_csv(ce_filep, dtype={"Census tract 2010 ID": "str"})

        # Columns to keep
        # Identified as disadvantaged
        # Census tract 2010 ID
        keep_cols = ["Census tract 2010 ID", "Identified as disadvantaged"]
        cejst_sub = cejst[keep_cols]
        # Rename columns
        cejst_sub.columns = ["GEOID", "disadvantaged"]

        # Merge with tract_geo
        cejst_f = tract_geo[["GEOID", "geometry"]].merge(
            cejst_sub, on="GEOID", how="inner"
        )

        # Retain only the disadvantaged
        cejst_f = cejst_f[cejst_f["disadvantaged"] == True].drop(
            columns="disadvantaged"
        )

        # Write file
        cejst_out_filep = join(vuln_dir_i, "social", fips, "cejst.gpkg")
        unfile.prepare_saving(cejst_out_filep)
        cejst_f.to_file(cejst_out_filep, driver="GPKG")

        print("Processed cejst")

    if "svi" in sovi_list:
        svi_filename = "svi.csv"
        svi_filep = join(root_dir, svi_filename)
        svi = pd.read_csv(svi_filep)

        # Subset columns
        # The overall summary ranking variable is RPL_THEMES
        # From https://www.atsdr.cdc.gov/placeandhealth/svi/
        # documentation/SVI_documentation_2020.html
        keep_cols = ["FIPS", "RPL_THEMES"]
        svi_high = svi[keep_cols]

        # Rename FIPS to GEOID
        # Rename RPL_THEMES to sovi
        # GEOID needs to be a str, 11 characters long
        svi_high = svi_high.rename(columns={"FIPS": "GEOID", "RPL_THEMES": "sovi"})
        svi_high["GEOID"] = svi_high["GEOID"].astype(str).str.zfill(11)

        # Subset to tracts in our study area (using the tract_geo geometries)
        svi_f = tract_geo[["GEOID", "geometry"]].merge(
            svi_high, on="GEOID", how="inner"
        )

        # Write out file
        sovi_out_filep = join(vuln_dir_i, "social", fips, "sovi.gpkg")
        svi_f.to_file(sovi_out_filep, driver="GPKG")

        print("Processed CDC SVI")


def process_nfhl(fips, unzip_dir, pol_dir_i):
    """
    Process the raw NFHL data and write it out
    """
    # We want S_FLD_HAZ_AR
    fld_haz_fp = join(unzip_dir, fips, "S_FLD_HAZ_AR.shp")
    nfhl = gpd.read_file(fld_haz_fp)

    # Keep FLD_ZONE, FLD_AR_ID, STATIC_BFE, geometry
    keep_cols = ["FLD_ZONE", "FLD_AR_ID", "STATIC_BFE", "ZONE_SUBTY", "geometry"]
    nfhl_f = nfhl.loc[:, keep_cols]

    # Adjust .2 pct X zones to X_500
    nfhl_f.loc[
        nfhl_f["ZONE_SUBTY"] == "0.2 PCT ANNUAL CHANCE FLOOD HAZARD", "FLD_ZONE"
    ] = (nfhl_f["FLD_ZONE"] + "_500")

    # Update column names
    # Lower case
    nfhl_f.columns = [x.lower() for x in nfhl_f.columns]

    # Drop ZONE_SUBTY
    nfhl_f = nfhl_f.drop(columns=["zone_subty"])

    # Write file
    nfhl_out_filep = join(pol_dir_i, fips, "fld_zones.gpkg")
    unfile.prepare_saving(nfhl_out_filep)
    nfhl_f.to_file(nfhl_out_filep, driver="GPKG")
    # TODO better logging
    print("Wrote NFHL for county")


def get_ref_ids(exp_gdf, clip_str, ref_id_names_dict, ref_dir_i, exp_dir_i):
    """
    Spatially join a gdf representing an administrative
    reference, like census tract, to individual structures.

    Parameters
    ----------
    exp_gdf : geopandas.GeoDataFrame
        GeoDataFrame containing the geometry to merge with the reference 
        files. Typically represents NSI but can also be custom structure
        inventory. The index must be set to the unique structure id. 
    
    clip_str : str
        Used to organize output files in the directory structure. Often
        the FIPS code for the county or area being processed. Can also be
        the name of a catchment area or other unit that may overlap with
        several counties. 

    ref_id_names_dict: dict
        A dictionary that links the ref id name to its unique id in the
        dataset (e.g., census tracts have an id called 'GEOID')
    
    ref_dir_i : str or Path
        Path to the interim directory where clipped files are located.

    exp_dir_i : str or Path
        Path to the interim directory where the 
        "clip_str"_ref.pqt file will be saved.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame of the id and ref_ids linked together
    
    Notes
    -----
    - All reference files are reprojected to match the CRS of clip_gdf before clipping
    - There is a single output file of structure id to ref id matches
    """
    if exp_gdf.index.name is None:
        no_id_warn = ("Warning: No ID set as index. It is highly recommended" +
                       " to set an index for consistent merges later in your workflow.")
        warnings.warn(no_id_warn)

    ref_df_list = []
    for ref_name, ref_id in ref_id_names_dict.items():
        # We don't need to process county if it's in REF_ID_NAMES_DICT
        # because that can be inferred from other reference data
        if ref_name != "county":
            ref_filep = join(ref_dir_i, clip_str, ref_name + ".gpkg")

            # Load in the ref file
            ref_geo = gpd.read_file(ref_filep)
            print("Read ref file: " + ref_name)

            # Limit the geodataframe to our ref id and 'geometry' column
            keep_col = [ref_id, "geometry"]
            ref_geo_sub = ref_geo[keep_col]

            # Limit the exp to our geometry column
            keep_col_nsi = ["geometry"]
            exp_sub = exp_gdf[keep_col_nsi]

            # For now, do centroid of structures if not already
            # the geometry type
            if any(exp_gdf.geometry.type == 'Polygon'):
                # Make sure we are in a projected geometry
                # when getting the centroid
                exp_gdf['geometry'] = exp_gdf['geometry'].to_crs(epsg='5070')
                exp_gdf['geometry'] = exp_gdf['geometry'].centroid

            # Reproj nsi_sub to the reference crs
            exp_reproj = exp_sub.to_crs(ref_geo.crs)
            
            # Do a spatial join
            exp_ref = gpd.sjoin(exp_reproj, ref_geo_sub, predicate="within")
            print("Spatial join with structures")

            # Set index to fd_id and just keep the ref_id
            # Rename that column to our ref_name + '_id'
            # Append this to our ref_df_list
            exp_ref_f = exp_ref[[ref_id]]
            exp_ref_f = exp_ref_f.rename(columns={ref_id: ref_name + "_id"})
            ref_df_list.append(exp_ref_f)

            # Helpful message
            print("Linked reference to structures: " + ref_name + "_id")

    # Can concat and write
    return pd.concat(ref_df_list, axis=1).reset_index()


def get_spatial_var(nsi_gdf, var_gdf, var_name, fips, exp_dir_i, var_keep_cols=None):
    """
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
    """

    nsi_reproj = nsi_gdf.to_crs(var_gdf.crs)
    nsi_sub = nsi_reproj[["fd_id", "geometry"]]

    # TODO - could accommodate other kinds of
    # spatial joins, hypothetically
    nsi_joined = gpd.sjoin(nsi_sub, var_gdf, predicate="within")

    # We'll keep fd_id + what is passed in or
    # all the columns in the var_gdf
    keep_cols = ["fd_id"]
    if var_keep_cols is not None:
        keep_cols = keep_cols + var_keep_cols
    else:
        keep_cols = keep_cols + var_gdf.columns
    nsi_out = nsi_joined[keep_cols]

    nsi_out_filep = join(exp_dir_i, fips, "nsi_" + var_name + ".pqt")
    unfile.prepare_saving(nsi_out_filep)
    nsi_out.to_parquet(nsi_out_filep)
    print("Wrote out: " + var_name)


def get_inundations(nsi_gdf, haz_crs, ret_pers, haz_dir_uz, haz_filen, scens=None):
    """
    Reproject nsi into the hazard CRS and sample the depths
    from each of the depth grids that are provided in the
    external hazard directory.

    nsi_gdf: GeoDataFrame, all structures with Point geometries
    fips: str, the county code
    """

    # TODO if UNSAFE ever departs from relying on the NSI, it might
    # be helpful to have a more general inundation sampling procedure
    # for rasterized shapes, too (a point would be a 1 in a 0/1 raster
    # of structure locations)

    nsi_reproj = nsi_gdf.to_crs(haz_crs)

    # For each depth grid, we will sample from the grid
    # by way of a list of coordinates from the reprojected
    # nsi geodataframe (this is the fastest way I know to do it
    # for point based spatial data)
    coords = zip(nsi_reproj["geometry"].x, nsi_reproj["geometry"].y)
    coord_list = [(x, y) for x, y in coords]
    print("Store NSI coordinates in list")

    # We'll store series of fd_id/depth pairs for each depth grid
    # in a list and concat this into a df after iterating
    depth_list = []
    dg_dict = {}

    # Loop through RPs
    # TODO it would be better not to always assume you
    # have depth grids that correspond to return periods.
    # Right now this code is probably too specific to the case study,
    # but is easily adaptable
    if scens is not None:
        for scen in scens:
            for rp in ret_pers:
                dg = unfile.read_dg(rp, haz_dir_uz, haz_filen, scen)
                print("Read in " + rp + " depth grid")

                sampled_depths = [x[0] for x in dg.sample(coord_list)]
                print("Sampled depths from grid")

                name = scen + "_" + rp if len(scens) > 1 else rp
                depths = pd.Series(sampled_depths, index=nsi_reproj["fd_id"], name=name)

                depth_list.append(depths)
                print("Added depths to list\n")
    else:
        for rp in ret_pers:
            dg = unfile.read_dg(rp, haz_dir_uz, haz_filen)
            print("Read in " + rp + " depth grid")

            sampled_depths = [x[0] for x in dg.sample(coord_list)]
            print("Sampled depths from grid")

            depths = pd.Series(sampled_depths, index=nsi_reproj["fd_id"], name=rp)

            depth_list.append(depths)
            print("Added depths to list\n")

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
    depth_df_f = depth_df_f * uncnst.MTR_TO_FT

    # DDFs do not have the precision to handle
    # any finer rounding than this.
    return depth_df_f.round(2)
