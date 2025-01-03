#!/bin/sh

#SBATCH -A wrfruc
#SBATCH -t 08:00:00
#SBATCH --ntasks=1
#SBATCH --partition=orion

machine=orion
src_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts
work_dir=`pwd`

date

cd ${src_dir}
git log | head -n 8 >> ${work_dir}/code_version.txt
git status >> ${work_dir}/code_version.txt
cd ${work_dir}

source ${src_dir}/env/py_${machine}.env
cp ${src_dir}/plotting/plot_driver.py .
python plot_driver.py plot_param.yml
python plot_driver.py plot_param_precip.yml

date
