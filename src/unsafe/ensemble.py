import os
import json
from pathlib import Path
from os.path import join

os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd
import pandas as pd
import numpy as np
from unsafe.files import *
from unsafe.ddfs import *
import unsafe.const as unconst

def get_base_df(fips, exp_dir_i):
    """
    Return a dataframe of structures with all the
    relevant characteristics needed for
    generating our ensemble and estimating losses

    fips: str, county code
    """

    nsi_struct = gpd.read_file(join(exp_dir_i, fips, "nsi_sf.gpkg"))
    nsi_ref = pd.read_parquet(join(exp_dir_i, fips, "nsi_ref.pqt"))
    nsi_depths = pd.read_parquet(join(exp_dir_i, fips, "nsi_depths.pqt"))
    nsi_fz = pd.read_parquet(join(exp_dir_i, fips, "nsi_fz.pqt"))

    # Filter to properties with > 0
    depths_df = nsi_depths[nsi_depths.iloc[:, 1:].sum(axis=1) > 0].set_index("fd_id")
    depths_df.columns = ["depth_" + x for x in depths_df.columns]

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
    keep_cols = [
        "fd_id",
        "occtype",
        "val_struct",
        "bldgtype",
        "found_type",
        "num_story",
        "found_ht",
    ]
    nsi_res = nsi_struct[keep_cols]

    # We need reference ids for spatially defined distributions
    # for certain characteristics
    nsi_res = nsi_res.merge(nsi_ref, on="fd_id")
    # We're also going to merge in fzs
    nsi_res = nsi_res.merge(nsi_fz[["fd_id", "fld_zone"]], on="fd_id")

    print("Merged flood zones into nsi")

    # Split occtype to get the number of stories and basement
    # TODO - only would work for residential properties, I think
    # We only need to keep stories for the purposes
    # of estimating the distribution that stories comes from
    # We will draw basement from the foundation type
    # distribution which also gives us first floor elevation
    structs = nsi_res["occtype"].str.split("-").str[1]
    basements = structs.str[2:]
    stories = structs.str[:2]

    nsi_res = nsi_res.assign(stories=stories)

    # Retain only the rows that correspond to structures
    # that are exposed to flood depths
    nsi_res_f = nsi_res[nsi_res["fd_id"].isin(nsi_depths["fd_id"])].set_index("fd_id")

    print("Subset to exposed structures")

    # Merge in the depths to the struct df you are working with
    # Also merge in the refs - note that there are inconsistencies
    # with the cbfips column from nsi directly and the
    # block data downloaded from the census webpage
    # You retain more structures if you use the block data we
    # downloaded in UNSAFE
    full_df = (nsi_res_f.join(depths_df)).reset_index()

    print("Merged depths")

    # We also need the fld_zone column processed for using hazus ddfs
    # Get the first character of the flood zone and only retain it
    # if it's a V zone. We are going to use A zone for A and outside
    # (if any) flood zone depth exposuresgi
    ve_zone = np.where(full_df["fld_zone"].str[0] == "V", "V", "A")
    full_df = full_df.assign(fz_ddf=ve_zone)

    print("Prepared base data frame")

    return full_df

def get_loss_ensemble(
    structures_df,
    depths_df,
    config=None,
    vuln_dir=None,
    random_seed=None
):
    
    """
    Generate an ensemble of structure realizations with uncertainty and calculate damages.
    
    This function creates multiple realizations of structures by introducing
    uncertainty in selected characteristics and calculating damages.
    
    Parameters
    ----------
    structures_df : pandas.DataFrame or geopandas.GeoDataFrame
        DataFrame containing all structures with their characteristics.
        Must have a unique identifier column (specified in config['id_col']).
    
    depths_df : pandas.DataFrame
        DataFrame containing depth values for structures.
        Index or id_column should match structures_df's id_column.
        Only structures with non-zero depths will be used for ensemble generation.
    
    vuln_dir : str or Path
        Path to directory containing processed DDF files.
    
    config : dict, optional
        Configuration dictionary with the following keys:
        - 'n_sow': Number of ensemble members (default: 1000)
        - 'struct_list': List of characteristics to vary (e.g., ['ffe', 'val_struct'])
        - 'ffe_dict': Dict mapping foundation types to FFE distribution parameters
        - 'coef_var': Float for structure value uncertainty (default: 0.2)
        - 'ref_col': Column name for spatial reference (default: 'tract_id')
        - 'id_col': Column name for structure identifier (default: 'fd_id')
        - 'ddfs': List of depth-damage function types to use (e.g., ['hazus', 'naccs'])
        - 'base_adj': Boolean for starting basement flooding from bottom of basement
        - 'found_param': Prop. of structures in each ref_id area with various foundation types
        - 'stories_param': Prop. of structures in each ref_id area with various stories
        - 'depth_min': float for filtering low depths (in m) from damage estimation (default: 0)
    
    random_seed : int, optional
        Random seed for reproducibility.
    
    Returns
    -------
    pandas.DataFrame
        DataFrame containing the ensemble with n_sow realizations of each structure.
        Includes columns for each uncertain characteristic and damage estimates.
    
    Notes
    -----
    The function follows this workflow:
    1. Generate reference distributions from the full structures dataset
    2. Filter structures to those with non-zero depths (if depths_df provided)
    3. Generate ensemble members for the filtered structures
    4. Calculate damages using the specified DDFs
    """
    # If required columns are not all present, throw exception
    req_cols = ['tract_id', 'val_struct', 'num_story',
                'found_type', 'occtype']
    if not all([x in structures_df.columns for x in req_cols]):
        raise KeyError('Structures DataFrame missing required column: ' + str(req_cols))

    # Set random seed if provided
    if random_seed is not None:
        rng = np.random.default_rng(random_seed)
    else:
        rng = np.random.default_rng()
       
    # Set default configuration if not provided
    if config is None:
        config = {}
    
    # Extract configuration parameters with defaults
    n_sow = config.get('n_sow', 1000)
    struct_list = config.get('struct_list', ['val_struct'])
    ffe_dict = config.get('ffe_dict', {'S': [0, 0.5, 1.5],
                                       'C': [0, 1.5, 4],
                                       'B': [0, 1.5, 4]})
    coef_var = config.get('coef_var', 0.2)
    ref_col = config.get('ref_col', 'tract_id')
    id_col = config.get('id_col', 'fd_id')
    base_adj = config.get('base_adj', True)
    ddfs = config.get('ddfs', ['naccs'])
    found_param = config.get('found_param', None)
    stories_param = config.get('stories_param', None)
    depth_min = config.get('depth_min', 0)

    print(f"Generating ensemble with {n_sow} states of the world...")
    print(f"Uncertain characteristics: {struct_list}")

    # Drop any depths as required
    # If depth_min is 0, this drops any null depths
    depths_df = depths_df[depths_df.sum(axis=1) > depth_min]

    # Convert depths to ft
    depths_df = depths_df*unconst.MTR_TO_FT

    # Create the ens_df based on a join of the structures_df and depths_df
    # We join on the shared index and then get the id_col into the 
    # dataframe before generating the full ensemble dataframe
    base_df = structures_df.join(depths_df, how='inner').reset_index()

    # We need a dataframe of the right size and index
    ens_df = base_df.loc[np.repeat(base_df.index, n_sow)].reset_index(drop=True)

    # We will subset structures_df to a dataframe that
    # corresponds to all entries in the same census tract
    # as those in ens_df. This approach assumes there is no correlation of
    # the foundation type proportions and number of stories
    # with features that vary within a census tract.
    struct_tot = structures_df[structures_df[ref_col].isin(base_df[ref_col])]
    # Also make sure the foundation type is one of C, S, or B
    # TODO this should be updated to link more foundation types
    # and damage functions
    struct_tot = struct_tot[struct_tot["found_type"].isin(["B", "C", "S"])]

    # We also want the occtype
    # TODO - may want to treat this as uncertain characteristic
    occtypes = ens_df['occtype'].copy()

    # If a variable is in struct_list, we will sample from a distribution
    # If not, we will use the single value from base_df

    if "val_struct" in struct_list:
        # Draw from the structure value distribution for each property
        # normal(val_struct, val_struct*CF_DET) where these are array_like
        # Using 1 as an artificial, arbitrary lower bound on value
        # Very low probability of getting a negative number but we cannot
        # allow that because you cannot have negative risk
        vals = rng.normal(ens_df["val_struct"], ens_df["val_struct"] * coef_var)
        vals[vals < 1] = 1
    else:
        vals = ens_df["val_struct"].copy()

    print("Draw values")

    if "num_story" in struct_list:
        if stories_param is None:
            # Determine the #stories distribution
            # Get the total number of structures w/ number of stories
            # in each ref_col
            stories_sum = struct_tot.groupby([ref_col, "num_story"]).size()
            # Then get the proportion
            stories_prop = stories_sum / struct_tot.groupby([ref_col]).size()
            # Our parameters can be drawn from this table based on the bg_id
            # of a structure we are estimating losses for
            stories_param = (
                stories_prop.reset_index()
                .pivot(index=ref_col, columns="num_story", values=0)
                .fillna(0)
            )
        # Since it's a binomial distribution, we only need to specify
        # one param. Arbitrarily choose 1
        # Round the param to the hundredth place
        # Store in a dict
        stories_param = stories_param[1].round(3)
        stry_dict = dict(stories_param)

        # Draw from the #stories distribution
        # We do this by mapping ens_df values with STRY_DICT
        # and passing this parameter to rng.binomial()
        # We also need to create an array of 1s
        bin_n = np.ones(len(ens_df), dtype=np.int8)
        bin_p = ens_df[ref_col].map(stry_dict).values
        # This gives us an array of 0s and 1s
        # Based on how STRY_DICT is defined, the probability of
        # success parameter corresponds to 1S, so we need to
        # swap out 1 with 1S and 0 with 2S
        stories = rng.binomial(bin_n, bin_p)
        stories[stories == 0] = 2
    else:
        stories = ens_df["num_story"].copy()

    print("Draw stories")

    if "found_type" in struct_list:
        if found_param is None:
            # Get the foundation type distribution
            found_sum = struct_tot.groupby([ref_col, "found_type"]).size()
            found_prop = found_sum / struct_tot.groupby([ref_col]).size()
            found_param = (
                found_prop.reset_index()
                .pivot(index=ref_col, columns="found_type", values=0)
                .fillna(0)
            )

        # If any of the foundation types are missing from our
        # ffe_dict, we need to add a column of 0
        for f_type in list(ffe_dict.keys()):
            if f_type not in found_param.columns:
                found_param[f_type] = 0

        # We want a dictionary of ref id to a list of B, C, S
        # for direct use in our multinomial distribution draw
        # Store params in a list (each row is ref_col id and corresponds to
        # its own probabilities of each foundation type)
        # This ensures alphabetical ordering which the mapping approach
        # below relies on
        found_param = found_param.sort_index(axis=1)
        params = found_param.values
        # Then create our dictionary
        fnd_dict = dict(zip(found_param.index, params))

        # Draw from the fnd_type distribution
        # We do the same thing as w/ stories but with
        # the fnd_dict. This is a multinomial distribution
        # and 0, 1, 2 correspond to B, C, S
        # We get an array returned of the form
        # [0, 0, 1] (if we have Slab foundation, for example)
        # so we need to transform this into the corresponding
        # foundation type array
        # Can do this with fnds[fnds[0] == 1] = 'B'
        # fnds[fnds[1]] == 1] = 'C' & fnds[fnds[2] == 1] = 'S'
        # One way to do the mapping is by treating each
        # row-array as a binary string and converting it
        # to an int
        # So you get [a, b, c] => a*2^2 + b*2^1 + c*2^0
        # This uniquely maps to 4, 2, and 1
        # So we can create a dict for 4: 'B', 2: 'C', and 1: 'S'
        # and make it a pd.Series() (I think this is useful because
        # pandas can combine this with the 1S and 2S string easily
        # into a series and we'll need to use that bld_type
        # for the other dicts we have)

        # This is our ens_df index aligned multinomial
        # probabilities array

        mult_p = np.stack(ens_df[ref_col].map(fnd_dict))
        # This is our map of binary string/int
        # conversions to the foundation type
        bin_str_map = {4: "B", 2: "C", 1: "S"}
        # We need our np.ones array
        mult_n = np.ones(len(ens_df), dtype=np.int8)
        # Draw from mult_p
        fnds = rng.multinomial(mult_n, mult_p)
        # Create a series of 4, 2, and 1 from the binary strings
        # This code accomplishes the conversion outlined in the
        # note above and comes from this stackoverflow post
        # https://stackoverflow.com/questions/41069825/
        # convert-binary-01-numpy-to-integer-or-binary-string
        fnds_ints = pd.Series(fnds.dot(2 ** np.arange(fnds.shape[1])[::-1]))
        # Replace these values with the fnd_type
        fnd_types = fnds_ints.map(bin_str_map)

    else:
        fnd_types = ens_df["found_type"]

    print("Draw foundation types")

    if "ffe" in struct_list:
        # We are going to use the fnd_type to draw from the
        # FFE distribution
        # Need to use np.stack to get the array of floats
        tri_params = np.stack(fnd_types.map(ffe_dict))
        # Can use [:] to access like a matrix and directly input to
        # rng.triangular
        # 0, 1, and 2 are column indices corresponding to left,
        # mode, and right
        # We round this to the nearest tenth of a foot
        ffes = np.round(
            rng.triangular(tri_params[:, 0], tri_params[:, 1], tri_params[:, 2]),
            1
        )
    else:
        ffes = ens_df["found_ht"]

    print("Generated structure characteristics")

    # We take fnd_types for two tasks now
    # First, if B, it's WB type home and we
    # combine this with stories to get the bld_type
    # This is naccs_ddf_type
    # We combine bld_type with fz_ddf to get hazus_ddf_type
    # For our case study, it turns out we will use the same hazus
    # ddf for the basement houses (_A) since no V zone houses
    # For no basement, hazus_ddf_type does not add the _fz
    base_types = np.where(fnd_types == "B", "WB", "NB")
    # RES3 DDFs have NB in their name but apply to either
    # so we have to adjust for DDF purposes only
    # It's safe to do at this point because we already used
    # fnd_type to adjust first-floor elevation
    # base_types = np.where(occtypes == 'RES3A',
    #                       'NB',
    #                       base_types)

    # If RES3A  no basement occtype, we need to update num_story to 3
    # if it's not a 1 story building (just for fitting with
    # damage function names)
    # Othewrise, keep the # of stories you have
    stories = np.where((occtypes == 'RES3A') & (stories > 1) & (base_types == 'NB'),
                       3,
                       stories)

    stories = np.char.add(stories.astype(str), "S")

    bld_types = pd.Series(stories) + pd.Series(base_types)

    if 'hazus' in ddfs:
        hazus_ddf_types = np.where(
            base_types == "WB", bld_types + "_" + ens_df["fz_ddf"], bld_types
        )

    # We use a dictionary for losses where the key is the
    # ddf name since it's easier to keep track when we have
    # multiple ddfs. We will have loss and eal dictionaries
    losses = {}
    for ddf in ddfs:
        print("DDF: " + ddf)
        ddf_types = (
            pd.Series(hazus_ddf_types) if ddf == "hazus" else pd.Series(bld_types)
        )
        ddf_types = np.where(
            (base_types == 'WB') & (occtypes == 'RES3A'),
            ddf_types + '_RES1',
            ddf_types + '_' + occtypes
        )
        losses[ddf] = get_losses(ens_df[depths_df.columns],
                                 ffes,
                                 ddf,
                                 ddf_types,
                                 vals,
                                 vuln_dir,
                                 base_adj)

    print("Estimated losses")
    # Now we want a final dataframe of our ensemble. To err on the side of
    # less redundant memory storage, we will only return the characteristics
    # related to losses, the id_col, the state of world index, and the
    # losses and eal. Anything else is linked to id_col already and can
    # be merged in when needed.

    # To prepare this, we need to do some pre-processing on the losses &
    # eals dicts, adding the ddf name before the columns in the associated
    # dataframe.
    final_losses = pd.DataFrame(index=depths_df.index)
    for ddf, df in losses.items():
        df.columns = [ddf + "_" + x for x in df.columns]
        final_losses = pd.concat([final_losses, df], axis=1)

    final_ens_df = pd.concat(
        [
            ens_df[[id_col]],
            final_losses,
            pd.Series(stories, name="stories"),
            pd.Series(fnd_types, name="fnd_type"),
            pd.Series(ffes, name="ffe"),
            pd.Series(vals, name="val_s"),
        ],
        axis=1,
    )
    # Let's also get the SOW index - start at 0
    sow_ind = np.arange(len(final_ens_df)) % n_sow
    final_ens_df = pd.concat([final_ens_df, pd.Series(sow_ind, name="sow_ind")], axis=1)

    print("Prepared final ensemble")

    return final_ens_df

def generate_ensemble(
    nsi_sub, base_df, ddf_list, struct_list, n_sow, ffe_dict, coef_variation, vuln_dir_i
):
    """
    Return a dataframe of length number of structures * N_SOW
    This dataframe has N_SOW realizations of the uncertain
    structures specified in struct_list and corresponding
    estimates of losses. base_df is subset
    to properties with non-zero hazard and nsi_sub is not. We
    learn from nsi_sub to sample certain characteristics. We also
    pass in constants that are defined from config.yaml

    nsi_sub: DataFrame of the relevant characteristics from the NSI
    for all structures like the ones we will estimate losses for
    base_df: DataFrame of the relevant characteristics from the NSI
    subset to the structures we will estimate losses for
    ddf_list: list of ddfs as strings we will estimate losses from
    struct_list: list of characteristics as strings we wish to sample
    from
    n_sow: int, number of ensemble members per structure
    ffe_dict: dict, maps foundation types to first floor elevation
    distribution
    stry_dict: dict, maps tract ids to number of stories distribution
    fnd_dict: dict, maps tract ids to foundation type distribution
    coef_variation: float, what we scale the NSI value point estimate
    by to get the standard deviation of the structure value distribution
    """
    # We need a randon number generator
    rng = np.random.default_rng()

    # TODO we might want to allow the user to specify
    # whether they'd like to use a different reference id
    # than census tract. Maybe this can be specified in
    # the config?
    STRUCT_REF = "tract_id"
    # We create the tract_id column from the cbfips column
    # provided in the nsi data
    nsi_sub["tract_id"] = nsi_sub["cbfips"].str[:11]

    # We need a dataframe of the right size and index
    ens_df = base_df.loc[np.repeat(base_df.index, n_sow)].reset_index(drop=True)
    print("Created Index for Ensemble")

    # First, we will subset nsi_sub to a dataframe that
    # corresponds to all entries in the same census tract
    # as those in base_df. This approach assumes there is no correlation of
    # the foundation type proportions and number of stories
    # with features that vary within a census tract.
    struct_tot = nsi_sub[nsi_sub[STRUCT_REF].isin(base_df[STRUCT_REF])]
    # Also make sure the foundation type is one of C, S, or B
    # TODO this should be updated to link more foundation types
    # and damage functions
    struct_tot = struct_tot[struct_tot["found_type"].isin(["B", "C", "S"])]

    # If a variable is in struct_list, we will sample from a distribution
    # If not, we will use the single value from base_df

    if "val_struct" in struct_list:
        # Draw from the structure value distribution for each property
        # normal(val_struct, val_struct*CF_DET) where these are array_like
        # Using 1 as an artificial, arbitrary lower bound on value
        # Very low probability of getting a negative number but we cannot
        # allow that because you cannot have negative risk
        vals = rng.normal(ens_df["val_struct"], ens_df["val_struct"] * coef_variation)
        vals[vals < 1] = 1
    else:
        vals = ens_df["val_struct"].copy()

    print("Draw values")

    if "stories" in struct_list:
        # Determine the #stories distribution
        # Get the total number of structures w/ number of stories
        # in each block gruop
        stories_sum = struct_tot.groupby([STRUCT_REF, "num_story"]).size()
        # Then get the proportion
        stories_prop = stories_sum / struct_tot.groupby([STRUCT_REF]).size()
        # Our parameters can be drawn from this table based on the bg_id
        # of a structure we are estimating losses for
        stories_param = (
            stories_prop.reset_index()
            .pivot(index=STRUCT_REF, columns="num_story", values=0)
            .fillna(0)
        )
        # Since it's a binomial distribution, we only need to specify
        # one param. Arbitrarily choose 1
        # Round the param to the hundredth place
        # Store in a dict
        stories_param = stories_param[1].round(2)
        stry_dict = dict(stories_param)

        # Draw from the #stories distribution
        # We do this by mapping ens_df values with STRY_DICT
        # and passing this parameter to rng.binomial()
        # We also need to create an array of 1s with length
        # N_SOW * len(full_df) - i.e. len(ens_df)
        # full_df['bg_id'].map(STRY_DICT)
        bin_n = np.ones(len(ens_df), dtype=np.int8)
        bin_p = ens_df[STRUCT_REF].map(stry_dict).values
        # This gives us an array of 0s and 1s
        # Based on how STRY_DICT is defined, the probability of
        # success parameter corresponds to 1S, so we need to
        # swap out 1 with 1S and 0 with 2S
        stories = rng.binomial(bin_n, bin_p)
    else:
        stories = ens_df["num_story"].copy()

    stories = np.where(stories == 1, "1S", "2S")
    print("Draw stories")

    if "basement" in struct_list:
        # Get the foundation type distribution
        found_sum = struct_tot.groupby([STRUCT_REF, "found_type"]).size()
        found_prop = found_sum / struct_tot.groupby([STRUCT_REF]).size()
        found_param = (
            found_prop.reset_index()
            .pivot(index=STRUCT_REF, columns="found_type", values=0)
            .fillna(0)
        )

        # We want a dictionary of bg_id to a list of B, C, S
        # for direct use in our multinomial distribution draw
        # Store params in a list (each row is bg_id and corresponds to
        # its own probabilities of each foundation type)
        params = found_param.values
        # Then create our dictionary
        fnd_dict = dict(zip(found_param.index, params))

        # Draw from the fnd_type distribution
        # We do the same thing as w/ stories but with
        # the fnd_dict. This is a multinomial distribution
        # and 0, 1, 2 correspond to B, C, S
        # We get an array returned of the form
        # [0, 0, 1] (if we have Slab foundation, for example)
        # so we need to transform this into the corresponding
        # foundation type array
        # Can do this with fnds[fnds[0] == 1] = 'B'
        # fnds[fnds[1]] == 1] = 'C' & fnds[fnds[2] == 1] = 'S'
        # One way to do the mapping is by treating each
        # row-array as a binary string and converting it
        # to an int
        # So you get [a, b, c] => a*2^2 + b*2^1 + c*2^0
        # This uniquely maps to 4, 2, and 1
        # So we can create a dict for 4: 'B', 2: 'C', and 1: 'S'
        # and make it a pd.Series() (I think this is useful because
        # pandas can combine this with the 1S and 2S string easily
        # into a series and we'll need to use that bld_type
        # for the other dicts we have)

        # This is our ens_df index aligned multinomial
        # probabilities array
        # np.stack makes sure the dtype is correct
        # Not sure why it is cast to object dtype if
        # I call .values, but this works...

        mult_p = np.stack(ens_df[STRUCT_REF].map(fnd_dict))
        # This is our map of binary string/int
        # conversions to the foundation type
        bin_str_map = {4: "B", 2: "C", 1: "S"}
        # We need our np.ones array
        mult_n = np.ones(len(ens_df), dtype=np.int8)
        # Draw from mult_p
        fnds = rng.multinomial(mult_n, mult_p)
        # Create a series of 4, 2, and 1 from the binary strings
        # This code accomplishes the conversion outlined in the
        # note above and comes from this stackoverflow post
        # https://stackoverflow.com/questions/41069825/
        # convert-binary-01-numpy-to-integer-or-binary-string
        fnds_ints = pd.Series(fnds.dot(2 ** np.arange(fnds.shape[1])[::-1]))
        # Replace these values with the fnd_type
        fnd_types = fnds_ints.map(bin_str_map)

    else:
        fnd_types = ens_df["found_type"]

    print("Draw foundation types")

    # We take fnd_types for two tasks now
    # First, if B, it's WB type home and we
    # combine this with stories to get the bld_type
    # This is naccs_ddf_type
    # We combine bld_type with fz_ddf to get hazus_ddf_type
    # For our case study, it turns out we will use the same hazus
    # ddf for the basement houses (_A) since no V zone houses
    # For no basement, hazus_ddf_type does not add the _fz

    base_types = np.where(fnd_types == "B", "WB", "NB")
    bld_types = pd.Series(stories) + pd.Series(base_types)

    hazus_ddf_types = np.where(
        base_types == "WB", bld_types + "_" + ens_df["fz_ddf"], bld_types
    )

    if "ffe" in struct_list:
        # We are going to use the fnd_type to draw from the
        # FFE distribution
        # Need to use np.stack to get the array of floats
        tri_params = np.stack(fnd_types.map(ffe_dict))
        # Can use [:] to access like a matrix and directly input to
        # rng.triangular
        # 0, 1, and 2 are column indices corresponding to left,
        # mode, and right
        # We round this to the nearest foot
        ffes = np.round(
            rng.triangular(tri_params[:, 0], tri_params[:, 1], tri_params[:, 2])
        )
    else:
        ffes = ens_df["found_ht"]

    print("Generated structure characteristics")

    # Before estimating losses, we adjust
    # the depths by first-floor elevation
    depth_cols = [x for x in base_df.columns if "depth" in x]
    depth_ffe_df = ens_df[depth_cols].subtract(ffes, axis=0).round(1)

    # We use a dictionary for losses where the key is the
    # ddf name since it's easier to keep track when we have
    # multiple ddfs. We will have loss and eal dictionaries
    losses = {}
    for ddf in ddf_list:
        print("DDF: " + ddf)
        ddf_types = (
            pd.Series(hazus_ddf_types) if ddf == "hazus" else pd.Series(bld_types)
        )
        losses[ddf] = get_losses(depth_ffe_df, ddf, ddf_types, vals, vuln_dir_i)

    print("Estimated losses")
    # Now we want a final dataframe of our ensemble. To err on the side of
    # less redundant memory storage, we will only return the characteristics
    # related to losses, the fd_id, the state of world index, and the
    # losses and eal. Anything else is linked to fd_id already and can
    # be merged in when needed.

    # To prepare this, we need to do some pre-processing on the losses &
    # eals dicts, adding the ddf name before the columns in the associated
    # dataframe.
    final_losses = pd.DataFrame(index=depth_ffe_df.index)
    for ddf, df in losses.items():
        df.columns = [ddf + "_" + x for x in df.columns]
        final_losses = pd.concat([final_losses, df], axis=1)

    final_ens_df = pd.concat(
        [
            ens_df[["fd_id"]],
            depth_ffe_df,
            final_losses,
            pd.Series(stories, name="stories"),
            pd.Series(fnd_types, name="fnd_type"),
            pd.Series(ffes, name="ffe"),
            pd.Series(vals, name="val_s"),
        ],
        axis=1,
    )
    # Let's also get the SOW index - start at 0
    sow_ind = np.arange(len(final_ens_df)) % n_sow
    final_ens_df = pd.concat([final_ens_df, pd.Series(sow_ind, name="sow_ind")], axis=1)

    print("Prepared final ensemble")

    return final_ens_df

def benchmark_naccs_loss(structures_df, depths_df, vuln_dir_i, base_adj=True, depth_min=None):
    """
    Estimate losses without any uncertainty using NSI
    and NACCS most likely curves

    structures_df: pd.DataFrame 
        DataFrame of core attributes for loss estimation
        Must be a NSI dataframe with 'found_ht' column

    depths_df: pd.DataFrame
        DataFrame of depths, must share index with base_df

    vuln_dir_i: str, location of the ddfs

    base_adj: boolean, whether inundation starts at bottom of basement

    depth_min: Integer, filter for when to apply DDFs (default: None)
    """
    # We need the DDFs w/o uncertainty
    naccs_ddfs = pd.read_parquet(join(vuln_dir_i, "physical", "naccs_ddfs.pqt"))
    with open(join(vuln_dir_i, "physical", "naccs.json"), "r") as fp:
        NACCS_MAX_DICT = json.load(fp)

    # Make a column for most likely damage
    # and get a max dam dict for most likely
    naccs_ddfs['ml_dam'] = naccs_ddfs['params'].apply(lambda x: x[1])
    naccs_max_ml = {k: v[1] for k, v in NACCS_MAX_DICT.items()}

    # Convert depths to ft
    depths_df = depths_df*unconst.MTR_TO_FT

    # Drop any depths as required
    # If depth_min is 0, this drops any null depths
    depths_df = depths_df[depths_df.sum(axis=1) > depth_min]

    # Join structures and depths
    base_df = structures_df.join(depths_df, how='inner')

    # Update occtypes for buildings with basements
    base_df['occtype'] = np.where(((base_df['occtype'] == 'RES3A') &
                                   (base_df['found_type'] == 'B')),
                                   'RES1',
                                   base_df['occtype'])

    # Preparing the building type variable
    stories = np.where(((base_df['occtype'] == 'RES3A') &
                        (base_df['num_story'] > 1)),
                       3,
                       base_df['num_story'])
    stories = np.char.add(stories.astype(str), "S")
    fnd_types = base_df["found_type"].copy()
    base_types = np.where(fnd_types == "B", "WB", "NB")
    bld_types = (pd.Series(stories, index=base_df.index)
                 + pd.Series(base_types, index=base_df.index))
    ddf_types = bld_types + '_' + base_df['occtype']

    # Loss estimation routine
    loss = {}
    for d_col in depths_df.columns:
        nounc_rel_loss = est_naccs_loss_nounc(
            ddf_types,
            base_df[d_col],
            base_df['found_ht'],
            naccs_ddfs,
            naccs_max_ml,
            base_adj
        )
        loss[d_col] = nounc_rel_loss.values * base_df["val_struct"]
        print("Estimate Losses for NACCS Default: " + d_col)

    loss_df = pd.DataFrame.from_dict(loss)
    loss_df.columns = ["naccs_loss_" + x for x in loss_df.columns]

    # Return a dataframe with loss estimates
    naccs_nounc = pd.DataFrame(loss_df, index=base_df.index)

    return naccs_nounc

def benchmark_loss(structures_df, depths_df, vuln_dir_i, base_adj=True):
    """
    Estimate losses without any uncertainty using NSI
    and HAZUS curves

    structures_df: pd.DataFrame 
        DataFrame of core attributes for loss estimation
        Must be a NSI dataframe with 'found_ht' column

    depths_df: pd.DataFrame
        DataFrame of depths, must share index with base_df

    vuln_dir_i: str, location of the ddfs
    """
    # We need the DDFs w/o uncertainty
    hazus_nounc = pd.read_parquet(join(vuln_dir_i, "physical", "hazus_ddfs_nounc.pqt"))
    with open(join(vuln_dir_i, "physical", "hazus_nounc.json"), "r") as fp:
        HAZUS_MAX_NOUNC_DICT = json.load(fp)

    # Convert depths to ft
    depths_df = depths_df*unconst.MTR_TO_FT

    # Join structures and depths
    base_df = structures_df.join(depths_df, how='inner')

    # Preparing the hazus building type variable
    stories = np.where(base_df["num_story"] == 1, "1S", "2S")
    fnd_types = base_df["found_type"].copy()
    base_types = np.where(fnd_types == "B", "WB", "NB")
    bld_types = (pd.Series(stories, index=base_df.index)
                 + pd.Series(base_types, index=base_df.index))
    hazus_ddf_types = np.where(
        base_types == "WB", bld_types + "_" + base_df["fz_ddf"], bld_types
    )

    # Subset depths_df to records in the base df for loss estimation
    depths_df = depths_df[depths_df.index.isin(base_df.index)].copy()

    # Loss estimation routine
    loss = {}
    for d_col in depths_df.columns:
        rp = d_col.split("_")[-1]
        nounc_rel_loss = est_hazus_loss_nounc(
            hazus_ddf_types,
            depths_df[d_col],
            base_df['found_ht'],
            hazus_nounc,
            HAZUS_MAX_NOUNC_DICT,
            base_adj
        )
        loss[rp] = nounc_rel_loss.values * base_df["val_struct"]
        print("Estimate Losses for Hazus Default, RP: " + rp)

    loss_df = pd.DataFrame.from_dict(loss)
    loss_df.columns = ["loss_" + x for x in loss_df.columns]

    print("Estimate losses")

    # Return a dataframe with loss estimates and eal
    hazus_nounc = pd.DataFrame(loss_df, index=base_df.index)

    return hazus_nounc
