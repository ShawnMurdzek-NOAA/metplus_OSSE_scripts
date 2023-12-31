"""
Plot Vertical Profiles For Upper-Air Verification Using METplus Output

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
parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/'
input_sims = {'ctrl':{'dir':parent_dir + 'winter_updated/upper_air/output/point_stat',
                      'color':'r'},
              'no_aircft':{'dir':parent_dir + 'winter_no_aircft/upper_air/output/point_stat',
                           'color':'b'},
              'no_raob':{'dir':parent_dir + 'winter_no_raob/upper_air/output/point_stat',
                         'color':'orange'},
              'no_sfc':{'dir':parent_dir + 'winter_no_sfc/upper_air/output/point_stat',
                        'color':'gray'}}
input_sims = {'real':{'dir':parent_dir + 'real_red_sims/winter_updated/upper_air/output/point_stat',
                      'color':'r'},
              'OSSE':{'dir':parent_dir + 'syn_data_sims/winter_updated/upper_air/output/point_stat',
                      'color':'b'}}
line_type = 'vl1l2'
plot_var = 'UGRD_VGRD'
plot_stat = 'MAG_BIAS_DIFF'
ob_subset = 'ADPUPA'

# Other plotting options
toggle_pts = True
exclude_plvl = []

# Valid times (as datetime objects)
valid_times = [dt.datetime(2022, 2, 1, 10) + dt.timedelta(hours=i) for i in range(158)]
valid_times = [dt.datetime(2022, 2, 1, 15) + dt.timedelta(hours=i) for i in range(6*24)]

# Forecast lead times (hrs)
fcst_lead = 3

out_tag = 'ctrl' 


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

out = mp.plot_ua_vprof(input_sims, valid_times, fcst_lead=fcst_lead, line_type=line_type,
                       plot_var=plot_var, plot_stat=plot_stat, ob_subset=ob_subset, 
                       toggle_pts=toggle_pts, out_tag=out_tag, exclude_plvl=exclude_plvl,
                       verbose=False)


"""
End plot_ua_vprof.py 
"""
