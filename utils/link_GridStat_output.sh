
# Link METplus output files into a structure that is useable by plot_driver.py

verifDIR=('/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring'
	  '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_uas_35km'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_uas_75km'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_uas_100km'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_uas_150km'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_uas_300km'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/spring_uas_35km_autocorr0.75'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/winter'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/winter_uas_35km'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/winter_uas_75km'
          '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/winter_uas_100km'
	  '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/rrfs-workflow_orion/winter_uas_150km')
#verif_types=("sfc" "upper_air")
#verif_types=("sfc" "precip_radar" "severe_wx_env" "lower_atm" "additional_2D" "upper_air")
#verif_types=("sfc" "precip_radar" "lower_atm" "additional_2D" "upper_air")
#verif_types=("ceil_exp2")
verif_types=("upper_air_below_sfc_mask" "lower_atm_below_sfc_mask")

#---------------------------------------------------------------------------------------------------

for vD in ${verifDIR[@]}; do
  echo "Performing linking for ${vD}"
  for v in ${verif_types[@]}; do
    out_dir=${vD}/${v}/output/GridStat
    mkdir -p ${out_dir}
    all_dir=(${vD}/${v}/2*)
    for d in ${all_dir[@]}; do
      all_subdir=(${d}/output/GridStat/2*)
      for sd in ${all_subdir[@]}; do
	if [[ -d ${sd} ]]; then
          cd ${sd}
          files=(./grid*)
          for f in ${files[@]}; do
            ln -sf ${sd}/${f} ${out_dir}/${f}
	  done
	fi
      done
    done
  done
done
