"""
Functions to Help Manipulate METplus Output in Python

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import scipy.stats as ss


#---------------------------------------------------------------------------------------------------
# Functions
#---------------------------------------------------------------------------------------------------

def confidence_interval_t_mean(data, level=0.95, acct_lag_corr=False, mats_ste=False):
    """
    Compute the confidence interval for the mean of a dataset using a t distribution

    Parameters
    ----------
    data : np.array
        Input data
    level : Float, optional
        Confidence level for the confidence interval
    acct_lag_corr : Boolean, optional
        Option to account to autocorrelated data by using the lag-1 autocorrelation when computing 
        the standard error. Method is based on Wilks (2011), eqn 5.12 (note that this is slightly 
        different from the equation used in MATS at GSL). Note that this assumes that the input 
        data are "in order" (e.g., each data point is an hour after the previous data point).
    mats_ste : Boolean, optional
        Option to use the MATS formulation for standard error when accounting for temporal
        autocorrelation. For information on the MATS method, see here:
        https://ruc.noaa.gov/stats/vertical/StdErrorcalculationonEMBverificationpages/StdErrorcalculationonEMBverificationpages.html

    Returns
    -------
    ci : Tuple
        Upper and lower bound of the confidence interval

    """

    n = len(data)
    avg = np.mean(data)
    std = np.std(data) 
    t_low = ss.t.ppf(0.5 * (1 - level), n - 1)

    # Compute standard error
    if acct_lag_corr:
        auto_corr = np.corrcoef(data[1:], data[:-1])[0, -1]
    else:
        auto_corr = 0
    if mats_ste:
        ste = std / (np.sqrt((n - 1) * (1 - auto_corr)))
    else:
        ste = std / (np.sqrt(n * (1 - auto_corr) / (1 + auto_corr)))

    ci = (avg + (t_low * ste), avg - (t_low * ste))

    return ci


def confidence_interval_bootstrap_mean(data, level=0.95, bootstrap_kw={}):
    """
    Compute the confidence interval for the mean of a dataset using a bootstrap

    Parameters
    ----------
    data : np.array
        Input data
    level : Float, optional
        Confidence level for the confidence interval
    bootstrap_kw : Dictionary, optional
        Keyword to pass to bootstrap function

    Returns
    -------
    ci : Tuple
        Upper and lower bound of the confidence interval

    """

    out = ss.bootstrap((data,), np.mean, **bootstrap_kw)
    ci = (out.confidence_interval.high, out.confidence_interval.low)

    return ci


def confidence_interval_mean(data, level=0.95, option='t_dist', ci_kw={}):
    """
    Compute the confidence interval for the mean of a dataset

    Parameters
    ----------
    data : np.array
        Input data
    level : Float, optional
        Confidence level for the confidence interval
    option : String, optional
        Method used to compute confidence interval ('t_dist' or 'bootstrap')
    ci_kw : Dictionary, optional
        Keywords passed to the confidence interval function

    Returns
    -------
    ci : Tuple
        Upper and lower bound of the confidence interval

    """

    if option == 't_dist':
        ci = confidence_interval_t_mean(data, level=level, **ci_kw)
    elif option == 'bootstrap':
        ci = confidence_interval_bootstrap_mean(data, level=level, **ci_kw)
    else:
        print('confidence interval option {option} does not exist'.format(option=option))

    return ci


def compute_stdev(sum_val, sum_sq, n):
    """
    Compute the standard deviation from partial sums. Based on calculate_stddev from METcalcpy.

    Parameters
    ----------
    sum_val : Float
        Sum of all the values in the data set
    sum_sq : Float
        Sum of all the squared values in the data set
    n : Integer
        Number of values in the data set

    Returns
    -------
    s : Float
        Standard deviation

    """

    s = np.sqrt((sum_sq - (sum_val * sum_val) / n) / (n - 1))

    return s


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
            df = pd.read_csv(f, sep='\s+')
            if len(df) > 0:
                raw_dfs.append(df)
        except FileNotFoundError:
            if verbose:
                print('File not found: %s' % f)
            continue
    verif_df = pd.concat(raw_dfs)

    return verif_df


def subset_verif_df(df, param):
    """
    Select rows from a verification DataFrame that meet certain conditions

    Parameters
    ----------
    df : pd.DataFrame
        MET verification output
    param : dictionary
        Row conditions. Key = column name, value = column value

    Returns
    -------
    subset_df : pd.DataFrame
        Copy of the input DataFrame with certain rows selected

    """

    cond = np.ones(len(df), dtype=bool)
    for k in param.keys():
        cond = cond * (df[k] == param[k])
    subset_df = df.loc[cond, :].copy()

    return subset_df


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

    Notes
    -----
    Some of these calculations come from METcalcpy. See 
    https://github.com/dtcenter/METcalcpy/blob/main_v2.1/metcalcpy/util/sl1l2_statistics.py

    """

    new_df = verif_df.copy()

    if line_type == 'sl1l2':
        new_df['MSE'] = verif_df['FFBAR'] - 2.*verif_df['FOBAR'] + verif_df['OOBAR']
        new_df['RMSE'] = np.sqrt(new_df['MSE'])
        new_df['BIAS_RATIO'] = verif_df['FBAR'] / verif_df['OBAR']
        new_df['BIAS_DIFF'] = verif_df['FBAR'] - verif_df['OBAR']

    elif line_type == 'vl1l2':
        new_df['VECT_MSE'] = verif_df['UVFFBAR'] - 2.*verif_df['UVFOBAR'] + verif_df['UVOOBAR']
        new_df['VECT_RMSE'] = np.sqrt(new_df['VECT_MSE'])
        new_df['MAG_BIAS_RATIO'] = verif_df['F_SPEED_BAR'] / verif_df['O_SPEED_BAR']
        new_df['MAG_BIAS_DIFF'] = verif_df['F_SPEED_BAR'] - verif_df['O_SPEED_BAR']

    return new_df


def compute_stats_entire_df(verif_df, line_type='sl1l2', agg=False, ci=False, ci_lvl=0.95,
                            ci_opt='t_dist', ci_kw={}):
    """
    Compute statistics using all lines in a MET output DataFrame.

    Parameters
    ----------
    verif_df : pd.DataFrame
        DataFrame with MET output from read_ascii()
    line_type : string, optional
        MET output line type
    agg : Boolean, optional
        Option to compute statistics by aggregating the partial sums. This is the more "correct"
        method, but is not compatible with confidence intervals. Currently only available for
        'sl1l2' and 'vl1l2' line_type.
    ci : Boolean, optional
        Option to draw confidence intervals
    ci_lvl : Float, optional
        Confidence interval level as a fraction
    ci_opt : String, optional
        Method used to create confidence intervals
    ci_kw : Dictionary, optional
        Additional keywords passed to confidence interval function

    Returns
    -------
    new_df : pd.DataFrame
        DataFrame with a single line of statistics summarizing the entire input DataFrame

    """

    if (agg and not ci) and (line_type in ['sl1l2', 'vl1l2']):
 
        # Update means to include all lines in the input DataFrame
        cols = []
        for c in verif_df.columns:
            if c[-3:] == 'BAR':
                cols.append(c)

        new_means = {}
        new_means['TOTAL'] = np.sum(verif_df['TOTAL'].values)

        # Check to ensure that length of verif_df is not 0
        if len(verif_df) == 0:
            print('Warning: mt.compute_stats_entire_df: Length of verif_df = 0')

        for c in cols:
            new_means[c] = np.zeros(1)
            new_means[c][0] = (np.sum(verif_df[c].values * verif_df['TOTAL'].values) /
                               new_means['TOTAL'])

        combined_df = pd.DataFrame(new_means)

        # Compute statistics
        new_df = compute_stats(combined_df, line_type=line_type)

    else:

        # Compute statistics first, then average
        verif_df = compute_stats(verif_df, line_type=line_type)
        new_means = {}
        avg_col = []
        for c in verif_df.columns:
            if (type(verif_df[c].values[0]) != str) and (len(np.unique(verif_df[c].values)) > 1): 
                avg_col.append(c)
                new_means[c] = np.zeros(1)
                new_means[c][0] = np.mean(verif_df[c].values)
        new_means['TOTAL'] = np.sum(verif_df['TOTAL'].values)
        if 'TOTAL' in avg_col:
            avg_col.remove('TOTAL')

        #cols_old = verif_df.columns
        #verif_df = compute_stats(verif_df, line_type=line_type) 
        #cols_new = verif_df.columns
        #new_means = {}
        #avg_col = []
        #new_means['TOTAL'] = np.sum(verif_df['TOTAL'].values)
        #print(cols_new)  # SSM DEBUG
        #for c in cols_new:
        #    if c not in cols_old:
        #        print(c)  # SSM DEBUG
        #        avg_col.append(c)
        #        new_means[c] = np.zeros(1)
        #        new_means[c][0] = np.mean(verif_df[c].values)

        #new_df = pd.DataFrame(new_means)

        # Compute confidence intervals
        if ci:
            # If accounting for temporal autocorrelation, ensure that values are in temporal order
            verif_df.sort_values('FCST_VALID_BEG', axis=0, inplace=True)
            for c in avg_col:
                ci_vals = confidence_interval_mean(verif_df[c].values, level=ci_lvl, 
                                                   option=ci_opt, ci_kw=ci_kw)
                new_means['low_%s' % c] = np.array([ci_vals[0]])
                new_means['high_%s' % c] = np.array([ci_vals[1]])

        new_df = pd.DataFrame(new_means)

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
