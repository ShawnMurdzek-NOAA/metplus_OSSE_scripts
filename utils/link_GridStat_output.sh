
# Link METplus output files into a structure that is useable by plot_driver.py

verifDIR='/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/spring_uas_35km'
verif_types=("sfc" "upper_air")

#---------------------------------------------------------------------------------------------------

for v in ${verif_types[@]}; do
  out_dir=${verifDIR}/${v}/output/GridStat
  mkdir -p ${out_dir}
  all_dir=(${verifDIR}/${v}/2*)
  for d in ${all_dir[@]}; do
    all_subdir=(${d}/output/GridStat/2*)
    for sd in ${all_subdir[@]}; do
      cd ${sd}
      files=(./grid*)
      for f in ${files[@]}; do
        ln -sf ${sd}/${f} ${out_dir}/${f}
      done
    done
  done
done
