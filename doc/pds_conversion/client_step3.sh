#!/bin/ksh

   NAME=$1

# rm trace in px

   pxSender ${NAME} stop
   rm /apps/px/log/${NAME}.log
   mv /apps/px/etc/tx/${NAME}.conf mv /apps/px/etc/tx/${NAME}.conf.off
   px reload
