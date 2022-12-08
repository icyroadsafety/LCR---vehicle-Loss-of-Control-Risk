#!/bin/bash
# purpose download from 
# usage: nomads-download.sh  model-name model-date model-run
#
# examples:
#
# nomads-download.sh gfs 20221208 00
# nomads-download.sh hrr 20221207 06

model=$1
modeldate=$2
modelrun=$3

DBG=1

if [[ $DBG -eq 1 ]]; then
   Args="-4 -O -d time,0,1"
else
  Args="-4 -O"  
fi

Vars="-v tmp2m,dpt2m,rh2m,apcpsfc,cfrzrsfc" 


case "$model" in
    
    gfs)
	url="https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs${modeldate}/gfs_0p25_${modelrun}z"
        ;; 

    hrr)
       url="https://nomads.ncep.noaa.gov/dods/hrrr/hrrr${modeldate}/hrrr_sfc.t${modelrun}z"   
       ;;
   
esac

fileNameOut=${model}-${modeldate}-${modelrun}.nc

# delete if it already exists
if [[ -e "$fileNameOut" ]]; then
    rm "$fileNameOut"
fi

# do the deed
ncks $Args $Vars  $url "$fileNameOut"


