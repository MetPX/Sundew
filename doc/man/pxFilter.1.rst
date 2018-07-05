
==========
 PXFilter
==========

----------------------------------------
Metpx program to manage filter processes
----------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite


SYNOPSIS
========

**pxFilter** *filter_name* [ *start|stop|restart|reload|status* ]...

DESCRIPTION
===========

A filter, in the METPX suite, is a program that scans endlessly its queue directory namely
$PXROOT/fxq/"filter_name" for the reception of products. Once a product arrives, the filter
processes it according to its configuration, puts the derived product into the product database
(simple file/directory hiearchy) and distributes the product to any METPX filters,senders,tranceivers
(if any) that are configured to process it.

The configuration of a filter is a simple ascii file. It must be placed in 
directory $PXROOT/etc/fx (PXROOT is usually /apps/px). The file's name must be
the filter_name with the suffix .conf. For example, if file $PXROOT/etc/fx/from-gif-to-png.conf
exists and is syntactically correct, then the following commands are valid::
   
   pxFilter from-gif-to-png start
   pxFilter from-gif-to-png restart
   pxFilter from-gif-to-png reload
   pxFilter from-gif-to-png status
   pxFilter from-gif-to-png stop

The action arguments do simply what they mean. 

**reload**
reloads the filter configuration and possibly the routing table. After reloading, the program resumes to its normal state.
    
**restart**
restarts the filter. It is equivalent to a stop followed by a start.
    
**start**
starts the filter program. It includes : saving the process id in the lock file $PXROOT/fxq/"filter_name"/.lock,
loading its configuration and possibly the routing table, and starting the filtering process which depends of the filter's configuration.
    
**status**
returns the state of filter (running, locked or stopped). It gets the process id in the lock file $PXROOT/fxq/"filter_name"/.lock (if not found the filter is assumed to be stopped), than check to see if the pid is a running process... If the pid is found but the process is not, the filter is assumed to be locked
    
**stop**
stops the filter program. It includes a proper handling of file processing (if any) and it removes the lock file in the $PXROOT/fxq/"filter_name"/.lock.

RECEIVER TYPES
==============

The possible type are :

**filter**
the routing of the converted product is done without consideration to its content. The filename is used to route the file to the clients (see imask, emask, accept, reject directives).

**filter-bulletin**
the routing of the converted product considers its content; it must be a meteorological bulletin.

CONFIGURATION
=============

As said earlier, the configuration file for a filter resides in $PXROOT/etc/fx/"**FilterName**".conf
The syntax of the file is simple. A comment is a line that begins with **#**. Empty lines are permitted.
To declare or set an option you simply use one of these form (depending on the option) ::

  **option <value>**
  **option <value1,value2,...>**
  **option <value1 value2 ...>**

GENERAL CONFIGURATION OPTIONS
=============================

**fx_script script (default:None)**
Filter configuration must define a script.  The script must be in python and reside in $PXROOT/etc/scripts.
The fx_script must end with the line ::

         self.fx_script = module

where the module is a valid python module having 2 arguments : ipath, logger.
ipath is the path of the incoming file to apply the fx on.  logger is an internal metpx class
that can be used to log messages to the filter's log file.  It supports 3 levels of messages::

        logger.debug  ("message1")
        logger.warning("message2")
        logger.error  ("message3")

The module must return one of the 3 following:: 

        ipath         return the incoming filename path means that the filter did not apply
                      to that file (in this case the incoming file is discarted)

        opath         return the modified filename path (newly created filepath)

        None          return None means that nothing could be done with input file
                      (in this case the incoming file is discarted)

**lx_script script (default:None)**
Filter configuration may define a script that will act on all the files 
found in the filter's queue. For example, a filter that serves as a bulletin
collector would use an lx_script. The script must be in python and reside in 
$PXROOT/etc/scripts. The lx_script must end with the line ::

         self.lx_script = module

where the module is a valid python module having 2 arguments : filelist, logger.
**filelist** is a python list containing all the filepaths currently in queue.
The **logger** can be used to log messages to the filter's log file.  It supports the same 3 levels of messages as the fx_script.
The script must return a python list (that can be empty) containing the files that should be ingested (can be newly created files by the script). The lx script is responsible to get rid of the files that will not be used/ingested by the filter.

**validation boolean (default:True )**

Validate if the filename have the following form:
SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339
The priority field and the timestamp field are checked for validity.
In practice, never used for sources. But turned off if you want to
behave like the PDS.
   
PRODUCT ROUTING OPTIONS
=======================

::
  **accept <regexp pattern>**
  **reject <regexp pattern>**
  **imask <filepattern>**
  **routemask boolean (default: False)**
  **routingTable filename (default: pxRouting.conf)**
  **feed receivername**

After determining the ingest_name, the ingest_name is matched against the **accept\fR and \fBreject**
regexp patterns of the filter's configuration file. The default is for the file to be accepted.  
**reject** (exclusion) can be used to suppress reception of files with a certain pattern. 
Files suppressed are not ingested into the DB.

The filter can use a routing table (more efficient).
In that case you must do the following:

1- the **routemask** option must be set to True

2- use **accept** directives to declare the products to be filtered

3- derived products must match an **accept** directives in the configuration file
   that contains parenthesis.  The enclosed derived filename parts are 
   concatenated with "_" forming a routing key

4- use **routingTable** to set the routing table file. The default is pxRouting.conf and it must be
   located in $PXROOT/etc. The resulting possible keys from (3) must be defined in the routing table file 
   with the filters/clients/transceivers and priority. Ex.: key CHART_GIF client1,client2 3

Some filters may want to feed a receiver. The option **feed** must than be used.
Ex.: feed receiver_name_2

FILE RECEPTION OPTIONS
======================

**batch integer (default:100 )**
The maximum number of files that will be read from disk in one cycle. 

**mtime integer (default:0 )**
Number of seconds a file must not have been modified before we process it. 
If set to 0, this is equivalent to not checking the modification time.
This option is useful for files received by rcp, ftp, etc.

**noduplicates boolean (default:False )**

if set to true, the filter computes the md5checksum of the incoming product. 
It compares this number with its cached md5checksum numbers of received products. 
If a match is found, the product is not ingested.

DEVELOPER SPECIFIC OPTIONS
==========================

**sorter keyword (Default: MultiKeysStringSorter)**
other keyword could be None, StandardSorter.  Determine which type of sorter will be used. In practice, never used.

**patternMatching boolean  (Default: True)**

If the option **patternMatching** is True by default. But if it is set to False, the products' file name
will not be matched against the **accept\fR and \fBreject** regexp patterns of the sender's configuration file.
For sender of type single-file, no product is processed. For senders of type am or wmo, all products are processed.

**emask/imask <filepattern>**

**emask/imask\fR are an older version of \fBaccept/reject** and use filepattern instead of regexp pattern.
They are still working for now  but consider them obsolete.

**clientsPatternMatching boolean  (Default: True)**
If **clientsPatternMatching** is set to False, the filter will not 
scans the options **accept/reject** presents in all its client's.
The product is routed to the client. The client will have to determine
if it accepts or rejects the product.
