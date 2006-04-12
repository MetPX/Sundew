#!/bin/bash
# This script will change the dates of the reports in the input dir to be a 
# certain number of hours old

# edit the first test file:
NUM_HOURS_IN_FUTURE=12
INPUTDIR=`pwd`/input

# for each file in the inputdir,
for bulletin in `ls $INPUTDIR`
do
   if [ -f $bulletin ]
   then
     OLDDATE=`cat $INPUTDIR/$bulletin |cut -d' ' -f3|head -1`
     #echo "OLDDATE is: $OLDDATE"
     #NEWDATE=`date -d "+$NUM_HOURS_IN_FUTURE hour" +%d%H%M`
     NEWDATE=`date -d "+$NUM_HOURS_IN_FUTURE hour" +%d%H`00
     #echo "NEWDATE is: $NEWDATE"
   
     ../_searchAndChangeInFiles.sh "$INPUTDIR" $bulletin $OLDDATE $NEWDATE
   fi
done
