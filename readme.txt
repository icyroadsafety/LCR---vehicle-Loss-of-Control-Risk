****************************************************
* LCR (vehicle Loss-of-Control Risk) script documentation
* Current version 1.1 updated Dcember 7, 2022
* All downloads: http://icyroadsafety.com/lcr/
****************************************************

The LCR script runs using NCO Toolkit commands in Linux. To run the script, you will need a Linux machine (or a virtual machine running Linux in Windows or Mac). Both the NCO Toolkit and Ubuntu Linux are free and open-source. You can use the free Windows Subsystem for Linux (WSL) to install and run Ubuntu Linux within Windows (you will need to enable virtualization both in Windows and in your BIOS).

Install the NCO toolkit and related functions in Linux. From a fresh Linux install, type and run the following commands in sequence:

    sudo apt-get update

    sudo apt-get install nco

    sudo apt-get install netcdf-bin

    sudo apt-get install cdo

Download the LCR script to your Linux installation. The URL for the script is:

       https://icyroadsafety.com/lcr/lcr.nco

   You can use a browser like Lynx for this (install it with the command "sudo apt-get install lynx").

Download model data with the ncks command. The following command will download the necessary parameters in model output from the NOAA Nomads server:

       ncks -v tmp2m,dpt2m,rh2m,apcpsfc,cfrzrsfc OpenDap-Model-URL outputfile.nc

    OpenDap-Model-URL is the location of the OpenDAP data file on the NOMADS server. 
    This will be different for each model. Go to the NOMADS home page and click the
    OpenDAP link for the model you need.

    Constrain data by latitude/longitude: You may want to limit the download of data to a
    specific region like the CONUS or an even smaller geographic area. For example, the 
    full global GFS data download for the LCR-required variables will be over 2GB. To 
    save time and limit the data download to CONUS gridpoints only, use the following:

        ncks -d lat,20.0,60.0 -d lon,210.0,310.0 -v tmp2m,dpt2m,rh2m,apcpsfc,cfrzrsfc OpenDap-Model-URL outputfile.nc

Run the LCR script on the downloaded model data file. Run the following command to calculate LCR and BFP from the downloaded data:

       ncap2 -4 -S lcr.nco downloaded-model-data-file.nc outputfile-lcr.nc

    downloaded-model-data-file.nc is the outputfile.nc from the previous download step, 
    outputfile-lcr.nc here is the final file containing the LCR and BFP calculations.

Use the data viewer of your choice to generate charts from the resulting file. The free software McIDAS is a good way to generate charts of the resulting data. Choose the "color shaded plan view" and download the XML files to import the color scale for LCR or BFP, and set the scale range from 0 to 12 for LCR or 0 to 0.1 for BFP.

To generate Day 1 and Day 2 forecast charts: The ncwa command generates a new .nc file containing maximum LCR or BFP values over a specified time period.

        ncwa -v lcr -d time,startframe,endframe -a time -y max inputfile-lcr.nc outputfile-lcrmax.nc

    Replace startframe with the time step number where you want the maximum 
    value calculation to begin, replace endframe with the time step number where you want it to end.

    For 1-hour models like the HRRR, there are 24 timesteps in a day. For models like the 
    GFS which use 3-hour time steps, there are 8 timesteps in a day. 

    If you wanted to perform a maximum calculation for the 00z HRRR for the 24-hour period 
    ending at 00z the following day, the startframe would be 1 and the endframe would be 24.
    For the same situation with the 00z GFS, the startframe would be 1 and the endframe 
    would be 8. If you wanted to do a "Day 2" forecast for tomorrow (00z tonight through
    00z tomorrow) from the 18z HRRR, you would make the startframe 6 and the endframe 30.

    Example: 24-hour maximum LCR chart from the 00z HRRR:

       ncwa -v lcr -d time,1,24 -a time -y max inputfile-lcr.nc outputfile-lcrmax.nc

    Example: 24-hour maximum Day 2 BFP chart from the 18z HRRR:

       ncwa -v bfp -d time,6,30 -a time -y max inputfile-lcr.nc outputfile-bfpmax.nc
