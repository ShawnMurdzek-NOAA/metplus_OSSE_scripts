
# Make input and output file lists for RRFS output (each RRFS forecast length will have its own subdirectory)
# Submit ceiling preprocess jobs

machine=hercules
partition=${machine}

parentDIR=/work2/noaa/wrfruc/murdzek/HRRR_OSSE/hercules_test2/test/WRF_FCST_OSSE/run
fcst_len=(00 01 02 03 06 12)
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts  # Path to metplus_OSSE_scripts

in_fname='in_files.txt'
out_fname='out_files.txt'

for flen in ${fcst_len[@]}; do

  echo "creating and submitting ceiling preprocess job for forecast length ${flen}"

  # Make subdirectory if it doesn't exist
  out_dir=f${flen}h
  if [ ! -d ${out_dir} ]; then
    mkdir  ${out_dir}
  fi

  # Remove input and output files if they exist
  if [ -f ${out_dir}/${in_fname} ]; then
    rm ${out_dir}/${in_fname}
  fi
  if [ -f ${out_dir}/${out_fname} ]; then
    rm ${out_dir}/${out_fname}
  fi

  # Create input and output file lists
  subdir=(`ls ${parentDIR}`)
  for s in ${subdir[@]}; do
    if [ ${s:0:2} == '20' ]; then
      in_file=${parentDIR}/${s}/postprd/wrfprs_hrconus_${flen}.grib2
      if [ -f ${in_file} ]; then
        echo ${in_file} >> ${out_dir}/${in_fname}
        echo HRRR_ceil_${s}00_f${flen}.nc >> ${out_dir}/${out_fname}
      fi
    fi
  done

  # Submit job to preprocess ceilings
  cp ${script_dir}/ceil/run_ceil_preprocess.sh ./${out_dir}/
  cd ${out_dir}
  sed -i "s/{PARTITION}/${partition}/" run_ceil_preprocess.sh
  sed -i "s/{MACHINE}/${machine}/" run_ceil_preprocess.sh
  sbatch run_ceil_preprocess.sh
  cd ..

done
