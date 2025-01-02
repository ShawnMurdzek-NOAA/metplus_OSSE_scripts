
# Link METplus output files into a structure that is useable by plot_driver.py

verifDIR=('/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_no_aircft/ceil/verif'
	  '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_uas_35km_add_typ133_DAerr/ceil/verif'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_uas_35km_no_aircft/ceil/verif')
#verif_types=("sfc" "precip_radar" "severe_wx_env" "lower_atm" "additional_2D" "upper_air")
verif_types=("ceil_exp2")

#---------------------------------------------------------------------------------------------------

for vD in ${verifDIR[@]}; do
  for v in ${verif_types[@]}; do
    out_dir=${vD}/${v}/output/GridStat
    mkdir -p ${out_dir}
    all_dir=(${vD}/${v}/2*)
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
done
