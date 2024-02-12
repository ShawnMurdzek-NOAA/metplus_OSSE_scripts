"""
METplus Plotting Driver

If using GridStat output, use the link_GridStat_output.sh script to organize the METplus output
files into the proper format first before running this script.

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import datetime as dt
import numpy as np
import os
import copy
import matplotlib.pyplot as plt
import yaml

import metplus_plots as mp


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input YAML file name
yaml_name = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/plots/app_orion/winter/ctrl/point_stat/plot_param.yml'
with open(yaml_name, 'r') as fptr:
    param = yaml.safe_load(fptr)

# Read in parameters
sim_dict = param['sim_dict']
verif_type = param['verif_type']
file_prefix = param['file_prefix']
out_dir = param['out_dir']
out_tag = param['out_tag']
valid_time_start = param['valid_time_start']
valid_time_step = param['valid_time_step']
valid_time_end_hr = param['valid_time_end_hr']
valid_time_ua_start = param['valid_time_ua_start']
valid_time_ua_step = param['valid_time_ua_step']
valid_time_ua_end_hr = param['valid_time_ua_end_hr']
itime_exclude = param['itime_exclude']
vtime_exclude = param['vtime_exclude']
plot_dict = param['plot_dict']
fcst_lead_dieoff = param['fcst_lead_dieoff']
fcst_lead_other = param['fcst_lead_other']

# Create lists of valid times
valid_times = [valid_time_start + dt.timedelta(hours=i) 
               for i in range(0, valid_time_end_hr, valid_time_step)]
valid_times_ua = [valid_time_ua_start + dt.timedelta(hours=i) 
                  for i in range(0, valid_time_ua_end_hr, valid_time_ua_step)]

# Change exclude times to empty lists
if itime_exclude == [None]:
    itime_exclude = []
if vtime_exclude == [None]:
    vtime_exclude = []


#---------------------------------------------------------------------------------------------------
# Create Plots
#---------------------------------------------------------------------------------------------------

os.system('mkdir -p {d}'.format(d=out_dir))

for plot_var in plot_dict.keys():
    for plot_stat in plot_dict[plot_var]['plot_stat']:
        print('creating plots for {v} {stat}'.format(v=plot_var, stat=plot_stat))

        # Surface verification
        for ob_subset in plot_dict[plot_var]['sfc_ob_subset']:
            input_sims_sfc = copy.deepcopy(sim_dict)
            for key in input_sims_sfc:
                input_sims_sfc[key]['dir'] = input_sims_sfc[key]['dir'].format(typ=verif_type, subtyp='sfc')
            _ = mp.plot_sfc_dieoff(input_sims_sfc, valid_times, 
                                   fcst_lead=fcst_lead_dieoff, 
                                   file_prefix=file_prefix,
                                   line_type=plot_dict[plot_var]['line_type'],
                                   plot_var=plot_var,
                                   plot_lvl=plot_dict[plot_var]['sfc_plot_lvl'],
                                   plot_stat=plot_stat,
                                   ob_subset=ob_subset,
                                   toggle_pts=True,
                                   out_tag=out_tag,
                                   verbose=False)
            plt.close()
            for ftime in fcst_lead_other:
                vtimes = valid_times[ftime:]
                for t in itime_exclude:
                    t_adjust = t + dt.timedelta(hours=ftime)
                    if t_adjust in vtimes:
                        vtimes.remove(t_adjust)
                for t in vtime_exclude:
                    if t in vtimes:
                        vtimes.remove(t)
                _ = mp.plot_sfc_timeseries(input_sims_sfc, vtimes, 
                                           fcst_lead=ftime, 
                                           file_prefix=file_prefix,
                                           line_type=plot_dict[plot_var]['line_type'],
                                           plot_var=plot_var,
                                           plot_lvl=plot_dict[plot_var]['sfc_plot_lvl'],
                                           plot_stat=plot_stat,
                                           ob_subset=ob_subset,
                                           toggle_pts=False,
                                           out_tag=out_tag,
                                           verbose=True)
                plt.close()

        # Upper-air verification   
        for ob_subset in plot_dict[plot_var]['ua_ob_subset']:
            input_sims_ua = copy.deepcopy(sim_dict)
            for key in input_sims_ua:
                input_sims_ua[key]['dir'] = input_sims_ua[key]['dir'].format(typ=verif_type, subtyp='upper_air')
            for lvl in plot_dict[plot_var]['ua_plot_lvl']:
                _ = mp.plot_sfc_dieoff(input_sims_ua, valid_times_ua, 
                                       fcst_lead=fcst_lead_dieoff, 
                                       file_prefix=file_prefix,
                                       line_type=plot_dict[plot_var]['line_type'],
                                       plot_var=plot_var,
                                       plot_lvl=lvl,
                                       plot_stat=plot_stat,
                                       ob_subset=ob_subset,
                                       toggle_pts=True,
                                       out_tag=out_tag,
                                       verbose=False)
                plt.close()
            for ftime in fcst_lead_other:
                _ = mp.plot_ua_vprof(input_sims_ua, valid_times_ua, 
                                     fcst_lead=ftime, 
                                     file_prefix=file_prefix,
                                     line_type=plot_dict[plot_var]['line_type'],
                                     plot_var=plot_var,
                                     plot_stat=plot_stat,
                                     ob_subset=ob_subset,
                                     toggle_pts=True,
                                     out_tag=out_tag,
                                     exclude_plvl=[],
                                     verbose=False)
                plt.close()
                vtimes = valid_times_ua
                for t in itime_exclude:
                    t_adjust = t + dt.timedelta(hours=ftime)
                    if t_adjust in vtimes:
                        vtimes.remove(t_adjust)
                for t in vtime_exclude:
                    if t in vtimes:
                        vtimes.remove(t)
                for lvl in plot_dict[plot_var]['ua_plot_lvl']:
                    _ = mp.plot_sfc_timeseries(input_sims_ua, vtimes, 
                                               fcst_lead=ftime, 
                                               file_prefix=file_prefix,
                                               line_type=plot_dict[plot_var]['line_type'],
                                               plot_var=plot_var,
                                               plot_lvl=lvl,
                                               plot_stat=plot_stat,
                                               ob_subset=ob_subset,
                                               toggle_pts=False,
                                               out_tag=out_tag,
                                               verbose=True)
                plt.close()

os.system('mv *.png {d}/'.format(d=out_dir))

# Save code version information
os.system('git log | head -n 8 >> {d}/code_version.txt'.format(d=out_dir))
os.system('git status >> {d}/code_version.txt'.format(d=out_dir))


"""
End plot_driver.py
"""
