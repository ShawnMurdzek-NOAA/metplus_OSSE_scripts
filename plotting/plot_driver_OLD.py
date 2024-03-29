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

# Dictionary of simulation information. First set of keys is the season. Second set of keys are tags 
# for the output files. Third set are the labels for the legends of the plot. Each season will be 
# placed in a separate directory
parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion'
sim_dict = {}
#for season in ['spring', 'winter']:
for season in ['spring']:
    sim_dict[season] = {}
    for sim_type in ['syn_data', 'real_red_data']:
        sim_dict[season][sim_type] = {}
        for exp, c in zip(['ctrl', 'no_aircft', 'no_raob', 'no_sfc'], ['r', 'b', 'orange', 'gray']):
            sim_dict[season][sim_type][exp] = {'dir':'%s/sims_%s/%s_%s' % (parent_dir, sim_type, season, exp),
                                               'color':c}
            if exp == 'ctrl':
                sim_dict[season][sim_type][exp]['dir'] = '%s/sims_%s/%s' % (parent_dir, sim_type, season)
    sim_dict[season]['ctrl'] = {}
    for exp, c in zip(['real_red_data', 'syn_data'], ['r', 'b']):
        sim_dict[season]['ctrl'][exp] = {'color':c}
        sim_dict[season]['ctrl'][exp]['dir'] = '%s/sims_%s/%s' % (parent_dir, exp, season)

sim_dict = {'winter':
               {'check_wind_rot':
                   {'syn_data_rot_perf':
                       {'color':'b',
                        'dir':'/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion/sims_syn_data/winter_tune_oberr_noGVF'},
                    'syn_data_unrot_err':
                       {'color':'g',
                        'dir':'/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion_OLD/syn_data_sims/winter_updated'},
                    'real_red':
                       {'color':'r',
                        'dir':'/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion/sims_real_red_data/winter'}}}}

sim_dict = {'winter':
               {'compare_real':
                    {'real':
                       {'color':'b',
                        'dir':'/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion/sims_real_data/winter'},
                     'real_prepbufr_decoder':
                       {'color':'r',
                        'dir':'/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion/sims_real_data/winter_prepbufr_decoder'}}}}

# Verification type ('point_stat' or 'GridStat')
verif_type = 'point_stat'
file_prefix = 'point_stat'

# Valid times and forecast lead times
valid_times = {'winter':[dt.datetime(2022, 2, 1, 9) + dt.timedelta(hours=i) for i in range(7)],
               'spring':[dt.datetime(2022, 4, 29, 21) + dt.timedelta(hours=i) for i in range(36)]}
valid_times_ua = {'winter':[dt.datetime(2022, 2, 1, 12) + dt.timedelta(hours=i) for i in range(0, 36, 12)],
                  'spring':[dt.datetime(2022, 4, 30, 0) + dt.timedelta(hours=i) for i in range(0, 36, 12)]}
fcst_lead_dieoff = [0, 1]
fcst_lead_other = [0, 1]

# Initial times to exclude (usually owing to missing forecast data)
itime_exclude = {'winter': [dt.datetime(2022, 2, 1, 17),
                            dt.datetime(2022, 2, 1, 18), 
                            dt.datetime(2022, 2, 1, 22), 
                            dt.datetime(2022, 2, 2, 14), 
                            dt.datetime(2022, 2, 2, 15),
                            dt.datetime(2022, 2, 2, 19),
                            dt.datetime(2022, 2, 2, 20),
                            dt.datetime(2022, 2, 2, 21)],
                 'spring': []}

# Valid times to exclude (usually owing to missing obs data)
vtime_exclude = {'winter': [],
                 'spring': []}

# Dictionary of plotting information. Program will loop over each variable (first set of keys), each
# statistic ('plot_stat' key) and each ob_subset ('sfc_ob_subset' and 'ua_ob_subset'). For 
# grid-to-grid verification, the ob_subset should be ['NR'].
plot_dict = {'TMP':{'line_type':'sl1l2',
                    'sfc_plot_lvl':'Z2',
                    'sfc_ob_subset':['ADPSFC'],
                    'ua_plot_lvl':['P500'],
                    'ua_ob_subset':['ADPUPA'],
                    'plot_stat':['RMSE', 'TOTAL', 'BIAS_DIFF']},
             'SPFH':{'line_type':'sl1l2',
                     'sfc_plot_lvl':'Z2',
                     'sfc_ob_subset':['ADPSFC'],
                     'ua_plot_lvl':['P500'],
                     'ua_ob_subset':['ADPUPA'],
                     'plot_stat':['RMSE', 'TOTAL', 'BIAS_DIFF']}, 
             'UGRD_VGRD':{'line_type':'vl1l2',
                          'sfc_plot_lvl':'Z10',
                          'sfc_ob_subset':['ADPSFC'],
                          'ua_plot_lvl':['P500', 'P250'],
                          'ua_ob_subset':['ADPUPA'],
                          'plot_stat':['VECT_RMSE', 'TOTAL', 'MAG_BIAS_DIFF']}}


#---------------------------------------------------------------------------------------------------
# Create Plots
#---------------------------------------------------------------------------------------------------

for season in sim_dict.keys():
    for sim_set in sim_dict[season].keys():
        os.system('mkdir -p %s/%s/%s' % (season, sim_set, verif_type))
        for plot_var in plot_dict.keys():
            for plot_stat in plot_dict[plot_var]['plot_stat']:
                print('creating plots for %s %s %s %s' % (season, sim_set, plot_var, plot_stat))

                # Surface verification
                for ob_subset in plot_dict[plot_var]['sfc_ob_subset']:
                    input_sims_sfc = copy.deepcopy(sim_dict[season][sim_set])
                    for key in input_sims_sfc:
                        input_sims_sfc[key]['dir'] = input_sims_sfc[key]['dir'] + '/sfc/output/' + verif_type
                    _ = mp.plot_sfc_dieoff(input_sims_sfc, valid_times[season], 
                                           fcst_lead=fcst_lead_dieoff, 
                                           file_prefix=file_prefix,
                                           line_type=plot_dict[plot_var]['line_type'],
                                           plot_var=plot_var,
                                           plot_lvl=plot_dict[plot_var]['sfc_plot_lvl'],
                                           plot_stat=plot_stat,
                                           ob_subset=ob_subset,
                                           toggle_pts=True,
                                           out_tag=sim_set,
                                           verbose=False)
                    plt.close()
                    for ftime in fcst_lead_other:
                        vtimes = valid_times[season][ftime:]
                        for t in itime_exclude[season]:
                            t_adjust = t + dt.timedelta(hours=ftime)
                            if t_adjust in vtimes:
                                vtimes.remove(t_adjust)
                        for t in vtime_exclude[season]:
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
                                                   out_tag=sim_set,
                                                   verbose=True)
                        plt.close()

                # Upper-air verification   
                for ob_subset in plot_dict[plot_var]['ua_ob_subset']:
                    input_sims_ua = copy.deepcopy(sim_dict[season][sim_set])
                    for key in input_sims_ua:
                        input_sims_ua[key]['dir'] = input_sims_ua[key]['dir'] + '/upper_air/output/' + verif_type
                    for lvl in plot_dict[plot_var]['ua_plot_lvl']:
                        _ = mp.plot_sfc_dieoff(input_sims_ua, valid_times_ua[season], 
                                               fcst_lead=fcst_lead_dieoff, 
                                               file_prefix=file_prefix,
                                               line_type=plot_dict[plot_var]['line_type'],
                                               plot_var=plot_var,
                                               plot_lvl=lvl,
                                               plot_stat=plot_stat,
                                               ob_subset=ob_subset,
                                               toggle_pts=True,
                                               out_tag=sim_set,
                                               verbose=False)
                        plt.close()
                    for ftime in fcst_lead_other:
                        _ = mp.plot_ua_vprof(input_sims_ua, valid_times_ua[season], 
                                             fcst_lead=ftime, 
                                             file_prefix=file_prefix,
                                             line_type=plot_dict[plot_var]['line_type'],
                                             plot_var=plot_var,
                                             plot_stat=plot_stat,
                                             ob_subset=ob_subset,
                                             toggle_pts=True,
                                             out_tag=sim_set,
                                             exclude_plvl=[],
                                             verbose=False)
                        plt.close()
                        vtimes = valid_times_ua[season]
                        for t in itime_exclude[season]:
                            t_adjust = t + dt.timedelta(hours=ftime)
                            if t_adjust in vtimes:
                                vtimes.remove(t_adjust)
                        for t in vtime_exclude[season]:
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
                                                       out_tag=sim_set,
                                                       verbose=True)
                        plt.close()

        os.system('mv *%s*.png ./%s/%s/%s/' % (sim_set, season, sim_set, verif_type))


"""
End plot_driver.py
"""
