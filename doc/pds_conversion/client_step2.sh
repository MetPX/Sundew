#!/bin/ksh

   set -x

   NAME=$1

   cp ./${NAME}.conf.px /apps/px/etc/tx/${NAME}.conf

   pxReceiver fromPds stop
   pxSender ${NAME} stop

   sleep 5

   rm /apps/px/log/rx_fromPds.log
   rm /apps/px/log/tx_${NAME}.log

   pxReceiver fromPds start
   pxSender   ${NAME} start
   px reload

   sleep 5

   .  ./touch_test

   echo "CHECK FOR LOG"
   echo 
   cat /apps/px/log/tx_${NAME}.log

   echo "----------------------------------------------"
   echo "CHECK FOR THIS ON GROGNE"
   echo 
   cat ./drop_test
