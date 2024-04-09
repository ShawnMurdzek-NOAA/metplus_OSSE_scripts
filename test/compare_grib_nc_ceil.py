"""
Compare Ceilings from Input GRIB Files and Output NetCDF Files

Command-Line Arguments
----------------------
    argv[1] : Input GRIB file
    argv[2] : Output netCDF file

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import xarray as xr
import netCDF4 as nc
import numpy as np
import sys


#---------------------------------------------------------------------------------------------------
# Compare Ceiling Fields
#---------------------------------------------------------------------------------------------------

err = 0
ds_grib = xr.open_dataset(sys.argv[1], engine='pynio')
nc_fptr = nc.Dataset(sys.argv[2])

# Check that terrain fields match
terrain_rmsd = np.sqrt(np.mean((ds_grib['HGT_P0_L1_GLC0'].values - 
                                nc_fptr['TERRAIN_HGT'][:, :])**2))
print(f'Terrain RMSD = {terrain_rmsd}')
if not np.isclose(terrain_rmsd, 0):
    err = 1

# Check that ceiling fields are similar
maxdiff_thres = 75
rmsd_thres = 12
ceil_fields = {'CEIL_LEGACY':'HGT_P0_L215_GLC0',
               'CEIL_EXP1':'CEIL_P0_L215_GLC0',
               'CEIL_EXP2':'CEIL_P0_L2_GLC0'}

for key in ceil_fields:
    ceil_grib_asl = ds_grib[ceil_fields[key]].values
    ceil_grib_asl[np.isclose(ceil_grib_asl, 2e4)] = np.nan
    ceil_grib = ceil_grib_asl - ds_grib['HGT_P0_L1_GLC0'].values
    ceil_grib[np.isnan(ceil_grib)] = 2e4
    diff = ceil_grib - nc_fptr[key][:, :].data
    maxdiff = np.amax(np.abs(diff))
    rmsd = np.sqrt(np.mean(diff**2))
    
    print()
    print(key)
    print(f'maxdiff = {maxdiff}')
    print(f'RMSD = {rmsd}')

    if maxdiff >= maxdiff_thres:
        err = 2
    if rmsd >= rmsd_thres:
        err = 3
    if not np.all(np.isclose(ceil_grib, 2e4) == np.isclose(nc_fptr[key][:, :].data, 2e4)):
        print('"no ceiling" obs do not match')
        err = 4

print()
print(err)


"""
End compare_grib_nc_ceil.py
"""
