# Scripts for running METplus

METplus is a wrapper for the Model Evaluation Tools (MET) package. MET is a very comprehensive model verification package that can handle many different kind of verification. The scripts in this repository only support a small subset of all the tools available in MET.

## Contents

- `utils`: Directory containing scripts for plotting and analyzing METplus output.
- `GridStat_sfc.conf`: Configuration file for surface grid-to-grid verification using the GridStat tool. Verification statistics are generated for 2-m T, 2-m Q, and 10-m winds.
- `GridStat_ua.conf`: Configuration file for upper-air grid-to-grid verification using the GridStat tool. Verification statistics are generated for T, Q, and winds at mandatory pressure levels between 1000 and 100 hPa.
- `make_submit_metplus_jobs.sh`: Helper script to make METplus configuration files and submit job scripts for the GridStat tool. A new set of configuration files and job scripts is created every 12 hours in model time. These jobs should be small enough to finish within the maximum allowed walltime (8 hours).
- `metplus_orion.env`: File containing the METplus environment.
- `PB2NC.conf`: Configuration file for the PB2NC tool, which converts prepBUFR files to netCDF files that can be used by MET. 
- `PointStat_sfc.conf`: Configuration file for surface verification using the PointStat tool. Verification statistics are generated for 2-m T, 2-m Q, and 10-m winds. Both ADPSFC and SFCSHP platforms are used. 
- `PointStat_ua.conf`: Configuration file for upper-air verification using the PointStat tool. Verification statistics are generated for T, Q, and winds at mandatory pressure lebels between 1000 and 100 hPa. Only the ADPUPA platforms is used. 
- `run_metplus.sh`: Main driver to run METplus.
- `smurdzek_orion.conf`: Configuration file containing the input and output directories.

## Assumptions

It is assumed that the user is performing verification on MSU's Orion machine. Other machines can be used, but the environment would need to be modified and METplus would need to be installed if it is not already. A list of machines that already have METplus installed can be found [here](https://dtcenter.org/community-code/metplus/metplus-5-0-existing-builds).

It is also assumed that the observations are originally in prepBUFR format and that the forecasts are grib2 files in UPP format.

## Running the METplus

### Option 1

1. Copy `run_metplus.sh`, `metplus_orion.env`, `smurdzek_orion.conf`, and the desired MET tool configuration file (e.g., `PB2NC.conf`) to your run directory.
2. Edit `smurdzek_orion.conf` to have the proper input and output directories.
3. Edit `run_metplus.sh` to include the proper MET tool configuration file.
4. Edit the MET tool configuration file.
5. Run using `sbatch run_metplus.sh`. Note that this script handles setting up the environment.
6. Use the scripts in `utils` to analyze output.

### Option 2 (preferred for grid-to-grid verification)

1. Copy `make_submit_metplus_jobs.sh` to your run directory.
2. Edit `make_submit_metplus_jobs.sh`. Only the section above the horizontal line should need editing.
3. Run using `bash make_submit_metplus_jobs.sh`. This will create the configuration files for METplus and submit the slurm jobs.

NOTE: To run PointStat, obs must first be converted from prepBUFR to netCDF using PB2NC. 

## Useful Documentation

- [MET](https://met.readthedocs.io/en/latest/index.html): Includes in-depth details about all the various options for the MET tools.  
- [METplus](https://metplus.readthedocs.io/en/latest/index.html): Includes information about the METplus wrapper options, but the user will need to refer to the MET documentation for details.
