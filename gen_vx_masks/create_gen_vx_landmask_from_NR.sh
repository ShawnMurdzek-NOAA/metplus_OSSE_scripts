#!/bin/sh

#SBATCH -A rtrr
#SBATCH -t 00:15:00
#SBATCH --ntasks=1
#SBATCH --partition=hercules

machine=hercules
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts  # Path to metplus_OSSE_scripts
in_files=(/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP/20220501/wrfprs_202205010000_er.grib2)
out_files=(NR_landmask.nc)

date

for i in ${!in_files[@]}; do

  echo
  echo "======================================"
  echo "input file = ${in_files[i]}"

  # Run gen_vx_mask
  source ${script_dir}/env/metplus_${machine}.env
  gen_vx_mask \
    ${in_files[i]} \
    ${in_files[i]} \
    ${out_files[i]} \
    -type data \
    -mask_field 'name="LAND"; level="R653";' \
    -thresh 'gt0.5'

done

date
