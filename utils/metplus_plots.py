"""
Functions to Create Various METplus Verification Plots

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import datetime as dt

import metplus_tools as mt


#---------------------------------------------------------------------------------------------------
# Functions
#---------------------------------------------------------------------------------------------------

def plot_sfc_timeseries(input_sims, valid_times, fcst_lead=6, line_type='sl1l2', plot_var='TMP', 
                        plot_lvl='Z2', plot_stat='RMSE', ob_subset='ADPSFC', toggle_pts=True, 
                        out_tag='', verbose=False):
    """
    Plot time series for surface verification

    Parameters
    ----------
    input_sims : Dictionary
        METplus output files. Key is simulation name (used in the legend). The value is another
        dictionary containing 'dir' (METplus output directory) and 'color'.
    valid_times : List of dt.datetime objects
        Forecast valid times
    fcst_lead : Integer, optional
        Forecast lead time (hrs)
    line_type : String, optional
        METplus line type
    plot_var : String, optional
        Variable to plot from the METplus output
    plot_lvl : String, optional
        Variable vertical level
    plot_stat : String, optional
        Forecast statistic to plot
    ob_subset : String, optional
        Observation subset to use for verification
    toggle_pts : Boolean, optional
        Turn individual points on or off
    out_tag : String, optional
        String to add to the output file
    verbose : Boolean, optional
        Option to have verbose output from mt.read_ascii()

    Returns
    -------
    verif_df : pd.DataFrame
        DataFrame containing METplus output

    """

    output_file = ('%s_%s_%s_%s_%dhr_%s_sfc_timeseries.png' % 
                   (plot_var, plot_lvl, plot_stat, ob_subset, fcst_lead, out_tag))

    # Read in data
    verif_df = {}
    for key in input_sims.keys():
        fnames = ['%s/point_stat_%02d0000L_%sV_%s.txt' %
                  (input_sims[key]['dir'], fcst_lead, t.strftime('%Y%m%d_%H%M%S'), line_type) for t in
                  valid_times]
        verif_df[key] = mt.read_ascii(fnames, verbose=verbose)

        # Compute derived statistics
        verif_df[key] = mt.compute_stats(verif_df[key], line_type=line_type)

    # Make plot
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
    for key in input_sims.keys():
        plot_df = verif_df[key].loc[(verif_df[key]['FCST_VAR'] == plot_var) &
                                    (verif_df[key]['FCST_LEV'] == plot_lvl) &
                                    (verif_df[key]['OBTYPE'] == ob_subset)].copy()
        if toggle_pts:
            ax.plot(valid_times, plot_df[plot_stat], linestyle='-', marker='o', c=input_sims[key]['color'],
                    label='%s (mean = %.6f)' % (key, np.mean(plot_df[plot_stat])))
        else:
            ax.plot(valid_times, plot_df[plot_stat], linestyle='-', c=input_sims[key]['color'],
                    label='%s (mean = %.6f)' % (key, np.mean(plot_df[plot_stat])))
    if plot_stat == 'TOTAL':
        ax.set_ylabel('number', size=14)
    else:
        ax.set_ylabel('%s %s %s (%s)' % (plot_lvl, plot_var, plot_stat, plot_df['FCST_UNITS'].values[0]), size=14)
    ax.set_title('%d-hr Forecast, Verified Against %s' % (fcst_lead, ob_subset), size=18)
    ax.grid()
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))
    plt.savefig(output_file)

    return verif_df


def plot_sfc_dieoff(input_sims, valid_times, fcst_lead=[0, 1, 2, 3, 6, 12], line_type='sl1l2', 
                    plot_var='TMP', plot_lvl='Z2', plot_stat='RMSE', ob_subset='ADPSFC', 
                    toggle_pts=True, out_tag='', verbose=False):
    """
    Plot die-off curves for surface verification

    Parameters
    ----------
    input_sims : Dictionary
        METplus output files. Key is simulation name (used in the legend). The value is another
        dictionary containing 'dir' (METplus output directory) and 'color'.
    valid_times : List of dt.datetime objects
        Forecast valid times
    fcst_lead : List, optional
        Forecast lead times (hrs)
    line_type : String, optional
        METplus line type
    plot_var : String, optional
        Variable to plot from the METplus output
    plot_lvl : String, optional
        Variable vertical level
    plot_stat : String, optional
        Forecast statistic to plot
    ob_subset : String, optional
        Observation subset to use for verification
    toggle_pts : Boolean, optional
        Turn inidvidual points on or off
    out_tag : String, optional
        String to add to the output file
    verbose : Boolean, optional
        Option to have verbose output from mt.read_ascii()

    Returns
    -------
    verif_df : pd.DataFrame
        DataFrame containing METplus output

    """

    output_file = ('%s_%s_%s_%s_%s_sfc_dieoff.png' % (plot_var, plot_lvl, plot_stat, ob_subset, out_tag))

    # Read in data
    verif_df = {}
    for key in input_sims.keys():
        fnames = []
        for t in valid_times:
            for l in fcst_lead:
                fnames.append('%s/point_stat_%02d0000L_%sV_%s.txt' %
                              (input_sims[key]['dir'], l, t.strftime('%Y%m%d_%H%M%S'), line_type))
        verif_df[key] = mt.read_ascii(fnames, verbose=verbose)

        # Compute derived statistics
        verif_df[key] = mt.compute_stats(verif_df[key], line_type=line_type)

    # Make plot
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
    for key in input_sims.keys():
        yplot = []
        for l in fcst_lead:
            red_df = verif_df[key].loc[(verif_df[key]['FCST_VAR'] == plot_var) &
                                       (verif_df[key]['FCST_LEV'] == plot_lvl) &
                                       (verif_df[key]['OBTYPE'] == ob_subset) &
                                       (verif_df[key]['FCST_LEAD'] == l*1e4)].copy()
            stats_df = mt.compute_stats_entire_df(red_df, line_type=line_type)
            yplot.append(stats_df[plot_stat].values[0])
        yplot = np.array(yplot)
        if toggle_pts:
            ax.plot(fcst_lead, yplot, linestyle='-', marker='o', c=input_sims[key]['color'],
                    label='%s (mean = %.6f)' % (key, np.mean(yplot)))
        else:
            ax.plot(fcst_lead, yplot, linestyle='-', c=input_sims[key]['color'],
                    label='%s (mean = %.6f)' % (key, np.mean(yplot)))
    if plot_stat == 'TOTAL':
        ax.set_ylabel('number', size=14)
    else:
        ax.set_ylabel('%s %s %s (%s)' % (plot_lvl, plot_var, plot_stat, red_df['FCST_UNITS'].values[0]), size=14)
    ax.set_xlabel('lead time (hr)', size=14)
    ax.set_title('Die-Off, Verified Against %s' % ob_subset, size=18)
    ax.grid()
    ax.legend()
    plt.savefig(output_file)

    return verif_df


def plot_ua_vprof(input_sims, valid_times, fcst_lead=6, line_type='sl1l2', plot_var='TMP', 
                  plot_stat='RMSE', ob_subset='ADPUPA', toggle_pts=True, out_tag='', 
                  exclude_plvl=[], verbose=False):
    """
    Plot vertical profiles for upper-air verification

    Parameters
    ----------
    input_sims : Dictionary
        METplus output files. Key is simulation name (used in the legend). The value is another
        dictionary containing 'dir' (METplus output directory) and 'color'.
    valid_times : List of dt.datetime objects
        Forecast valid times
    fcst_lead : Integer, optional
        Forecast lead time (hrs)
    line_type : String, optional
        METplus line type
    plot_var : String, optional
        Variable to plot from the METplus output
    plot_stat : String, optional
        Forecast statistic to plot
    ob_subset : String, optional
        Observation subset to use for verification
    toggle_pts : Boolean, optional
        Turn inidvidual points on or off
    out_tag : String, optional
        String to add to the output file
    exclude_plvl : List of floats, optional
        Pressure levels to exclude from the plot
    verbose : Boolean, optional
        Option to have verbose output from mt.read_ascii()

    Returns
    -------
    verif_df : pd.DataFrame
        DataFrame containing METplus output

    """

    output_file = ('%s_%s_%s_%dhr_%s_ua_vprof.png' % 
                   (plot_var, plot_stat, ob_subset, fcst_lead, out_tag))

    # Read in data
    verif_df = {}
    for key in input_sims.keys():
        fnames = ['%s/point_stat_%02d0000L_%sV_%s.txt' %
                  (input_sims[key]['dir'], fcst_lead, t.strftime('%Y%m%d_%H%M%S'), line_type) for t in valid_times]
        verif_df[key] = mt.read_ascii(fnames, verbose=verbose)

        # Compute derived statistics
        verif_df[key] = mt.compute_stats(verif_df[key], line_type=line_type)

    # Make plot
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 7))
    for key in input_sims.keys():
        red_df = verif_df[key].loc[(verif_df[key]['FCST_VAR'] == plot_var) &
                                   (verif_df[key]['OBTYPE'] == ob_subset)].copy()
        prslev = [int(s[1:]) for s in np.unique(red_df['FCST_LEV'].values)]
        if len(exclude_plvl) > 0:
            for p in exclude_plvl:
                if p in prslev:
                    prslev.remove(p)
        prslev = np.sort(np.array(prslev))
        xplot = np.zeros(prslev.shape)
        for j, p in enumerate(prslev):
            prs_df = red_df.loc[red_df['FCST_LEV'] == ('P%d' % p)]
            stats_df = mt.compute_stats_entire_df(prs_df, line_type=line_type)
            xplot[j] = stats_df[plot_stat].values[0]
        if toggle_pts:
            ax.plot(xplot, prslev, linestyle='-', marker='o', c=input_sims[key]['color'],
                    label='%s (mean = %.6f)' % (key, np.mean(xplot)))
        else:
            ax.plot(xplot, prslev, linestyle='-', c=input_sims[key]['color'],
                    label='%s (mean = %.6f)' % (key, np.mean(xplot)))
    if plot_stat == 'TOTAL':
        ax.set_xlabel('number', size=14)
    else:
        ax.set_xlabel('%s %s (%s)' % (plot_var, plot_stat, red_df['FCST_UNITS'].values[0]), size=14)
    ax.set_ylabel('pressure (hPa)', size=14)
    ax.set_ylim([1050, 80])
    ax.set_yscale('log')
    ax.set_title('%d-hr Forecast, Verified Against %s' % (fcst_lead, ob_subset), size=18)
    ax.grid()
    ax.legend()
    plt.savefig(output_file)

    return verif_df


def plot_sawtooth(input_sims, init_times, fcst_lead=[0, 1], verif_type='sfc', line_type='sl1l2', 
                  plot_var='TMP', plot_lvl1='Z2', plot_lvl2='Z2', plot_stat='RMSE', 
                  ob_subset='ADPSFC', toggle_pts=True, out_tag='', verbose=False):
    """
    Plot sawtooth diagrams for surface or upper-air verification

    Parameters
    ----------
    input_sims : Dictionary
        METplus output files. Key is simulation name (used in the legend). The value is another
        dictionary containing 'dir' (METplus output directory) and 'color'.
    init_times : List of dt.datetime objects
        Forecast initialization times
    fcst_lead : List of Integers, optional
        Forecast lead time (hrs)
    verif_type : String, optional
        Verification type ('sfc' or 'ua')
    line_type : String, optional
        METplus line type
    plot_var : String, optional
        Variable to plot from the METplus output
    plot_lvl1 : String, optional
        Variable vertical level
    plot_lvl2 : String, optional
        Variable vertical level. For surface verification, plot_lvl2 should equal plot_lvl1. For
        upper-air verification, plot_lvl2 should be the maximum value of the vertical coordinate over
        which the averaging is performed and plot_lvl1 should be the minimum value.
    plot_stat : String, optional
        Forecast statistic to plot
    ob_subset : String, optional
        Observation subset to use for verification
    toggle_pts : Boolean, optional
        Turn inidvidual points on or off
    out_tag : String, optional
        String to add to the output file
    verbose : Boolean, optional
        Option to have verbose output from mt.read_ascii()

    Returns
    -------
    verif_df : pd.DataFrame
        DataFrame containing METplus output

    """

    output_file = ('%s_%s_%s_%s_%s_sawtooth.png' %
                   (plot_var, plot_stat, ob_subset, out_tag, verif_type))

    # Read in data
    verif_df = {}
    for key in input_sims.keys():
        verif_df[key] = {}
        for itime in init_times:
            vtimes = [itime + dt.timedelta(hours=fl) for fl in fcst_lead]
            fnames = ['%s/point_stat_%02d0000L_%sV_%s.txt' %
                      (input_sims[key]['dir'], fl, t.strftime('%Y%m%d_%H%M%S'), line_type)
                      for t, fl in zip(vtimes, fcst_lead)]
            verif_df[key][itime] = mt.read_ascii(fnames, verbose=verbose)

            # Compute derived statistics
            verif_df[key][itime] = mt.compute_stats(verif_df[key][itime], line_type=line_type)

    # Make plot
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
    for key in input_sims.keys():
        for j, itime in enumerate(init_times):
            tmp_df = verif_df[key][itime].loc[(verif_df[key][itime]['FCST_VAR'] == plot_var) &
                                              (verif_df[key][itime]['OBTYPE'] == ob_subset)].copy()
            if plot_lvl1 == plot_lvl2:
                plot_df = tmp_df.loc[tmp_df['FCST_LEV'] == plot_lvl1].copy()
            else:
                plot_df = mt.compute_stats_vert_avg(tmp_df, vcoord=plot_lvl1[0],
                                                    vmin=float(plot_lvl1[1:]),
                                                    vmax=float(plot_lvl2[1:]),
                                                    line_type=line_type)
            xplot = [dt.datetime.strptime(t, '%Y%m%d_%H%M%S') for t in plot_df['FCST_VALID_BEG']]
            if toggle_pts:
                lead = [t for t in plot_df['FCST_LEAD']]
                for fl, m in zip(fcst_lead, ['*', 'o', 's', '^']):
                    plot_1row = plot_df.loc[plot_df['FCST_LEAD'] == fl*1e4]
                    if len(plot_1row) == 0:
                        continue
                    x = dt.datetime.strptime(plot_1row['FCST_VALID_BEG'].values[0], '%Y%m%d_%H%M%S')
                    ax.plot(x, plot_1row[plot_stat].values[0], marker=m, ms=10, c=input_sims[key]['color'])
            if j == 0:
                ax.plot(xplot, plot_df[plot_stat], linestyle='-', c=input_sims[key]['color'],
                    label=key)
            else:
                ax.plot(xplot, plot_df[plot_stat], linestyle='-', c=input_sims[key]['color'])
    if plot_stat == 'TOTAL':
        ax.set_ylabel('number', size=14)
    else:
        if plot_lvl1 == plot_lvl2:
            ax.set_ylabel('%s %s %s (%s)' % (plot_lvl1, plot_var, plot_stat, tmp_df['FCST_UNITS'].values[0]), size=14)
        else:
            ax.set_ylabel('%s$-$%s %s %s (%s)' % (plot_lvl1, plot_lvl2, plot_var, plot_stat,
                                                  tmp_df['FCST_UNITS'].values[0]), size=14)
    ax.set_title('Verified Against %s' % ob_subset, size=18)
    ax.grid()
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))
    plt.savefig(output_file)

    return verif_df


"""
End metplus_plots.py 
"""
