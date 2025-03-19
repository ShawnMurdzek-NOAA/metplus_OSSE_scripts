"""
Create MET Masks for Pressure Levels Beneath the Surface

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import sys
import argparse
import copy
import datetime as dt
import xarray as xr
import numpy as np


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

    parser = argparse.ArgumentParser(description='This script creates masks for the MET \
                                                  verification package that mask gridpoints on a \
                                                  given pressure level that have at least one time \
                                                  step where the pressure level lies beneath the \
                                                  surface.')
    
    # Positional arguments
    parser.add_argument('input_files', 
                        help='Text file containing the names of the pressure-level output files \
                              used to create the MET masks. Output files should be in UPP GRIB \
                              format and all contain the same number of pressure levels.',
                        type=str)
    
    parser.add_argument('baseline_mask', 
                        help='MET mask netCDF file. The new masks will be the intersection of this \
                              mask and the gridpoints with heights that lie above the surface.',
                        type=str)

    # Optional arguments
    parser.add_argument('-v',
                        dest='verbose',
                        default=0,
                        help='Verbosity level. Increasing the level increases the amount of output \
                              printed to the screen.',
                        type=int)

    parser.add_argument('--hgt',
                        dest='hgt_field',
                        default='HGT_P0_L100_GLC0',
                        help='Input field that corresponds to the height of the pressure level.',
                        type=str)

    parser.add_argument('--sfc',
                        dest='sfc_field',
                        default='HGT_P0_L1_GLC0',
                        help='Input field that corresponds to the surface elevation.',
                        type=str)

    parser.add_argument('--basename',
                        dest='baseline_name',
                        default='shape_mask',
                        help='Name of the baseline mask field in the baseline_mask file.',
                        type=str)

    return parser.parse_args(argv)


def create_below_sfc_mask(param):
    """
    Create masks for each pressure level with gridpoints below the surface masked

    """

    # Get list of input files
    with open(param.input_files, 'r') as fptr:
        in_files = fptr.readlines()
    if param.verbose > 0: print(f"Number of input files = {len(in_files)}")

    # Read in first file and create initial masks
    # We assume that the first dimension of hgt_field is pressure (should always be the case for 
    # UPP output)
    if param.verbose > 0: print(f"Iterating over {in_files[0].strip()}")
    ds = xr.open_dataset(in_files[0].strip(), engine='pynio')
    prs1d = ds[ds[param.hgt_field].dims[0]].values
    sfc = ds[param.sfc_field].values
    if param.verbose > 0: print(f"Number of pressure levels = {len(prs1d)}")
    mask_dict = {}
    for i, prs in enumerate(prs1d):
        mask_dict[int(prs)] = ds[param.hgt_field][i, :, :].values > sfc

    # Loop over remaining input files
    if len(in_files) > 1:
        for f in in_files[1:]:
            if param.verbose > 0: print(f"Iterating over {f.strip()}")
            ds = xr.open_dataset(f.strip(), engine='pynio')
            for j, prs in enumerate(mask_dict.keys()):
                mask_dict[prs] = np.logical_and(mask_dict[prs], 
                                                ds[param.hgt_field][j, :, :].values > sfc)

    return mask_dict


def blend_save_mask(mask_dict, param):
    """
    Blend mask in mask_dict with the baseline mask and save output

    """

    # Read baseline mask
    base_mask = xr.open_dataset(param.baseline_mask)
    if param.verbose > 1: print(f"Baseline mask has {np.sum(base_mask[param.baseline_name].values)}" +
                                f" of {base_mask[param.baseline_name].size} grid points unmasked")

    # Blend and save mask
    for key in mask_dict.keys():
        if param.verbose > 1: print(f"{key} mask has {np.sum(mask_dict[key])} of" +
                                    f" {mask_dict[key].size} grid points unmasked prior to blending" +
                                     " with baseline mask")
        field = f"P{key}_mask"
        out_mask = copy.deepcopy(base_mask)
        out_mask = out_mask.rename({param.baseline_name:field})
        out_mask[field].attrs['long_name'] = f"{field} masking region"
        out_mask[field].values = np.int64(out_mask[field].values * mask_dict[key])
        out_mask.to_netcdf(f"{field}.nc")

    return None


if __name__ == '__main__':

    start = dt.datetime.now()
    print('Starting create_below_sfc_mask.py')
    print(f"Time = {start.strftime('%Y%m%d %H:%M:%S')}\n")

    # Read in input parameters
    param = parse_in_args(sys.argv[1:])

    # Create masks using pressure level heights
    mask_dict = create_below_sfc_mask(param)

    # Blend masks with the baseline mask and save output
    _ = blend_save_mask(mask_dict, param)

    print('\nProgram Finished!')
    print(f"Elapsed time = {(dt.datetime.now() - start).total_seconds()} s")


"""
End create_below_sfc_mask.py
"""
