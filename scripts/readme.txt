****************************************************
* LCR (vehicle Loss-of-Control Risk) script documentation
* Current version 1.1.1 updated December 13, 2022
* All downloads: http://icyroadsafety.com/lcr/
****************************************************

The LCR script runs using NCO Toolkit commands in Linux. To run the script, you will need
a Linux machine (or a virtual machine running Linux in Windows or Mac). Both the NCO 
Toolkit and Ubuntu Linux are free and open-source. You can use the free Windows 
Subsystem for Linux (WSL) to install and run Ubuntu Linux within Windows (you will 
need to enable virtualization both in Windows and in your BIOS).

1.) Install the NCO toolkit and related functions in Linux. From a fresh Linux install, type
    and run the following commands in sequence:

       sudo apt-get update

       sudo apt-get install nco

       sudo apt-get install netcdf-bin

       sudo apt-get install cdo

       sudo apt-get install lynx

2.) Download the LCR script to your Linux installation. You can do this with Lynx with the
    following command:

       lynx https://icyroadsafety.com/lcr/lcr.nco

    Once the script loads in Lynx, press P to save it.
    
3.) Download model data and run the scripts: There are two ways to do this: using shell (bash)
    scripts or using manual commands.

    Using bash scripts:
    The easiest way to generate LCR and BFP data is to use the bash scripts, which
    automate the downloading of the model data, execute the LCR script and create 
    the Day 1 and Day 2 data files. Follow these instruactions to run the bash scripts:

       -Download each .sh file into Linux (links above). These need to be downloaded into the same
        Linux folder as the lcr.no script file.

       -chmod each .sh file to 755 by typing the following command and pressing enter:

           chmod 755 scriptname.sh

       -Edit the date and model run time in each script. The date format is YYYYMMDD and the model run times are HHz.
        Run the bash script by typing the following command and pressing enter:

           ./scriptname.sh

    Manual steps:
    Follow these steps to do the process manually:

       -Download model data with the ncks command. The following command will download the necessary
        parameters in model output from the NOAA Nomads server:

           ncks -v tmp2m,dpt2m,rh2m,apcpsfc,cfrzrsfc OpenDap-Model-URL outputfile.nc

        OpenDap-Model-URL is the location of the OpenDAP data file on the NOMADS server. 
        This will be different for each model. Go to the NOMADS home page and click the 
        OpenDAP link for the model you need.

       -Constrain data by latitude/longitude: You may want to limit the download of data to a specific 
        region like the CONUS or an even smaller geographic area. For example, the full global GFS
        data download for the LCR-required variables will be over 2GB. To save time and limit the data
        download to CONUS gridpoints only, use the following:

           ncks -d lat,20.0,60.0 -d lon,210.0,310.0 -v tmp2m,dpt2m,rh2m,apcpsfc,cfrzrsfc OpenDap-Model-URL outputfile.nc

       -Run the LCR script on the downloaded model data file. Run the following command to calculate
        LCR and BFP from the downloaded data:

           ncap2 -4 -S lcr.nco downloaded-model-data-file.nc outputfile-lcr.nc

        downloaded-model-data-file.nc is the outputfile.nc from the previous download step,
        outputfile-lcr.nc here is the final file containing the LCR and BFP calculations.
        
       -Generate 24-hour maximum charts: The ncwa command can generate a new .nc file
        containing maximum LCR or BFP values over a specified time period.

           ncwa -v lcr -d time,startframe,endframe -a time -y max inputfile-lcr.nc outputfile-lcrmax.nc

       -Replace startframe with the time step number where you want the maximum value calculation to
        begin, replace endframe with the time step number where you want it to end.

        For 1-hour models like the HRRR, there are 24 timesteps in a day. For models like the GFS
        which use 3-hour time steps, there are 8 timesteps in a day. If you wanted to perform a maximum
        calculation for the 00z HRRR for the 24-hour period ending at 00z the following day, the
        startframe would be 1 and the endframe would be 24. For the same situation with the 00z GFS,
        the startframe would be 1 and the endframe would be 8. If you wanted to do a "Day 2" forecast
        for tomorrow (00z tonight through 00z tomorrow) from the 18z HRRR, you would make the startframe
        6 and the endframe 30.

        Example: 24-hour maximum LCR chart from the 00z HRRR:

           ncwa -v lcr -d time,1,24 -a time -y max inputfile-lcr.nc outputfile-lcrmax.nc

        Example: Day 2 24-hour maximum BFP chart from the 18z HRRR:

           ncwa -v bfp -d time,6,30 -a time -y max inputfile-bfp.nc outputfile-bfpmax.nc

4.) Copy the final LCR data files to Windows (in WSL): Type the following command to open the Linux 
    directory in a Windows File Explorer window (note the space and period after exe):

       explorer.exe .

    You can drag-and-drop or copy the .nc data files over to Windows this way. This folder does
    not auto-refresh, you'll need to manually refresh it to see new/changed Linux files. Note:
    This file transfer menthod only works in one direction, Linux > Windows. Files copied from
    Windows to Linux this way are often not readable in Linux.

5.) Use the data viewer of your choice to generate charts from the resulting files. The free 
    software McIDAS-V is a good way to generate charts of the resulting data. Choose the "color
    shaded plan view" and download the XML files to import the color scale for LCR or BFP, and
    set the scale range from 0 to 12 for LCR or 0 to 0.1 for BFP.

Script Version Notes

  Version 1.1.1

   -Added Piedmont/Coastal Plain of North Carolina and Tidewater/southeastern Virginia to the
    reduced de-icing region. LCR is now increased by 1 in these areas, the same value as assigned
    to the area between the 35°N and 34°N latitudes.

  Version 1.1

   -Fixed an error with the temperature history factor variable not converted to Fahrenheit. Since
    the threshold of this factor is 32, the value being in Celsius meant that it would always
    trigger the temperature history factor LCR increment. This caused LCR to be 1 point higher
    everywhere on the map and causing all LCR-activated gridpoints to start at 2 instead of 1.

   -Rewrote the LCR processing section to add the lcron variable as the "master" control in the 
    conditional factor "where" statements. This ensures the incremental factors don't activate at
    a gridpoint when LCR is zero.
    
   -Increased the temperature threshold of LCR-1 to 38°F and a wet bulb temp of 33°F. This should
    help ensure that the vast majority of above-freezing heavy snow events trigger LCR at a gridpoint.

   -Lowered the relative humidity thresholds for the freezing fog factors to 92 percent for LCR-1
    and 98 percent for LCR-2. This should help to catch more of the lower-end freezing fog events
    that can initiate at lower RH levels.
    
   -Added freezing rain precipitation type to the below-freezing temperature factor. This is meant
    to maintain increased LCR for freezing rain events occuring at temperatures above freezing.
