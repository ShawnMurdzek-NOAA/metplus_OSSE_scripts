"""
Compute RHobT and Save to a Separate GRIB File

Owing to odd behavior with pygrib and the forecast output GRIB files, RH values are only precise 
within 1%

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import pygrib as pyg
import metpy.calc as mc
from metpy.units import units
import scipy.interpolate as si
import datetime as dt
import sys
import argparse


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

def parse_in_args(argv):
    """
    Parse input arguments

    Parameters
    ----------
    argv : list
        Command-line arguments from sys.argv[1:]
    
    Returns
    -------
    Namespace data structure

    """

    parser = argparse.ArgumentParser(description='This script computes RHobT (relative humidity \
                                                  using the observed temperature and forecasted \
                                                  specific humidity) and saves the output to a \
                                                  separate GRIB file.')
    
    # Positional arguments
    parser.add_argument('NR_fname', 
                        help='GRIB file containing the nature run output. The temperature values \
                              are used from this file (must have units of K).',
                        type=str)
    
    parser.add_argument('fcst_fname', 
                        help='GRIB file containing the forecast output. The specific humidity \
                              values are used from this file (must have units of kg / kg).',
                        type=str)

    parser.add_argument('out_fname', 
                        help='Output GRIB file. RHobT will be on the same grid as fcst_fname.',
                        type=str)

    # Optional arguments
    parser.add_argument('-v',
                        dest='verbose',
                        default=0,
                        help='Verbosity level. Increasing the level increases the amount of output \
                              printed to the screen.',
                        type=int)

    return parser.parse_args(argv)


def compute_RHobT(param):
    """
    Compute RHobT on the forecast model grid

    Parameters
    ----------
    param : Namespace data structure
        Input parameters

    Returns
    -------
    out_grbs : list
        List of output GRIB messages with RHobT values

    """

    # Open GRIB files
    if param.verbose > 0: print('Opening files')
    NR_all_grbs = pyg.open(param.NR_fname)
    fcst_all_grbs = pyg.open(param.fcst_fname)

    # Extract grid information (needed for interpolation later on)
    NR_lat, NR_lon = NR_all_grbs.message(1).latlons()
    fcst_lat, fcst_lon = fcst_all_grbs.message(1).latlons()

    # Compute RHobT
    out_grbs = []
    NR_T_grbs = NR_all_grbs.select(name='Temperature', typeOfLevel='isobaricInhPa')
    NR_lvl = np.array([grb.level for grb in NR_T_grbs])
    fcst_RH_grbs = fcst_all_grbs.select(name='Relative humidity', typeOfLevel='isobaricInhPa')
    for grb in fcst_RH_grbs:
        lvl = grb.level
        if lvl in NR_lvl:

            if param.verbose > 0: print(f'Computing RHobT for {lvl} hPa')

            # Determine matching pressure index for NR, then create nearest neighbor interpolator
            NR_idx = np.where(lvl == NR_lvl)[0][0]
            T_NR = NR_T_grbs[NR_idx].values
            interp = si.NearestNDInterpolator(list(zip(np.ravel(NR_lon), np.ravel(NR_lat))), np.ravel(T_NR))
            T = interp(fcst_lon, fcst_lat) * units.K

            # Compute RH with MetPy
            q = fcst_all_grbs.select(name='Specific humidity', typeOfLevel='isobaricInhPa', level=lvl)[0].values
            p = lvl * units.hPa
            RH = mc.relative_humidity_from_specific_humidity(p, T, q).to('percent').magnitude
            grb.values = RH

            out_grbs.append(grb)

    # Close forecast and NR files
    NR_all_grbs.close()
    fcst_all_grbs.close()

    return out_grbs


def write_RHobT(param, out_grbs):
    """
    Write RHobT values to output GRIB file

    Parameters
    ----------
    param : Namespace data structure
        Input parameters
    out_grbs : list
        List of output GRIB messages with RHobT values
        
    Returns
    -------
    None

    """

    if param.verbose > 0: print('Writing output GRIB file')
    out_fptr = open(param.out_fname, 'wb')
    for grb in out_grbs:
        out_fptr.write(grb.tostring())

    return None


if __name__ == '__main__':

    start = dt.datetime.now()
    print('\nStarting compute_RHobT.py')
    print(f"Time = {start.strftime('%Y%m%d %H:%M:%S')}\n")

    # Read in input parameters
    param = parse_in_args(sys.argv[1:])

    # Compute RHobT
    out_grbs = compute_RHobT(param)

    # Write to output file
    _ = write_RHobT(param, out_grbs)

    print('\nProgram finished!')
    print(f"Elapsed time = {(dt.datetime.now() - start).total_seconds()} s\n")


"""
End compute_RHobT.py
"""
