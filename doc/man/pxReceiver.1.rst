============
 PXReceiver
============

------------------------------------------
Metpx program to manage receiver processes
------------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite


SYNOPSIS
========

**pxReceiver** *receiver_name* [ *start|stop|restart|reload|status* ]...

DESCRIPTION
===========

A receiver, in the METPX suite, is a program that waits (directory watching or socket 
reading) for the reception of products. When a product arrives, the receiver processes it according 
to its configuration, puts the product into the product database (simple file/directory hiearchy)
and queues the product up for any METPX filters,senders,tranceivers (if any) 
configured to process it.

The receiver configuration is a simple ascii file. It must be placed in directory 
$PXROOT/etc/rx (PXROOT is usually /apps/px). The file's name must be
the receiver_name with the suffix .conf. For example if file $PXROOT/etc/rx/wmo-bulletins.conf
exists and is syntaxically correct than the following commands are valid ::

   pxReceiver wmo-bulletins start
   pxReceiver wmo-bulletins restart
   pxReceiver wmo-bulletins reload
   pxReceiver wmo-bulletins status
   pxReceiver wmo-bulletins stop

The action arguments do simply what they mean. 
   
**reload**
reloads the receiver configuration. It includes the routing table, the station dictionnary, the config file, and the determination of potential clients. After reloading, the program resumes to its normal state.

**restart**
restarts the receiver. It is equivalent to a stop followed by a start.

**start**
starts the receiver program. It includes : saving the process id in the lock file $PXROOT/rxq/"receiver_name"/.lock,
loading its configuration, getting informations about all possible clients (receivers,filters,senders,tranceivers), 
loading the routing table, stations table, and starting the receiving process which depends of the receiver
type in its config.

**status**
returns the state of receiver (running, locked or stopped). It gets the process id in the lock file $PXROOT/rxq/"receiver_name"/.lock (if not found the receiver is assumed to be stopped), than check to see if the pid is a running process... If the pid is found but the process is not, the receiver is assumed to be locked
.TP
**stop**
stops the receiver program. It includes a proper handling of the socket reading buffer (if any), the termination of file processing (if any) and it removes the lock file $PXROOT/rxq/"receiver_name"/.lock.
.SH RECEIVER TYPES
The possible type are :

**am**
open/read a socket using the Alpha Manager (AM) protocol (Environment Canada proprietary). The incoming data are bulletins.

**amqp**
open/read a socket using the Advanced Messaging Queue Protocol (AMQP). The incoming data are bulletins.


**wmo**
open/read a socket using WMO protocol. The incoming data are bulletins.

**bulletin-file**
the directory $PXROOT/rxq/"receiver_name" is scannned endlessly. Any files written in that directory is considered a new product to process. When a file is processed, there is an important consideration to its content; it must be a meteorological bulletin.

**collector**
the directory $PXROOT/rxq/"receiver_name" is scannned endlessly. Any files written in that directory must be a meteorological bulletin. Rules in the configuration defines how bulletins will be collected (per bulletin type). The receiver ingests (databasing and client distribution) only the resulting "collected" bulletins. 

**single-file**
the directory $PXROOT/rxq/"receiver_name" is scannned endlessly. Any files written in that directory is considered a new product to process. The file is processed without consideration to its content. The file name is used to route the file to the clients (see imask, emask, accept, reject directives).

**pull-bulletin**
the configuration defines a remote host and an account to use. It also defines directories and files to retrieve from that site. New files are retreived and written into the receiver directory $PXROOT/rxq/"receiver_name". The rest of the process is identical to a receiver of type bulletin-file. When the receiver directory holds a file named .sleep, the receiver doesn't get any file. The .sleep file becomes useful on a clustered implementation of metpx.

**pull-file**
the configuration defines a remote host and an account to use. It also defines directories and files to retrieve from that site. New files are retreived and written into the receiver directory $PXROOT/rxq/"receiver_name". The rest of the process is identical to a receiver of type single-file. When the receiver directory holds a file named .sleep, the receiver doesn't get any file. The .sleep file becomes useful on a clustered implementation of metpx.

CONFIGURATION
=============

As stated above, the configuration file for a receiver resides in $PXROOT/etc/rx/"**ReceiverName**".conf
The syntax of the file is simple. A comment is a line that begins with **#**. Empty lines are permitted.
To declare or set an option you simply use one of these form (depending on the option) ::

  **option <value>**
  **option <value1,value2,...>**
  **option <value1 value2 ...>**

GENERAL CONFIGURATION OPTIONS
=============================

**type keyword (default: none)**

This option defines the type of the receiver... keyword is one of::

    am              - receive and ingest bulletins using AM  protocol through a socket
    amqp            - receive and ingest bulletins using AMQP protocol 
    wmo             - receive and ingest bulletins using WMO protocol through a socket
    bulletin-file   - receive and ingest files that contain bulletin
    collector       - receive files that contain bulletin, create and ingest collections
    single-file     - receive and ingest plain files (like PDS)
    pull-bulletin   - retrieve bulletins from remote host then ingest them as bulletin-file
    pull-file       - retrieve products  from remote host then ingest them as single-file


**extension string (default:  MISSING:MISSING:MISSING:MISSING:)**

The extension is a text to be added to the end of a file name to make it suitable for ingest into metpx.
Five fields separated by four colons.  keyword substitutions are supported:: 

    -CCCC           - replaced by the bulletin origin site
    -TT             - replaced by the bulletin type (first 2 letters)
    -PRIPRIOTY      - replaced by the bulletin priority found in the routing table
    -NAME           - replaced by the receiver's name

For bulletins, the convention is: extension -NAME:-CCCC:-TT:-CIRCUIT:Direct

In general, we choose the extension's fields to be: originSystem:originSite:dataType:priority:dataFormat
This extension is suffixed with a timestamp (20051116212028) will be added to the ingested file or bulletin.

**fx_script script (default:None)**
For receiver that do not process bulletins, it is possible to define a script to modify the file's content.
The script must be in python and reside in $PXROOT/etc/scripts.  The fx_script must end with the line ::


         self.fx_script = module

where the module is a valid python module having 2 arguments : ipath and logger.
ipath is the path of the incoming file to apply the fx on.  logger is an internal metpx class
that can be used to log messages to the receiver's log file.  It supports 3 levels of messages ::

        logger.debug  ("message1")
        logger.warning("message2")
        logger.error  ("message3")

The module must return one of the 3 following :: 

        return ipath  (means that the input file is accepted as is )
        return opath  (means that the new file opath was created from the
                       input file, opath is ingested and ipath discarded)
        return None   (means that nothing could be done with input file
                       no file will be ingested, ipath is discarded)

**pull_script script (default:None)**
Receiver that are not pull-file or pull-bulletin can implement their own
pull mechanism. You can define a script that will retrieve the files
into the receiver's queue directory prior to their ingestion. For example,
a receiver that gets and ingests products from the web would implement a
pull_script. The script must be in python and reside in $PXROOT/etc/scripts.
The pull_script must end with the line ::

         self.pull_script = module

where the module is a valid python module having 3 arguments : flow, logger, sleeping.
The flow is more for development. It is the receiver's python class. You would use it
if you would like to implement options in the receiver to be used in the pull_script.
The **logger** can be used to log messages into the receiver's log file exactly as 
described for the fx_script option.  **sleeping** is a boolean for the presence of
a .sleep file in the receiver's queue (see pull-file or pull-bulletin).
The script must return a python list (that can be empty) containing the filepaths of
the pulled files. The pull script is responsible to make sure it will not retrieve the
same files over and over again.
   
**validation boolean (default:False )**
   
Validate that the file name has the following form:
SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339
The priority field and the timestamp field are checked for validity.
In practice, never used for sources. Turn on to emulate PDS behaviour.
   
PRODUCT ROUTING OPTIONS
=======================

::   
  **accept <regexp pattern>**
  **reject <regexp pattern>**
  **routemask boolean (default: False)**
  **routingTable filename (default: pxRouting.conf)**
  **feed receivername**

After determining the ingest_name, the ingest_name is matched against the 
**accept** and **reject** regexp patterns of the receiver's
configuration file.  The default is for the file to be accepted.  **reject** can be
used to suppress reception of files with a certain pattern. Files suppressed are not
ingested into the DB.

If the receiver processes bulletins, the routing table is always used.  The key 
generated from a bulletin is T1T2A1A1ii_CCCC (see wmo bulletin definition). For 
example  SACN31_CWAO .

When products are not bulletins, the receiver may still use a routing table 
(more efficient).
In that case you must do the following:

1- the **routemask** option must be set to True

2- **accept** directives must contains parenthesis. 
   The enclosed filename parts are concatenated with "_" forming the key

3- use option **routingTable** to define the routing table file (default pxRouting.conf)
   The file must be located in $PXROOT/etc. 

4- The resulting possible keys from (2) must be defined in the routing table file 
   with their clients and priority. Ex.: key CHART_GIF client1,client2 3

If the routemask is false, then routing is like the PDS, applying routing masks of all clients instead of a routing table.

Some receivers may want to have another receiver as client. 
The option **feed** must than be used.
Ex.: feed receiver_name_2

FILE RECEPTION OPTIONS
======================

These options applies for all receivers except AM and WMO which use sockets 
instead of files.

**batch integer (default:100 )**
The maximum number of files that will be read from disk in one cycle. 

**mtime integer (default:0 )**
Number of seconds a file must not have been modified before we process it. 
If set to 0, this is equivalent to not checking the modification time.
This option is useful for files received by rcp, ftp, etc.

**noduplicates boolean (default:False )**

If set to true, the receiver computes the MD5 checksum of the incoming product. 
It compares this number with its cache of MD5 checksums from products already received.
If a match is found, the product is not ingested.


TYPE AM SPECIFIC OPTIONS
========================

**port integer (default:None)**
Port to bind for the AM reception.

**arrival type min max**
Mapping of what the valid times to receive a given type of bulletin are.
In the following example for CA's, -5 or +20 minutes versus the issue time is 
the valid interval::

       arrival CA 5 20


**AddSMHeader boolean (Default: False)**
True if a header is to be inserted at the beginning of a SM or SI bulletins.
The header is of the form: "AAXX jjhh4\\n". 

**keepAlive boolean (Default:True)**
This option set the unix socket option SO_KEEPALIVE to the value of that option

TYPE AMQP SPECIFIC OPTIONS
==========================

**destination url (Default: None )**
**url** stands for Uniform Resource Locator and can be used to designate where
the amqp receiver should connect to.::

  The url syntax is   ampq://user:password@remotehost//realm
  Ex. :
       destination amqp://guest:totospw@rabbitmqhost//data

TYPE PULL-BULLETIN or BULLETIN-FILE SPECIFIC OPTION
===================================================

**addStationInFilename (Default: True )**
This option is used to add or not the station name in the filename.

TYPE WMO SPECIFIC OPTIONS
=========================

**port integer (default:None)**
Port to bind for the WMO reception.

**keepAlive boolean (Default:True)**
This option set the unix socket option SO_KEEPALIVE to the value of that option

TYPE COLLECTION SPECIFIC OPTIONS
================================

**header type (Default: None)**
Defines a bulletin header to collect. Ex.:  header SA

**issue hourlist primary secondaries (Default: None)**
Defines how to collect the header. hourlist is a comma separated list of hours or the keywork 'all'
primary is the minute after the collect hour to issue the primary collection.
secondaries is the cycle in minutes to issue the other bulletins received 
after the primary collection Ex.::

    issue all 7 5
                    collect all hours, 
                    primary issue is 7 mins after the hour
                    secondaries are issued in cycle of 5 mins after
                                the primary so at the hour past 12,17...etc

    issue 0,6,12,18 12 5
                    collect data at 0,6,12,18
                    primary issue is 12 mins after the collect hour
                    secondaries are issued in cycle of 5 mins

**history hours (Default: 24 )**
The amount of time in hours for which it is valid to collect a bulletin
Ex.: history 24  means that a bulletin older than 24 hours is not collected.

**future minutes (Default: 40)**
Specified in minutes.  Maximum limit to consider valid a report dated in the future

TYPE PULL SPECIFIC OPTIONS (pull-bulletin,pull-file)
====================================================

**protocol (Default: ftp )**
For the moment only protocol ftp and sftp are supported by the pulls

**host remotehost (Default: None )**
the host where we are going to pull the files

**user username (Default: None )**
the user on the remote host where we are going to use to pull the files

**password pw (Default: None )**
the password for the user  on the remote host

**key_file path (Default: None )**
When sftp is used, key_file gives the path to the ssh key
for the username given by the user option.

**ftp_mode mode (Default: passive )**
the ftp mode is either active or passive.

**directory <dir>**

::
  directory //absolute/directory
  directory /relative/directory

defines the directory where the files are going to be pulled

Some pattern placed anywhere in the directory name are going to
be systematicaly replaced ::

  ${YYYYMMDD}     replaced by today's date
  ${YYYYMMDD-1D}  replaced by yesterday's date
  ${YYYYMMDD-2D}  replaced by the date  2 days earlier than today
  ${YYYYMMDD-3D}  replaced by the date  3 days earlier than today
  ${YYYYMMDD-4D}  replaced by the date  4 days earlier than today
  ${YYYYMMDD-5D}  replaced by the date  5 days earlier than today

**get <regexp>**

defines a regexp pattern for filename matching to get.
Ex.:  get .*CHART    will get all files that ends with CHART

**timeout_get seconds (default:30)**
set the elapsed time after which a get will be considered timed out.

**pull_sleep seconds (default:300)**
set the remote host polling interval. 

**delete boolean (default:False)**
Once a file was retrieved, determines whether it is deleted on the remote host.

**pull_prefix string (default:\'\')**

When a file is pulled, modify its name, by prefixing it with string.
Keyword  HDATETIME  can be used to prefix the filename with the remote host
datetime for the pulled file... the prefix has a YYYYMMDDhhmm\_  form.

DEVELOPER SPECIFIC OPTIONS
==========================

**sorter keyword (Default: MultiKeysStringSorter)**
other keyword could be None, StandardSorter.  Determine which type of sorter will be used. In practice, never used.

**patternMatching boolean  (Default: True)**

If the option **patternMatching** is True by default. But if it is set to False, 
the products' file name will not be matched against the **accept** and **reject** 
regexp patterns of the sender's configuration file.
For sender of type single-file, no product is processed. For senders of type am or wmo, all products are processed.

**emask/imask <filepattern>**
**emask/imask** are an older version of **accept/reject** and use filepattern instead of regexp pattern.
They are still working for now  but are deprecated.

**clientsPatternMatching boolean  (Default: True)**
If **clientsPatternMatching** is set to False, the receiver will not 
scan the options **accept/reject** presents in all its client's.
The product is routed to the client. The client will have to determine
if it accepts or rejects the product.
