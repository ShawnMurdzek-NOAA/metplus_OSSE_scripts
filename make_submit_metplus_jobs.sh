
# Looping uses INIT times rather than VALID times
# To prevent weird things from happening, ensure that $VALID_BEG is within $step of $INIT_BEG
INIT_BEG=2022042921
INIT_END=2022050612

VALID_BEG=2022043000
VALID_END=2022050612

step=160  # Recommended for PointStat
#step=12    # Recommended for GridStat

fcst_name='osse_spring_ctrl'
fcst_dir='/work2/noaa/wrfruc/murdzek/RRFS_OSSE/syn_data_app_orion/spring'
obs_dir='/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion/obs_syn_with_errors/spring/output/pb2nc'

metplusDIR='/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts'
verif_templates=("${metplusDIR}/PointStat_sfc.conf" "${metplusDIR}/PointStat_ua.conf")
verif_type="PointStat"
verif_subtypes=("sfc" "upper_air")
user_template="${metplusDIR}/smurdzek_orion.conf"
slurm_template="${metplusDIR}/run_metplus.sh"

#---------------------------------------------------------------------------------------------------

parentDIR=`pwd`

begin_init=${INIT_BEG}
begin_valid=${VALID_BEG}
hr_minus_one=$((step-1))
end=`date -d "${begin_init::8} ${begin_init:8:2} + ${hr_minus_one} hours" +%Y%m%d%H`
while [ ${end} -le ${INIT_END} ]; do
  for j in ${!verif_templates[@]}; do
    echo "${begin_init}: ${verif_subtypes[j]}"
    dir=${parentDIR}/${verif_subtypes[j]}/${begin_init}
    mkdir -p ${dir}/output
    cp ${metplusDIR}/metplus_orion.env ${dir}/
    
    # Create METplus configuration files. Use = as the sed delimiter b/c we are using paths that contain /
    conf_fname=${verif_type}_${verif_subtypes[j]}.conf
    cp ${verif_templates[j]} ${dir}/${conf_fname}
    sed -i "s={INIT_BEG}=${begin_init}=" ${dir}/${conf_fname}
    sed -i "s={INIT_END}=${end}=" ${dir}/${conf_fname}
    sed -i "s={VALID_BEG}=${begin_valid}=" ${dir}/${conf_fname}
    sed -i "s={VALID_END}=${end}=" ${dir}/${conf_fname}
    sed -i "s={FCST_DIR}=${fcst_dir}=" ${dir}/${conf_fname}
    sed -i "s={OBS_DIR}=${obs_dir}=" ${dir}/${conf_fname}
    sed -i "s={FCST_NAME}=${fcst_name}=" ${dir}/${conf_fname}

    # Rewrite the OUTPUT_BASE directory in the user config file
    user_fname=user.conf
    cp ${user_template} ${dir}/${user_fname}
    sed -i "s={OUTPUT_BASE}=${dir}/output=" ${dir}/${user_fname}
  
    # Create and submit the slurm job submission file
    slurm_fname=metplus_${verif_subtypes[j]}_${begin_init}.sh 
    cp ${slurm_template} ${dir}/${slurm_fname}
    sed -i "s={CONF_FILE}=./${conf_fname}=" ${dir}/${slurm_fname} 
    sed -i "s={USER_FILE}=./${user_fname}=" ${dir}/${slurm_fname} 
    cd ${dir}
    sbatch ${slurm_fname}
    cd ${parentDIR}

  done
  begin_init=`date -d "${begin_init::8} ${begin_init:8:2} + ${step} hours" +%Y%m%d%H`
  begin_valid=`date -d "${begin_valid::8} ${begin_valid:8:2} + ${step} hours" +%Y%m%d%H`
  end=`date -d "${end::8} ${end:8:2} + ${step} hours" +%Y%m%d%H`
done
