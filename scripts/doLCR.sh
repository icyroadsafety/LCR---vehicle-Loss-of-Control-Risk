#!/usr/bin/bash

# run the custom lcr.nco script and then
# create image  lcr map and bfp map
# create kml files for both lcr and bfp
# the script must be run in root directory of the project 
# This is the first script argument 

DEBUG=0;

doMAP=1
doKML=1

#gfs or nam or hrrr netcdf4 ? file
projectDir=$1;
inputNcFile=$2;
srtIndex=$3
endIndex=$4
Caption=$5

cntIndex=$(( endIndex - srtIndex -1 ))

plainName=$( basename $inputNcFile );

#helps with the script names - but still need absolute paths for lcrmap and bfpmap
cd $projectDir


tmpNcFile="scratch/tmp_$plainName";
ncoNcFile="scratch/nco_$plainName";
lcrNcFile="scratch/lcr_$plainName"; 

# output image name - normally to the directory ~/lcr/png
# the python lcrmap.py prefers absolute filenames
outputLcrImage="png/${plainName%.nc}_${srtIndex}_${endIndex}_lcr.png";
outputBfpImage="png/${plainName%.nc}_${srtIndex}_${endIndex}_bfp.png";

# output kml files
outputLcrKml="kml/${plainName%.nc}_${srtIndex}_${endIndex}_lcr.kml";
outputBfpKml="kml/${plainName%.nc}_${srtIndex}_${endIndex}_bfp.kml";


LcrCaption="LCR ${Caption}"
BfpCaption="BFP+ ${Caption}"

#return if images already exists
[[ -e $outputLcrImage ]] && [[ -e $outputBfpImage ]] && exit 10

[[ $DEBUG -gt 0 ]] &&  echo "$0: outputLcrImage=$outputLcrImage num args=${#} LcrCaption=${LcrCaption}"


vars="-v afp,bfp,nfp,lcr,cip";

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
CMD="ncwa -O  $vars -a time -y max -d time,1,${cntIndex} $ncoNcFile $lcrNcFile"
[[ $DEBUG -gt 0 ]] && echo "$CMD";
# do the deed
$CMD
if [[ $? -ne 0 ]]; then
   exit 2
fi    

# add the variable bfpmerged. Used in bfpkml.py
CMD="ncap2 -A -D 2 -v -S "scripts/bfpmerge.nco"  $lcrNcFile $lcrNcFile" 
[[ $DEBUG -gt 0 ]] && echo "$CMD";
$CMD
[[ $? -ne 0   ]] && exit 2




# bfp taking toooooo long
if [[ $doMAP -gt 0 ]]; then 

    CMD="python scripts/lcrmap.py $lcrNcFile $outputLcrImage ${LcrCaption@Q}  &> /tmp/lcrmap.txt"
    [[ $DEBUG -gt 0 ]] && echo "$CMD";
    # run command in backround
    eval ${CMD} 
    # error ? then dump stdout, stderr to stderr
    # if [[  $? -ne 0 ]]; then
    #     cat /tmp/lcrmap.txt
    #     exit 3
    # fi


    CMD="python scripts/bfpmap.py  $lcrNcFile $outputBfpImage ${BfpCaption@Q} >&  /tmp/bfpmap.txt"
    [[ $DEBUG -gt 0 ]] && echo "$CMD";
    eval ${CMD}   
    # error ? then dump stdout, stderr to stderr
    if [[  $? -ne 0 ]]; then
	    cat /tmp/bfpmap.txt
	    exit 4
    fi

    wait

    # double check
    [[ !  -e $outputLcrImage ]] && exit 3
    [[ !  -e $outputBfpImage ]] && exit 4


fi


if [[ $doKML -gt 0 ]]; then 

    CMD="python scripts/bfpkml.py  $lcrNcFile $outputBfpKml  >&  /tmp/bfpkml.txt"
    [[ $DEBUG -gt 0 ]] && echo "$CMD";
    eval ${CMD}   
    # error ? then dump stdout, stderr to stderr
    if [[  $? -ne 0 ]]; then
        cat /tmp/bfpkml.txt
        exit 8
    fi

    CMD="python scripts/lcrkml.py  $lcrNcFile $outputLcrKml  >&  /tmp/lcrkml.txt"
    [[ $DEBUG -gt 0 ]] && echo "$CMD";
    eval ${CMD}   
    # error ? then dump stdout, stderr to stderr
    if [[  $? -ne 0 ]]; then
        cat /tmp/lcrkml.txt
        exit 8
    fi

    # double check
    [[ !  -e $outputLcrKml ]] && exit 8
    [[ !  -e $outputBfpKml ]] && exit 8


fi



# delete temporary file
[[ -e $lcrNcFile ]] && rm $lcrNcFile;

# delete temporary files
[[ -e $tmpNcFile ]] && rm $tmpNcFile;
[[ -e $ncoNcFile ]] && rm $ncoNcFile;




exit 0;


