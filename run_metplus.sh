#!/bin/sh

#SBATCH -A rtrr
#SBATCH -t 03:00:00
#SBATCH --ntasks=1
#SBATCH --partition=orion

date

source ./metplus_orion.env
run_metplus.py \
    -c ./PB2NC.conf \
    -c ./smurdzek_orion.conf

date
