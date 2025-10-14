#!/bin/sh

#SBATCH -A rtrr
#SBATCH -t 05:00:00
#SBATCH --ntasks=1
#SBATCH --partition=hercules

machine=hercules
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts  # Path to metplus_OSSE_scripts
in_files=( ./rrfs.t00z.prslev.f000.conus_3km.grib2 
	   ./rrfs.t00z.prslev.f001.conus_3km.grib2 )

# Option to clean temporary files
clean=0

date

#module load wgrib2  # causes infinite loop and may not be needed??
source ${script_dir}/env/metplus_${machine}.env

for i in ${!in_files[@]}; do

  echo
  echo "======================================"
  echo "input file = ${in_files[i]}"

  # Extract 80-m winds
  wgrib2 ${in_files[i]} -for_n 955:956:1 -grib uv80m_fcst_${i}.grib2

  # Compute wind speed
  wgrib2 uv80m_fcst_${i}.grib2 -wind_speed wspd80m_fcst_${i}.grib2

  # Run PCP-Combine
  if [[ ${i} -gt 0 ]]; then
    pcp_combine \
      -subtract \
      wspd80m_fcst_${i}.grib2 'name="WIND"; level="Z80";' \
      wspd80m_fcst_$((i-1)).grib2 'name="WIND"; level="Z80";' \
      wspd80m_fcst_diff_${i}.nc
  fi

  # Clean
  if [[ ${clean} -gt 0 ]]; then
    if [[ -f uv80m_fcst_${i-1}.grib2 ]]; then
      rm uv80m_fcst_$((i-1)).grib2
      rm wspd80m_fcst_$((i-1)).grib2
    fi
  fi
 
done

date
