
# Quick bash script to check whether UPP output files for a set of simulations exist and have sizes > 0

parent="/work2/noaa/wrfruc/murdzek/RRFS_OSSE/syn_data_rrfs-workflow_orion"
sims=( "${parent}/spring/NCO_dirs/ptmp/prod/rrfs.YYYYMMDD/HH/rrfs.tHHz.prslev.fFFF.conus_3km.grib2"
       "${parent}/spring_uas_35km/NCO_dirs/ptmp/prod/rrfs.YYYYMMDD/HH/rrfs.tHHz.prslev.fFFF.conus_3km.grib2"
       "${parent}/spring_no_aircft/NCO_dirs/ptmp/prod/rrfs.YYYYMMDD/HH/rrfs.tHHz.prslev.fFFF.conus_3km.grib2"
       "${parent}/spring_uas_35km_no_aircft/NCO_dirs/ptmp/prod/rrfs.YYYYMMDD/HH/rrfs.tHHz.prslev.fFFF.conus_3km.grib2" )

start_time=2022042921
end_time=2022050612

# Forecast hours (these use the FFF placeholder)
fhrs=( 000 001 003 006 )

#-------------------------------------------------------------------------------

current=${start_time}
while [ ${current} -le ${end_time} ]; do
  
  YYYY=${current::4}
  MM=${current:4:2}
  DD=${current:6:2}
  HH=${current:8:2}

  for s in ${sims[@]}; do
    tmp1=${s//YYYY/${YYYY}}
    tmp2=${tmp1//MM/${MM}}
    tmp3=${tmp2//DD/${DD}}
    tmp4=${tmp3//HH/${HH}}
    for f in ${fhrs[@]}; do
      fname=${tmp4//FFF/${f}}
      if [ -f ${fname} ]; then
        size=`stat -c %s ${fname}`
	if [ ${size} -eq 0 ]; then
          echo "${fname} has a size of 0"
        fi
      else
        echo "${fname} does not exist"
      fi
    done
  done

  current=`date '+%Y%m%d%H' --date="${current::8} ${current:8:4} 60 minutes"`

done
