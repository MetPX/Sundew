#!/bin/ksh

# decide which one we are doing

  CONF=$1
  NAME=${CONF%%.conf}
  LOG=$2

# get one test file per imask of the PDS config

  rm ./touch_test 2> /dev/null
  rm ./drop_test  2> /dev/null

  cat ${CONF} | grep imask | grep -v '#' | awk '{print $2 " " $5}' > .tmp

  PAT=`cat .tmp | awk '{print $1}'`
  for p2 in $PAT; do
      p=`echo $p2 | sed 's/\*/\.\*/g'`
      line=`grep $p ${CONF} | grep sent | head -1`
      FILE=`echo $line | awk '{print $8}' | sed 's/::2007..........:pds.//' | sed 's/:2007..........:pds.//'`
      DDIR=`grep $p .tmp | awk '{print $2}'`
      DROP=`echo $line | awk '{print $13}'`
      echo 'touch /apps/px/rxq/fromPds/'$FILE >> ./touch_test
      echo $DDIR ' ' $DROP >> ./drop_test
  done
  chmod 755 ./touch_test

# translate to px

  mup=`cat clientlist | grep $NAME | awk '{ print $2 " " $3 " " $4 }'`

  client_translate.py $NAME $mup > ./$NAME.conf.px

