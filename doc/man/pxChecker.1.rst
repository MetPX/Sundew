
===========
 pxChecker
===========

----------------------------------------------------
Metpx script to check that all processes are running
----------------------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite


SYNOPSIS
========

**pxChecker**

DESCRIPTION
===========

Automatically set in the crontab.
This script verifies that all metpx processes are currently running.
If you stop a process it .lock file will not be present in its queue and
therefore pxChecker will assume that the associated process is stopped and
should not be running for now. If the .lock file is present, it contains
the pid of the process and this process should be executing or else pxChecker
will restart that process.
