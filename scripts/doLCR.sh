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


tmpNcFile="$projectDir/scratch/tmp-$plainName";
# the python lcrmap.py prefers absolute filenames
lcrNcFile="$projectDir/scratch/lcr-$plainName"; 

# output image name - normally to the directory ~/lcr/png
if [[ $# -gt 2 ]]; then
    outputImage=$3;
else
    # the python lcrmap.py prefers absolute filenames
    outputImage="$projectDir/png/lcr-${plainName%.nc}.png";
fi

echo "$0: outputImage=$outputImage num args=${#}"

vars="-v afp,bfp,nfp,lcr";


# run the lcr script
CMD="ncap2 -v -O -S scripts/lcr-v-1-2.nco $inputNcFile  ${tmpNcFile}"   

[[ $DEBUG -gt 0 ]] && echo "$CMD";
# do the deed
$CMD

if [[ $? -ne 0   ]]; then
    [[  -e  "${tmpNcFile}" ]] && rm "$tmpNcFile"
    exit 1
fi

ncdump -k $tmpNcFile >& /tmp/ncdump.txt || exit 1
# check we have an ncfile
if [[ $? -ne 0  ]]; then
    exit 1
fi    

ncks -M $vars $tmpNcFile  >& /tmp/ncks.txt || exit 1
# check variables are present
if [[ $? -ne 0    ]]; then
    exit 1
fi    

# find the max values of afp,bfp,nfp,lcr along the time dimension 
CMD="ncwa -O  $vars -a time -y max -d time,1, $tmpNcFile $lcrNcFile"
[[ $DEBUG -gt 0 ]] && echo "$CMD";
# do the deed
$CMD
if [[ $? -ne 0 ]]; then
   exit 2
fi    

# tidy up
# [[ $DEBUG -gt 0 ]] && rm $tmpNcFile $lcrNcFile

python scripts/lcrmap.py $lcrNcFile $outputImage





exit 0;


