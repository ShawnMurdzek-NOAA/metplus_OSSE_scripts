
# Change DESC Fields in MET Output Files
# ======================================

# Inputs
# ------
#    $1 : Old DESC to replace
#    $2 : New DESC
#    $3 : Text file containing the names of all files to operate on

#-------------------------------------------------------------------------------

usage() { echo "usage: ${0} [-h] old_DESC new_DESC list_of_files" 1>&2; exit; }

# Gather inputs
while getopts "h" flag; do
  case "${flag}" in
    h) usage ;; 
  esac
  shift $((OPTIND-1))
done

old=$1
new=$2
all_files=(`cat $3`)

echo
echo "replacing '${old}' with '${new}' in ${#all_files[@]} files"
echo

# Replace strings using sed
for f in ${all_files[@]}; do
  sed -i "s/${old}/${new}/" ${f}
done
