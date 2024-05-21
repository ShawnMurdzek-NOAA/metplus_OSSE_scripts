
# Functional Test for the Pipeline Used to Preprocess Cloud Ceilings
#===================================================================

# User-specified input files
in_files=( /work2/noaa/wrfruc/murdzek/nature_run_winter/UPP/20220202/wrfprs_202202020300_er.grib2
           /work2/noaa/wrfruc/murdzek/nature_run_winter/UPP/20220202/wrfprs_202202020400_er.grib2 )

# Path to the METplus scripts
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts

# Option to clean up afterwards
clean=1

# Machine (options: orion, hercules)
machine="hercules"
partition=${machine}

#----------------------------------------------------------------------

# Remove old temporary files
tmp_files=( in_files.txt out_files.txt 
            run_ceil_preprocess.sh regrid.out )
for f in ${tmp_files[@]}; do
  if [ -f ${f} ]; then
    rm ${f}
  fi
done

# Create Inputs
echo 'Creating inputs...'
tmp_in=()
tmp_out=()
for i in ${!in_files[@]}; do
  tmp_in+=( input${i}.grib2 )
  tmp_out+=( output${i}.nc )

  cp ${in_files[i]} ${tmp_in[i]}
  echo ${tmp_in[i]} >> in_files.txt
  echo ${tmp_out[i]} >> out_files.txt
done

# Run regrid data plane pipeline
echo 'Running run_ceil_preprocess.sh...'
cp ${script_dir}/ceil/run_ceil_preprocess.sh .
sed -i "s/{PARTITION}/${partition}/" run_ceil_preprocess.sh
sed -i "s/{MACHINE}/${machine}/" run_ceil_preprocess.sh
bash run_ceil_preprocess.sh > regrid.out
err=$?
if [ ${err} -gt 0 ]; then
  echo "run_ceil_preprocess.sh raised error ${err}"
else
  echo "run_ceil_preprocess.sh ran without errors"
fi

# Check to make sure output files were created
echo
for f in ${tmp_out[@]}; do
  if [ ! -f ${f} ]; then
    echo "output file ${f} was not created!"
  else
    echo "output file ${f} was created successfully!"
  fi
done

# Check output
echo
source ${script_dir}/env/py_${machine}.env
for i in ${!tmp_in[@]}; do
  python compare_grib_nc_ceil.py ${tmp_in[i]} ${tmp_out[i]} > py_test${i}.out
  py_err=`tail -1 py_test${i}.out`
  if [[ ${py_err} -gt 0 ]]; then
    echo "compare_grib_nc_ceil.py raised error ${py_err}"
    if [ ${py_err} -gt ${err} ]; then
      err=${py_err}
    fi
  fi
done

# Final result
echo
if [ ${err} -gt 0 ]; then
  echo "Test failed with error code ${err}"
else
  echo "Test succesful!!"
fi

# Clean up
if [ ${clean} -eq 1 ]; then
  for f in ${tmp_files[@]}; do
    rm ${f}
  done

  for f in ${tmp_in[@]}; do
    rm ${f}
  done

  for f in ${tmp_out[@]}; do
    rm ${f}
  done

  for i in ${!tmp_in[@]}; do
    rm py_test${i}.out
  done
fi
