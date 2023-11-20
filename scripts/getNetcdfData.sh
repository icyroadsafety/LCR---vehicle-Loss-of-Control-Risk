## GRAB FILES FROM GRADS NOAA SERVER
# usage GetNetcdfData.sh $serverpath $filename $type
# $filename should not  have an extension 
# $type should be one of following {nc,info,dds,das}
#
# The general usage is to check for the presence of "das" or "dds" file before 
# attempting to get a Netcdf "nc" file.
# If file exists then ncks uses the Netcdf DAP library to retrieve file data
# NB This script is specific to the Grads NOAA server -
# When file isnt present on the server a html explanation is returned
# For "das" and "dds" files the first line of output is checked 
# Return file type for "info" is a html file
#


DEBUG=0;

serverpath=$1;
fullfilename=$2;
type=$3
dtime="";


# nb last arg in command line 
case $4 in
large) dtime="-d time,0,23"
;;

medium) dtime="-d time,0,18"
;;

small) dtime="-d time,0,6"
;;

tst) dtime="-d time,0,1"
;;     
    

*) dtime="-d time,0,1"

esac

if [ "$DEBUG" -gt 0  ];then
   wget_flags="-nv"
   ncks_flags="-D 5 -O"
 else
   wget_flags="-q"
   ncks_flags="-O"
fi   




lcr3vars="apcpsfc,asnowsfc,cfrzrsfc,csnowsfc,gustsfc,tcdcclm,dpt2m,rh2m,tmp2m";



#deal with nc file here
if [ "$type" = "nc" ];then 
   ncks -4 -L 1  $ncks_flags  $dtime -v $lcr3vars $serverpath $fullfilename;
   
   if [ ! -e $fullfilename ]; then 
    exit 1  
  fi  
   # check file for errors
  if grep -q '^Error ' $fullfilename   ; then
    rm $fullfilename; 
    exit 1  
  fi

  # rename ww3 vars back to ww2 vars   
  # ncrename $rename_string $fullfilename;
  
  # as download files has _FillValue and missing_value - delete the latter
  ncatted -a missing_value,,d,, $fullfilename;

  exit 0;  
fi



case $type in

# info file about Data
info)
   wget "$wget_flags"  $serverpath -O  $fullfilename;
   result="GOOD";
;;
# Data structure
dds)
   wget "$wget_flags" $serverpath -O $fullfilename;
   if  head -1 $fullfilename | grep -iq '^Dataset' ; then
     result="GOOD";
   else
     result="BAD";
   fi    
;;

# Data Attributes Structure
das)
   wget "$wget_flags"  $serverpath -O $fullfilename "$wget_flag" ;
   if  head -1 $fullfilename | grep -iq '^Attributes' ; then
     result='GOOD';
   else
    result="BAD"
  fi    
;;

esac

if [ "$result" = "BAD" ] ; then 
    rm $fullfilename;
    exit 1
fi

# echo -n $result;

exit 0;


