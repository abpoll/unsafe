# Packages
import pandas as pd
import numpy as np
import os
import json

from unsafe.const import *
from unsafe.files import *

'''
Helpful functions for processing depth-damage functions
that are stored in different data structures
'''

# HAZUS and USACE DDFs can be
# formatted in tidy df format
# this way
def tidy_ddfs(raw_ddf, idvars):
    # For HAZUS we have occtype and fld_zone
    # For NACCS we have Occupancy and DamageCategory
    ddf_melt = raw_ddf.melt(id_vars=idvars,
                            var_name='depth_str',
                            value_name='pct_dam')
    # # Need to convert depth_ft into a number
    # Replace ft with empty character
    # If string ends with m, make negative number
    # Else, make positive number
    ddf_melt['depth_str'] = ddf_melt['depth_str'].str.replace('ft', '')
    negdepth = ddf_melt.loc[ddf_melt['depth_str'].str[-1] == 
                            'm']['depth_str'].str[:-1].astype(float)*-1
    posdepth = ddf_melt.loc[ddf_melt['depth_str'].str[-1] != 
                            'm']['depth_str'].astype(float)

    ddf_melt.loc[ddf_melt['depth_str'].str[-1] == 'm',
                'depth_ft'] = negdepth
    ddf_melt.loc[ddf_melt['depth_str'].str[-1] != 'm',
                'depth_ft'] = posdepth

    # Divide pct_dam by 100
    ddf_melt['rel_dam'] = ddf_melt['pct_dam']/100
    
    return ddf_melt

def ddf_max_depth_dict(tidy_ddf, dam_col):
    # We want all depths above max depths for the DDFs
    # to take the param values of the max depth DDF
    # First, we groupby bld type for naccs and get max depth for
    # each bld type
    max_ddf_depths = tidy_ddf.groupby(['ddf_id'])['depth_ft'].idxmax()
    # Locate these rows in the dataframe for the ddfs
    max_d_params = tidy_ddf.iloc[max_ddf_depths]
    # Can create a dict of bld_type to params
    # which will be called for any instance in loss estimation
    # where a depth value is not null, but the params value is
    # We will just use this dict to fill the param values
    # with those corresponding to the max depth for that same bld type
    DDF_DICT = dict(zip(max_d_params['ddf_id'], max_d_params[dam_col]))

    return DDF_DICT


def process_naccs(vuln_dir_uz, vuln_dir_i):
    '''
    Default processing and generation of the NACCS DDFs
    '''
    naccs = pd.read_csv(join(vuln_dir_uz, "naccs_ddfs.csv"))

    # For NACCS, we have the RES 1 DDFs
    # NACCS need some preprocessing as well
    # First, subset to the relevant Occupancy types
    # We want to end up with ddf ids 1swb, etc.
    # don't need to keep the RES1- part for this case study
    naccs['res_type'] = naccs['Occupancy'].str.split('-').str[0]
    naccs['bld_type'] = naccs['Occupancy'].str.split('-').str[1]
    occ_types = ['1SWB', '2SWB', '1SNB', '2SNB']
    naccs_res = naccs.loc[(naccs['bld_type'].isin(occ_types)) &
                        (naccs['res_type'] == 'RES1')]

    # Next, drop columns we don't need
    drop_cols = ['Description', 'Source', 'Occupancy', 'res_type']
    naccs_res = naccs_res.drop(columns=drop_cols)

    # Rename DamageCategory
    naccs_res = naccs_res.rename(columns={'DamageCategory': 'dam_cat',
                                        'bld_type': 'ddf_id'})
    
    # Now get the melted dataframe
    idvars = ['ddf_id', 'dam_cat']
    naccs_melt = tidy_ddfs(naccs_res, idvars)

    # Drop columns we don't need
    drop_cols = ['depth_str', 'pct_dam']
    naccs_f = naccs_melt.drop(columns=drop_cols)

    # We want to pivot the dataframe so that Min/ML/Max are our columns
    naccs_piv = naccs_f.pivot(index=['ddf_id', 'depth_ft'],
                            columns='dam_cat')['rel_dam'].reset_index()


    # We do the interpolation again
    df_int_list = []
    for ddf_id, df in naccs_piv.groupby('ddf_id'):
        # This creates the duplicate rows
        ddf_int = df.loc[np.repeat(df.index, 10)].reset_index(drop=True)
        # Now we have to make them nulls by finding
        # the "original" indexed rows
        float_cols = ['depth_ft', 'ML', 'Max', 'Min']
        ddf_int.loc[ddf_int.index % 10 != 0,
                    float_cols] = np.nan
        # Now we interpolate (again, on floats)
        ddf_int_floats = ddf_int[float_cols].interpolate().round(2)
        # Add in our ddf id col
        ddf_int_floats['ddf_id'] = ddf_id
        # Drop duplicate rows (this happens for the max depth values)
        ddf_int = ddf_int_floats.drop_duplicates()
        # And append
        df_int_list.append(ddf_int)
    naccs_ddfs = pd.concat(df_int_list, axis=0)

    # We want to obtain our 'params' column
    # same as above
    p_cols = ['Min', 'ML', 'Max']
    tri_params = naccs_ddfs[p_cols].values
    # Drop the p_cols
    naccs_out = naccs_ddfs.drop(columns=p_cols)
    naccs_out = naccs_out.assign(params=tri_params.tolist())

    # Get out dict of max depths
    NACCS_MAX_DICT = ddf_max_depth_dict(naccs_out.reset_index(drop=True),
                                        'params')
    
    # Main directory
    ddf_out_dir = join(vuln_dir_i, 'physical')
    naccs_out_filep = join(ddf_out_dir, 'naccs_ddfs.pqt')
    naccs_max_filep = join(ddf_out_dir, 'naccs.json')

    # Only need to call this for one of the files
    # since they share the same parent directory
    prepare_saving(naccs_out_filep)

    # Save as parquet file since
    # these will directly read in the
    # DDF params as a list, not as a string
    naccs_out.to_parquet(naccs_out_filep)

    # Save the json files
    with open(naccs_max_filep, 'w') as fp:
        json.dump(NACCS_MAX_DICT, fp)

    #TODO improve logging
    print('NACCS DDFs Processed')

def process_hazus(vuln_dir_uz, vuln_dir_i, unif_unc=.3):
    '''
    Default processing and generation of the HAZUS DDFs
    These are generated with some uniform uncertainty, default
    30% of the point estimate value following
    https://www.nature.com/articles/s41467-020-19188-9
    but these can also be used for estimating losses
    without uncertainty
    '''
    hazus = pd.read_csv(join(vuln_dir_uz, "haz_fl_dept.csv"))

    # First, preprocessing for hazus ddfs
    # For basements, use FIA (MOD.) which does one and two floors by
    # A and V zones
    # For no basements, use USACE - IWR
    # which does one and two floor, no flood zone specified
    # 106: FIA (MOD.) 1S WB A zone
    # 114: "" V zone
    # 108: FIA (MOD.) 1S WB A zone
    # 116: "" V zone
    # 129: USACE - IWR 1S NB
    # 130: USCAE - IWR 2S+ NB
    # For elevating homes, we can use Pile foundation DDFs
    # from USACE - Wilmington
    # 178 - 1S Pile Foundation
    # 183 - 2S Pile Foundation
    # These are no basement homes, so to speak
    # The USACE New Orleans DDFs have some pier foundation
    # DDFs with fresh & salt water and long & short duration
    # but this does not appear to apply to out study area
    # Subset to DmgFnId in the codes above
    dmg_ids = [106, 108, 114, 116, 129, 130, 178, 183]
    hazus_res = hazus[(hazus['DmgFnId'].isin(dmg_ids)) & 
                    (hazus['Occupancy'] == 'RES1')]
    
    # Make occtype column in the same form that the NSI has
    # e.g. RES1-1SNB
    # Add column for A or V zone
    # Note: outside SFHA basement homes will take A zone
    # What other option do we have? 

    # Split Description by comma. 
    # The split[0] element tells us stories (but description sometimes
    # says floors instead of story...)
    # Can get around this issue by looking at first word
    # The split[1] element
    # tells us w/ basement or no basement. Use this to create occtype
    desc = hazus_res['Description'].str.split(',')
    s_type = desc.str[0].str.split(' ').str[0]
    s_type = s_type.str.replace('one', '1').str.replace('two', '2')
    b_type = desc.str[1].str.strip()
    # Below, we are just trying to get archetypes like
    # 1SNB, 2SWB, 1SPL -- for pile foundation
    occtype = np.where(b_type == 'w/ basement',
                    s_type + 'SWB',
                    s_type + 'SNB')
    occtype = np.where(b_type == 'Pile foundation',
                    s_type + 'SPL',
                    occtype)
    # Some of these HAZUS DDFs require us to keep track of the
    # flood zone they're in
    # I don't think this matters for our case study since
    # there are no high wave coastsal zones
    # This line is designed to work specifically 
    # with the way the descriptions
    # are written out for the DDFs used in UNSAFE v0.1
    fz = desc.str[-1].str.lower().str.replace('structure', '').str.strip()

    # Need occtype, flood zone, depth_ft, and rel_dam columns
    # Follow steps from naccs processing to get depth_ft and rel_dam
    # First, drop unecessary columns
    # Don't need Source_Table, Occupy_Class, Cover_Class, empty columns
    # Description, Source, DmgFnId, Occupancy and first col (Unnamed: 0)
    # because index was written out
    # Don't need all na columns either (just for automobiles, apparently)
    hazus_res = hazus_res.loc[:,[col for col in hazus_res.columns if 'ft' in col]]
    hazus_res = hazus_res.dropna(axis=1, how='all')
    # Add the occtype and fld_zone columns
    hazus_res = hazus_res.assign(occtype=occtype,
                                fld_zone=fz.str[0])

    # Then, occtype and fld_zone as index and melt rest of columns. 
    idvars = ['occtype', 'fld_zone']

    # Get a tidy ddf back
    hazus_melt = tidy_ddfs(hazus_res, idvars)

    # Delete depth_str and pctdam and standardize
    # column names
    # Since we just have the building types, call this
    # bld_type instead of occtype
    dropcols = ['depth_str', 'pct_dam', 'occtype', 'fld_zone']

    # We create an "id" col for the ddfs
    # Our key for HAZUS is bld_type & fld_zone
    ddf_id = np.where(hazus_melt['fld_zone'].notnull(),
                    hazus_melt['occtype'] + '_' + hazus_melt['fld_zone'],
                    hazus_melt['occtype'])

    # Add this to our dataframe so that we can drop bld_type & fld_zone
    # Easier to have the flood zone as a capital letter
    # It's lower case because of earlier code to do
    # some processing
    hazus_melt = hazus_melt.assign(ddf_id=pd.Series(ddf_id).str.upper())
    # Drop columns
    hazus = hazus_melt.drop(columns=dropcols)

    # We need to interpolate between the values of the DDF that we
    # are given. Generally speaking, this introduces artificial spread
    # in the relative damage distribution since the interpolation is
    # actually a combo of measurement & modeling uncertainty that
    # the DDF bounds yield. But, linear interpolation between DDF points
    # is so common that UNSAFE will not depart from that before a paper
    # makes the rigorous case that the approach is not needed once
    # you use DDFs w/ uncertainty bounds

    # To do this interpolation, we loop through each ddf_id, 
    # and then we will just sample 10 points and create nan rows
    # (besides ddf_id). Then we interpolate, store in a list
    # and concat at the end
    df_int_list = []
    for ddf_id, df in hazus.groupby('ddf_id'):
        # This creates the duplicate rows
        ddf_int = df.loc[np.repeat(df.index, 10)].reset_index(drop=True)
        # Now we have to make them nulls by finding
        # the "original" indexed rows
        ddf_int.loc[ddf_int.index % 10 != 0, ['depth_ft', 'rel_dam']] = np.nan
        # Now we interpolate (just on floats)
        ddf_int_floats = ddf_int[['depth_ft', 'rel_dam']].interpolate()
        # And add on the ddf_id column back
        ddf_int_floats['ddf_id'] = ddf_id
        # Drop duplicate rows (this happens for the max depth values)
        ddf_int = ddf_int_floats.drop_duplicates()
        # And append
        df_int_list.append(ddf_int)
    hazus_ddfs = pd.concat(df_int_list, axis=0)

    # Now we're going to process this tidy dataframe into a dictionary
    # for easier ensemble generation
    dam_low = np.maximum(0,
                        hazus_ddfs['rel_dam'] - unif_unc*hazus_ddfs['rel_dam']).round(2)
    dam_high = np.minimum(1,
                        hazus_ddfs['rel_dam'] + unif_unc*hazus_ddfs['rel_dam']).round(2)

    # Add these columns into our dataframe
    hazus_ddfs = hazus_ddfs.assign(low=dam_low,
                                high=dam_high)

    # For reasons that will become more obvious later,
    # it is really helpful to store our params as a list
    # Get param cols
    uni_params = ['low', 'high']

    # Get df of ddf_id, depth_ft, rel_dam
    hazus_f = hazus_ddfs[['ddf_id', 'depth_ft', 'rel_dam']]
    # Now store params as a list
    hazus_f = hazus_f.assign(params=hazus_ddfs[uni_params].values.tolist())

    # We are going to write out hazus_f 
    # In generating the ensemble for losses
    # we are going to merge this dataframe
    # with our structure ensemble - merged with
    # depths. So, on haz_depth & depth_ft from hazus_f
    # plus the structure archetype, we can get
    # the rel_dam parameters. We will draw from this
    # and get the rel_dam realization for this
    # state of the world
    # But, the way this data is stored requires a few assumptions
    # about loss estimation
    # First, any depths below that lowest depth have 0 loss
    # Second, any depths above the highest depth have the same
    # loss as the highest depth 
    # To implement this, we will check depths (after drawing from their
    # distribution at each location) for whether they are inside
    # the range of the particular DDF which can be defined with 
    # conastants. If below, loss is 0. If above, swap with
    # the upper bound
    # This is why it's very helpful to have the params stored as 
    # a list, because now we can get unique key/value pairs
    # for the ddf_id and the params
    # We need two dicts for HAZUS
    # One is with the params list
    # One is just ddf_id to rel_dam (for benchmark loss calculations
    # when uncertainty is not considered)

    # We can call our helper function to get our dictionaries
    HAZUS_MAX_DICT = ddf_max_depth_dict(hazus_f.reset_index(drop=True),
                                        'params')
    HAZUS_MAX_NOUNC_DICT = ddf_max_depth_dict(hazus, 'rel_dam')

    # We need one hazus file with params for 
    # uncertainty and one w/ just rel_dam
    hazus_unc = hazus_f[['ddf_id', 'depth_ft', 'params']]
    hazus_nounc = hazus_f[['ddf_id', 'depth_ft', 'rel_dam']]

    # Main directory
    ddf_out_dir = join(vuln_dir_i, 'physical')

    # Main ddf files
    hazus_out_filep = join(ddf_out_dir, 'hazus_ddfs.pqt')
    hazus_nounc_out_filep = join(ddf_out_dir, 'hazus_ddfs_nounc.pqt')

    # Dictionaries - save as .json for simplicity
    hazus_max_filep = join(ddf_out_dir, 'hazus.json')
    hazus_max_nounc_filep = join(ddf_out_dir, 'hazus_nounc.json')


    # Only need to call this for one of the files
    # since they share the same parent directory
    prepare_saving(hazus_out_filep)

    # Save as parquet files since
    # these will directly read in the
    # DDF params as a list, not as a string
    hazus_unc.to_parquet(hazus_out_filep)
    hazus_nounc.to_parquet(hazus_nounc_out_filep)

    # Save the json files
    with open(hazus_max_filep, 'w') as fp:
        json.dump(HAZUS_MAX_DICT, fp)

    with open(hazus_max_nounc_filep, 'w') as fp:
        json.dump(HAZUS_MAX_NOUNC_DICT, fp)

    # TODO better to do this in a log with timings
    print('HAZUS DDFs processed')

def est_naccs_loss(bld_types, depths, ddfs, MAX_DICT):
    # We are going to use a random number generator
    rng = np.random.default_rng()

    # Combine building types and depths on index
    bld_depths = pd.concat([bld_types, pd.Series(depths)], axis=1)
    # Rename columns to correspond to each series
    bld_depths.columns = ['ddf_id', 'depth_ft']
    # Merge bld_type/depths with the ddfs to get params linked up
    # Need to create columns for the merge
    # We use the number 100, since this is our floating point precision
    # for these DDFs
    bld_depths['merge'] = np.where(bld_depths['depth_ft'].isnull(),
                                    -9999,
                                    np.round(bld_depths['depth_ft']*100)).astype(int)
    ddfs['merge'] = np.round(ddfs['depth_ft']*100).astype(int) 
    # Drop column 'depth_ft' from ddfs for the merge
    loss_prep = bld_depths.merge(ddfs.drop(columns='depth_ft'),
                                 on=['ddf_id', 'merge'], how='left')
    # Drop the merge column
    loss_prep = loss_prep.drop(columns='merge')
    # Helpful to have a mask for where there are no flood depths
    loss_mask = loss_prep['depth_ft'].notnull()
    # When depths are null, no flooding so no damages
    loss_prep.loc[~loss_mask, 'rel_dam'] = 0
    # There are some depths greater than the support from DDFs
    # We are going to use the max_d_dict from preparing the DDFs to
    # assign the params from the max depth for the same bld_type
    missing_rows = ((loss_mask) &
                    (loss_prep['params'].isnull()))
    missing_params = loss_prep.loc[missing_rows]['ddf_id'].map(MAX_DICT)

    # Replace the entries with missing params but positive depths
    loss_prep.loc[missing_rows, 'params'] = missing_params
    # Now we can estimate losses for all notnull() depth_ft rows
    # using the triangular distribution with the 'params' column
    # Using the loss_mask, which gives us rows with flooding,
    # we will first get the ddf_params from 'parms' and
    # use np.stack to access the columns for rng()
    ddf_params = pd.DataFrame(np.stack(loss_prep.loc[loss_mask]['params']),
                              columns=['left', 'mode', 'right'],
                              index=loss_prep.loc[loss_mask].index)
    # We separate left, mode, max as columns
    # which makes it much easier to get the damage values we need
    loss_df = pd.concat([loss_prep.loc[loss_mask], ddf_params], axis=1)
    
    # When there is no actual triangular distribution, because values are
    # equal, just return one of the param values, 
    no_tri_mask = loss_df['left'] == loss_df['right']
    loss_df.loc[no_tri_mask, 'rel_dam'] = loss_df.loc[no_tri_mask]['left']
    
    # Otherwise we draw
    # from the triangular distribution
    loss_df.loc[~no_tri_mask,
                'rel_dam'] = rng.triangular(loss_df.loc[~no_tri_mask]['left'],
                                            loss_df.loc[~no_tri_mask]['mode'],
                                            loss_df.loc[~no_tri_mask]['right'])
    
    # Combine to get our losses series
    fld_loss = loss_df['rel_dam']
    no_fld = loss_prep[loss_prep['rel_dam'].notnull()]['rel_dam']
    losses = pd.concat([fld_loss, no_fld], axis=0).sort_index()

    # Return our loss estimates
    return losses

def est_hazus_loss(hazus_ddf_types, depths, ddfs, MAX_DICT):
    # We are going to use a random number generator
    rng = np.random.default_rng()

    # Combine building types and depths on index
    bld_depths = pd.concat([hazus_ddf_types, pd.Series(depths)], axis=1)
    # Rename columns to correspond to each series
    bld_depths.columns = ['ddf_id', 'depth_ft']
    # Merge bld_type/depths with the ddfs to get params linked up
    # Need to create columns for the merge
    # We use the number 10, since this is our floating point precision
    bld_depths['merge'] = np.where(bld_depths['depth_ft'].isnull(),
                                -9999,
                                np.round(bld_depths['depth_ft']*10)).astype(int)
    ddfs['merge'] = np.round(ddfs['depth_ft']*10).astype(int) 
    # Drop column 'depth_ft' from ddfs for the merge
    loss_prep = bld_depths.merge(ddfs.drop(columns='depth_ft'),
                                on=['ddf_id', 'merge'], how='left')
    # Drop the merge column
    loss_prep = loss_prep.drop(columns='merge')
    # Helpful to have a mask for where there are no flood depths
    loss_mask = loss_prep['depth_ft'].notnull()
    # When depths are null, no flooding so no damages
    loss_prep.loc[~loss_mask, 'rel_dam'] = 0
    # There are some depths greater than the support from DDFs
    # We are going to use the max_d_dict from preparing the DDFs to
    # assign the params from the max depth for the same bld_type
    missing_rows = ((loss_mask) &
                    (loss_prep['params'].isnull()))
    missing_params = loss_prep.loc[missing_rows]['ddf_id'].map(MAX_DICT)
    # Replace the entries with missing params but positive depths
    loss_prep.loc[missing_rows, 'params'] = missing_params
    # Now we can estimate losses for all notnull() depth_ft rows
    # using the uniform distribution with the 'params' column
    # Using the loss_mask, which gives us rows with flooding,
    # we will first get the ddf_params from 'parms' and
    # use np.stack to access the columns for rng()
    ddf_params = pd.DataFrame(np.stack(loss_prep.loc[loss_mask]['params']),
                              columns=['low', 'high'],
                              index=loss_prep.loc[loss_mask].index)
    # We separate low and high as columns
    # which makes it much easier to get the damage values we need
    loss_df = pd.concat([loss_prep.loc[loss_mask], ddf_params], axis=1)
    
    # When values are
    # equal, just return one of the param values, 
    no_uni_mask = loss_df['low'] == loss_df['high']
    loss_df.loc[no_uni_mask, 'rel_dam'] = loss_df.loc[no_uni_mask]['low']
    
    # Otherwise we draw
    # from the triangular distribution
    loss_df.loc[~no_uni_mask,
                'rel_dam'] = rng.uniform(loss_df.loc[~no_uni_mask]['low'],
                                         loss_df.loc[~no_uni_mask]['high'])
    
    # Combine to get our losses series
    fld_loss = loss_df['rel_dam']
    no_fld = loss_prep[loss_prep['rel_dam'].notnull()]['rel_dam']
    losses = pd.concat([fld_loss, no_fld], axis=0).sort_index()

    # Return our loss estimates
    return losses

def est_hazus_loss_nounc(bld_types, depths, ddfs, MAX_DICT):
    # Combine building types and depths on index
    bld_depths = pd.concat([bld_types, pd.Series(depths)], axis=1)
    # Rename columns to correspond to each series
    bld_depths.columns = ['ddf_id', 'depth_ft']
    # Merge bld_type/depths with the ddfs to get params linked up
    # Need to create columns for the merge
    # We use the number 10, since this is our floating point precision
    bld_depths['merge'] = np.where(bld_depths['depth_ft'].isnull(),
                                -9999,
                                np.round(bld_depths['depth_ft']*10)).astype(int)
    ddfs['merge'] = np.round(ddfs['depth_ft']*10).astype(int) 
    # Drop column 'depth_ft' from ddfs for the merge
    loss_prep = bld_depths.merge(ddfs.drop(columns='depth_ft'),
                                on=['ddf_id', 'merge'], how='left')
    # Drop the merge column
    loss_prep = loss_prep.drop(columns='merge')
    # Helpful to have a mask for where there are no flood depths
    loss_mask = loss_prep['depth_ft'].notnull()
    # When depths are null, no flooding so no damages
    loss_prep.loc[~loss_mask, 'rel_dam'] = 0
    # There could be some depths greater than the support from DDFs
    # Fill these in based on the HAZUS_DEF_MAX_DICT
    missing_rows = ((loss_mask) &
                    (loss_prep['rel_dam'].isnull()))
    missing_dams = loss_prep.loc[missing_rows]['ddf_id'].map(MAX_DICT)
    # Replace the entries with missing params but positive depths
    loss_prep.loc[missing_rows, 'rel_dam'] = missing_dams
    
    # We go directly to losses now
    losses = loss_prep['rel_dam']

    return losses

def get_losses(depth_ffe_df, ddf, ddf_types, s_values,
               vuln_dir_i):
    '''
    For a given dataframe of depths relative to first floor elevation
    and a given depth-damage function library (i.e. hazus), call
    the corresponding functions to get losses for each scenario/rp
    in depth_ffe_df. This returns relative losses scaled by
    the quantitites provided in the s_values serires

    depth_ffe_df: DataFrame, scenarios/return periods with depths relative to ffe
    linked to each structure
    ddf: str, the name of the ddf library
    ddf_types: Series, the occupancy codes that tell us what ddf to use
    s_values: Series, the value realizations for the structures
    '''
    # We need to load ddf data for loss estimation
    naccs_ddfs = pd.read_parquet(join(vuln_dir_i, 'physical', 'naccs_ddfs.pqt'))
    hazus_ddfs = pd.read_parquet(join(vuln_dir_i, 'physical', 'hazus_ddfs.pqt'))
    with open(join(vuln_dir_i, 'physical', 'hazus.json'), 'r') as fp:
        HAZUS_MAX_DICT = json.load(fp)
    with open(join(vuln_dir_i, 'physical', 'naccs.json'), 'r') as fp:
        NACCS_MAX_DICT = json.load(fp)
    
    # Get the relative loss based on the ddf provided
    # and then scale this by the values series
    loss = {}
    for d_col in depth_ffe_df.columns:
        rp = d_col.split('_')[-1]
        if ddf == 'naccs':
            rel_loss = est_naccs_loss(ddf_types,
                                      depth_ffe_df[d_col],
                                      naccs_ddfs,
                                      NACCS_MAX_DICT)
        elif ddf == 'hazus':
            rel_loss = est_hazus_loss(ddf_types,
                                      depth_ffe_df[d_col],
                                      hazus_ddfs,
                                      HAZUS_MAX_DICT)
        
        loss[rp] = rel_loss.values*s_values
        print('Losses estimated in RP: ' + rp)
    
    loss_df = pd.DataFrame.from_dict(loss)
    loss_df.columns = ['loss_' + x for x in loss_df.columns]

    return loss_df

def get_eal(loss_df, rp_list):
    '''
    We use trapezoidal approximation to get the expected annual loss
    from a dataframe of losses based on design events. rp_list 
    is sorted from most to least frequent design event

    loss_df: DataFrame, losses in different design events
    rp_list: list of str, sorted list of the return period from
    most to least frequent
    '''
    p_rp_list = [round(1/int(x), 4) for x in rp_list]
    loss_list = ['loss_' + str(x) for x in rp_list]

    # Need eal series with the same index as the loss_df
    eal = pd.Series(index=loss_df.index).fillna(0)

    # We loop through our loss list and apply the 
    # trapezoidal approximation
    # We need these to be sorted from most frequent
    # to least frequent
    for i in range(len(loss_list) - 1):
        loss1 = loss_df[loss_list[i]]
        loss2 = loss_df[loss_list[i+1]]
        rp1 = p_rp_list[i]
        rp2 = p_rp_list[i+1]
        eal += (loss1 + loss2)*(rp1-rp2)/2
    final = eal + loss_df[loss_list[-1]]*p_rp_list[-1]

    # This is the final trapezoid to add in
    final_eal = eal + loss_df[loss_list[-1]]*p_rp_list[-1]
    print('Calculated EAL')

    return final_eal