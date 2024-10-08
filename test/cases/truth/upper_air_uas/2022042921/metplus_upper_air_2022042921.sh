#!/bin/sh

#SBATCH -A rtrr
#SBATCH -t 08:00:00
#SBATCH --ntasks=1
#SBATCH --partition=hercules

date

source ./metplus_hercules.env
run_metplus.py \
    -c ./GridStat_upper_air.conf \
    -c ./user.conf

date
