"""
Compute Cloud Ceilings AGL for MET-style NetCDF Files

Passed Arguments
----------------
    argv[1] : Input MET netCDF file

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import netCDF4 as nc
import numpy as np
import metpy.calc as mc
from metpy.units import units
import metpy.constants as const
import sys
import datetime as dt


#--------------------------------------------------------------------------------------------------
# Main Code
#--------------------------------------------------------------------------------------------------

def parse_inputs(argv):
    in_fname = sys.argv[1]

    print(f'Input fname: {in_fname}')

    return in_fname


def convert_ceil_agl(nc_fptr, no_ceil=2e4):

    # Field names
    ceil_fields = ['CEIL_LEGACY', 'CEIL_EXP1', 'CEIL_EXP2']
    terrain_field = 'TERRAIN_HGT'

    # Extract terrain
    terrain = fptr.variables[terrain_field][:, :].copy()
    np.ma.set_fill_value(terrain, np.nan)
    terrain = terrain.filled()

    # Convert to height AGL
    for f in ceil_fields:
        try:
            ceil_asl = fptr.variables[f][:, :].copy()
            fill = ceil_asl.fill_value
            ceil_mask = ceil_asl.mask

            # MetPy cannot handle masked arrays, so set masked values to NaN
            # These NaNs represent "no ceiling" forecasts, so set 2e4 to NaN as well
            np.ma.set_fill_value(ceil_asl, np.nan)
            ceil_asl_filled = ceil_asl.filled()
            ceil_asl_filled[np.isclose(ceil_asl_filled, 2e4)] = np.nan

            ceil = (mc.geopotential_to_height(ceil_asl_filled * units.m * const.g).magnitude - 
                    mc.geopotential_to_height(terrain * units.m * const.g).magnitude)
            #ceil = ceil_asl - terrain

            ceil[np.isnan(ceil)] = no_ceil
            new_ceil = np.ma.masked_array(ceil, np.zeros(ceil.shape))
            np.ma.set_fill_value(new_ceil, fill)

            fptr.variables[f][:, :] = new_ceil
            fptr.variables[f].units = 'm AGL'
        except KeyError:
            print(f'Field {f} not in dataset. Skipping.')

    return nc_fptr


if __name__ == '__main__':
    start = dt.datetime.now()
    print(start)
    in_fname = parse_inputs(sys.argv)
    fptr = nc.Dataset(in_fname, mode='r+')
    fptr = convert_ceil_agl(fptr)
    fptr.close()
    print('elapsed time = {t} s'.format(t=(dt.datetime.now() - start).total_seconds()))


"""
End compute_ceil_agl_MET.py
"""
