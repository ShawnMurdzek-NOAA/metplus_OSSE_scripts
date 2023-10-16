"""
Plot Time Series For Surface Verification Using METplus Output

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
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input file information
#parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/real_red_sims/'
parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/syn_data_sims/'
input_sims = {'ctrl':{'dir':parent_dir + 'winter_updated/output/point_stat',
                      'color':'r'},
              'no_aircft':{'dir':parent_dir + 'winter_no_aircft/output/point_stat',
                           'color':'b'},
              'no_raob':{'dir':parent_dir + 'winter_no_raob/output/point_stat',
                         'color':'orange'},
              'no_sfc':{'dir':parent_dir + 'winter_no_sfc/output/point_stat',
                        'color':'gray'}}
line_type = 'sl1l2'
plot_var = 'TMP'
plot_lvl = 'Z2'
plot_stat = 'RMSE'
ob_subset = 'ADPSFC'

# Other plotting options
toggle_pts = False

# Valid times (as datetime objects)

# Winter real_red sims
#valid_times = [dt.datetime(2022, 2, 1, 10) + dt.timedelta(hours=i) for i in range(158)] # 1-hr forecasts
#valid_times = [dt.datetime(2022, 2, 1, 12) + dt.timedelta(hours=i) for i in range(156)] # 3-hr forecasts
#valid_times = [dt.datetime(2022, 2, 1, 15) + dt.timedelta(hours=i) for i in range(153)] # 6-hr forecasts

# Winter synthetic sims
#valid_times = [dt.datetime(2022, 2, 1, 10) + dt.timedelta(hours=i) for i in 
#               list(range(83)) + list(range(84, 158))] # 1-hr forecasts
#valid_times = [dt.datetime(2022, 2, 1, 12) + dt.timedelta(hours=i) for i in 
#               list(range(83)) + list(range(84, 156))] # 3-hr forecasts
valid_times = [dt.datetime(2022, 2, 1, 15) + dt.timedelta(hours=i) for i in 
               list(range(83)) + list(range(84, 153))] # 6-hr forecasts

# Forecast lead time (hrs)
fcst_lead = 6

output_file = ('%s_%s_%dhr_%s_%s_timeseries_syn.png' % 
               (plot_var, plot_lvl, fcst_lead, plot_stat, ob_subset))


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

# Read in data
verif_df = {}
for key in input_sims.keys():
    fnames = ['%s/point_stat_%02d0000L_%sV_%s.txt' %
              (input_sims[key]['dir'], fcst_lead, t.strftime('%Y%m%d_%H%M%S'), line_type) for t in
              valid_times]
    verif_df[key] = mt.read_ascii(fnames)

    # Compute derived statistics
    if line_type == 'sl1l2':
        verif_df[key] = mt.compute_stats_sl1l2(verif_df[key])
    elif line_type == 'vl1l2':
        verif_df[key] = mt.compute_stats_vl1l2(verif_df[key])

# Make plot
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
for key in input_sims.keys():
    plot_df = verif_df[key].loc[(verif_df[key]['FCST_VAR'] == plot_var) &
                                (verif_df[key]['FCST_LEV'] == plot_lvl) &
                                (verif_df[key]['OBTYPE'] == ob_subset)].copy()
    if toggle_pts:
        ax.plot(valid_times, plot_df[plot_stat], linestyle='-', marker='o', c=input_sims[key]['color'], 
                label='%s (mean = %.5f)' % (key, np.mean(plot_df[plot_stat])))
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


"""
End plot_sfc_timeseries.py 
"""
