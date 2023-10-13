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


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input file information
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
plot_stat = 'MAE'
ob_subset = 'ADPSFC'

# Valid times (as datetime objects)
valid_times = [dt.datetime(2022, 2, 1, 10) + dt.timedelta(hours=i) for i in range(12)]

# Forecast lead time (hrs)
fcst_lead = 1

output_file = 'T2m_timeseries_syn.png'


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

# Read in data
verif_df = {}
for key in input_sims.keys():
    raw_dfs = []
    for t in valid_times:
        raw_dfs.append(pd.read_csv('%s/point_stat_%02d0000L_%sV_%s.txt' % 
                                   (input_sims[key]['dir'], fcst_lead, t.strftime('%Y%m%d_%H%M%S'), line_type), 
                                   delim_whitespace=True))
    verif_df[key] = pd.concat(raw_dfs)

    # Compute derived statistics
    if line_type == 'sl1l2':
        verif_df[key]['RMSE'] = np.sqrt(verif_df[key]['FFBAR'] - 2.*verif_df[key]['FOBAR'] + 
                                        verif_df[key]['OOBAR'])

# Make plot
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
for key in input_sims.keys():
    plot_df = verif_df[key].loc[(verif_df[key]['FCST_VAR'] == plot_var) &
                                (verif_df[key]['FCST_LEV'] == plot_lvl) &
                                (verif_df[key]['OBTYPE'] == ob_subset)].copy()
    ax.plot(valid_times, plot_df[plot_stat], linestyle='-', marker='o', c=input_sims[key]['color'], 
            label='%s (mean = %.5f)' % (key, np.mean(plot_df[plot_stat])))
if plot_stat == 'TOTAL':
    ax.set_ylabel('number', size=14)
else:
    ax.set_ylabel('%s %s %s (%s)' % (plot_lvl, plot_var, plot_stat, plot_df['FCST_UNITS'].values[0]), size=14)
ax.set_title('%d-hr Forecast' % fcst_lead, size=18)
ax.grid()
ax.legend()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))
plt.savefig(output_file)


"""
End plot_sfc_timeseries.py 
"""
