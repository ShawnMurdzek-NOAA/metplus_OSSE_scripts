"""
Quickly Check CTC Stats

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import xarray as xr
import numpy as np


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

obs_file = '/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP/20220430/wrfprs_202204300100_er.grib2'
fcst_file = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/syn_data_rrfs-workflow_orion/spring_uas_150km/NCO_dirs/ptmp/prod/rrfs.20220430/00/rrfs.t00z.prslev.f001.conus_3km.grib2'
field = 'REFC_P0_L200_GLC0'
thres = 20
comparison = 'gt'


#---------------------------------------------------------------------------------------------------
# Compute CTC Stats
#---------------------------------------------------------------------------------------------------

ds_obs = xr.open_dataset(obs_file, engine='pynio')
ds_fcst = xr.open_dataset(fcst_file, engine='pynio')

# These indices work when comparing the NR to RRFS
obs_field = ds_obs[field][2::3, 2::3].values
fcst_field = ds_fcst[field].values

if comparison == 'gt':
    obs_bool = obs_field > thres
    fcst_bool = fcst_field > thres
elif comparison == 'ge':
    obs_bool = obs_field >= thres
    fcst_bool = fcst_field >= thres
elif comparison == 'lt':
    obs_bool = obs_field < thres
    fcst_bool = fcst_field < thres
elif comparison == 'le':
    obs_bool = obs_field <= thres
    fcst_bool = fcst_field <= thres

print(field)
print(f"{np.size(obs_bool)} {np.sum(obs_bool * fcst_bool)} {np.sum(~obs_bool * fcst_bool)} {np.sum(obs_bool * ~fcst_bool)} {np.sum(~obs_bool * ~fcst_bool)}")


"""
End check_CTC_stats.py
"""
