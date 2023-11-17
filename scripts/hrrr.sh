#!/bin/bash
echo Downloading 2m temperature data
ncks -v tmp2m https://nomads.ncep.noaa.gov/dods/hrrr/hrrr20231028/hrrr_sfc.t12z hrrr1.nc
echo Downloading 2m dewpoint data
ncks -v dpt2m https://nomads.ncep.noaa.gov/dods/hrrr/hrrr20231028/hrrr_sfc.t12z hrrr2.nc
echo Downloading 2m relative humidity data
ncks -v rh2m https://nomads.ncep.noaa.gov/dods/hrrr/hrrr20231028/hrrr_sfc.t12z hrrr3.nc
echo Downloading precipitation data
ncks -v apcpsfc https://nomads.ncep.noaa.gov/dods/hrrr/hrrr20231028/hrrr_sfc.t12z hrrr4.nc
echo Downloading freezing precipitation data
ncks -v cfrzrsfc https://nomads.ncep.noaa.gov/dods/hrrr/hrrr20231028/hrrr_sfc.t12z hrrr5.nc
echo Downloading snowfall data
ncks -v asnowsfc https://nomads.ncep.noaa.gov/dods/hrrr/hrrr20231028/hrrr_sfc.t12z hrrr6.nc
echo Downloading cloud cover data
ncks -v tcdcclm https://nomads.ncep.noaa.gov/dods/hrrr/hrrr20231028/hrrr_sfc.t12z hrrr7.nc
echo Downloading surface wind gust data
ncks -v gustsfc https://nomads.ncep.noaa.gov/dods/hrrr/hrrr20231028/hrrr_sfc.t12z hrrr8.nc
echo Merging files
cdo merge hrrr1.nc hrrr2.nc hrrr12.nc
cdo merge hrrr3.nc hrrr4.nc hrrr34.nc
cdo merge hrrr5.nc hrrr6.nc hrrr56.nc
cdo merge hrrr7.nc hrrr8.nc hrrr78.nc
cdo merge hrrr12.nc hrrr34.nc hrrr1234.nc
cdo merge hrrr56.nc hrrr78.nc hrrr5678.nc
cdo merge hrrr5678.nc hrrr1234.nc hrrrmerged.nc
echo Removing individual variable files
rm hrrr1.nc
rm hrrr2.nc
rm hrrr3.nc
rm hrrr4.nc
rm hrrr5.nc
rm hrrr6.nc
rm hrrr7.nc
rm hrrr8.nc
rm hrrr12.nc
rm hrrr34.nc
rm hrrr56.nc
rm hrrr78.nc
rm hrrr1234.nc
rm hrrr5678.nc
echo Running LCR and BFP calculations
ncap2 -4 -S lcr-v-1-2.nco hrrrmerged.nc hrrr-lcr.nc
ncwa -v lcr -d time,1,24 -a time -y max hrrr-lcr.nc hrrr-day1lcr.nc
ncwa -v bfp -d time,1,24 -a time -y max hrrr-lcr.nc hrrr-day1bfp.nc
ncwa -v lcr -d time,6,30 -a time -y max hrrr-lcr.nc hrrr-day1lcr-1.nc
ncwa -v bfp -d time,6,30 -a time -y max hrrr-lcr.nc hrrr-day1bfp-1.nc
ncwa -v lcr -d time,24,48 -a time -y max hrrr-lcr.nc hrrr-day2lcr.nc
ncwa -v bfp -d time,24,48 -a time -y max hrrr-lcr.nc hrrr-day2bfp.nc
echo Delete initial model data download Y or N
read modeldelete
if [ $modeldelete == Y ]
then
rm hrrrmerged.nc
fi
