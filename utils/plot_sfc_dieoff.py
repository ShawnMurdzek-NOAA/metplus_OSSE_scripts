"""
Plot Die-Off Curves For Surface Verification Using METplus Output

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
#parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/syn_data_sims/'
parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/'
input_sims = {'ctrl':{'dir':parent_dir + 'winter_updated/sfc/output/point_stat',
                      'color':'r'},
              'no_aircft':{'dir':parent_dir + 'winter_no_aircft/sfc/output/point_stat',
                           'color':'b'},
              'no_raob':{'dir':parent_dir + 'winter_no_raob/sfc/output/point_stat',
                         'color':'orange'},
              'no_sfc':{'dir':parent_dir + 'winter_no_sfc/sfc/output/point_stat',
                        'color':'gray'}}
input_sims = {'real':{'dir':parent_dir + 'real_red_sims/winter_updated/sfc/output/point_stat',
                      'color':'r'},
              'OSSE':{'dir':parent_dir + 'syn_data_sims/winter_updated/sfc/output/point_stat',
                      'color':'b'}}
line_type = 'sl1l2'
plot_var = 'TMP'
plot_lvl = 'Z2'
plot_stat = 'TOTAL'
ob_subset = 'ADPSFC'

# Other plotting options
toggle_pts = True

# Valid times (as datetime objects)
valid_times = [dt.datetime(2022, 2, 1, 10) + dt.timedelta(hours=i) for i in range(158)]

# Forecast lead times (hrs)
fcst_lead = [0, 1, 2, 3, 6, 12]

output_file = ('%s_%s_%s_%s_dieoff_ctrl.png' % 
               (plot_var, plot_lvl, plot_stat, ob_subset))


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

# Read in data
verif_df = {}
for key in input_sims.keys():
    fnames = []
    for t in valid_times:
        for l in fcst_lead:
            fnames.append('%s/point_stat_%02d0000L_%sV_%s.txt' %
                          (input_sims[key]['dir'], l, t.strftime('%Y%m%d_%H%M%S'), line_type))
    verif_df[key] = mt.read_ascii(fnames)

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


"""
End plot_sfc_dieoff.py 
"""
