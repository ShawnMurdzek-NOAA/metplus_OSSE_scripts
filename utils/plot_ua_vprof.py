"""
Plot Vertical Profiles For Upper-Air Verification Using METplus Output

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
#parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/'
input_sims = {'ctrl':{'dir':parent_dir + 'winter_updated/upper_air/output/point_stat',
                      'color':'r'},
              'no_aircft':{'dir':parent_dir + 'winter_no_aircft/upper_air/output/point_stat',
                           'color':'b'},
              'no_raob':{'dir':parent_dir + 'winter_no_raob/upper_air/output/point_stat',
                         'color':'orange'},
              'no_sfc':{'dir':parent_dir + 'winter_no_sfc/upper_air/output/point_stat',
                        'color':'gray'}}
#input_sims = {'real':{'dir':parent_dir + 'real_red_sims/winter_updated/upper_air/output/point_stat',
#                      'color':'r'},
#              'OSSE':{'dir':parent_dir + 'syn_data_sims/winter_updated/upper_air/output/point_stat',
#                      'color':'b'}}
line_type = 'sl1l2'
plot_var = 'TMP'
plot_stat = 'TOTAL'
ob_subset = 'ADPUPA'

# Other plotting options
toggle_pts = True
exclude_plvl = [950]

# Valid times (as datetime objects)
valid_times = [dt.datetime(2022, 2, 1, 10) + dt.timedelta(hours=i) for i in range(158)]
valid_times = [dt.datetime(2022, 2, 1, 15) + dt.timedelta(hours=i) for i in range(6*24)]

# Forecast lead times (hrs)
fcst_lead = 6

output_file = ('%s_%s_%s_%dhr_vprof_syn.png' % 
               (plot_var, plot_stat, ob_subset, fcst_lead))


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

# Read in data
verif_df = {}
for key in input_sims.keys():
    fnames = ['%s/point_stat_%02d0000L_%sV_%s.txt' % 
              (input_sims[key]['dir'], fcst_lead, t.strftime('%Y%m%d_%H%M%S'), line_type) for t in valid_times]
    verif_df[key] = mt.read_ascii(fnames)

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


"""
End plot_ua_vprof.py 
"""
