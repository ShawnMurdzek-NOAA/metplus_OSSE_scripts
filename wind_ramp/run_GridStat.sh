#!/bin/sh

#SBATCH -A zrtrr
#SBATCH -t 08:00:00
#SBATCH --ntasks=1
#SBATCH --partition=hercules

date

source ../env/metplus_orion.env
run_metplus.py \
    -c ./GridStat_wind_ramp.conf \
    -c ./user.conf

date
