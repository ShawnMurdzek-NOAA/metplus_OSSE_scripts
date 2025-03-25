#!/bin/sh

date

# Configure Python environment (must contain pygrib)
source ${ENV_FILE}
module list
which python
echo

# Create working directory
echo "WORKDIR = ${WORKDIR}"
mkdir -p ${WORKDIR}

# Loop over each forecast hour and run compute_RHobT.py
for fhr in ${FCST_HRS}; do
  FCST_FILE=${FCST_TMPL//"{FHR}"/"$fhr"}
  NR_FILE=`date "+${NR_TMPL}" --date="${INIT::8} ${INIT:8:2} ${fhr} hours"`
  echo
  echo "fhr = ${fhr}"
  echo "FCST_FILE = ${FCST_FILE}"
  echo "NR_FILE = ${NR_FILE}"
  if [[ ! -f ${NR_FILE} ]]; then
    echo "NR_FILE ${NR_FILE} does not exist! Skipping..."
  elif [[ ! -f ${FCST_FILE} ]]; then
    echo "FCST_FILE ${FCST_FILE} does not exist! Skipping..."
  else
    echo "Running ${SCRIPT}"
    python -u ${SCRIPT} ${NR_FILE} \
  	                ${FCST_FILE} \
			${WORKDIR}/RHobT_${fhr}.grib2 \
			-v 1
  fi
done

date
