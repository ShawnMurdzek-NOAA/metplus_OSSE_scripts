
INIT_BEG=2022042912
INIT_END=2022050612

fcst_name='spring_ctrl_grid'
fcst_dir='/work2/noaa/wrfruc/murdzek/RRFS_OSSE/syn_data/spring'
obs_dir='/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP'

metplusDIR='/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts'
verif_templates=("${metplusDIR}/GridStat_sfc.conf" "${metplusDIR}/GridStat_ua.conf")
verif_types=("sfc" "upper_air")
user_template="${metplusDIR}/smurdzek_orion.conf"
slurm_template="${metplusDIR}/run_metplus.sh"

#---------------------------------------------------------------------------------------------------

parentDIR=`pwd`

begin=${INIT_BEG}
end=`date -d "${begin::8} ${begin:8:2} + 11 hours" +%Y%m%d%H`
while [ ${end} -le ${INIT_END} ]; do
  for j in ${!verif_templates[@]}; do
    echo "${begin}: ${verif_types[j]}"
    dir=${parentDIR}/${verif_types[j]}/${begin}
    mkdir -p ${dir}/output
    cp ${metplusDIR}/metplus_orion.env ${dir}/
    
    # Create METplus configuration files. Use = as the sed delimiter b/c we are using paths that contain /
    conf_fname=GridStat_${verif_types[j]}.conf
    cp ${verif_templates[j]} ${dir}/${conf_fname}
    sed -i "s={INIT_BEG}=${begin}=" ${dir}/${conf_fname}
    sed -i "s={INIT_END}=${end}=" ${dir}/${conf_fname}
    sed -i "s={FCST_DIR}=${fcst_dir}=" ${dir}/${conf_fname}
    sed -i "s={OBS_DIR}=${obs_dir}=" ${dir}/${conf_fname}
    sed -i "s={FCST_NAME}=${fcst_name}=" ${dir}/${conf_fname}

    # Rewrite the OUTPUT_BASE directory in the user config file
    user_fname=user.conf
    cp ${user_template} ${dir}/${user_fname}
    sed -i "s={OUTPUT_BASE}=${dir}/output=" ${dir}/${user_fname}
  
    # Create and submit the slurm job submission file
    slurm_fname=metplus_${verif_types[j]}_${begin}.sh 
    cp ${slurm_template} ${dir}/${slurm_fname}
    sed -i "s={CONF_FILE}=./${conf_fname}=" ${dir}/${slurm_fname} 
    sed -i "s={USER_FILE}=./${user_fname}=" ${dir}/${slurm_fname} 
    cd ${dir}
    sbatch ${slurm_fname}
    cd ${parentDIR}

  done
  begin=`date -d "${begin::8} ${begin:8:2} + 12 hours" +%Y%m%d%H`
  end=`date -d "${end::8} ${end:8:2} + 12 hours" +%Y%m%d%H`
done
