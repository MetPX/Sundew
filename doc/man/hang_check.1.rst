============
 hang_check
============

-----------------------------------------------------------
hang_check \- Metpx script to check that no process is hung
-----------------------------------------------------------


:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite


SYNOPSIS
========

**hang_check**

DESCRIPTION
===========

Automatically set in the crontab.
This solve the problem when an client has a communication problem.
If the timeout is not set it may happen that the process hangs forever.
The script check the age of the log file, and the age of the file in queue.
If a file has been sitting there for more than 5 mins and nothing is logged
than the process is restarted.
