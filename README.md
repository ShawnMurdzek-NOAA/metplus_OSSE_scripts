# Scripts for running METplus

METplus is a wrapper for the Model Evaluation Tools (MET) package. MET is a very comprehensive model verification package that can handle many different kind of verification. The scripts in this repository only support a small subset of all the tools available in MET.

## Contents

- `utils`: Directory containing scripts for plotting and analyzing METplus output.
- `metplus_orion.env`: File containing the METplus environment.
- `PB2NC.conf`: Configuration file for the PB2NC tool, which converts prepBUFR files to netCDF files that can be used by MET. 
- `run_metplus.sh`: Main driver to run METplus.
- `smurdzek_orion.conf`: Configuration file containing the input and output directories.

## Assumptions

It is assumed that the user is performing verification on MSU's Orion machine. Other machines can be used, but the environment would need to be modified and METplus would need to be installed if it is not already. A list of machines that already have METplus installed can be found [here](https://dtcenter.org/community-code/metplus/metplus-5-0-existing-builds).

It is also assumed that the observations are originally in prepBUFR format and that the forecasts are grib2 files in UPP format.

## Running the METplus

1. Copy `run_metplus.sh`, `metplus_orion.env`, `smurdzek_orion.conf`, and the desired MET tool configuration file (e.g., `PB2NC.conf`) to your run directory.
2. Edit `smurdzek_orion.conf` to have the proper input and output directories.
3. Edit `run_metplus.sh` to include the proper MET tool configuration file.
4. Edit the MET tool configuration file.
5. Run using `sbatch run_metplus.sh`. Note that this script handles setting up the environment.
6. Use the scripts in `utils` to analyze output.

NOTE: To run PointStat, obs must first be converted from prepBUFR to netCDF using PB2NC. 

## Useful Documentation

[MET](https://met.readthedocs.io/en/latest/index.html): Includes in-depth details about all the various options for the MET tools.
[METplus](https://metplus.readthedocs.io/en/latest/index.html): Includes information about the METplus wrapper options, but the user will need to refer to the MET documentation for details.
