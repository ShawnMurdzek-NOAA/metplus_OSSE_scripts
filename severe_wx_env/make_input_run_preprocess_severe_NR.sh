
# Make input and output file lists for NR output
# Submit ceiling preprocess jobs

parentDIR=/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP
subdir=( 20220429 20220430 20220501 20220502 20220503 20220504 20220505 20220506 )
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
    echo ${path_arr[-1]::19}_severe_wx_env_mask.nc >> ${out_fname}
  done
done

# Submit job to preprocess ceilings
cp ${script_dir}/severe_wx_env/create_gen_vx_mask_from_NR.sh .
sbatch create_gen_vx_mask_from_NR.sh
