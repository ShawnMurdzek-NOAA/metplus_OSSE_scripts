#!/bin/sh

#SBATCH -A wrfruc
#SBATCH -t 08:00:00
#SBATCH --ntasks=1
#SBATCH --partition=orion

src_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts

date

source ${src_dir}/env/py_orion.env
cp ${src_dir}/plotting/plot_driver.py .
python plot_driver.py plot_param.yml

date
