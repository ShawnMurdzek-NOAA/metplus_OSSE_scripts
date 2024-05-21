#!/bin/sh

#SBATCH -A wrfruc
#SBATCH -t 08:00:00
#SBATCH --ntasks=1
#SBATCH --partition={PARTITION}

date

machine={MACHINE}
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts  # Path to metplus_OSSE_scripts
in_files=(`cat in_files.txt`)
out_files=(`cat out_files.txt`)

for i in ${!in_files[@]}; do

  echo
  echo "======================================"
  echo "input file = ${in_files[i]}"

  # Run regrid_data_plane
  source ${script_dir}/env/metplus_${machine}.env
  regrid_data_plane -v 10 -method NEAREST -width 1 \
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
  #cp ${out_files[i]} ${out_files[i]}_ORIGINAL
  conda deactivate
  source ${script_dir}/env/py_${machine}.env
  python ${script_dir}/ceil/compute_ceil_agl_MET.py ${out_files[i]}

done
date
