"""
Plot Sawtooth Diagrams Using Surface or Upper-Air Verification From METplus

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
parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/real_red_sims/'
#parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/syn_data_sims/'
input_sims = {'ctrl':{'dir':parent_dir + 'winter_updated/sfc/output/point_stat',
                      'color':'r'},
              'no_aircft':{'dir':parent_dir + 'winter_no_aircft/sfc/output/point_stat',
                           'color':'b'},
              'no_raob':{'dir':parent_dir + 'winter_no_raob/sfc/output/point_stat',
                         'color':'orange'},
              'no_sfc':{'dir':parent_dir + 'winter_no_sfc/sfc/output/point_stat',
                        'color':'gray'}}
input_sims = {'raob_only':{'dir':parent_dir + 'winter_raob_only/upper_air/output/point_stat',
                           'color':'r'},
              'ctrl':{'dir':parent_dir + 'winter_updated/upper_air/output/point_stat',
                      'color':'b'},
              'no_raob':{'dir':parent_dir + 'winter_no_raob/upper_air/output/point_stat',
                         'color':'orange'}}
#input_sims = {'raob_only':{'dir':parent_dir + 'winter_raob_only/sfc/output/point_stat',
#                           'color':'r'},
#              'ctrl':{'dir':parent_dir + 'winter_updated/sfc/output/point_stat',
#                      'color':'b'}}
verif_type = 'ua'
line_type = 'sl1l2'
plot_var = 'TMP'
plot_lvl1 = 'P100'
plot_lvl2 = 'P1000'
plot_stat = 'RMSE'
ob_subset = 'ADPUPA'

# Other plotting options
toggle_pts = True

# Initial times (as datetime objects)
#init_times = [dt.datetime(2022, 2, 1, 9) + dt.timedelta(hours=i) for i in range(5)]
init_times = [dt.datetime(2022, 2, 1, 9) + dt.timedelta(hours=i) for i in range(4)]

# Forecast lead time(hrs)
fcst_lead = [0, 1, 2, 3]

out_tag = 'raob_only' 


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

out = mp.plot_sawtooth(input_sims, init_times, fcst_lead=fcst_lead, verif_type=verif_type, 
                       line_type=line_type, plot_var=plot_var, plot_lvl1=plot_lvl1, 
                       plot_lvl2=plot_lvl2, plot_stat=plot_stat, ob_subset=ob_subset, 
                       toggle_pts=toggle_pts, out_tag=out_tag, verbose=False)


"""
End plot_sawtooth.py 
"""
