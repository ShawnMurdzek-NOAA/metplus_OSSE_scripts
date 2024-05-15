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
yaml_name = '/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts/test/cases/plots/upper_air/plot_param.yml'
with open(yaml_name, 'r') as fptr:
    param = yaml.safe_load(fptr)

# Read in parameters
sim_dict = param['sim_dict']
verif_type = param['verif_type']
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
ci_kw = param['ci_kw']
plot_dict = param['plot_dict']
fcst_lead_dieoff = param['fcst_lead_dieoff']
fcst_lead_other = param['fcst_lead_other']

# Create lists of valid times
valid_times = [valid_time_start + dt.timedelta(hours=i) 
               for i in range(0, valid_time_end_hr, valid_time_step)]
valid_times_ua = [valid_time_ua_start + dt.timedelta(hours=i) 
                  for i in range(0, valid_time_ua_end_hr, valid_time_ua_step)]

# Change initial and exclude times to empty lists
if itime_exclude == [None]:
    itime_exclude = []
if vtime_exclude == [None]:
    vtime_exclude = []

# Change surface or upper-air verification to empty dictionaries if no entries
if plot_dict['surface'] == None:
    plot_dict['surface'] = {}
if plot_dict['upper_air'] == None:
    plot_dict['upper_air'] = {}


#---------------------------------------------------------------------------------------------------
# Create Plots
#---------------------------------------------------------------------------------------------------

# Surface verification
print()
print('Surface Verification')
print('--------------------')
for subtyp in plot_dict['surface'].keys():
    os.system(f'mkdir -p {out_dir}/{subtyp}')
    for plot_var in plot_dict['surface'][subtyp].keys():
        var_dict = plot_dict['surface'][subtyp][plot_var]
        for plot_stat in var_dict['plot_stat']:
            print(f'creating plots for {subtyp} {plot_var} {plot_stat}')
            if plot_stat in ['BIAS_DIFF', 'MAG_BIAS_DIFF']:
                var_dict['kwargs']['include_zero'] = False
            ci_kw_copy = ci_kw.copy()
            if plot_stat in ['TOTAL']:
                ci_kw_copy['ci'] = False
            input_sims_sfc = copy.deepcopy(sim_dict)
            for key in input_sims_sfc:
                input_sims_sfc[key]['dir'] = input_sims_sfc[key]['dir'].format(typ=verif_type, subtyp=subtyp)
            _ = mp.plot_sfc_dieoff(input_sims_sfc, valid_times, 
                                fcst_lead=fcst_lead_dieoff, 
                                plot_stat=plot_stat,
                                toggle_pts=True,
                                out_tag=out_tag,
                                verbose=False,
                                **var_dict['kwargs'],
                                **ci_kw_copy)
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
                                        plot_stat=plot_stat,
                                        toggle_pts=False,
                                        out_tag=out_tag,
                                        verbose=True,
                                        **var_dict['kwargs'])
                plt.close()
    os.system(f'mv *.png {out_dir}/{subtyp}/')

# Upper-air verification
print()
print('Upper-Air Verification')
print('----------------------')
for subtyp in plot_dict['upper_air'].keys():
    os.system(f'mkdir -p {out_dir}/{subtyp}')
    for plot_var in plot_dict['upper_air'][subtyp].keys():
        var_dict = plot_dict['upper_air'][subtyp][plot_var]
        var_dict_lvl = copy.deepcopy(plot_dict['upper_air'][subtyp][plot_var])
        for plot_stat in var_dict['plot_stat']:
            print(f'creating plots for {subtyp} {plot_var} {plot_stat}')
            if plot_stat in ['BIAS_DIFF', 'MAG_BIAS_DIFF']:
                var_dict['kwargs']['include_zero'] = False
            ci_kw_copy = ci_kw.copy()
            if plot_stat in ['TOTAL']:
                ci_kw_copy['ci'] = False
            input_sims_ua = copy.deepcopy(sim_dict)
            for key in input_sims_ua:
                input_sims_ua[key]['dir'] = input_sims_ua[key]['dir'].format(typ=verif_type, subtyp=subtyp)
            for lvl in var_dict['plot_lvl']:
                var_dict_lvl['kwargs']['plot_param']['FCST_LEV'] = lvl
                _ = mp.plot_sfc_dieoff(input_sims_ua, valid_times_ua, 
                                    fcst_lead=fcst_lead_dieoff, 
                                    plot_stat=plot_stat,
                                    toggle_pts=True,
                                    out_tag=out_tag,
                                    verbose=False,
                                    **var_dict_lvl['kwargs'],
                                    **ci_kw_copy)
                plt.close()
            for ftime in fcst_lead_other:
                _ = mp.plot_ua_vprof(input_sims_ua, valid_times_ua, 
                                    fcst_lead=ftime, 
                                    plot_stat=plot_stat,
                                    toggle_pts=True,
                                    out_tag=out_tag,
                                    exclude_plvl=[],
                                    verbose=False,
                                    ylim=var_dict['prs_limit'],
                                    **var_dict['kwargs'],
                                    **ci_kw_copy)
                plt.close()
                if valid_time_ua_step == 1:
                    vtimes = valid_times_ua[ftime:]
                else:
                    vtimes = valid_times_ua
                for t in itime_exclude:
                    t_adjust = t + dt.timedelta(hours=ftime)
                    if t_adjust in vtimes:
                        vtimes.remove(t_adjust)
                for t in vtime_exclude:
                    if t in vtimes:
                        vtimes.remove(t)
                for lvl in var_dict['plot_lvl']:
                    var_dict_lvl['kwargs']['plot_param']['FCST_LEV'] = lvl
                    _ = mp.plot_sfc_timeseries(input_sims_ua, vtimes, 
                                            fcst_lead=ftime, 
                                            plot_stat=plot_stat,
                                            toggle_pts=False,
                                            out_tag=out_tag,
                                            verbose=True,
                                            **var_dict_lvl['kwargs'])
                plt.close()
    os.system(f'mv *.png {out_dir}/{subtyp}/')

# Save code version information
os.system(f'git log | head -n 8 >> {out_dir}/code_version.txt')
os.system(f'git status >> {out_dir}/code_version.txt')


"""
End plot_driver.py
"""
