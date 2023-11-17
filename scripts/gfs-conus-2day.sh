#!/bin/bash
echo Downloading 2m temperature data
ncks -v tmp2m -d time,0,48 -d lat,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs1.nc
echo Downloading 2m depoint data
ncks -v dpt2m -d time,0,48 -d lat,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs2.nc
echo Downloading 2m relative humidity data
ncks -v rh2m -d time,0,48 -d lat,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs3.nc
echo Downloading precipitation data
ncks -v apcpsfc -d time,0,48 -d lat -d time,1,48,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs4.nc
echo Downloading freezing rain ptype data
ncks -v cfrzrsfc -d time,0,48 -d lat -d time,1,48,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs5.nc
echo Downloading snow ptype data
ncks -v csnowsfc -d time,0,48 -d lat -d time,1,48,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs6.nc
echo Downloading cloud cover data
ncks -v tcdcclm -d time,0,48 -d lat -d time,1,48,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs7.nc
echo Downloading surface wind gust data
ncks -v gustsfc -d time,0,48 -d lat -d time,1,48,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs8.nc
echo Downloading upper air data 1 of 4
ncks -d lev,500.0,1000.0 -d time,0,12 -v tmpprs   -d lat,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs20231022_gfs_12z-t1.nc --no_tmp_fl -O --mk_rec_dmn time
echo Downloading upper air data 2 of 4
ncks -d lev,500.0,1000.0 -d time,13,24 -v tmpprs   -d lat,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs20231022_gfs_12z-t2.nc --no_tmp_fl -O --mk_rec_dmn time
echo Downloading upper air data 3 of 4
ncks -d lev,500.0,1000.0 -d time,25,36 -v tmpprs   -d lat,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs20231022_gfs_12z-t3.nc --no_tmp_fl -O --mk_rec_dmn time
echo Downloading upper air data 4 of 4
ncks -d lev,500.0,1000.0 -d time,37,48  -v tmpprs   -d lat,20.0,60.0 -d lon,210.0,310.0 https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20231022/gfs_0p25_12z gfs20231022_gfs_12z-t4.nc --no_tmp_fl -O --mk_rec_dmn time
echo Calculating upper air maximum temperature
ncwa -a lev -y max gfs20231022_gfs_12z-t1.nc ncwa-t1.nc
echo  --- Completed 1 of 4
ncwa -a lev -y max gfs20231022_gfs_12z-t2.nc ncwa-t2.nc
echo  --- Completed 2 of 4
ncwa -a lev -y max gfs20231022_gfs_12z-t3.nc ncwa-t3.nc
echo  --- Completed 3 of 4
ncwa -a lev -y max gfs20231022_gfs_12z-t4.nc ncwa-t4.nc
echo  --- Completed 4 of 4
echo Merging upper air maximum temp data files
ncrcat ncwa-t?.nc maxtemp.nc
echo Calculating Kuchera ratio
ncap2 -4 -S kuchera.nco maxtemp.nc kuchera.nc
echo Merging variable files
cdo merge gfs1.nc kuchera.nc gfs1k.nc
cdo merge gfs1k.nc gfs2.nc gfs12.nc
cdo merge gfs3.nc gfs4.nc gfs34.nc
cdo merge gfs5.nc gfs6.nc gfs56.nc
cdo merge gfs7.nc gfs8.nc gfs78.nc
cdo merge gfs12.nc gfs34.nc gfs1234.nc
cdo merge gfs56.nc gfs78.nc gfs5678.nc
cdo merge gfs5678.nc gfs1234.nc gfsmerged.nc
echo Removing individual variable files
rm kuchera.nc
rm gfs1.nc
rm gfs1k.nc
rm gfs2.nc
rm gfs3.nc
rm gfs4.nc
rm gfs5.nc
rm gfs6.nc
rm gfs7.nc
rm gfs8.nc
rm gfs12.nc
rm gfs34.nc
rm gfs56.nc
rm gfs78.nc
rm gfs1234.nc
rm gfs5678.nc
echo Running LCR and BFP calculations
ncap2 -4 -S lcr-v-1-2.nco gfsmerged.nc gfs-lcr.nc
echo Creating daily maximum datasets for days 1 through 5
ncwa -v lcr -d time,1,24 -a time -y max gfs-lcr.nc gfs-day1lcr1.nc
ncwa -v bfp -d time,1,24 -a time -y max gfs-lcr.nc gfs-day1bfp1.nc
ncwa -v lcr -d time,1,36 -a time -y max gfs-lcr.nc gfs-day1-2lcr1.nc
ncwa -v bfp -d time,1,36 -a time -y max gfs-lcr.nc gfs-day1-2bfp1.nc
ncwa -v lcr -d time,24,48 -a time -y max gfs-lcr.nc gfs-day2lcr1.nc
ncwa -v bfp -d time,24,48 -a time -y max gfs-lcr.nc gfs-day2bfp1.nc
ncwa -v lcr -d time,1,48 -a time -y max gfs-lcr.nc gfs-2daymax.nc
ncwa -v bfp -d time,1,48 -a time -y max gfs-lcr.nc gfs-2daymax.nc
echo Delete initial model data download Y or N
read modeldelete
if [ $modeldelete == Y ]
then
rm gfsmerged.nc
fi