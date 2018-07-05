
==========
 mr-clean
==========

-----------------------------------------------------------------
Metpx script to cleanup TXQ of outdated yyyymmddhh subdirectories
-----------------------------------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite

SYNOPSIS
========

**mr-clean**

DESCRIPTION
===========

Automatically set in the crontab.
A client TXQ has the following form $PXROOT/txq/client/prio/yyyymmddhh/*products*
Each receiver or filter, will create the directory if it doesn't exist before
disseminate the product to the queue. The mr-clean cleans all outdated yyyymmddhh
subdirectories.
