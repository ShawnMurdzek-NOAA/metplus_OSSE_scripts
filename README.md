# Scripts for running METplus

METplus is a wrapper for the Model Evaluation Tools (MET) package. MET is a very comprehensive model verification package that can handle many different kind of verification. The scripts in this repository only support a small subset of all the tools available in MET.

## Contents

- `ceil/`: Directory containing various scripts for ceiling verification.
- `env/`: Directory containing various environment-related files. When porting to a new machine, only files in here should need to be changed.
- `gen_vx_masks/`: Directory containing scripts to create various masks (with the exception of the severe\_wx\_env mask).
- `plotting/`: Directory containing various plotting scripts. For plotting, it is recommended to use `plotting/plot_driver.py` with a YAML file similar to `plotting/plot_param_SAMPLE.yml`.
- `RHobT/`: Directory containing various script for computing and verifying RHobT.
- `severe_wx_env/`: Directory containing various scripts for severe weather environment verification (i.e., verification of CAPE, CIN, SRH, etc when MUCAPE > 50 J/kg).
- `test/`: Directory containing various tests for the METplus helper functions.
- `upper_air_with_mask/`: Directory containing configuration files and other scripts for upper-air and lower-atmosphere verification with pressure levels beneath the surface masked.
- `utils/`: Directory containing various scripts that might be helpful.
- `make_submit_metplus_jobs.sh`: Helper script to make METplus configuration files and submit job scripts. A new set of configuration files and job scripts is created every 12 hours in model time. These jobs should be small enough to finish within the maximum allowed walltime (8 hours).
- `run_metplus.sh`: Main driver to run METplus.

## Supported Machines

Only the following machines are currently supported:

- Orion (MSU HPC2)
- Hercules (MSU HPC2)

Other machines can be used, but METplus would need to be installed if it is not already and various machine-specific files would need to be added to `env/`. A list of machines that already have METplus installed can be found [here](https://dtcenter.org/community-code/metplus/metplus-5-0-existing-builds).

## Assumptions

It is assumed that the observations are originally in prepBUFR format and that the forecasts are grib2 files in UPP format.

### A Note Regarding Wind Vector Directions

Model output may contain either grid-relative or Earth-relative coordinates for vector winds. MET will automatically rotate forecast model winds from grid-relative to Earth-relative if needed as long as the forecast model output is in GRIB format (for more information, see this [discussion](https://github.com/dtcenter/METplus/discussions/2370)). To check whether grid-relative winds are being rotated properly, set `LOG_MET_VERBOSITY = 5` and check for the following line in the log files:

```
Rotating U and V wind components from grid-relative to earth-relative.
```

Keep in mind that MET DOES NOT automatically rotate winds in the "truth" dataset. So the nature run output used for verification must have Earth-relative winds. To check whether the winds in a GRIB file are grid-relative or Earth-relative, run the following command: `wgrib2 -vector_dir <fname>`. Earth-relative winds will appear as "winds(N/S)". The wgrib2 utility can be used to rotate winds so they are Earth-relative.

## Running METplus

### General Instructions

#### Option 1

1. Create a verification mask using one of the scripts in `gen_vx_masks`. You will likely need to edit the paths.
2. Copy `run_metplus.sh`, `metplus_orion.env`, `smurdzek_orion.conf`, and the desired MET tool configuration file (e.g., `PB2NC.conf`) to your run directory.
3. Edit `smurdzek_orion.conf` to have the proper input and output directories.
4. Edit `run_metplus.sh` to include the proper MET tool configuration file.
5. Edit the MET tool configuration file.
6. Run using `sbatch run_metplus.sh`. Note that this script handles setting up the environment.
7. For GridStat verification, the `utils/link_GridStat_output.sh` script needs to be run before plotting to put the MET output files in the expected directory structure.
8. Create plots using `plotting/plot_driver.py`, which uses a YAML input file (see `test/cases/plots/*/plot_param.yml` for examples). Note that precipitation verification cannot be plotted for hour 0, so it is recommended that a separate YAML input file be used for precip verification.

#### Option 2 (preferred option)

1. Create a verification mask using one of the scripts in `gen_vx_masks`. You will likely need to edit the paths.
2. Copy `make_submit_metplus_jobs.sh` to your run directory.
3. Edit `make_submit_metplus_jobs.sh`. Only the section above the horizontal line should need editing.
4. Run using `bash make_submit_metplus_jobs.sh`. This will create the configuration files for METplus and submit the slurm jobs.
5. For GridStat verification, the `utils/link_GridStat_output.sh` script needs to be run before plotting to put the MET output files in the expected directory structure.
6. Create plots using `plotting/plot_driver.py`, which uses a YAML input file (see `test/cases/plots/*/plot_param.yml` for examples). Note that precipitation verification cannot be plotted for hour 0, so it is recommended that a separate YAML input file be used for precip verification.

NOTE: To run PointStat, obs must first be converted from prepBUFR to netCDF using PB2NC. 

### Specific Instructions for Certain Verification Types

#### General Verification

For the following verification types, use the following configuration files (`.conf`) with the "general instructions" above:

- `GridStat_2D.conf`: Grid-to-grid verification using the GridStat tool for 80-m winds and PBL height.
- `GridStat_lower_atm.conf`: Upper-air grid-to-grid verification using the GridStat tool. Verification statistics are generated for T, Q, and winds every 25 hPa between 1000 and 600 hPa. Note that pressure levels beneath the surface are not masked.
- `GridStat_precip_radar.conf`: Grid-to-grid verification using the GridStat tool for 1-hr precipitation totals and composite reflectivity. Verification uses contingency table metrics with various thresholds.
- `GridStat_sfc.conf`: Surface grid-to-grid verification using the GridStat tool. Verification statistics are generated for 2-m T, 2-m Q, and 10-m winds.
- `GridStat_ua.conf`: Upper-air grid-to-grid verification using the GridStat tool. Verification statistics are generated for T, Q, and winds at mandatory pressure levels between 1000 and 100 hPa. Note that pressure levels beneath the surface are not masked.
- `PointStat_sfc.conf`: Surface verification using the PointStat tool. Verification statistics are generated for 2-m T, 2-m Q, and 10-m winds. Both ADPSFC and SFCSHP platforms are used. 
- `PointStat_ua.conf`: Upper-air verification using the PointStat tool. Verification statistics are generated for T, Q, and winds at mandatory pressure levels between 1000 and 100 hPa. Only the ADPUPA platforms is used.
- `PB2NC.conf`: Converts prepBUFR files to netCDF files that can be used by MET. Must be done prior to running any PointStat tool.

#### Ceiling Verification

Ceiling verification is a bit more convoluted than the verification types listed above. Ceilings must first be converted from gpm ASL (above sea level) to m AGL before running verification. Ceiling heights AGL are saved to a netCDF file the follows the MET conventions owing to the difficulties of modifying (or saving data to) GRIB files. This is a two-step process that involves converting the GRIB output to netCDF using RegridDataPlane and then using a Python script to convert ceilings from gpm ASL to m AGL. After this is finished, verification can be performed using MET. Generally, ceiling verification follows these steps:

1. Use `ceil/make_input_run_preprocess_ceil_NR.sh` to convert NR ceilings to m AGL. This will likely require copying the script to your work directory, editing the top portion, and running.
2. Use `ceil/make_input_run_preprocess_ceil_RRFS.sh` to convert RRFS ceilings to m AGL. This will likely require copying the script to your work directory, editing the top portion, and running.
3. Use `make_submit_metplus_jobs.sh` to run the ceiling verification (template: `ceil/GridStat_ceil.conf`). These steps are the same as "Option 2" in the "General Instructions" section above.

#### Severe Weather Environment Verification

Severe weather environment verification first requires the creation of mask using gen\_vx\_mask that identifies regions where MUCAPE > 50 J/kg in the nature run. This mask can then be used to perform GridStat verification only using regions where MUCAPE > 50 J/kg. The general steps for severe weather environment verification are as follows:

1. Create a base verification mask using one of the scripts in `gen_vx_masks`. You will likely need to edit the paths.
2. Use `severe_wx_env/make_input_run_preprocess_severe_NR.sh` to create the MUCAPE mask from the nature run output. This will likely require copying the script to your work directory, editing the top portion, and running.
3. Use `make_submit_metplus_jobs.sh` to run the severe weather environment verification (template: `severe_wx_env/GridStat_severe_wx_env.conf`). These steps are the same as "Option 2" in the "General Instructions" section above. Note that this configuration file uses GRIB records to extract various severe weather fields, and that these records might change depending on the UPP version being used.

#### Upper-Air and Lower-Atmosphere Verification with Pressure Levels Beneath the Surface Masked

By default, MET does not mask pressure levels that are beneath the surface. Adding in the capability is a bit clunky and requires a separate 2D mask for each pressure level considered by the verification. 

To create the masks, use the `create_below_sfc_mask.py` script. The `create_file_name_list.sh` script is useful for creating a text file with the list of nature run output files, which is required by `create_below_sfc_mask.py`. For the usage of `create_below_sfc_mask.py`, run `python create_below_sfc_mask.py -h`.

Once the masks are created, the `.conf` files in this directory can be used. Note that when using these configuration files, `{MASK_DIR}` must be replaced with the path leading to the masks. These configuration files also have a lot of variables in them (each pressure level and model variable combination is a separate variable for verification). This can be quite cumbersome to deal with, so the `write_FCST_OBS_fields.sh` script can be used to write the FCST and OBS field specifications to a text file, where they can then be copied into the METplus configuration files.

#### RHobT Verification

Most of the upper-air and lower_atm verification configuration files verify specific humidity as the moisture variable. The `RHobT` directory contains scripts that allow the user to verify RHobT (i.e., relative humidity computed using the temperature from the nature run and specific humidity from the forecast runs).

First, RHobT must be computed using a Python script (`RHobT/compute_RHobT.py`) that relies on pygrib instead of xarray for GRIB file manipulation (this is because pygrib can edit GRIB files whereas xarray can only read GRIB files). This script computes RHobT from nature run and forecast run GRIB output and saves RHobT to a separate GRIB file. This new GRIB file can then be used for verification. Computing RHobT for all pressure levels can be rather time consuming, so a Rocoto workflow is provided to automate the process. To run, copy `RHobT/preprocess_RHobT_EXAMPLE.xml` to your working directory, edit the variables in the workflow as needed, then run as a cron job.

Second, to perform verification, use the `RHobT/GridStat_RHobT.conf` configuration file (or something similar).

## Useful Documentation

- [MET](https://met.readthedocs.io/en/latest/index.html): Includes in-depth details about all the various options for the MET tools.  
- [METplus](https://metplus.readthedocs.io/en/latest/index.html): Includes information about the METplus wrapper options, but the user will need to refer to the MET documentation for details.
