#!/bin/sh

#SBATCH -A {ALLOCATION}
#SBATCH -t 08:00:00
#SBATCH --ntasks=1
#SBATCH --partition={PARTITION}

date

source {ENV_FILE}
run_metplus.py \
    -c {CONF_FILE} \
    -c {USER_FILE}

date
