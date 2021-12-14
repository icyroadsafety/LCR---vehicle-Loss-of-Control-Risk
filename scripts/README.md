To download data from NOAA
Use OpenDAP which is built into NCO

Examples - required variables - tmpsfc,tmp2m,dpt2m,rh2m,apcpsfc
to download global data from the gdas 0.25 model do the following.

ncks -v tmpsfc,tmp2m,dpt2m,rh2m,apcpsfc https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20211214/gfs_0p25_06z gfs20211214_06z.nc

to download say from the CONUS model:

ncks -v tmpsfc,tmp2m,dpt2m,rh2m,apcpsfc https://nomads.ncep.noaa.gov/dods/hiresw/hiresw20211214/hiresw_conusarw_00z hireswhiresw20211214_00z.nc


Tidy up file and calculate LCR.
This script renames some variables changes some units and calculates LCR

ncap2 -4 -S scripts/gfs-tidy data/gfs20211214_06z.nc data/gfs20211214_06z-lcr.nc


ncap2 -4  -A  -S scripts/lcr.nco data/hireswhiresw20211214_00z.nc data/hireswhiresw20211214_00z-lcr.nc


