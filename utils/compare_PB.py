"""
Compare MET PB2NC Output to prepBUFR_decoder Output

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime as dt

import pyDA_utils.bufr as bufr


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

pb_nc_fname = '/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts/real_data_pt_ob_verif/PB2NC/output/pb2nc/2022020100_rap.nc'
pb_csv_fname = '/work2/noaa/wrfruc/murdzek/nature_run_winter/obs/perfect_conv_v2/real_csv/202202010000.rap.prepbufr.csv'


#---------------------------------------------------------------------------------------------------
# Compare Decoded PrepBUFR Files
#---------------------------------------------------------------------------------------------------

pb_nc = xr.open_dataset(pb_nc_fname)
pb_csv = bufr.bufrCSV(pb_csv_fname).df
cycletime = dt.datetime.strptime(str(pb_csv['cycletime'].values[0]), '%Y%m%d%H')

# Convert prepBUFR netCDF to a DataFrame
# While this seemed like a good idea, there are some bugs. It would be better to loop over all the
# obs rather than all the headers b/c some headers can contain multiple levels, which should be
# assigned multiple rows in the DataFrame.
'''
print('Converting NetCDF DataSet to a Pandas DataFrame')
var_names = {'SPFH':'QOB', 'TMP':'TOB', 'UGRD':'UOB', 'VGRD':'VOB', 'HGT':'ZOB'}
var_qm = {'SPFH':'QQM', 'TMP':'TQM', 'UGRD':'WQM', 'VGRD':'WQM', 'HGT':'ZQM'}
pb_nc_dict = {}
pb_nc_dict['SID'] = pb_nc['hdr_sid_table'].values[np.int64(pb_nc['hdr_sid'].values)]
pb_nc_dict['subset'] = pb_nc['hdr_typ_table'].values[np.int64(pb_nc['hdr_typ'].values)]
pb_nc_dict['XOB'] = pb_nc['hdr_lon'].values
pb_nc_dict['YOB'] = pb_nc['hdr_lat'].values
pb_nc_dict['ELV'] = pb_nc['hdr_elv'].values
pb_nc_dict['TYP'] = pb_nc['hdr_prpt_typ'].values
pb_nc_dict['cycletime'] = np.ones(len(pb_nc_dict['SID']), dtype=int) * pb_csv['cycletime'].values[0]

tmp_dhr = pb_nc['hdr_vld_table'].values[np.int64(pb_nc['hdr_vld'].values)]
pb_nc_dict['DHR'] = np.zeros(len(tmp_dhr))
for i, t in enumerate(tmp_dhr):
    pb_nc_dict['DHR'][i] = (dt.datetime.strptime(str(t)[2:-1], '%Y%m%d_%H%M%S') - cycletime).total_seconds() / 3600.

for col in ['POB', 'QOB', 'TOB', 'ZOB', 'UOB', 'VOB', 'PWO', 'QQM', 'TQM', 'ZQM', 'WQM']:
    pb_nc_dict[col] = np.zeros(len(pb_nc['nhdr'])) * np.nan

for i in range(len(pb_nc['nobs'])):
    obs_var = str(pb_nc['obs_var'].values[int(pb_nc['obs_vid'].values[i])])[2:-1]
    ihdr = int(pb_nc['obs_hid'].values[i])
    pb_nc_dict['POB'][ihdr] = pb_nc['obs_lvl'].values[i]
    if obs_var in var_names.keys():
        pb_nc_dict[var_names[obs_var]][ihdr] = pb_nc['obs_val'].values[i]
        pb_nc_dict[var_qm[obs_var]][ihdr] = pb_nc['obs_qty_table'].values[int(pb_nc['obs_qty'].values[i])]

pb_nc_dict['QOB'] = pb_nc_dict['QOB'] * 1e6
pb_nc_dict['TOB'] = pb_nc_dict['TOB'] - 273.15
pb_nc_df = pd.DataFrame(pb_nc_dict)
pb_nc_df = bufr.match_bufr_prec(pb_nc_df)
'''

# Compute DHRs for pb_nc
tmp_dhr = pb_nc['hdr_vld_table'].values[np.int64(pb_nc['hdr_vld'].values)]
nc_DHR = np.zeros(len(tmp_dhr))
for i, t in enumerate(tmp_dhr):
    nc_DHR[i] = (dt.datetime.strptime(str(t)[2:-1], '%Y%m%d_%H%M%S') - cycletime).total_seconds() / 3600.

# Compute differences
print('Computing Differences')
diffs = {}
varlist = ['TOB', 'QOB', 'ZOB', 'UOB', 'VOB']
var_names = {'SPFH':'QOB', 'TMP':'TOB', 'UGRD':'UOB', 'VGRD':'VOB', 'HGT':'ZOB'}
for key in varlist:
    diffs[key] = []
for i, s_raw in enumerate(pb_nc['hdr_sid_table'].values[:20]):
    print(i)
    sid = str(s_raw)[2:-1]
    hdr_idx = np.where(pb_nc['hdr_sid'].values == i)[0]
    for ihdr in hdr_idx:
        ob_idx = np.where(pb_nc['obs_hid'].values == ihdr)[0]
        for iob in ob_idx:
            try:
                var = var_names[str(pb_nc['obs_var'].values[int(pb_nc['obs_vid'].values[iob])])[2:-1]]
            except KeyError:
                continue
            icsv = np.where((pb_csv['DHR'] == nc_DHR[ihdr]) & (pb_csv['SID'] == sid) & 
                            np.isclose(pb_csv['POB'], pb_nc['obs_lvl'].values[iob]) & 
                            (pb_csv['TYP'] == pb_nc['hdr_prpt_typ'].values[ihdr]))[0]
            if len(icsv) > 1:
                print('icsv is not unique!')
            if var == 'TOB':
                diffs[var].append((pb_nc['obs_val'].values[iob] - 273.15) - pb_csv[var][icsv[0]])
            elif var == 'QOB':
                diffs[var].append((pb_nc['obs_val'].values[iob] * 1e6) - pb_csv[var][icsv[0]])
            else:
                diffs[var].append(pb_nc['obs_val'].values[iob] - pb_csv[var][icsv[0]])

#for i in range(len(pb_nc_df)):
#for i in range(10000):
#    if (i % 500 == 0):
#        print(i)
#        print(dt.datetime.now())
#    try:
#        icsv = np.where((pb_csv['DHR'] == pb_nc_df['DHR'][i]) & (pb_csv['SID'] == str(pb_nc_df['SID'][i])[2:-1]) & 
#                        (pb_csv['POB'] == pb_nc_df['POB'][i]) & (pb_csv['TYP'] == pb_nc_df['TYP'][i]))[0][0]
#    except IndexError:
#        continue
#    for key in varlist:
#        diffs[key][i] = pb_csv[key][icsv] - pb_nc_df[key][i]

for key in varlist:
    diffs[key] = np.array(diffs[key])
    rmsd = np.sqrt(np.nanmean(diffs[key]**2))
    print('%s RMSD = %.2f' % (key, rmsd))


"""
End compare_PB.py 
"""
