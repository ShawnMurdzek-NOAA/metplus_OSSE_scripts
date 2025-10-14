#!/bin/sh

#SBATCH -A rtrr
#SBATCH -t 05:00:00
#SBATCH --ntasks=1
#SBATCH --partition=hercules

machine=hercules
script_dir=/work2/noaa/wrfruc/murdzek/src/metplus_OSSE_scripts  # Path to metplus_OSSE_scripts
init_mask_file=/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_grid_NR/NR_output/USA_mask/NR_USAmask.nc
in_files=( ./wrfprs_202204300000_er.grib2 
	   ./wrfprs_202204300100_er.grib2 )

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
  wgrib2 ${in_files[i]} -for_n 547:548:1 -grib uv80m_${i}.grib2

  # Compute wind speed
  wgrib2 uv80m_${i}.grib2 -wind_speed wspd80m_${i}.grib2

  # Run PCP-Combine
  if [[ ${i} -gt 0 ]]; then
    pcp_combine \
      -subtract \
      wspd80m_${i}.grib2 'name="WIND"; level="Z80";' \
      wspd80m_$((i-1)).grib2 'name="WIND"; level="Z80";' \
      wspd80m_diff_${i}.nc
  fi

  # Run gen_vx_mask
  gen_vx_mask \
    ${init_mask_file} \
    wspd80m_${i}.grib2 \
    wspd_mask_NR_${i}.nc \
    -type data \
    -mask_field 'name="WIND"; level="Z80";' \
    -thresh 'gt3' \
    -intersection

  gen_vx_mask \
    wspd_mask_NR_${i}.nc \
    wspd80m_${i}.grib2 \
    wspd_mask_NR_${i}.nc \
    -type data \
    -mask_field 'name="WIND"; level="Z80";' \
    -thresh 'lt15' \
    -intersection
 
  # Clean
  if [[ ${clean} -gt 0 ]]; then
    if [[ -f uv80m_${i-1}.grib2 ]]; then
      rm uv80m_$((i-1)).grib2
      rm wspd80m_$((i-1)).grib2
    fi
  fi
 
done

date
