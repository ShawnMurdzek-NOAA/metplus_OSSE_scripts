"""
Preprocess ADPUPA Obs in Synthetic prepBUFR CSV Files Prior to Running PB2NC

This script is needed b/c when performing upper-air verification with METplus, the obs pressure
must perfectly match the desired pressure level for verification (i.e., there is no interpolation
of the obs to the desired pressure level). Thus, even if the pressure level if off by a fraction
of an hPa, it is omitted from verification.

During the synthetic obs generation process, some of the pressure values were alterd by 0.1 hPa
owing to rounding. This is obviously not a big deal for DA, but it prevents the obs from being used
in METplus for verification. This script undoes this rounding so that the obs can be used for 
verification.

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import glob
import datetime as dt

import pyDA_utils.bufr as bufr


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input prepBUFR CSV files
#in_fnames = glob.glob('/work2/noaa/wrfruc/murdzek/nature_run_winter/obs/corr_errors_1st_iter_v2/err_csv/*.rap.fake.prepbufr.csv')
in_fnames = glob.glob('/work2/noaa/wrfruc/murdzek/nature_run_spring/obs/corr_errors/err_csv/*.rap.fake.prepbufr.csv')

# Output prepBUFR CSV files
out_fnames = []
#out_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/syn_obs_with_errors/winter/obs_csv/'
out_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/syn_obs_with_errors/spring/obs_csv/'
for f in in_fnames:
    out_fnames.append('%s/%s' % (out_dir, f.split('/')[-1]))

# Pressure levels to undo rounding for (hPa)
prslev = [1000, 925, 850, 700, 500, 400, 300, 250, 200, 150, 100]

# Tolerance (pressure values within <tolerance> hPa of <prslev> will be changed to <prslev>)
tolerance = 0.101


#---------------------------------------------------------------------------------------------------
# Preprocess Obs
#---------------------------------------------------------------------------------------------------

start = dt.datetime.now()
print('start time = ', start)

for i, (in_f, out_f) in enumerate(zip(in_fnames, out_fnames)):
    print('(%d of %d): Processing file %s' % (i+1, len(in_fnames), in_f))
    csv_df = bufr.bufrCSV(in_f).df
    for p in prslev:
        idx = ((csv_df['subset'] == 'ADPUPA') & (csv_df['POB'] >= (p - tolerance)) & 
               (csv_df['POB'] <= (p + tolerance)))
        csv_df.loc[idx, 'POB'] = p
    bufr.df_to_csv(csv_df, out_f)

end = dt.datetime.now()
print('elapse time = %.2f min' % ((end - start).total_seconds() / 60.))


"""
End preprocess_syn_ADPUPA_obs.py
"""
