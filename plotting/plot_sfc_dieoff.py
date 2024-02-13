"""
Plot Die-Off Curves For Surface Verification Using METplus Output

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import datetime as dt

import metplus_tools as mt
import metplus_plots as mp

#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input file information
#parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/real_red_sims/'
#parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/syn_data_sims/'
parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion/sims_real_red_data/'
input_sims = {'ctrl':{'dir':parent_dir + 'winter/sfc/2022020109/output/point_stat',
                      'color':'r'},
              'no_sfc':{'dir':parent_dir + 'winter_no_sfc/sfc/2022020109/output/point_stat',
                        'color':'b'}}
line_type = 'sl1l2'
plot_var = 'TMP'
plot_lvl = 'Z2'
plot_stat = 'RMSE'
ob_subset = 'ADPSFC'

# Other plotting options
toggle_pts = True

# Valid times (as datetime objects)
valid_times = [dt.datetime(2022, 2, 1, 10) + dt.timedelta(hours=i) for i in range(158)]

# Forecast lead times (hrs)
fcst_lead = [0, 1, 2, 3, 6, 12]

# Confidence interval options
ci = True
ci_lvl = 0.95
acct_lag_corr = True

out_tag = 'lag'


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

out = mp.plot_sfc_dieoff(input_sims, valid_times, fcst_lead=fcst_lead, line_type=line_type,
                         plot_var=plot_var, plot_lvl=plot_lvl, plot_stat=plot_stat, 
                         ob_subset=ob_subset, toggle_pts=toggle_pts, out_tag=out_tag, verbose=False,
                         ci=ci, ci_lvl=ci_lvl, acct_lag_corr=acct_lag_corr)


"""
End plot_sfc_dieoff.py 
"""
