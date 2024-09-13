# Scripts for running METplus

METplus is a wrapper for the Model Evaluation Tools (MET) package. MET is a very comprehensive model verification package that can handle many different kind of verification. The scripts in this repository only support a small subset of all the tools available in MET.

## Contents

- `ceil/`: Directory containing various scripts for ceiling verification.
- `env/`: Directory containing various environment-related files. When porting to a new machine, only files in here should need to be changed.
- `plotting/`: Directory containing various plotting scripts. For plotting, it is recommended to use `plotting/plot_driver.py` with a YAML file similar to `plotting/plot_param_SAMPLE.yml`.
- `severe_wx_env/`: Directory containing various scripts for severe weather environment verification (i.e., verification of CAPE, CIN, SRH, etc when MUCAPE > 50 J/kg).
- `test/`: Directory containing various tests for the METplus helper functions.
- `utils/`: Directory containing various scripts that might be helpful.
- `make_submit_metplus_jobs.sh`: Helper script to make METplus configuration files and submit job scripts. A new set of configuration files and job scripts is created every 12 hours in model time. These jobs should be small enough to finish within the maximum allowed walltime (8 hours).
- `run_metplus.sh`: Main driver to run METplus.

## Supported Machines

Only the following machines are currently supported:

- Orion (MSU)
- Hercules (MSU)

Other machines can be used, but METplus would need to be installed if it is not already and various machine-specific files would need to be added to `env/`. A list of machines that already have METplus installed can be found [here](https://dtcenter.org/community-code/metplus/metplus-5-0-existing-builds).

## Assumptions

It is assumed that the observations are originally in prepBUFR format and that the forecasts are grib2 files in UPP format.

## Running METplus

### General Instructions

#### Option 1

1. Create a landmask using `utils/create_gen_vx_landmask_from_NR.sh`.
2. Copy `run_metplus.sh`, `metplus_orion.env`, `smurdzek_orion.conf`, and the desired MET tool configuration file (e.g., `PB2NC.conf`) to your run directory.
3. Edit `smurdzek_orion.conf` to have the proper input and output directories.
4. Edit `run_metplus.sh` to include the proper MET tool configuration file.
5. Edit the MET tool configuration file.
6. Run using `sbatch run_metplus.sh`. Note that this script handles setting up the environment.
7. For GridStat verification, the `utils/link_GridStat_output.sh` script needs to be run before plotting to put the MET output files in the expected directory structure.
8. Create plots using `plotting/plot_driver.py`, which uses a YAML input file (see `test/cases/plots/*/plot_param.yml` for examples). Note that precipitation verification cannot be plotted for hour 0, so it is recommended that a separate YAML input file be used for precip verification.

#### Option 2 (preferred option)

1. Create a landmask using `utils/create_gen_vx_landmask_from_NR.sh`.
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
- `GridStat_lower_atm.conf`: Upper-air grid-to-grid verification using the GridStat tool. Verification statistics are generated for T, Q, and winds every 25 hPa between 1000 and 600 hPa.
- `GridStat_precip_radar.conf`: Grid-to-grid verification using the GridStat tool for 1-hr precipitation totals and composite reflectivity. Verification uses contingency table metrics with various thresholds.
- `GridStat_sfc.conf`: Surface grid-to-grid verification using the GridStat tool. Verification statistics are generated for 2-m T, 2-m Q, and 10-m winds.
- `GridStat_ua.conf`: Upper-air grid-to-grid verification using the GridStat tool. Verification statistics are generated for T, Q, and winds at mandatory pressure levels between 1000 and 100 hPa.
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

1. Use `severe_wx_env/make_input_run_preprocess_severe_NR.sh` to create the MUCAPE mask from the nature run output. This will likely require copying the script to your work directory, editing the top portion, and running.
2. Use `make_submit_metplus_jobs.sh` to run the severe weather environment verification (template: `severe_wx_env/GridStat_severe_wx_env.conf`). These steps are the same as "Option 2" in the "General Instructions" section above. Note that this configuration file uses GRIB records to extract various severe weather fields, and that these records might change depending on the UPP version being used.

## Useful Documentation

- [MET](https://met.readthedocs.io/en/latest/index.html): Includes in-depth details about all the various options for the MET tools.  
- [METplus](https://metplus.readthedocs.io/en/latest/index.html): Includes information about the METplus wrapper options, but the user will need to refer to the MET documentation for details.
