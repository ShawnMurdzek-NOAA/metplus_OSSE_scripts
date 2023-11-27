#!/bin/sh

#SBATCH -A rtrr
#SBATCH -t 08:00:00
#SBATCH --ntasks=1
#SBATCH --partition=orion

date

source ./metplus_orion.env
run_metplus.py \
    -c {CONF_FILE} \
    -c {USER_FILE}

date
