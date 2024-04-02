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

def get_base_df(fips, exp_dir_i):
    '''
    Return a dataframe of structures with all the
    relevant characteristics needed for
    generating our ensemble and estimating losses

    fips: str, county code
    '''

    nsi_struct = gpd.read_file(join(exp_dir_i, fips, 'nsi_sf.gpkg'))
    nsi_ref = pd.read_parquet(join(exp_dir_i, fips, 'nsi_ref.pqt'))
    nsi_depths = pd.read_parquet(join(exp_dir_i, fips, 'nsi_depths.pqt'))
    nsi_fz = pd.read_parquet(join(exp_dir_i, fips, 'nsi_fz.pqt'))

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

    print('Merged flood zones into nsi')

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

    print('Subset to exposed structures')

    # Merge in the depths to the struct df you are working with
    # Also merge in the refs - note that there are inconsistencies
    # with the cbfips column from nsi directly and the
    # block data downloaded from the census webpage
    # You retain more structures if you use the block data we
    # downloaded in UNSAFE
    full_df = (nsi_res_f.join(depths_df)).reset_index()

    print('Merged depths')

    # We also need the fld_zone column processed for using hazus ddfs
    # Get the first character of the flood zone and only retain it
    # if it's a V zone. We are going to use A zone for A and outside
    # (if any) flood zone depth exposuresgi
    ve_zone = np.where(full_df['fld_zone'].str[0] == 'V',
                    'V',
                    'A')
    full_df = full_df.assign(fz_ddf = ve_zone)

    print('Prepared base data frame')

    return full_df

def generate_ensemble(nsi_sub,
                      base_df,
                      ddf_list,
                      struct_list,
                      n_sow,
                      ffe_dict,
                      coef_variation,
                      vuln_dir_i):
    '''
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
    '''
    # We need a randon number generator
    rng = np.random.default_rng()

    #TODO we might want to allow the user to specify
    # whether they'd like to use a different reference id
    # than census tract. Maybe this can be specified in
    # the config? 
    STRUCT_REF = 'tract_id'
    # We create the tract_id column from the cbfips column
    # provided in the nsi data
    nsi_sub['tract_id'] = nsi_sub['cbfips'].str[:11]

    # We need a dataframe of the right size and index
    ens_df = base_df.loc[np.repeat(base_df.index, n_sow)].reset_index(drop=True)
    print('Created Index for Ensemble')


    # First, we will subset nsi_sub to a dataframe that
    # corresponds to all entries in the same census tract
    # as those in base_df. This approach assumes there is no correlation of
    # the foundation type proportions and number of stories
    # with features that vary within a census tract.
    struct_tot = nsi_sub[nsi_sub[STRUCT_REF].isin(base_df[STRUCT_REF])]

    # If a variable is in struct_list, we will sample from a distribution
    # If not, we will use the single value from base_df

    if 'val_struct' in struct_list:
        # Draw from the structure value distribution for each property
        # normal(val_struct, val_struct*CF_DET) where these are array_like
        # Using 1 as an artificial, arbitrary lower bound on value
        # Very low probability of getting a negative number but we cannot
        # allow that because you cannot have negative risk
        vals = rng.normal(ens_df['val_struct'],
                          ens_df['val_struct']*coef_variation)
        vals[vals < 1] = 1
    else:
        vals = ens_df['val_struct'].copy()

    print('Draw values')

    if 'stories' in struct_list:
        # Determine the #stories distribution
        # Get the total number of structures w/ number of stories 
        # in each block gruop
        stories_sum = struct_tot.groupby([STRUCT_REF, 'num_story']).size()
        # Then get the proportion
        stories_prop = stories_sum/struct_tot.groupby([STRUCT_REF]).size()
        # Our parameters can be drawn from this table based on the bg_id
        # of a structure we are estimating losses for
        stories_param = stories_prop.reset_index().pivot(index=STRUCT_REF,
                                                         columns='num_story',
                                                         values=0).fillna(0)
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
        stories = ens_df['num_story'].copy()
    
    stories = np.where(stories == 1,
                       '1S',
                       '2S')
    print('Draw stories')

    if 'basement' in struct_list:
        # Get the foundation type distribution
        found_sum = struct_tot.groupby([STRUCT_REF, 'found_type']).size()
        found_prop = found_sum/struct_tot.groupby([STRUCT_REF]).size()
        found_param = found_prop.reset_index().pivot(index=STRUCT_REF,
                                                    columns='found_type',
                                                    values=0).fillna(0)

        # We want a dictionary of bg_id to a list of B, C, S
        # for direct use in our multinomial distribution draw
        # Store params in a list (each row is bg_id and corresponds to
        # its own probabilities of each foundation type)
        params = found_param.values.round(2)
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
        bin_str_map = {4: 'B', 2: 'C', 1: 'S'}
        # We need our np.ones array 
        mult_n = np.ones(len(ens_df), dtype=np.int8)
        # Draw from mult_p
        fnds = rng.multinomial(mult_n, mult_p)
        # Create a series of 4, 2, and 1 from the binary strings
        # This code accomplishes the conversion outlined in the
        # note above and comes from this stackoverflow post
        # https://stackoverflow.com/questions/41069825/
        # convert-binary-01-numpy-to-integer-or-binary-string
        fnds_ints = pd.Series(fnds.dot(2**np.arange(fnds.shape[1])[::-1]))
        # Replace these values with the fnd_type
        fnd_types = fnds_ints.map(bin_str_map)

    else:
        fnd_types = ens_df['found_type']

    print('Draw foundation types')

    # We take fnd_types for two tasks now
    # First, if B, it's WB type home and we
    # combine this with stories to get the bld_type
    # This is naccs_ddf_type 
    # We combine bld_type with fz_ddf to get hazus_ddf_type
    # For our case study, it turns out we will use the same hazus
    # ddf for the basement houses (_A) since no V zone houses
    # For no basement, hazus_ddf_type does not add the _fz

    base_types = np.where(fnd_types == 'B',
                          'WB',
                          'NB')
    bld_types = pd.Series(stories) + pd.Series(base_types)

    hazus_ddf_types = np.where(base_types == 'WB',
                               bld_types + '_' + ens_df['fz_ddf'],
                               bld_types)


    # We are going to use the fnd_type to draw from the
    # FFE distribution
    # Need to use np.stack to get the array of floats
    tri_params = np.stack(fnd_types.map(ffe_dict))
    # Can use [:] to access like a matrix and directly input to 
    # rng.triangular
    # 0, 1, and 2 are column indices corresponding to left,
    # mode, and right
    # We round this to the nearest foot
    ffes = np.round(rng.triangular(tri_params[:,0],
                                   tri_params[:,1],
                                   tri_params[:,2]))
    
    print('Generated structure characteristics')

    # Before estimating losses, we adjust
    # the depths by first-floor elevation
    depth_cols = [x for x in base_df.columns if 'depth' in x]
    depth_ffe_df = ens_df[depth_cols].subtract(ffes, axis=0).round(1) 

    # We use a dictionary for losses where the key is the
    # ddf name since it's easier to keep track when we have
    # multiple ddfs. We will have loss and eal dictionaries
    losses = {}
    eals = {}
    for ddf in ddf_list:
        print('DDF: ' + ddf)
        ddf_types = pd.Series(hazus_ddf_types) if ddf == 'hazus' else pd.Series(bld_types)
        losses[ddf] = get_losses(depth_ffe_df, ddf, ddf_types, vals, vuln_dir_i)
        # Define a return period list based on depth_ffe_df.columns
        # This will be used to determine probabilities of the scenarios
        # that are passed in and weigh them for expected annual loss.
        # TODO there needs to be more guidance about how depth_ffe_df
        # can be defined when design events are not specified
        rp_list = sorted([int(x.split('_')[-1]) for x in depth_ffe_df.columns])
        eals[ddf] = get_eal(losses[ddf], rp_list)

    print('Estimated losses and expected annual losses')
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
        df.columns = [ddf + '_' + x for x in df.columns]
        final_losses = pd.concat([final_losses, df], axis=1)
    final_eals = pd.DataFrame(index=depth_ffe_df.index)
    for ddf, df in eals.items():
        df.name = ddf + '_eal'
        final_eals = pd.concat([final_eals, df], axis=1)

    final_ens_df = pd.concat([ens_df[['fd_id']],
                              depth_ffe_df,
                              final_losses,
                              final_eals,
                              pd.Series(stories, name='stories'),
                              pd.Series(fnd_types, name='fnd_type'),
                              pd.Series(ffes, name='ffe'),
                              pd.Series(vals, name='val_s')],
                            axis=1)
    # Let's also get the SOW index - start at 0
    sow_ind = np.arange(len(final_ens_df))%n_sow
    final_ens_df = pd.concat([final_ens_df,
                              pd.Series(sow_ind, name='sow_ind')],
                            axis=1)
    
    print('Prepared final ensemble')

    return final_ens_df

def benchmark_loss(base_df,
                   vuln_dir_i):
    '''
    Estimate losses without any uncertainty using NSI
    and HAZUS defaults

    base_df: DataFrame of core attributes for loss estimation
    vuln_dir_i: str, location of the ddfs
    '''
    # We need the DDFs w/o uncertainty
    hazus_nounc = pd.read_parquet(join(vuln_dir_i, 'physical', 'hazus_ddfs_nounc.pqt'))
    with open(join(vuln_dir_i, 'physical', 'hazus_nounc.json'), 'r') as fp:
            HAZUS_MAX_NOUNC_DICT = json.load(fp)

    # Preparing the hazus building type variable
    stories = np.where(base_df['num_story'] == 1,
                       '1S',
                       '2S')
    fnd_types = base_df['found_type'].copy()
    base_types = np.where(fnd_types == 'B',
                          'WB',
                          'NB')
    bld_types = pd.Series(stories) + pd.Series(base_types)
    hazus_ddf_types = np.where(base_types == 'WB',
                               bld_types + '_' + base_df['fz_ddf'],
                               bld_types)


    # Similar to the code for the ensemble, we get depth relative to first-floor
    # elevation and estimate losses across return periods/scenarios.
    # In this case, we use the 'found_ht' variable from the NSI
    depth_cols = [x for x in base_df.columns if 'depth' in x]
    depth_ffe_df = base_df[depth_cols].subtract(base_df['found_ht'], axis=0).round(1)

    # Loss estimation routine
    loss = {}
    for d_col in depth_ffe_df.columns:
        rp = d_col.split('_')[-1]
        nounc_rel_loss = est_hazus_loss_nounc(pd.Series(hazus_ddf_types),
                                              depth_ffe_df[d_col],
                                              hazus_nounc,
                                              HAZUS_MAX_NOUNC_DICT)
        loss[rp] = nounc_rel_loss.values*base_df['val_struct']
        print('Estimate Losses for Hazus Default, RP: ' + rp)
    
    loss_df = pd.DataFrame.from_dict(loss)
    loss_df.columns = ['loss_' + x for x in loss_df.columns]

    # From losses to expected annual loss
    rp_list = sorted([int(x.split('_')[-1]) for x in depth_ffe_df.columns])
    eals = get_eal(loss_df, rp_list)
    print('Estimate expected annual loss')

    # Return a dataframe with loss estimates and eal
    hazus_nounc = pd.concat([base_df[['fd_id']],
                             loss_df,
                             pd.Series(eals, name='eal')], axis=1)
    
    return hazus_nounc