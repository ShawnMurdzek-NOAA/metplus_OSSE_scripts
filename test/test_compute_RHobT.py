"""
Tests for RHobT/compute_RHobT.py

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import pytest
import pygrib as pyg
import metpy.calc as mc
from metpy.units import units
from argparse import Namespace

import metplus_OSSE_scripts.RHobT.compute_RHobT as RHobT


#---------------------------------------------------------------------------------------------------
# Tests
#---------------------------------------------------------------------------------------------------

class TestRHobT():

    @pytest.fixture(scope='class')
    def sample_RRFS_namespace(self):

        param = Namespace(NR_fname='data/NR_TMP_202204300000.grib2',
                          fcst_fname='data/RRFS_2022043000_f000.grib2',
                          out_fname='tmp.grib2',
                          verbose=1)

        return param
    

    @pytest.fixture(scope='class')
    def sample_HRRR_namespace(self):

        param = Namespace(NR_fname='data/NR_TMP_202204300000.grib2',
                          fcst_fname='data/HRRR_2022043000_f000.grib2',
                          out_fname='tmp.grib2',
                          verbose=1)

        return param

   
    def test_compute_RHobT(self, sample_RRFS_namespace, sample_HRRR_namespace):

        for param, atol, name in zip([sample_RRFS_namespace, sample_HRRR_namespace], 
                                     [1, 0.3],
                                     ['RRFS', 'HRRR']):

            # Compute RHobT
            out_grbs = RHobT.compute_RHobT(param)

            # Re-open input files
            NR_grbs = pyg.open(param.NR_fname)
            fcst_grbs = pyg.open(param.fcst_fname)

            # Compute RHobT. Note that the NR grid is identical to the forecast grid when subsampled,
            # which should give us the same result as the nearest neighbor interpolation performed
            # in compute_RHobT
            for g in out_grbs:
                lvl = g.level
                T = NR_grbs.select(name='Temperature', level=lvl, typeOfLevel='isobaricInhPa')[0].values[2::3, 2::3]
                Q = fcst_grbs.select(name='Specific humidity', level=lvl, typeOfLevel='isobaricInhPa')[0].values
                RH = mc.relative_humidity_from_specific_humidity(lvl * units.hPa,
                                                                 T * units.K,
                                                                 Q).to('percent').magnitude

                print(f"Max absolute diff for {name} = {np.amax(np.abs(RH - g.values))}")
                assert np.all(np.isclose(RH, g.values, atol=atol))

                # Also ensure that we did indeed change the RH
                RH_original = fcst_grbs.select(name='Relative humidity', level=lvl, typeOfLevel='isobaricInhPa')[0].values
                assert np.amax(np.abs(g.values - RH_original)) > 10
            

"""
End test_compute_RHobT.py
"""
