# Make list of NR pressure-level output

parentDIR1=/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP
subdir1=( 20220429 20220430 20220501 20220502 20220503 20220504 20220505  20220506 )
parentDIR2=/work2/noaa/wrfruc/murdzek/nature_run_winter/UPP
subdir2=( 20220201 20220202 20220203 20220204 20220205 20220206 20220207  20220208 )
out_fname='NR_file_names.txt'

# Remove output file if it exists
if [ -f ${out_fname} ]; then
  rm ${out_fname}
fi

# Create file list
for s in ${subdir1[@]}; do
  files=(`ls ${parentDIR1}/${s}/wrfprs*`)
  for f in ${files[@]}; do
    echo ${f} >> ${out_fname}
  done
done

for s in ${subdir2[@]}; do
  files=(`ls ${parentDIR2}/${s}/wrfprs*`)
  for f in ${files[@]}; do
    echo ${f} >> ${out_fname}
  done
done
