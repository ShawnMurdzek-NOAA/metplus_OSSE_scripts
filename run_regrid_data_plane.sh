#!/bin/sh

#SBATCH -A wrfruc
#SBATCH -t 00:20:00
#SBATCH --ntasks=1
#SBATCH --partition=orion

date

machine=orion
in_files=(`cat in_files.txt`)
out_files=(`cat out_files.txt`)

for i in ${!in_files[@]}; do

  echo
  echo "======================================"
  echo "input file = ${in_files[i]}"

  # Run regrid_data_plane
  source ./metplus_${machine}.env
  /apps/contrib/MET/11.0.1/bin/regrid_data_plane -v 10 -method NEAREST -width 1 \
    -field 'name="HGT"; level="L0"; GRIB_lvl_typ=215;' \
    -field 'name="CEIL"; level="L0"; GRIB_lvl_typ=215;' \
    -field 'name="CEIL"; level="L0"; GRIB_lvl_typ=2;' \
    -field 'name="HGT"; level="L0"; GRIB_lvl_typ=1;' \
    -name CEIL_LEGACY,CEIL_EXP1,CEIL_EXP2,TERRAIN_HGT \
    ${in_files[i]} "${in_files[i]}" ${out_files[i]}

  # Convert ceilings to height AGL
  echo
  echo "---------------------------------"
  echo "Converting ceilings to height AGL"
  cp ${out_files[i]} ${out_files[i]}_ORIGINAL
  source ./py_${machine}.env
  python /work2/noaa/wrfruc/murdzek/metplus_TEST/regrid_output/compute_ceil_agl_MET.py ${out_files[i]}

done
date