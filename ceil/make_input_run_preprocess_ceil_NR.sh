
# Make input and output file lists for NR output
# Submit ceiling preprocess jobs

parentDIR=/work2/noaa/wrfruc/murdzek/nature_run_winter/UPP
subdir=( 20220201 20220202 20220203 20220204 20220205 20220206 20220207 )
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts  # Path to metplus_OSSE_scripts

in_fname='in_files.txt'
out_fname='out_files.txt'

#---------------------------------------------------------------------------------------------------

# Remove input and output files if they exist
if [ -f ${in_fname} ]; then
  rm ${in_fname}
fi
if [ -f ${out_fname} ]; then
  rm ${out_fname}
fi

# Create input and output file lists
for s in ${subdir[@]}; do
  files=(`ls ${parentDIR}/${s}/wrfprs*`)
  for f in ${files[@]}; do
    echo ${f} >> ${in_fname}
    # Time for some fancy parsing!
    path_arr=(${f//\// })
    echo ${path_arr[-1]::19}_ceil.nc >> ${out_fname}
  done
done

# Submit job to preprocess ceilings
cp ${script_dir}/ceil/run_ceil_preprocess.sh .
sbatch run_ceil_preprocess.sh
