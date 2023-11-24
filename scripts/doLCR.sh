#!/usr/bin/bash

# run the custom lcr.nco script and then
# create image  lcr map and bfp map
# This script uses absolute file names as this
# script is being run in ~/lcr/hrrr_nc_data  and the
# python scripts lcrmap.py and bfpmap.py require that  cwd is ~/lcr/map   
# scripts and directories are RELATIVE to this

DEBUG=1;

#gfs or nam or hrrr netcdf4 ? file
projectDir=$1;
inputNcFile=$2;

plainName=$( basename $inputNcFile );

#helps with the script names - but still need absolute paths for lcrmap and bfpmap
cd $projectDir


tmpNcFile="$projectDir/scratch/tmp-$plainName";
# the python lcrmap.py prefers absolute filenames
lcrNcFile="$projectDir/scratch/lcr-$plainName"; 

# output image name - normally to the directory ~/lcr/png
if [[ $# -gt 3 ]]; then
    outputLcrImage=$3;
    outputLcrImage=$4;
else
    # the python lcrmap.py prefers absolute filenames
    outputLcrImage="$projectDir/png/lcr-${plainName%.nc}.png";
    outputBfpImage="$projectDir/png/bfp-${plainName%.nc}.png";
fi

[[  $DEBUG -gt 0 ]] &&  echo "$0: outputLcrImage=$outputLcrImage num args=${#}"

vars="-v afp,bfp,nfp,lcr";


# run the lcr script
CMD="ncap2 -v -O -S "scripts/lcr-v-1-2.nco" $inputNcFile  ${tmpNcFile}"   

[[ $DEBUG -gt 0 ]] && echo "$CMD";
# do the deed
$CMD

if [[ $? -ne 0   ]]; then
    [[  -e  "${tmpNcFile}" ]] && rm "$tmpNcFile"
    exit 1
fi

ncdump -k $tmpNcFile >& /tmp/ncdump.txt || exit 1

ncks -M $vars $tmpNcFile  >& /tmp/ncks.txt || exit 1


# find the max values of afp,bfp,nfp,lcr along the time dimension 
CMD="ncwa -O  $vars -a time -y max -d time,1, $tmpNcFile $lcrNcFile"
[[ $DEBUG -gt 0 ]] && echo "$CMD";
# do the deed
$CMD
if [[ $? -ne 0 ]]; then
   exit 2
fi    


CMD="python scripts/lcrmap.py $lcrNcFile $outputLcrImage &> /tmp/lcrmap.txt"
[[ $DEBUG -gt 0 ]] && echo "$CMD";
$CMD
# error ? then dump stdout, stderr to stderr
if [[  $? -ne 0 ]]; then
    cat /tmp/lcrmap.txt
    exit 3
fi




CMD="python scripts/bfpmap.py  $lcrNcFile $outputBfpImage &> /tmp/bfpmap.txt"
[[ $DEBUG -gt 0 ]] && echo "$CMD";
$CMD
# error ? then dump stdout, stderr to stderr
if [[  $? -ne 0 ]]; then
    cat /tmp/bfpmap.txt
    exit 4
fi







exit 0;


