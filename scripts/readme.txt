** How to run the LCR script on model data **

The LCR script runs using NCO Toolkit commands in Linux.  To run the script, you will need a Linux machine (or a virtual machine running Linux in Windows or Mac). Both the NCO Toolkit and Ubuntu Linux are free and open-source. You can use the free Windows Subsystem for Linux (WSL) to install and run Ubuntu Linux within Windows (you will need to enable virtualization both in Windows and in your BIOS).

1.) Install the NCO toolkit in Linux. Install NCO with the following command:

	sudo apt-get install nco

If your Linux installation is new, you may get an error when running the above command. If that occurs, run the following command first:

	sudo apt-get update

2.) Download the lcr.nco script to your Linux installation. The URL for the script is:

	https://icyroadsafety.com/lcr/lcr-gfs.nco

You can use a browser like Lynx for this (install it with the command "sudo apt-get install lynx")
    
3.) Download model data with the ncks command. The following command will download the necessary parameters in model output from the NOAA Nomads server. Just replace the date in the command and the desired run of the model (00z, 06z, 12z, 18z for example):

	ncks -v tmp2m,dpt2m,rh2m,apcpsfc,cfrzrsfc https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20221201/gfs_0p25_12z gfs20221201_12z.nc

To limit the download to CONUS gridpoints:

	ncks -d lat,20.0,60.0 -d lon,210.0,310.0 -v tmp2m,dpt2m,rh2m,apcpsfc,cfrzrsfc https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20221205/gfs_0p25_18z gfs20221205_18z.nc
    
4.) Run the LCR script on the downloaded model data file. Edit the following command with the correct date and model run that you downloaded in the previous step, then run:

	ncap2 -4 -S lcr.nco gfs20211214_06z.nc gfs20211214_06z-lcr.nc

5.) Use the data viewer of your choice to generate charts from the resulting file. The free software McIDAS (https://www.ssec.wisc.edu/mcidas/) can generate charts of the resulting data. Choose the "color shaded plan view" and download the XML files to import the color scale for LCR or BFP, and set the scale range from 0 to 12 for LCR or 0 to 0.25 for BFP.

6.) To generate Day 1 and Day 2 forecast charts: The ncwa command generates a new .nc file containing maximum LCR values over a specified time period.

For a Day 1 forecast (06z to 00z) from the 00z GFS (gfs20221205_00z-lcr.nc is the input filename, gfs20221205_00z-lcrmax.nc is the output filename):

	ncwa -v lcr -d time,1,8 -a time -y max gfs20221205_00z-lcr.nc gfs20221205_00z-lcrmax.nc

For a Day 1 forecast (12z to 00z) from the 06z GFS (gfs20221205_06z-lcr.nc is the input filename, gfs20221205_06z-lcrmax.nc is the output filename):

	ncwa -v lcr -d time,1,6 -a time -y max gfs20221205_06z-lcr.nc gfs20221205_06z-lcrmax.nc

For a Day 1 forecast (18z to 00z) from the 12z GFS (gfs20221205_12z-lcr.nc is the input filename, gfs20221205_12z-lcrmax.nc is the output filename):

	ncwa -v lcr -d time,1,4 -a time -y max gfs20221205_12z-lcr.nc gfs20221205_12z-lcrmax.nc

For a Day 2 forecast (00z to 00z) from the 12z GFS (gfs20221205_12z-lcr.nc is the input filename, gfs20221205_12z-lcrmax.nc is the output filename):

	ncwa -v lcr -d time,3,12 -a time -y max gfs20221205_12z-lcr.nc gfs20221205_12z-lcrmax.nc

For a Day 2 forecast (00z to 00z) from the 18z GFS (gfs20221205_18z-lcr.nc is the input filename, gfs20221205_18z-lcrmax.nc is the output filename):

	ncwa -v lcr -d time,1,10 -a time -y max gfs20221205_18z-lcr.nc gfs20221205_18z-lcrmax.nc
