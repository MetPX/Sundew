#!/bin/ksh

# defining important variable

   export LOG=/var/log/px
   export TXQ=/var/spool/px/txq

   if [[ ! -z `echo $PXROOT` ]]; then
      export LOG=${PXROOT}/log
      export TXQ=${PXROOT}/txq
   fi

   export PATH=/apps/px/bin:$PATH

# awk instruction for the latest valid log line

   cat << EOF  > /tmp/awk_instructions
   BEGIN { v["[INFO]"] = 1; v["[WARNING]"] = 1; v["[ERROR]"] = 1; }
   { if ( \$3 in v ) line = \$0 }
   END { print line }
EOF

# check for hanging senders : loop on all running senders

   for sender in `px status | grep Sender | grep "is running" | awk '{print $2}'`; do

#      get most recent file in queue

       file=`ls -alrtR ${TXQ}/$sender/[12345]* | grep "^-" | grep -v lock | awk '{print $9}' | tail -1`
       if [[ -z "$file" ]]; then
           continue;
       fi
       file=`find ${TXQ}/$sender -type f | grep $file`

#      get most recent valid log line

       line=`cat ${LOG}/tx_$sender.log | awk -f /tmp/awk_instructions`
       if [[ -z "$line" ]]; then
           continue;
       fi

#      get time of most recent file to send  and
#      get time of latest log entry for that sender

       fxtime=`echo $file | sed 's/^.*://'`
       lxtime=`echo $line | awk '{ print $1 " " $2 }'` 

#      did not find one or the other... skipped

       if [[ -z "$fxtime" || -z "$lxtime" ]]; then
          continue;
       fi

#      reformat both dates for the date command usage

       ftime=`echo $fxtime | sed 's/^\(........\)\(..\)\(..\)\(..\)/\1 \2:\3:\4/'`
       ltime=`echo $lxtime | sed 's/,.*$//' | sed 's/-//g'`

#      find both epocal date in seconds

       sftime=`date -s "$ftime" +%s 2> /dev/null`
       sltime=`date -s "$ltime" +%s 2> /dev/null`

#      compute difference between last file arrival and last log entry

       (( shtime = sftime - sltime ))

#      if it is less than 5 minutes (300 seconds) skipped

       if (( shtime < 300 )); then
          continue
       fi

#      after 3 sec : check if file is sent

       sleep 3
       if [[ ! -f $file ]]; then
          continue
       fi

#      if some files have been waiting in queue for at least
#      5 minutes restart the sender

       echo `date +'%Y-%m-%d %H:%M:%S'` $sender "hung for " $shtime "seconds ...restarted" >> ${LOG}/hang_check.log
       pxSender $sender stop
       pxSender $sender start

   done

   rm /tmp/awk_instructions
