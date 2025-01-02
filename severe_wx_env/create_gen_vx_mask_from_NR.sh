#!/bin/sh

#SBATCH -A rtrr
#SBATCH -t 05:00:00
#SBATCH --ntasks=1
#SBATCH --partition=orion

machine=orion
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts  # Path to metplus_OSSE_scripts
init_mask_file=/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/NR_output/USA_mask/NR_USAmask.nc
in_files=(`cat in_files.txt`)
out_files=(`cat out_files.txt`)

date

for i in ${!in_files[@]}; do

  echo
  echo "======================================"
  echo "input file = ${in_files[i]}"

  # Run gen_vx_mask
  source ${script_dir}/env/metplus_${machine}.env
  gen_vx_mask \
    ${init_mask_file} \
    ${in_files[i]} \
    ${out_files[i]} \
    -type data \
    -mask_field 'name="CAPE"; level="R643";' \
    -thresh 'gt50' \
    -intersection
 
done

date
