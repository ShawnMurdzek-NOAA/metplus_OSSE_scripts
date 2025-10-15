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
import copy

import metplus_OSSE_scripts.plotting.metplus_tools as mt


#---------------------------------------------------------------------------------------------------
# Functions
#---------------------------------------------------------------------------------------------------

def diff_plot_prep(input_sims, diff_kw, line_type):
    """
    Determine the name of the ctrl simulation and add line_type to diff_kw

    Parameters
    ----------
    input_sims : Dictionary
        METplus output files. Key is simulation name (used in the legend). The value is another
        dictionary containing 'dir' (METplus output directory), 'color', and 'ctrl'.
    diff_kw : Dictionary
        Keyword arguments passed to compute_stats_diff()
    line_type : String
        METplus line type

    Returns
    -------
    ctrl_name : String
        Name of the control simulation
    diff_kw : Dictionary
        Keyword arguments passed to compute_stats_diff() with line_type added

    """

    for sim in input_sims:
        if input_sims[sim]['ctrl']:
            ctrl_name = sim
    if 'compute_kw' not in diff_kw:
        diff_kw['compute_kw'] = {}
    diff_kw['compute_kw']['line_type'] = line_type

    return ctrl_name, diff_kw


def plot_sfc_timeseries(input_sims, valid_times, fcst_lead=6, file_prefix='point_stat', 
                        line_type='sl1l2', diffs=False, include_ctrl=True, diff_kw={},
                        plot_param={'FCST_VAR':'TMP', 'FCST_LEV':'Z2', 'OBTYPE':'ADPSFC'},
                        plot_stat='RMSE', toggle_pts=True, out_tag='', verbose=False,
                        ax=None, include_zero=False, figsize=(8, 6)):
    """
    Plot time series for surface verification

    Parameters
    ----------
    input_sims : Dictionary
        METplus output files. Key is simulation name (used in the legend). The value is another
        dictionary containing 'dir' (METplus output directory), 'color', and 'ctrl'.
    valid_times : List of dt.datetime objects
        Forecast valid times
    fcst_lead : Integer, optional
        Forecast lead time (hrs)
    file_prefix : String, optional
        Prefix of METplus output files
    line_type : String, optional
        METplus line type
    diffs : Boolean, optional
        Option to plot differences between the input_sims with ctrl = True and all other simulations
    include_ctrl : Boolean, optional
        Option to include the control simulation when plotting differences between experiments and 
        the control
    diff_kw : Dictionary, optional
        Keyword arguments passed to compute_stats_diff()
    plot_param : dictionary, optional
        Parameters used to select which rows from the MET output to plot
    plot_stat : String, optional
        Forecast statistic to plot
    toggle_pts : Boolean, optional
        Turn individual points on or off
    out_tag : String, optional
        String to add to the output file
    verbose : Boolean, optional
        Option to have verbose output from mt.read_ascii()
    ax : matplotlib.axes object, optional
        Axes to draw plot on
    include_zero : Boolean, optional
        Option to include and bold the y = 0 line
    figsize : Tuple, optional
        Figure size

    Returns
    -------
    verif_df : pd.DataFrame
        DataFrame containing METplus output

    """

    # Make a copy of plot_param
    plot_param_local = copy.deepcopy(plot_param)
    if verbose:
        print('\nStarting plot_sfc_timeseries()')
        print('plot_param =')
        print(plot_param_local)

    # If computing differences, determine control simulation name and add line_type to diff_kw
    if diffs:
        ctrl_name, diff_kw = diff_plot_prep(input_sims, diff_kw, line_type)

    # Read in data
    verif_df = {}
    for key in input_sims.keys():
        fnames = ['%s/%s_%02d0000L_%sV_%s.txt' %
                  (input_sims[key]['dir'], file_prefix, fcst_lead, t.strftime('%Y%m%d_%H%M%S'), line_type) for t in
                  valid_times]
        verif_df[key] = mt.read_ascii(fnames, verbose=verbose)

        # Compute derived statistics
        if diffs and (key != ctrl_name):
            verif_df[key] = mt.compute_stats_diff(verif_df[key], verif_df[ctrl_name], **diff_kw)
        else:
            verif_df[key] = mt.compute_stats(verif_df[key], line_type=line_type)

    # Make plot
    save = False
    if ax == None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
        save = True
        param_str = ''
        for k in plot_param_local.keys():
            param_str = param_str + f'{plot_param_local[k]}_'
        output_file = f"{param_str}{plot_stat}_{fcst_lead}hr_{out_tag}_timeseries.png"
    for key in input_sims.keys():
        if diffs and not include_ctrl and (key == ctrl_name): continue
        if 'ls' not in input_sims[key].keys(): input_sims[key]['ls'] = '-'
        plot_df = mt.subset_verif_df(verif_df[key], plot_param_local)
        if verbose: print(f"\nin plot_sfc_timeseries(). Sim = {key}")
        if verbose: print(f"len(plot_df) = {len(plot_df)}")
        ylabel = f"{plot_df['FCST_LEV'].values[0]} {plot_df['FCST_VAR'].values[0]} {plot_stat} ({plot_df['FCST_UNITS'].values[0]})"
        if toggle_pts:
            ax.plot(valid_times, plot_df[plot_stat], linestyle=input_sims[key]['ls'], marker='o', 
                    c=input_sims[key]['color'], 
                    label='%s (mean = %.6f)' % (key, np.mean(plot_df[plot_stat])))
        else:
            ax.plot(valid_times, plot_df[plot_stat], linestyle=input_sims[key]['ls'], 
                    c=input_sims[key]['color'],
                    label='%s (mean = %.6f)' % (key, np.mean(plot_df[plot_stat])))
    if plot_stat == 'TOTAL':
        ax.set_ylabel('number', size=14)
    else:
        ax.set_ylabel(ylabel, size=14)
    ax.grid()
    ax.legend(fontsize=12)
    if include_zero:
        ax.axhline(0, c='k', lw=1.5, ls='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))

    param_key = list(plot_param_local.keys())
    for k in ['FCST_LEV', 'FCST_VAR', 'OBS_LEV', 'OBS_VAR']:
        if k in param_key:
            param_key.remove(k)
    ttl_list = [f'{k}: {plot_param_local[k]}' for k in param_key]
    ax.set_title(f"{fcst_lead}-hr Forecast\n{',  '.join(ttl_list)}", size=18)

    if save:
        plt.savefig(output_file)
        return verif_df
    else:
        return verif_df, ax


def plot_sfc_dieoff(input_sims, valid_times, fcst_lead=[0, 1, 2, 3, 6, 12], 
                    file_prefix='point_stat', line_type='sl1l2', 
                    diffs=False, include_ctrl=True, diff_kw={},
                    plot_param={'FCST_VAR':'TMP', 'FCST_LEV':'Z2', 'OBTYPE':'ADPSFC'}, 
                    plot_stat='RMSE', toggle_pts=True, out_tag='', 
                    verbose=False, ax=None, ci=False, ci_lvl=0.95, ci_opt='t_dist', ci_kw={},
                    mean_legend=True, include_zero=False, figsize=(8, 6)):
    """
    Plot die-off curves for surface verification

    Parameters
    ----------
    input_sims : Dictionary
        METplus output files. Key is simulation name (used in the legend). The value is another
        dictionary containing 'dir' (METplus output directory) and 'color'. Dictionary can also
        conatin 'subset', which overrides "OBTYPE" in plot_param, and 'prefix', which
        overrides the "file_prefix" keyword argument.
    valid_times : List of dt.datetime objects
        Forecast valid times
    fcst_lead : List, optional
        Forecast lead times (hrs)
    file_prefix : String, optional
        Prefix of METplus output files. Can also be set in input_sims dictionary.
    line_type : String, optional
        METplus line type
    diffs : Boolean, optional
        Option to plot differences between the input_sims with ctrl = True and all other simulations
    include_ctrl : Boolean, optional
        Option to include the control simulation when plotting differences between experiments and
        the control
    diff_kw : Dictionary, optional
        Keyword arguments passed to compute_stats_diff()
    plot_param : dictionary, optional
        Parameters used to select which rows from the MET output to plot
    plot_stat : String, optional
        Forecast statistic to plot
    toggle_pts : Boolean, optional
        Turn inidvidual points on or off
    out_tag : String, optional
        String to add to the output file
    verbose : Boolean, optional
        Option to have verbose output from this function and mt.read_ascii()
    ax : matplotlib.axes object, optional
        Axes to draw plot on
    ci : Boolean, optional
        Option to draw confidence intervals
    ci_lvl : Float, optional
        Confidence interval level as a fraction
    ci_opt : String, optional
        Method used to create confidence intervals
    ci_kw : Dictionary, optional
        Additional keyword arguments passed to the confidence interval function
    mean_legend : Boolean, optional
        Option to plot the mean forecast statistic in the legend
    include_zero : Boolean, optional
        Option to include and bold the y = 0 line
    figsize : Tuple, optional
        Figure size

    Returns
    -------
    verif_df : pd.DataFrame
        DataFrame containing METplus output

    """

    # Make a copy of plot_param
    plot_param_local = copy.deepcopy(plot_param)

    # If computing differences, determine control simulation name and add line_type to diff_kw
    if diffs:
        ctrl_name, diff_kw = diff_plot_prep(input_sims, diff_kw, line_type)

    # Read in data
    verif_df = {}
    for key in input_sims.keys():
        fnames = []
        if 'prefix' in input_sims[key].keys(): 
            file_prefix = input_sims[key]['prefix']
        for t in valid_times:
            for l in fcst_lead:
                fnames.append('%s/%s_%02d0000L_%sV_%s.txt' %
                              (input_sims[key]['dir'], file_prefix, l, t.strftime('%Y%m%d_%H%M%S'), line_type))
        verif_df[key] = mt.read_ascii(fnames, verbose=verbose)

    # Make plot
    save = False
    if ax == None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
        save = True
        param_str = ''
        for k in plot_param_local.keys():
            param_str = param_str + f'{plot_param_local[k]}_'
        output_file = f"{param_str}{plot_stat}_{out_tag}_dieoff.png"
    for key in input_sims.keys():
        if diffs and not include_ctrl and (key == ctrl_name): continue
        if 'ls' not in input_sims[key].keys(): input_sims[key]['ls'] = '-'
        if verbose: print()
        if verbose: print(f"in plot_sfc_dieoff(). Sim = {key}")
        yplot = []
        ci_low = []
        ci_high = []
        if 'subset' in input_sims[key].keys(): 
            plot_param_local['OBTYPE'] = input_sims[key]['subset']
        for l in fcst_lead:
            plot_param_local['FCST_LEAD'] = l*1e4
            red_df = mt.subset_verif_df(verif_df[key], plot_param_local)
            ylabel = f"{red_df['FCST_LEV'].values[0]} {red_df['FCST_VAR'].values[0]} {plot_stat} ({red_df['FCST_UNITS'].values[0]})"
            if verbose: print(f"forecast lead = {l}, len(red_df) = {len(red_df)}")
            if diffs and (key != ctrl_name):
                red_df_ctrl = mt.subset_verif_df(verif_df[ctrl_name], plot_param_local)
                stats_df = mt.compute_stats_entire_df(red_df, red_df_ctrl, line_type=line_type, 
                                                      diff_kw=diff_kw, ci=ci, ci_lvl=ci_lvl,
                                                      ci_opt=ci_opt, ci_kw=ci_kw)
            else:
                stats_df = mt.compute_stats_entire_df(red_df, line_type=line_type, ci=ci, ci_lvl=ci_lvl,
                                                      ci_opt=ci_opt, ci_kw=ci_kw)
            yplot.append(stats_df[plot_stat].values[0])
            if ci:
                ci_low.append(stats_df['low_%s' % plot_stat].values[0])
                ci_high.append(stats_df['high_%s' % plot_stat].values[0])
        yplot = np.array(yplot)
        if mean_legend:
            llabel = '%s (mean = %.6f)' % (key, np.mean(yplot))
        else:
            llabel = key
        if toggle_pts:
            ax.plot(fcst_lead, yplot, linestyle=input_sims[key]['ls'], marker='o', 
                    c=input_sims[key]['color'], label=llabel)
        else:
            ax.plot(fcst_lead, yplot, linestyle=input_sims[key]['ls'], c=input_sims[key]['color'], 
                    label=llabel)
        if ci:
            for j, fl in enumerate(fcst_lead):
                ax.plot([fl, fl], [ci_low[j], ci_high[j]], linestyle='-', marker='_', lw=0.5, 
                        c=input_sims[key]['color'])
    if plot_stat == 'TOTAL':
        ax.set_ylabel('number', size=14)
    else:
        ax.set_ylabel(ylabel, size=14)
    ax.set_xlabel('lead time (hr)', size=14)
    ax.grid()
    ax.legend(fontsize=12)
    if include_zero:
        ax.axhline(0, c='k', lw=1.5, ls='--')

    param_key = list(plot_param_local.keys())
    for k in ['FCST_LEV', 'FCST_VAR', 'OBS_LEV', 'OBS_VAR', 'FCST_LEAD']:
        if k in param_key:
            param_key.remove(k)
    ttl_list = [f'{k}: {plot_param_local[k]}' for k in param_key]
    ax.set_title(f"Die-Off\n{',  '.join(ttl_list)}", size=18)

    if save:
        plt.savefig(output_file)
        return verif_df, red_df
    else:
        return verif_df, ax


def plot_ua_vprof(input_sims, valid_times, fcst_lead=6, file_prefix='point_stat', line_type='sl1l2', 
                  diffs=False, include_ctrl=True, diff_kw={},
                  plot_param={'FCST_VAR':'TMP', 'OBTYPE':'ADPUPA'}, plot_stat='RMSE', 
                  toggle_pts=True, out_tag='', 
                  exclude_plvl=[], verbose=False, ax=None, ci=False, ci_lvl=0.95, ci_opt='t_dist',
                  ci_kw={}, mean_legend=True, ylim=[1050, 80], include_zero=False, figsize=(7, 7)):
    """
    Plot vertical profiles for upper-air verification

    Parameters
    ----------
    input_sims : Dictionary
        METplus output files. Key is simulation name (used in the legend). The value is another
        dictionary containing 'dir' (METplus output directory) and 'color'. Dictionary can also
        contain 'subset', which overrides "OBTYPE" in plot_param, and 'prefix', which
        overrides the "file_prefix" keyword argument.
        Optional keys for each simulation:
            ctrl: Whether this simulation is the control run (needed for differences)
            scale: Scalar that multiplies whatever is being plotted
    valid_times : List of dt.datetime objects
        Forecast valid times
    fcst_lead : Integer, optional
        Forecast lead time (hrs)
    file_prefix : String, optional
        Prefix of METplus output files. Can also be set in input_sims dictionary.
    line_type : String, optional
        METplus line type
    diffs : Boolean, optional
        Option to plot differences between the input_sims with ctrl = True and all other simulations
    include_ctrl : Boolean, optional
        Option to include the control simulation when plotting differences between experiments and
        the control
    diff_kw : Dictionary, optional
        Keyword arguments passed to compute_stats_diff()
    plot_param : dictionary, optional
        Parameters used to select which rows from the MET output to plot
    plot_stat : String, optional
        Forecast statistic to plot
    toggle_pts : Boolean, optional
        Turn inidvidual points on or off
    out_tag : String, optional
        String to add to the output file
    exclude_plvl : List of floats, optional
        Pressure levels to exclude from the plot
    verbose : Boolean, optional
        Option to have verbose output from mt.read_ascii()
    ax : matplotlib.axes object, optional
        Axes to draw plot on
    ci : Boolean, optional
        Option to draw confidence intervals
    ci_lvl : Float, optional
        Confidence interval level as a fraction
    ci_opt : String, optional
        Method used to create confidence intervals
    ci_kw : Dictionary, optional
        Additional keyword arguments passed to the confidence interval function
    mean_legend : Boolean, optional
        Option to plot the mean forecast statistic in the legend
    ylim : List of floats, optional
        Y-axis limits (hPa)
    include_zero : Boolean, optional
        Option to include and bold the x = 0 line
    figsize : Tuple, optional
        Figure size

    Returns
    -------
    verif_df : pd.DataFrame
        DataFrame containing METplus output

    """

    # Make a copy of plot_param
    plot_param_local = copy.deepcopy(plot_param)

    # If computing differences, determine control simulation name and add line_type to diff_kw
    if diffs:
        ctrl_name, diff_kw = diff_plot_prep(input_sims, diff_kw, line_type)

    # Read in data
    verif_df = {}
    for key in input_sims.keys():
        if 'prefix' in input_sims[key].keys(): 
            file_prefix = input_sims[key]['prefix']
        fnames = ['%s/%s_%02d0000L_%sV_%s.txt' %
                  (input_sims[key]['dir'], file_prefix, fcst_lead, t.strftime('%Y%m%d_%H%M%S'), line_type) for t in valid_times]
        verif_df[key] = mt.read_ascii(fnames, verbose=verbose)

    # Make plot
    save = False
    if ax == None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
        save = True
        param_str = ''
        for k in plot_param_local.keys():
            param_str = param_str + f'{plot_param_local[k]}_'
        output_file = f"{param_str}{plot_stat}_{fcst_lead}hr_{out_tag}_vprof.png"
    for key in input_sims.keys():
        if diffs and not include_ctrl and (key == ctrl_name): continue

        # Set default values
        if 'ls' not in input_sims[key].keys(): input_sims[key]['ls'] = '-'
        if 'scale' not in input_sims[key].keys(): input_sims[key]['scale'] = 1
        if 'subset' in input_sims[key].keys(): 
            plot_param_local['OBTYPE'] = input_sims[key]['subset']

        red_df = mt.subset_verif_df(verif_df[key], plot_param_local)
        xlabel = f"{red_df['FCST_VAR'].values[0]} {plot_stat} ({red_df['FCST_UNITS'].values[0]})"
        prslev = [int(s[1:]) for s in np.unique(red_df['FCST_LEV'].values)]
        if len(exclude_plvl) > 0:
            for p in exclude_plvl:
                if p in prslev:
                    prslev.remove(p)
        prslev = np.sort(np.array(prslev))
        xplot = np.zeros(prslev.shape)
        ci_low = np.zeros(prslev.shape)
        ci_high = np.zeros(prslev.shape)
        for j, p in enumerate(prslev):
            prs_df = red_df.loc[red_df['FCST_LEV'] == ('P%d' % p)]
            if diffs and (key != ctrl_name):
                prs_df_ctrl = mt.subset_verif_df(verif_df[ctrl_name], plot_param_local)
                stats_df = mt.compute_stats_entire_df(prs_df, prs_df_ctrl, line_type=line_type, 
                                                      diff_kw=diff_kw, ci=ci, ci_lvl=ci_lvl,
                                                      ci_opt=ci_opt, ci_kw=ci_kw)
            else:
                stats_df = mt.compute_stats_entire_df(prs_df, line_type=line_type, ci=ci, 
                                                      ci_lvl=ci_lvl,
                                                      ci_opt=ci_opt, ci_kw=ci_kw)
            xplot[j] = stats_df[plot_stat].values[0] * input_sims[key]['scale']
            if ci:
                ci_low[j] = stats_df['low_%s' % plot_stat].values[0] * input_sims[key]['scale']
                ci_high[j] = stats_df['high_%s' % plot_stat].values[0] * input_sims[key]['scale']
        if mean_legend:
            llabel = '%s (mean = %.6f)' % (key, np.mean(xplot))
        else:
            llabel = key
        if toggle_pts:
            ax.plot(xplot, prslev, linestyle=input_sims[key]['ls'], marker='o', 
                    c=input_sims[key]['color'], label=llabel)
        else:
            ax.plot(xplot, prslev, linestyle=input_sims[key]['ls'], c=input_sims[key]['color'], 
                    label=llabel)
        if ci:
            for j, p in enumerate(prslev):
                ax.plot([ci_low[j], ci_high[j]], [p, p], linestyle='-', marker='|', lw=0.5, 
                        c=input_sims[key]['color'])
    if plot_stat == 'TOTAL':
        ax.set_xlabel('number', size=14)
    else:
        ax.set_xlabel(xlabel, size=14)
    ax.set_ylabel('pressure (hPa)', size=14)
    ax.set_ylim(ylim)
    ax.set_yscale('log')
    ax.grid()
    ax.legend(fontsize=12)
    if include_zero:
        ax.axvline(0, c='k', lw=1.5, ls='--')

    param_key = list(plot_param_local.keys())
    for k in ['FCST_VAR', 'OBS_VAR']:
        if k in param_key:
            param_key.remove(k)
    ttl_list = [f'{k}: {plot_param_local[k]}' for k in param_key]
    ax.set_title(f"{fcst_lead}-hr Forecast\n{',  '.join(ttl_list)}", size=18)

    if save:
        plt.savefig(output_file)
        return verif_df
    else:
        return verif_df, ax


def plot_sawtooth(input_sims, init_times, fcst_lead=[0, 1], verif_type='sfc', 
                  file_prefix='point_stat', line_type='sl1l2', 
                  plot_param={'FCST_VAR':'TMP', 'OBTYPE':'ADPSFC'},
                  plot_lvl1='Z2', plot_lvl2='Z2', plot_stat='RMSE', toggle_pts=True, out_tag='', 
                  verbose=False, include_zero=False, figsize=(8, 6)):
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
    file_prefix : String, optional
        Prefix of METplus output files
    line_type : String, optional
        METplus line type
    plot_param : dictionary, optional
        Parameters used to select which rows from the MET output to plot
    plot_lvl1 : String, optional
        Variable vertical level
    plot_lvl2 : String, optional
        Variable vertical level. For surface verification, plot_lvl2 should equal plot_lvl1. For
        upper-air verification, plot_lvl2 should be the maximum value of the vertical coordinate over
        which the averaging is performed and plot_lvl1 should be the minimum value.
    plot_stat : String, optional
        Forecast statistic to plot
    toggle_pts : Boolean, optional
        Turn inidvidual points on or off
    out_tag : String, optional
        String to add to the output file
    verbose : Boolean, optional
        Option to have verbose output from mt.read_ascii()
    include_zero : Boolean, optional
        Option to include and bold the y = 0 line
    figsize : Tuple, optional
        Figure size

    Returns
    -------
    verif_df : pd.DataFrame
        DataFrame containing METplus output

    """

    # Make a copy of plot_param
    plot_param_local = copy.deepcopy(plot_param)

    param_str = ''
    for k in plot_param_local.keys():
        param_str = param_str + f'{plot_param_local[k]}_'
    output_file = f"{param_str}{plot_stat}_{out_tag}_{verif_type}_sawtooth.png"

    # Read in data
    verif_df = {}
    for key in input_sims.keys():
        verif_df[key] = {}
        for itime in init_times:
            vtimes = [itime + dt.timedelta(hours=fl) for fl in fcst_lead]
            fnames = ['%s/%s_%02d0000L_%sV_%s.txt' %
                      (input_sims[key]['dir'], file_prefix, fl, t.strftime('%Y%m%d_%H%M%S'), line_type)
                      for t, fl in zip(vtimes, fcst_lead)]
            verif_df[key][itime] = mt.read_ascii(fnames, verbose=verbose)

            # Compute derived statistics
            verif_df[key][itime] = mt.compute_stats(verif_df[key][itime], line_type=line_type)

    # Make plot
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
    for key in input_sims.keys():
        for j, itime in enumerate(init_times):
            tmp_df = mt.subset_verif_df(verif_df[key][itime], plot_param_local)
            ylabel = f"{tmp_df['FCST_VAR'].values[0]} {plot_stat} ({tmp_df['FCST_UNITS'].values[0]})"
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
            ax.set_ylabel(f"{plot_lvl1} {ylabel}", size=14)
        else:
            ax.set_ylabel(f"{plot_lvl1} {plot_lvl2} {ylabel}", size=14)
    ax.grid()
    ax.legend(fontsize=12)
    if include_zero:
        ax.axhline(0, c='k', lw=1.5, ls='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))

    param_key = list(plot_param_local.keys())
    for k in ['FCST_VAR']:
        param_key.remove(k)
    ttl_list = [f'{k}: {plot_param_local[k]}' for k in param_key]
    ax.set_title(',  '.join(ttl_list), size=18)

    plt.savefig(output_file)

    return verif_df


def plot_pct_diffs(verif_df_list, xvals, xlabel, plot_stat='RMSE', out_tag='', 
                   verbose=False, ax=None, ci=False, ci_lvl=0.95, ci_opt='bootstrap', ci_kw={},
                   figsize=(8, 6), plot_pct_diff_kw={}, plot_ci_kw={}):
    """
    Plot percent differences

    Parameters
    ----------
    verif_df_list : list of pd.DataFrame
        DataFrames containing that statistic listed in plot_stat
    xvals : list
        X-axis values (percent diffs are plotted on Y axis)
    xlabel : string
        X-axis label
    plot_stat : String, optional
        Forecast statistic to plot
    out_tag : String, optional
        String to add to the output file
    verbose : Boolean, optional
        Option to have verbose output from mt.read_ascii()
    ax : matplotlib.axes object, optional
        Axes to draw plot on
    ci : Boolean, optional
        Option to draw confidence intervals
    ci_lvl : Float, optional
        Confidence interval level as a fraction
    ci_opt : String, optional
        Method used to create confidence intervals
    ci_kw : Dictionary, optional
        Additional keyword arguments passed to the confidence interval function
    figsize : Tuple, optional
        Figure size
    plot_pct_diff_kw : dictionary, optional
        Keyword arguments passed to ax.plot() when plotting percent differences 
    plot_ci_kw : dictionary, optional
        Keyword arguments passed to ax.plot() when plotting confidence intervals

    Returns
    -------
    pct_diff : list
        Percent differences
    ci_sorted : list
        Confidence interval bounds. Only returned if ci = True.

    """

    # Compute percent differences for plot_stat
    ctrl_df = verif_df_list.pop(0)
    ctrl = ctrl_df[plot_stat].values
    pct_diff = [0]
    if ci:
        ci_vals = [(0, 0)]
    for verif_df in verif_df_list:
        pct_diff_all = 1e2 * (verif_df[plot_stat].values - ctrl) / ctrl
        pct_diff.append(np.mean(pct_diff_all))
        if ci:
            ci_vals.append(mt.confidence_interval_mean(pct_diff_all, level=ci_lvl, option=ci_opt, ci_kw=ci_kw))

    # Sort based on xvals
    xvals = np.array(xvals)
    pct_diff = np.array(pct_diff)
    sort_idx = np.argsort(xvals)
    xvals = xvals[sort_idx]
    pct_diff = pct_diff[sort_idx]
    if ci:
        ci_sorted = []
        for i in sort_idx:
            ci_sorted.append(ci_vals[i])

    # Make plot
    save = False
    if ax == None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
        save = True
        output_file = f"{plot_stat}_{out_tag}_pct_diff.png"
    ax.plot(xvals, pct_diff, **plot_pct_diff_kw)
    if ci:
        for i, x in enumerate(xvals):
            ax.plot([x, x], ci_sorted[i], marker='_', **plot_ci_kw)

    ax.grid()
    ax.set_xlabel(xlabel, size=14)
    ax.set_ylabel(f'{plot_stat} % difference', size=14)

    if save:
        plt.savefig(output_file)
    
    if ci:
        return pct_diff, ci_sorted
    else:
        return pct_diff


"""
End metplus_plots.py 
"""
