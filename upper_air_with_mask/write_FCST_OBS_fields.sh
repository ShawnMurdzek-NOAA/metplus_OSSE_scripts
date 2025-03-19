# Quick script to write a bunch of FCST and OBS field specifications to an output file
# These specifications can then be copy-and-pasted into a METplus .conf file

out_file='tmp.txt'
var=( 'TMP' 'SPFH' 'UGRD' 'VGRD' )
plvl=( 1000 975 950 925 900 875 850 825 800 775 750 725 700 675 650 625 600 )

i=1
for v in ${var[@]}; do
  for p in ${plvl[@]}; do
    echo "FCST_VAR${i}_NAME = ${v}" >> ${out_file}
    echo "FCST_VAR${i}_LEVELS = P${p}" >> ${out_file}
    echo "OBS_VAR${i}_NAME = ${v}" >> ${out_file}
    echo "OBS_VAR${i}_LEVELS = P${p}" >> ${out_file}
    echo "OBS_VAR${i}_OPTIONS = mask = {poly = [\"{MASK_DIR}/P${p}00_mask.nc\"];};" >> ${out_file}
    echo >> ${out_file}
    i=$(( i + 1 ))
  done
done
