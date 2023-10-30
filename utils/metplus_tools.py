"""
Functions to Help Manipulate METplus Output in Python

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np


#---------------------------------------------------------------------------------------------------
# Functions
#---------------------------------------------------------------------------------------------------

def read_ascii(fnames, verbose=True):
    """
    Read several ASCII MET output files and concatenate into a single DataFrame.

    Parameters
    ----------
    fnames : list of strings
        List of filenames to read in
    verbose : boolean, optional
        Option to print warning messages if a file does not exist

    Returns
    -------
    verif_df : pd.DataFrame
        Output DataFrame containing the MET output

    """

    raw_dfs = []
    for f in fnames:
        try:
            df = pd.read_csv(f, delim_whitespace=True)
            if len(df) > 0:
                raw_dfs.append(df)
        except FileNotFoundError:
            if verbose:
                print('File not found: %s' % f)
            continue
    verif_df = pd.concat(raw_dfs)

    return verif_df


def compute_stats(verif_df, line_type='sl1l2'):
    """
    Compute additional statistics for MET output.

    Parameters
    ----------
    verif_df : pd.DataFrame
        DataFrame with MET output from read_ascii()
    line_type : string, optional
        MET output line type

    Returns
    -------
    new_df : pd.DataFrame
        DataFrame with additional statistics

    """

    new_df = verif_df.copy()

    if line_type == 'sl1l2':
        new_df['RMSE'] = np.sqrt(verif_df['FFBAR'] - 2.*verif_df['FOBAR'] + verif_df['OOBAR'])
        new_df['BIAS_RATIO'] = verif_df['FBAR'] / verif_df['OBAR']
        new_df['BIAS_DIFF'] = verif_df['FBAR'] - verif_df['OBAR']

    elif line_type == 'vl1l2':
        new_df['VECT_RMSE'] = np.sqrt(verif_df['UVFFBAR'] - 2.*verif_df['UVFOBAR'] + verif_df['UVOOBAR'])
        new_df['MAG_BIAS_RATIO'] = verif_df['F_SPEED_BAR'] / verif_df['O_SPEED_BAR']
        new_df['MAG_BIAS_DIFF'] = verif_df['F_SPEED_BAR'] - verif_df['O_SPEED_BAR']

    return new_df


def compute_stats_entire_df(verif_df, line_type='sl1l2'):
    """
    Compute statistics using all lines in a MET output DataFrame.

    Parameters
    ----------
    verif_df : pd.DataFrame
        DataFrame with MET output from read_ascii()
    line_type : string, optional
        MET output line type

    Returns
    -------
    new_df : pd.DataFrame
        DataFrame with a single line of statistics summarizing the entire input DataFrame

    """
 
    # Update means to include all lines in the input DataFrame
    cols = []
    for c in verif_df.columns:
        if c[-3:] == 'BAR':
            cols.append(c)

    new_means = {}
    new_means['TOTAL'] = np.sum(verif_df['TOTAL'].values)
    for c in cols:
        new_means[c] = np.zeros(1)
        new_means[c][0] = (np.sum(verif_df[c].values * verif_df['TOTAL'].values) /
                           new_means['TOTAL'])

    combined_df = pd.DataFrame(new_means)

    # Compute statistics
    new_df = compute_stats(combined_df, line_type=line_type)

    return new_df


def compute_stats_vert_avg(verif_df, vcoord='P', vmin=100, vmax=1000, line_type='sl1l2'):
    """
    Compute vertically aggregated statistics from a MET output DataFrame.

    Parameters
    ----------
    verif_df : pd.DataFrame
        DataFrame with MET output from read_ascii()
    vcoord : string, optional
        Vertical coordinate. This is the first character in the FCST_LEV entries (usually 'P' or 
        'Z')
    vmin : float, optional
        Minimum value of the vertical coordinate for averaging
    vmax : float, optional
        Maximum value of the vertical coordinate for averaging
    line_type : string, optional
        MET output line type

    Returns
    -------
    new_df : pd.DataFrame
        DataFrame with statistics aggregated over vertical levels.

    """

    # Only retain rows within our vertical averaging column
    fcst_lev_num = np.array([float(s[1:]) for s in verif_df['FCST_LEV'].values])
    fcst_lev_type = np.array([s[0] for s in verif_df['FCST_LEV'].values])
    red_df = verif_df.loc[(fcst_lev_type == vcoord) & (fcst_lev_num >= vmin) & (fcst_lev_num <= vmax)].copy()

    # Loop over each unique combo of FCST_LEAD, FCST_VALID_BEG, FCST_VAR, and OBTYPE
    dfs = []
    combos = np.array(np.meshgrid(np.unique(red_df['FCST_LEAD'].values),
                                  np.unique(red_df['FCST_VALID_BEG'].values),
                                  np.unique(red_df['FCST_VAR'].values),
                                  np.unique(red_df['OBTYPE'].values))).T.reshape(-1, 4)
    for i in range(combos.shape[0]):
        subset = verif_df.loc[(red_df['FCST_LEAD'] == combos[i, 0]) &
                              (red_df['FCST_VALID_BEG'] == combos[i, 1]) &
                              (red_df['FCST_VAR'] == combos[i, 2]) &
                              (red_df['OBTYPE'] == combos[i, 3])].copy()
        tmp_df = compute_stats_entire_df(subset, line_type=line_type)
        dfs.append(tmp_df)

    new_df = pd.concat(dfs)
    for i, var in enumerate(['FCST_LEAD', 'FCST_VALID_BEG', 'FCST_VAR', 'OBTYPE']):
        new_df[var] = combos[:, i]

    return new_df


"""
End metplus_tools.py 
"""
