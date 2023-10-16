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

def read_ascii(fnames):
    """
    Read several ASCII MET output files and concatenate into a single DataFrame.

    Parameters
    ----------
    fnames : list of strings
        List of filenames to read in

    Returns
    -------
    verif_df : pd.DataFrame
        Output DataFrame containing the MET output

    """

    raw_dfs = []
    for f in fnames:
        raw_dfs.append(pd.read_csv(f, delim_whitespace=True))
    verif_df = pd.concat(raw_dfs)

    return verif_df


def compute_stats_sl1l2(verif_df):
    """
    Compute additional statistics for sl1l2 MET output.

    Parameters
    ----------
    verif_df : pd.DataFrame
        DataFrame with MET output from read_ascii()

    Returns
    -------
    new_df : pd.DataFrame
        DataFrame with additional statistics

    """

    new_df = verif_df.copy()
    new_df['RMSE'] = np.sqrt(verif_df['FFBAR'] - 2.*verif_df['FOBAR'] + verif_df['OOBAR'])
    new_df['BIAS_RATIO'] = verif_df['FBAR'] / verif_df['OBAR']
    new_df['BIAS_DIFF'] = verif_df['FBAR'] - verif_df['OBAR']

    return new_df


def compute_stats_vl1l2(verif_df):
    """
    Compute additional statistics for vl1l2 MET output.

    Parameters
    ----------
    verif_df : pd.DataFrame
        DataFrame with MET output from read_ascii()

    Returns
    -------
    new_df : pd.DataFrame
        DataFrame with additional statistics

    """

    new_df = verif_df.copy()
    new_df['VECT_RMSE'] = np.sqrt(verif_df['UVFFBAR'] - 2.*verif_df['UVFOBAR'] + verif_df['UVOOBAR'])

    return new_df


"""
End metplus_tools.py 
"""
