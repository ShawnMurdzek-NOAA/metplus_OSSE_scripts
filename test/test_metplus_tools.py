"""
Tests for metplus_tools.py

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import pytest
import yaml
import pandas as pd
import os
import glob

import metplus_OSSE_scripts.plotting.metplus_tools as mt


#---------------------------------------------------------------------------------------------------
# Tests
#---------------------------------------------------------------------------------------------------

class TestMETtools():

    @pytest.fixture(scope='class')
    def sample_ua_met(self):
    
        # Check that upper-air MET output directory isn't empty
        pwd = os.getcwd()
        ua_output_dir = f'{pwd}/cases/truth/upper_air/output/GridStat/'
        contents = os.listdir(ua_output_dir)
        if len(contents) == 0:
            print('Upper air MET output directory is empty!')

        # Create list of filenames
        fnames = glob.glob(f"{ua_output_dir}/*sl1l2.txt")

        # Read in MET output
        return mt.read_ascii(fnames)
    

    @pytest.fixture(scope='class')
    def sample_ua_uas_met(self):
    
        pwd = os.getcwd()
        ua_uas_output_dir = f'{pwd}/cases/truth/upper_air_uas/output/GridStat/'
        return mt.read_ascii(glob.glob(f"{ua_uas_output_dir}/*sl1l2.txt"))


    def test_subset_verif_df(self, sample_ua_met):
        cond = [{'FCST_LEAD': 0},
                {'FCST_VAR': 'TMP'},
                {'FCST_LEAD':0, 'FCST_VAR':'TMP'}]
        for d in cond:
            subset = mt.subset_verif_df(sample_ua_met, d)
            for key in d.keys():
                assert np.all(subset[key] == d[key])


    def test_compute_stats_diff(self, sample_ua_met, sample_ua_uas_met):
        diff_df = mt.compute_stats_diff(sample_ua_met, sample_ua_uas_met)
        diff_df2 = mt.compute_stats_diff(sample_ua_uas_met, sample_ua_met)

        # Compute RMSE diffs offline
        ua_met_stats = mt.compute_stats(sample_ua_met)
        ua_uas_subset = mt.subset_verif_df(sample_ua_uas_met, {'VX_MASK':'FULL'})
        ua_uas_met_stats = mt.compute_stats(ua_uas_subset)
        RMSE_diff = ua_met_stats['RMSE'].values - ua_uas_met_stats['RMSE'].values
        RMSE_diff2 = ua_uas_met_stats['RMSE'].values - ua_met_stats['RMSE'].values

        assert np.all(np.abs(diff_df['RMSE'].values - RMSE_diff) < 1e-6)
        assert np.all(np.abs(diff_df2['RMSE'].values - RMSE_diff2) < 1e-6)


"""
End test_metplus_tools.py
"""
