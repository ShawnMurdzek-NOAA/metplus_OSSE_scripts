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
    def sample_ua_met_sl1l2(self):
    
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
    def sample_ua_uas_met_sl1l2(self):
    
        pwd = os.getcwd()
        ua_uas_output_dir = f'{pwd}/cases/truth/upper_air_uas/output/GridStat/'
        return mt.read_ascii(glob.glob(f"{ua_uas_output_dir}/*sl1l2.txt"))


    def test_subset_verif_df(self, sample_ua_met_sl1l2):
        cond = [{'FCST_LEAD': 0},
                {'FCST_VAR': 'TMP'},
                {'FCST_LEAD':0, 'FCST_VAR':'TMP'}]
        for d in cond:
            subset = mt.subset_verif_df(sample_ua_met_sl1l2, d)
            for key in d.keys():
                assert np.all(subset[key] == d[key])


    def test_compute_stats_sl1l2(self, sample_ua_met_sl1l2):
        ua_met_stats = mt.compute_stats(sample_ua_met_sl1l2)

        # Check that all statistics are computed and that the original DataFrame is not altered
        for stat in ['MSE', 'RMSE', 'BIAS_RATIO', 'BIAS_DIFF']:
            assert stat in ua_met_stats.columns
            assert stat not in sample_ua_met_sl1l2


    def test_compute_stats_diff(self, sample_ua_met_sl1l2, sample_ua_uas_met_sl1l2):
        diff_df = mt.compute_stats_diff(sample_ua_met_sl1l2, sample_ua_uas_met_sl1l2)
        diff_df2 = mt.compute_stats_diff(sample_ua_uas_met_sl1l2, sample_ua_met_sl1l2)

        # Compute RMSE diffs offline
        ua_met_stats = mt.compute_stats(sample_ua_met_sl1l2)
        ua_uas_subset = mt.subset_verif_df(sample_ua_uas_met_sl1l2, {'VX_MASK':'FULL'})
        ua_uas_met_stats = mt.compute_stats(ua_uas_subset)
        RMSE_diff = ua_met_stats['RMSE'].values - ua_uas_met_stats['RMSE'].values
        RMSE_diff2 = ua_uas_met_stats['RMSE'].values - ua_met_stats['RMSE'].values

        assert np.all(np.abs(diff_df['RMSE'].values - RMSE_diff) < 1e-6)
        assert np.all(np.abs(diff_df2['RMSE'].values - RMSE_diff2) < 1e-6)

    
    def test_compute_stats_entire_df(self, sample_ua_met_sl1l2):

        # Only retain 0-hr TMP forecasts
        ua_subset = mt.subset_verif_df(sample_ua_met_sl1l2, 
                                       {'FCST_VAR':'TMP', 'FCST_LEAD':0})

        # Compute mean RMSE using compute_stats_entire_df
        # Turn on confidence intervals just to see if they run w/out error
        stat_df = mt.compute_stats_entire_df(ua_subset,
                                             verif_df2=None,
                                             line_type='sl1l2',
                                             agg=False,
                                             ci=True,
                                             ci_lvl=0.95,
                                             ci_opt='t_dist',
                                             ci_kw={})

        # Compute mean RMSE offline
        ua_met_stats = mt.compute_stats(ua_subset)
        mean_RMSE = np.mean(ua_met_stats['RMSE'].values)

        assert np.isclose(mean_RMSE, stat_df['RMSE']) 


    def test_compute_stats_entire_df_diff(self, sample_ua_met_sl1l2, sample_ua_uas_met_sl1l2):

        # Only retain 0-hr TMP forecasts
        ua_subset = mt.subset_verif_df(sample_ua_met_sl1l2, 
                                       {'FCST_VAR':'TMP', 'FCST_LEAD':0})
        ua_uas_subset = mt.subset_verif_df(sample_ua_uas_met_sl1l2, 
                                           {'FCST_VAR':'TMP', 'FCST_LEAD':0, 'VX_MASK':'FULL'})

        # Compute mean RMSE diff using compute_stats_entire_df
        # Turn on confidence intervals just to see if they run w/out error
        stat_df = mt.compute_stats_entire_df(ua_subset,
                                             verif_df2=ua_uas_subset,
                                             line_type='sl1l2',
                                             agg=False,
                                             diff_kw={'var':['RMSE']},
                                             ci=True,
                                             ci_lvl=0.95,
                                             ci_opt='t_dist',
                                             ci_kw={})

        # Compute mean RMSE diff offline
        ua_met_stats = mt.compute_stats(ua_subset)
        ua_uas_met_stats = mt.compute_stats(ua_uas_subset)
        mean_RMSE_diff = (np.mean(ua_met_stats['RMSE'].values) - 
                          np.mean(ua_uas_met_stats['RMSE'].values))

        assert np.isclose(mean_RMSE_diff, stat_df['RMSE']) 


    def test_compute_stats_entire_df_agg(self, sample_ua_met_sl1l2):

        # Only retain 0-hr TMP forecasts
        ua_subset = mt.subset_verif_df(sample_ua_met_sl1l2, 
                                       {'FCST_VAR':'TMP', 'FCST_LEAD':0})

        # Compute mean RMSE using compute_stats_entire_df
        stat_df = mt.compute_stats_entire_df(ua_subset,
                                             verif_df2=None,
                                             line_type='sl1l2',
                                             agg=True,
                                             ci=False)

        # Compute aggregate RMSE offline
        tot = np.sum(ua_subset['TOTAL'].values)
        FFBAR = np.sum(ua_subset['FFBAR'].values * ua_subset['TOTAL'].values) / tot
        FOBAR = np.sum(ua_subset['FOBAR'].values * ua_subset['TOTAL'].values) / tot
        OOBAR = np.sum(ua_subset['OOBAR'].values * ua_subset['TOTAL'].values) / tot
        agg_RMSE = np.sqrt(FFBAR - 2*FOBAR + OOBAR)

        assert np.isclose(agg_RMSE, stat_df['RMSE']) 


"""
End test_metplus_tools.py
"""
