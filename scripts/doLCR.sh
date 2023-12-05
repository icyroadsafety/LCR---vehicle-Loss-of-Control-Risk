#!/usr/bin/bash

# run the custom lcr.nco script and then
# create image  lcr map and bfp map
# This script uses absolute file names as this
# script is being run in ~/lcr/hrrr_nc_data  and the
# python scripts lcrmap.py and bfpmap.py require that  cwd is ~/lcr/map   
# scripts and directories are RELATIVE to this

DEBUG=0;

doBFP=1

#gfs or nam or hrrr netcdf4 ? file
projectDir=$1;
inputNcFile=$2;
srtIndex=$3
endIndex=$4
Caption=$5

plainName=$( basename $inputNcFile );

#helps with the script names - but still need absolute paths for lcrmap and bfpmap
cd $projectDir


tmpNcFile="$projectDir/scratch/tmp_$plainName";
ncoNcFile="$projectDir/scratch/nco_$plainName";
# the python lcrmap.py prefers absolute filenames
lcrNcFile="$projectDir/scratch/lcr_$plainName"; 

# output image name - normally to the directory ~/lcr/png
# the python lcrmap.py prefers absolute filenames
outputLcrImage="$projectDir/png/${plainName%.nc}_${srtIndex}_${endIndex}_lcr.png";
outputBfpImage="$projectDir/png/${plainName%.nc}_${srtIndex}_${endIndex}_bfp.png";

LcrCaption="LCR ${Caption}"
BfpCaption="BFP+ ${Caption}"

#return if images already exists
[[ -e $outputLcrImage ]] && [[ -e $outputBfpImage ]] && exit 10

[[ $DEBUG -gt 0 ]] &&  echo "$0: outputLcrImage=$outputLcrImage num args=${#} LcrCaption=${LcrCaption}"


vars="-v afp,bfp,nfp,lcr";

# cut down by time according to  indicies
CMD="ncks -O -d time,${srtIndex},${endIndex} $inputNcFile ${tmpNcFile}"
[[ $DEBUG -gt 0 ]] && echo "$CMD";
# do the deed
$CMD

if [[ $? -ne 0   ]]; then
    [[  -e  "${ncoNcFile}" ]] && rm "$ncoNcFile"
    exit 1
fi



# run the lcr script
CMD="ncap2 -D 2 -v -O -S "scripts/lcr-v-1-2.nco" $tmpNcFile  ${ncoNcFile}"   
[[ $DEBUG -gt 0 ]] && echo "$CMD";
# do the deed
eval $CMD

if [[ $? -ne 0   ]]; then
    exit 1
fi

ncdump -k $ncoNcFile >& /tmp/ncdump.txt || exit 1

ncks -M $vars $ncoNcFile  >& /tmp/ncks.txt || exit 1


# find the max values of afp,bfp,nfp,lcr along the time dimension 
CMD="ncwa -O  $vars -a time -y max -d time,1,6 $ncoNcFile $lcrNcFile"
[[ $DEBUG -gt 0 ]] && echo "$CMD";
# do the deed
$CMD
if [[ $? -ne 0 ]]; then
   exit 2
fi    





CMD="python scripts/lcrmap.py $lcrNcFile $outputLcrImage ${LcrCaption@Q}  &> /tmp/lcrmap.txt &"
[[ $DEBUG -gt 0 ]] && echo "$CMD";
# run command in backround
eval ${CMD} 
# error ? then dump stdout, stderr to stderr
# if [[  $? -ne 0 ]]; then
#     cat /tmp/lcrmap.txt
#     exit 3
# fi


# bfp taking toooooo long
if [[ $doBFP -gt 0 ]]; then 

    CMD="python scripts/bfpmap.py  $lcrNcFile $outputBfpImage ${BfpCaption@Q} >&  /tmp/bfpmap.txt"
    [[ $DEBUG -gt 0 ]] && echo "$CMD";
    eval ${CMD}   
    # error ? then dump stdout, stderr to stderr
    if [[  $? -ne 0 ]]; then
	cat /tmp/bfpmap.txt
	exit 4
    fi
fi

wait

[[ !  -e $outputLcrImage ]] ||  [[ !  -e $outputBfpImage ]] && exit 5

# delete temporary file
[[ -e $lcrNcFile ]] && rm $lcrNcFile;

# delete temporary files
[[ -e $tmpNcFile ]] && rm $tmpNcFile;
[[ -e $ncoNcFile ]] && rm $ncoNcFile;




exit 0;


