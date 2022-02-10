====
 PX
====

-------------------------------------
Metpx program to manage all processes
-------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite

SYNOPSIS
========

**px** [ *graceful|start|stop|restart|reload|status* ]

DESCRIPTION
===========

In the METPX suite, the px program globally manage all metpx processes.
Any actions performed using the px program will act on all metpx receiver,filters,senders and transceivers.
The px program doesn't need any configuration. Instead, the program determines all available and possible
metpx processes by searching through::

      $PXROOT/etc/rx      for valid  receiver   configuration files
      $PXROOT/rxq/*/.lock for active receiver   processes

      $PXROOT/etc/fx      for valid  filter     configuration files
      $PXROOT/fxq/*/.lock for active filter     processes

      $PXROOT/etc/tx      for valid  sender     configuration files
      $PXROOT/txq/*/.lock for active sender     processes

      $PXROOT/etc/trx     for valid tranceiver  configuration files

Going through all this information the px program determines which processes to act on.
The possible actions are ::

   px graceful
   px start
   px restart
   px reload
   px status
   px stop

The action arguments do simply what they mean. 
.TP
**graceful**
all metpx processes are asked to restart gracefully. It is equivalent to a stop followed by a start, but with a 1 second gap between each configuration.
.TP
.TP
**reload**
all metpx processes are asked to reload. This includes the routing table, the station dictionnary, the configuration file, and the determination of potential clients (for receivers,filters,transceivers). After reloading, the programs resume to their normal state.
.TP
**restart**
all metpx processes are asked to restart. It is equivalent to a stop followed by a start.
.TP
**start**
all metpx processes are asked to start. It includes : saving the process id in their lock file,
loading their configuration, getting informations about all possible clients (for receivers,filters,tranceivers), 
loading the routing table, stations table, and starting their individual product processing.
.TP
**status**
the state of all metpx processes is returned. The state is either running, locked or stopped. For each process, px gets the process id in its lock file (if not found the process is assumed to be stopped), than check to see if the pid is a running process... If the pid is found but the process is not, the process is assumed to be locked
.TP
**stop**
all metpx processes are asked to stop. It includes a proper handling of the socket buffer (if any), the termination of file processing (if any) and the removal of the lock files.
