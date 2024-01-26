# Packages
import pandas as pd
import numpy as np

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