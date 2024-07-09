
# Functional Test for the METplus Pipeline Using the Test Cases
#==============================================================

# NOTE: This test takes 90-100 min to run

# Option to clean up afterwards
clean=0

# Machine (options: orion, hercules)
machine="orion"
partition=${machine}
allocation="rtrr"

#----------------------------------------------------------------------

echo "METplus Pipeline Functional Test"
echo "--------------------------------"
echo
echo "start time"
date
echo

# Remove old temporary directory
top_dir=`pwd`
test_dir="${top_dir}/cases/tmp"
truth_dir="${top_dir}/cases/truth"
if [ -d ${test_dir} ]; then
  echo "Removing old test directory..."
  rm -r ${test_dir}
fi

# Create tmp directory and edit bash script to make + submit jobs
echo "Creating test directory and editing script to submit jobs..."
mkdir -p ${test_dir}
cp ./cases/make_submit_metplus_jobs.sh ${test_dir}/
sed -i "s/{{MACHINE}}/${machine}/" ${test_dir}/make_submit_metplus_jobs.sh
sed -i "s/{{PARTITION}}/${partition}/" ${test_dir}/make_submit_metplus_jobs.sh
sed -i "s/{{ALLOCATION}}/${allocation}/" ${test_dir}/make_submit_metplus_jobs.sh

# Submit jobs
echo "Submitting jobs..."
cd ${test_dir}
bash make_submit_metplus_jobs.sh
echo "Waiting 15 min..."
sleep 900

# Wait for jobs to finish, then check results
err=0
cd ${truth_dir}
verif_dir_all=( 'precip_radar' 'upper_air' )
for v in ${verif_dir_all[@]}; do
  echo
  echo "Checking ${v}"
  verif_dir=( `ls ./${v}/` )
  unset 'verif_dir[${#verif_dir[@]}-1]'
  for d in ${verif_dir[@]}; do

    finish=0
    while [ ${finish} -eq 0 ]; do
      nitems=`ls -l ${test_dir}/${v}/${d}/ | wc -l`
      if [ ${nitems} -gt 1 ]; then
        job_fname=`ls ${test_dir}/${v}/${d}/slurm*`
        job_edit_time=`date -r ${job_fname} '+%s'`
        now=`date '+%s'`
        age=`expr ${now} - ${job_edit_time}`
        if [ ${age} -gt 600 ]; then
          finish=1
        else
	  echo "${v} job is running, but not complete. Waiting 10 min"
	  sleep 600
        fi
      else
        echo "${v} job has not started yet. Waiting 15 min"
        sleep 900
      fi
    done

    echo "checking results of ${v}/${d} job"
    subdir=( `ls ${test_dir}/${v}/${d}/output/GridStat/` )
    for s in ${subdir[@]}; do
      files=( `ls ${test_dir}/${v}/${d}/output/GridStat/${s}/` )
      for f in ${files[@]}; do

        # Force MET version in test output to match truth
        test_out=${test_dir}/${v}/${d}/output/GridStat/${s}/${f}
        test_line=`tail -n1 ${test_out}`
        test_arr=(${test_line})
        test_ver=${test_arr[0]}

        truth_out=${truth_dir}/${v}/${d}/output/GridStat/${s}/${f}
        truth_line=`tail -n1 ${truth_out}`
        truth_arr=(${truth_line})
        truth_ver=${truth_arr[0]}

        sed -i "s/${test_ver}/${truth_ver}/" ${test_out}

        diff_len=`diff ${truth_out} ${test_out} | wc -l`
        if [ ${diff_len} -gt 0 ]; then
          echo "ERROR: ${f} differs!"
          err=1
        fi
      done
    done

  done
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
  rm -r ${test_dir}
fi
