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
            raw_dfs.append(pd.read_csv(f, delim_whitespace=True))
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
        DataFrame with additional statistics

    """
 
    condensed_dict = {}    

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


"""
End metplus_tools.py 
"""
