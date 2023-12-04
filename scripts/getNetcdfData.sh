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

model=$5

dtime="";
# nb last arg in command line 
case $4 in
large) dtime="-d time,0,23"
;;

medium) dtime="-d time,0,18"
;;

small) dtime="-d time,0,9"
;;

all) dtime="-d time,0,"
;;     

tst) dtime="-d time,0,1 -d lat,20,21 -d lon,0,4"
;;     
    

*) dtime="-d time,0,1"

esac

if [ "$DEBUG" -gt 0  ];then
   wget_flags="-nv"
   ncks_flags="-D 2 -O"
 else
   wget_flags="-q"
   ncks_flags="-O"
fi   

# use this variable to set the attribute  global@NoaaType
NoaaType=0

case $model in
    
    gfs)
     lcr3vars="apcpsfc,cfrzrsfc,csnowsfc,gustsfc,tcdcclm,dpt2m,rh2m,tmp2m";
     NoaaType=1  	
     ;;

    nam | nam1hr | nam_conusnet)
    lcr3vars="apcpsfc,cfrzrsfc,csnowsfc,gustsfc,tcdcclm,dpt2m,rh2m,tmp2m";
    NoaaType=2  	  	
     ;;

   hrrr)
    lcr3vars="apcpsfc,asnowsfc,cfrzrsfc,csnowsfc,gustsfc,tcdcclm,dpt2m,rh2m,tmp2m";
    NoaaType=3  	  	
     ;;

   
    *)
    lcr3vars="apcpsfc,cfrzrsfc,csnowsfc,gustsfc,tcdcclm,dpt2m,rh2m,tmp2m";
    NoaaType=0
     ;;  	

esac    



#deal with nc file here
if [ "$type" = "nc" ];then
    
   CMD="ncks -4 -L 1  $ncks_flags  $dtime -v $lcr3vars $serverpath $fullfilename";
   [ $DEBUG -gt 0 ] && echo "$CMD"
   # do command
   $CMD
   
   if [ ! -e $fullfilename ]; then 
    exit 1  
  fi  
   # check file for errors
  if grep -q '^Error ' $fullfilename   ; then
    rm $fullfilename; 
    exit 1  
  fi

  
  # delete missing_value as _FillValue is present
  # set global@NoaaType  
  ncatted -a missing_value,,d,, -a NoaaType,global,c,i,"$NoaaType" $fullfilename;

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


