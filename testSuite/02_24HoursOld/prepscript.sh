#!/bin/bash
# This script will change the dates of the reports in the input dir to be a 
# certain number of hours old

# edit the first test file:
NUM_HOURS_OLD=24
INPUTDIR=`pwd`
INPUTDIR=${INPUTDIR}/input

# for each file in the inputdir,
for bulletin in `ls $INPUTDIR`
do
   if [ -f $bulletin ]
   then
     #echo "INPUTDIR is $INPUTDIR"
     #echo "bulletin is $bulletin"
     # extract the date field from the bulletin
     OLDDATE=`cat $INPUTDIR/$bulletin |cut -d' ' -f3|head -1`
     #echo "OLDDATE is: $OLDDATE"
     # calculate the date X hours ago
     NEWDATE=`date -d "-$NUM_HOURS_OLD hour" +%d%H%M`
     #echo "NEWDATE is: $NEWDATE"
   
     ../_searchAndChangeInFiles.sh "$INPUTDIR" $bulletin $OLDDATE $NEWDATE
   fi
done
