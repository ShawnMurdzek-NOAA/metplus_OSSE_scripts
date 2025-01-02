#!/bin/sh

#SBATCH -A rtrr
#SBATCH -t 01:00:00
#SBATCH --ntasks=1
#SBATCH --partition=orion

machine=orion
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts  # Path to metplus_OSSE_scripts
shapefile=/home/smurdzek/.local/share/cartopy/shapefiles/natural_earth/cultural/ne_50m_admin_0_countries.shp
shape_num=16
in_files=(/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP/20220501/wrfprs_202205010000_er.grib2)
out_files=(NR_USAmask.nc)

date

for i in ${!in_files[@]}; do

  echo
  echo "======================================"
  echo "input file = ${in_files[i]}"

  # Run gen_vx_mask
  source ${script_dir}/env/metplus_${machine}.env
  gen_vx_mask \
    ${in_files[i]} \
    ${shapefile} \
    ${out_files[i]} \
    -type shape \
    -shapeno ${shape_num}

done

date
