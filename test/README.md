# Tests for Various METplus Scripts

Note that we are no where near full test coverage. Tests included here include...

- `cases/`: Cases for testing METplus scripts and plotting scripts. Useful to check whether updating to a new version of MET or porting to a new machine changes the verification output. Also useful when developing new scripts or plotting capabilities.
- `run_ceil_preprocess_test.sh`: Test ceiling preprocess capabilities (conversion from GRIB to netCDF using RegridDataPlane and converting ceilings to m AGL using Python)
- `check_CTC_stats.py`: Quick script that computes contingency table (CTC) output for a single forecast time and a single threshold. Can be used to cross-check CTC output from MET. Helps ensure that METplus is grabbing the correct GRIB fields.
