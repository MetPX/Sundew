#!/bin/sh
#
# searchAndChangeInFiles.sh
#
# This script searches for files from a given point, for a given search
# pattern and replaces the found pattern with a given value
#
# Usage:
# searchAndChangeInFiles.sh <SEARCH_START_POINT> <LIKE_FILE_NAME> <SEARCH_PATTERN> <SET_TO_VALUE>
#
#
# Revision History
# ----------------
# Sept 05/2003: Kaveh     Writing version 1.0
# Aug  18/2004: Kaveh     Improved the way files are found.
# Jan  03/2006: Kaveh     Ported to Debian Linux
#
#set -x
SCRIPT_NAME=$0
SEARCH_POINT=$1
LIKE_FILE=$2
SEARCH_PATTERN=$3
SET_TO_VALUE=$4
SHOW=$5
COUNT=0
REPLACED=0

if [ $# -lt 4 ]
then
  echo -e "\nUsage:\n\t${SCRIPT_NAME} <SEARCH_START_POINT> <\"LIKE_FILE_NAME\"> <\"SEARCH_PATTERN\"> <\"SET_TO_VALUE\"> [--show-only]"
  echo -e "\n\tNOTE: use the backslash(\) character to escape keywords in the text patterns.\n\n"
  exit -1
fi
#
if [ "${SHOW}" = "--show-only" ]
then
  SHOWING="YES"
else
  SHOWING="NO"  
fi    
#
echo -e "\nSearching from directory: ${SEARCH_POINT}"
echo "Searching for files named: ${LIKE_FILE}"
echo "Search pattern: ${SEARCH_PATTERN}"
echo "Set to pattern: ${SET_TO_VALUE}"
echo "Only Show: ${SHOWING}"
#
FOUND_SET=`find "${SEARCH_POINT}" -type f -name "${LIKE_FILE}" | xargs grep -H "${SEARCH_PATTERN}" | cut -d: -f1 | uniq 2> /dev/null`
#
echo "----------------------------------------"
for FILE in ${FOUND_SET}
do 
  echo -n "- ${FILE}: "
  BEFORE=`grep ${SEARCH_PATTERN} ${FILE}`
  AFTER=`grep ${SEARCH_PATTERN} ${FILE} | sed "s+${SEARCH_PATTERN}+${SET_TO_VALUE}+g"`
  echo -e "\n  ${BEFORE}  ->  ${AFTER}" 
  
  COUNT=`expr "${COUNT}" + 1`
  #
  if [ "${SHOWING}" = "NO" ]
  then
    sed "s+${SEARCH_PATTERN}+${SET_TO_VALUE}+g" < ${FILE} > ${FILE}.new
    RC=$?
    if [ ${RC} -eq 0 ]
    then
      cat ${FILE}.new > ${FILE} && rm ${FILE}.new
      REPLACED=`expr "${REPLACED}" + 1`
    fi
  fi   
done
echo "----------------------------------------"
echo -e "${COUNT} file(s) targeted, ${REPLACED} file(s) modified.\n"


