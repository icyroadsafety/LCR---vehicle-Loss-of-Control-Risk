ncks -d lev,500.0,1000.0 -d time,0,10 -v tmpprs   https://nomads.ncep.noaa.gov/dods/nam/nam20231017/nam1hr_18z nam20231017_nam1hr_18z-t1.nc --no_tmp_fl -O --mk_rec_dmn time
ncks -d lev,500.0,1000.0 -d time,11,20 -v tmpprs   https://nomads.ncep.noaa.gov/dods/nam/nam20231017/nam1hr_18z nam20231017_nam1hr_18z-t2.nc --no_tmp_fl -O --mk_rec_dmn time
ncks -d lev,500.0,1000.0 -d time,21,30 -v tmpprs   https://nomads.ncep.noaa.gov/dods/nam/nam20231017/nam1hr_18z nam20231017_nam1hr_18z-t3.nc --no_tmp_fl -O --mk_rec_dmn time
ncks -d lev,500.0,1000.0 -d time,31,36  -v tmpprs   https://nomads.ncep.noaa.gov/dods/nam/nam20231017/nam1hr_18z nam20231017_nam1hr_18z-t4.nc --no_tmp_fl -O --mk_rec_dmn time
ncrcat nam20231017_nam1hr_18z-t?.nc nam20231017_nam1hr_18z.nc --no_tmp_fl
ncwa -a lev -y max nam20231017_nam1hr_18z.nc nam20231017_nam1hr_18z_tmpprs_max.nc 
