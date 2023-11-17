#!/bin/bash
echo Downloading 2m temperature data
ncks -v tmp2m https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z namnest1.nc
echo Downloading 2m depoint data
ncks -v dpt2m https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z namnest2.nc
echo Downloading 2m relative humidity data
ncks -v rh2m https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z namnest3.nc
echo Downloading precipitation data
ncks -v apcpsfc https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z namnest4.nc
echo Downloading freezing rain ptype data
ncks -v cfrzrsfc https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z namnest5.nc
echo Downloading snow ptype data
ncks -v csnowsfc https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z namnest6.nc
echo Downloading cloud cover data
ncks -v tcdcclm https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z namnest7.nc
echo Downloading surface wind gust data
ncks -v gustsfc https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z namnest8.nc
echo Downloading upper air data 1 of 4
ncks -d lev,500.0,1000.0 -d time,0,10 -v tmpprs   https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z nam20231022_nam1hr_12z-t1.nc --no_tmp_fl -O --mk_rec_dmn time
echo Downloading upper air data 2 of 4
ncks -d lev,500.0,1000.0 -d time,11,20 -v tmpprs   https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z nam20231022_nam1hr_12z-t2.nc --no_tmp_fl -O --mk_rec_dmn time
echo Downloading upper air data 3 of 4
ncks -d lev,500.0,1000.0 -d time,21,30 -v tmpprs   https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z nam20231022_nam1hr_12z-t3.nc --no_tmp_fl -O --mk_rec_dmn time
echo Downloading upper air data 4 of 4
ncks -d lev,500.0,1000.0 -d time,31,36  -v tmpprs   https://nomads.ncep.noaa.gov/dods/nam/nam20231022/nam1hr_12z nam20231022_nam1hr_12z-t4.nc --no_tmp_fl -O --mk_rec_dmn time
echo Calculating upper air maximum temperature
ncwa -a lev -y max nam20231022_nam1hr_12z-t1.nc ncwa-t1.nc
ncwa -a lev -y max nam20231022_nam1hr_12z-t2.nc ncwa-t2.nc
ncwa -a lev -y max nam20231022_nam1hr_12z-t3.nc ncwa-t3.nc
ncwa -a lev -y max nam20231022_nam1hr_12z-t4.nc ncwa-t4.nc
echo Merging upper air maximum temp data files
ncrcat ncwa-t?.nc maxtemp.nc
echo Calculating Kuchera ratio
ncap2 -4 -S kuchera.nco maxtemp.nc kuchera.nc
echo Merging variable files
cdo merge namnest1.nc kuchera.nc namnest1k.nc
cdo merge namnest1k.nc namnest2.nc namnest12.nc
cdo merge namnest3.nc namnest4.nc namnest34.nc
cdo merge namnest5.nc namnest6.nc namnest56.nc
cdo merge namnest7.nc namnest8.nc namnest78.nc
cdo merge namnest12.nc namnest34.nc namnest1234.nc
cdo merge namnest56.nc namnest78.nc namnest5678.nc
cdo merge namnest5678.nc namnest1234.nc namnestmerged.nc
echo Removing individual variable files
rm kuchera.nc
rm namnest1.nc
rm namnest1k.nc
rm namnest2.nc
rm namnest3.nc
rm namnest4.nc
rm namnest5.nc
rm namnest6.nc
rm namnest7.nc
rm namnest8.nc
rm namnest12.nc
rm namnest34.nc
rm namnest56.nc
rm namnest78.nc
rm namnest1234.nc
rm namnest5678.nc
echo Running LCR and BFP calculations
ncap2 -4 -S lcr-v-1-2.nco namnestmerged.nc namnest-lcr.nc
ncwa -v lcr -d time,1,24 -a time -y max namnest-lcr.nc namnest-day1lcr1.nc
ncwa -v bfp -d time,1,24 -a time -y max namnest-lcr.nc namnest-day1bfp1.nc
ncwa -v lcr -d time,1,36 -a time -y max namnest-lcr.nc namnest-day1-2lcr1.nc
ncwa -v bfp -d time,1,36 -a time -y max namnest-lcr.nc namnest-day1-2bfp1.nc
echo Delete initial model data download Y or N
read modeldelete
if [ $modeldelete == Y ]
then
rm namnestmerged.nc
fi