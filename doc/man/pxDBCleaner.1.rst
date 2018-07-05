
=============
 pxDBCleaner
=============

-----------------------------------------------------
Metpx script that manages cleanups the metpx database
-----------------------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite


SYNOPSIS
========

**pxDBCleaner** [ *--days x* ]...

DESCRIPTION
===========

Automatically set in the crontab. It is called with its default
parameters which is to remove 30 days old products. There are
two ways to set up another removal limit. The first is to change
the crontab line and add the parameter "--days x" in command line or
to change the parameter "daysToKeepInDB x" in the global metpx
configuration file /etc/px/px.conf::

   pxDBCleaner
   pxDBCleaner --days x

The action argument does simply what it means.
