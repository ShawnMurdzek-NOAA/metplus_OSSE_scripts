"""
Plot MAE Time Series Using METplus Output

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
input_dir = '/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts/real_data_pt_ob_verif/PointStat/output/point_stat/'
line_type = 'sl1l2'
plot_var = 'TMP'
plot_lvl = 'Z2'
plot_stat = 'TOTAL'

# Valid times (as datetime objects)
valid_times = [dt.datetime(2022, 2, 1, 10) + dt.timedelta(hours=i) for i in range(19)]

# Forecast lead time (hrs)
fcst_lead = 1

output_file = 'N_T2m_timeseries.png'


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

# Read in data
raw_dfs = []
for t in valid_times:
    raw_dfs.append(pd.read_csv('%s/point_stat_%02d0000L_%sV_%s.txt' % 
                               (input_dir, fcst_lead, t.strftime('%Y%m%d_%H%M%S'), line_type), 
                               delim_whitespace=True))
verif_df = pd.concat(raw_dfs)

# Compute derived statistics
if line_type == 'sl1l2':
    verif_df['RMSE'] = np.sqrt(verif_df['FFBAR'] - 2.*verif_df['FOBAR'] + verif_df['OOBAR'])

# Make plot
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
plot_df = verif_df.loc[np.logical_and(verif_df['FCST_VAR'] == plot_var,
                                      verif_df['FCST_LEV'] == plot_lvl)].copy()
ax.plot(valid_times, plot_df[plot_stat], linestyle='-', marker='o', c='r', label='N')
#ax.plot(valid_times, plot_df['MAE'], linestyle='-', marker='o', c='b', label='MAE')
#ax.set_ylabel('%s %s (%s)' % (plot_lvl, plot_var, plot_df['FCST_UNITS'].values[0]), size=14)
ax.set_ylabel('number', size=14)
ax.set_title('%d-hr Forecast' % fcst_lead, size=18)
ax.grid()
ax.legend()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))
plt.savefig(output_file)
plt.show()


"""
End plot_mae_timeseries.py 
"""
