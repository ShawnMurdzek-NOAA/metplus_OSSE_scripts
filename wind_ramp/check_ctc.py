
import xarray as xr
import numpy as np

#---------------------------------------------------------------------------------------------------
# Compute contingency table counts using raw inputs
#---------------------------------------------------------------------------------------------------

ds_NR_0 = xr.open_dataset('wrfprs_202204300000_er.grib2', engine='pynio')
ds_NR_1 = xr.open_dataset('wrfprs_202204300100_er.grib2', engine='pynio')
ds_RRFS_0 = xr.open_dataset('rrfs.t00z.prslev.f000.conus_3km.grib2', engine='pynio')
ds_RRFS_1 = xr.open_dataset('rrfs.t00z.prslev.f001.conus_3km.grib2', engine='pynio')

wspd_NR_0 = np.sqrt(ds_NR_0['UGRD_P0_L103_GLC0'][1, 2::3, 2::3].values**2 + 
                    ds_NR_0['VGRD_P0_L103_GLC0'][1, 2::3, 2::3].values**2)
wspd_NR_1 = np.sqrt(ds_NR_1['UGRD_P0_L103_GLC0'][1, 2::3, 2::3].values**2 + 
                    ds_NR_1['VGRD_P0_L103_GLC0'][1, 2::3, 2::3].values**2)
wspd_RRFS_0 = np.sqrt(ds_RRFS_0['UGRD_P0_L103_GLC0'][3, :, :].values**2 + 
                      ds_RRFS_0['VGRD_P0_L103_GLC0'][3, :, :].values**2)
wspd_RRFS_1 = np.sqrt(ds_RRFS_1['UGRD_P0_L103_GLC0'][3, :, :].values**2 + 
                      ds_RRFS_1['VGRD_P0_L103_GLC0'][3, :, :].values**2)

diff_w_NR = wspd_NR_1 - wspd_NR_0
diff_w_RRFS = wspd_RRFS_1 - wspd_RRFS_0

diff_w_gt3_NR = diff_w_NR > 3
diff_w_gt3_RRFS = diff_w_RRFS > 3

print()
print(f"FY_OY = {np.sum(diff_w_gt3_NR * diff_w_gt3_RRFS)}")
print(f"FY_ON = {np.sum(np.logical_not(diff_w_gt3_NR) * diff_w_gt3_RRFS)}")
print(f"FN_OY = {np.sum(diff_w_gt3_NR * np.logical_not(diff_w_gt3_RRFS))}")
print(f"FN_ON = {np.sum(np.logical_not(diff_w_gt3_NR) * np.logical_not(diff_w_gt3_RRFS))}")


#---------------------------------------------------------------------------------------------------
# Compare raw inputs to intermediate files
#---------------------------------------------------------------------------------------------------

uv_NR_ds_0 = xr.open_dataset('./output/uv80m_0.grib2', engine='pynio')
uv_NR_ds_1 = xr.open_dataset('./output/uv80m_1.grib2', engine='pynio')
wspd_NR_ds_0 = xr.open_dataset('./output/wspd80m_0.grib2', engine='pynio')
wspd_NR_ds_1 = xr.open_dataset('./output/wspd80m_1.grib2', engine='pynio')
diff_NR_ds_1 = xr.open_dataset('./output/wspd80m_diff_1.nc')

uv_RRFS_ds_0 = xr.open_dataset('./output/uv80m_fcst_0.grib2', engine='pynio')
uv_RRFS_ds_1 = xr.open_dataset('./output/uv80m_fcst_1.grib2', engine='pynio')
wspd_RRFS_ds_0 = xr.open_dataset('./output/wspd80m_fcst_0.grib2', engine='pynio')
wspd_RRFS_ds_1 = xr.open_dataset('./output/wspd80m_fcst_1.grib2', engine='pynio')
diff_RRFS_ds_1 = xr.open_dataset('./output/wspd80m_fcst_diff_1.nc')

# Compare U and V from extracted GRIB2 file
print()
print(f"NR 0 U RMSD = {np.sqrt(np.mean((ds_NR_0['UGRD_P0_L103_GLC0'][1, :, :].values - uv_NR_ds_0['UGRD_P0_L103_GLC0'][:, :].values)**2))}")
print(f"NR 0 V RMSD = {np.sqrt(np.mean((ds_NR_0['VGRD_P0_L103_GLC0'][1, :, :].values - uv_NR_ds_0['VGRD_P0_L103_GLC0'][:, :].values)**2))}")

# Compare WSPD from extracted GRIB2 file
print()
print(f"NR 0 WSPD RMSD = {np.sqrt(np.mean((wspd_NR_0 - wspd_NR_ds_0['WIND_P0_L103_GLC0'][2::3, 2::3].values)**2))}")
print(f"RRFS 0 WSPD RMSD = {np.sqrt(np.mean((wspd_RRFS_0 - wspd_RRFS_ds_0['WIND_P0_L103_GLC0'].values)**2))}")

# Compute contingency table counts with intermediate WSPD files
diff_w_NR_i1 = wspd_NR_ds_1['WIND_P0_L103_GLC0'][2::3, 2::3].values - wspd_NR_ds_0['WIND_P0_L103_GLC0'][2::3, 2::3].values
diff_w_RRFS_i1 = wspd_RRFS_ds_1['WIND_P0_L103_GLC0'].values - wspd_RRFS_ds_0['WIND_P0_L103_GLC0'].values
diff_w_gt3_NR_i1 = diff_w_NR_i1 > 3
diff_w_gt3_RRFS_i1 = diff_w_RRFS_i1 > 3
print()
print(f"FY_OY = {np.sum(diff_w_gt3_NR_i1 * diff_w_gt3_RRFS_i1)}")
print(f"FY_ON = {np.sum(np.logical_not(diff_w_gt3_NR_i1) * diff_w_gt3_RRFS_i1)}")
print(f"FN_OY = {np.sum(diff_w_gt3_NR_i1 * np.logical_not(diff_w_gt3_RRFS_i1))}")
print(f"FN_ON = {np.sum(np.logical_not(diff_w_gt3_NR_i1) * np.logical_not(diff_w_gt3_RRFS_i1))}")
