
==============
 PXTranceiver
==============

---------------------------------------------
Metpx program to manage transceiver processes
---------------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite

SYNOPSIS
========

 **pxTranceiver** *transceiver_name* [ *start|stop|restart|reload|status* ]...

DESCRIPTION
===========

A transceiver, in the METPX suite, is a program that is a receiver and a sender
at the same time. 

receiver part (man pxReceiver): Waits (socket reading) for the reception of products. When a product
arrives, the receiver processes it according to its configuration, puts the product into the product database  (simple  file/directory  hiearchy)
and queues the product up for any METPX filters,senders,tranceivers (if any) configured to process it.

sender part(man pxSender): Deliver products to a client.
The products it processes usually comes from a METPX receiver (or a filter). Once
a receiver databased a product and determined that a transceiver should transmit that
product, it links the database file in the transceiver's transmission directory tree...
namely under $PXROOT/txq/"transceiver_name"/priority/YYYYMMDDHH where YYYYMMDDHH is
the current date and time. The receiver will create the directory if it does not exist.
The transceiver scans endlessly all directories under $PXROOT/txq/"transceiver_name" in
search of products.  When products are present, the transceiver processes them according
to its configuration, and delivers them to the client defined in its configuration file.
The products file are finally unlinked from its transmission directory tree.
The priority is either 0,1,2,3,4,5.  A receiver will never create a 0 priority
directory.  The 0 priority directory is used for retransmission. Any product put
under the 0 priority directory will be sent to the client (without duplicate checking)
if it meets the routing criteria.

The configuration of a transceiver is a simple ascii file. It must be placed in 
directory $PXROOT/etc/trx (PXROOT is usually /apps/px). The file's name must be
the transceiver_name with the suffix .conf. For example if the 
file $PXROOT/etc/trx/aftn.conf exists and is syntactically correct, then 
the following commands are valid ::

   pxTransceiver aftn start
   pxTransceiver aftn restart
   pxTransceiver aftn reload
   pxTransceiver aftn status
   pxTransceiver aftn stop

The action arguments do simply what they mean. 

**reload**
reloads the transceiver configuration. After reloading, the program resumes to its normal state.

**restart**
restarts the transceiver. It is equivalent to a stop followed by a start.

**start**
starts the transceiver program. It includes : saving the process id in the lock file $PXROOT/rxq/"transceiver_name"/.lock,
loading its configuration, and starting the process with options defined in it's config. file.

**status**
returns the state of transceiver (running, locked or stopped). It gets the process id in the lock file $PXROOT/rxq/"transceiver_name"/.lock (if not found the transceiver is assumed to be stopped), than check to see if the pid is a running process... If the pid is found but the process is not, the transceiver is assumed to be locked

**stop**
stops the transceiver program. It includes a proper handling of the socket writing buffer (if any), the termination of file processing (if any) and it removes the lock file $PXROOT/rxq/"transceiver_name"/.lock.

TRANSCEIVER TYPES
=================

The possible types are :

**aftn**
listen for a Message Handling System (MHS) to connect or connect to a MSH via socket using 
Aeronautical Fixed Telecommunication Network (AFTN) protocol. The output data are bulletins

CONFIGURATION
=============

As said earlier, the configuration file for a transceiver resides 
in $PXROOT/etc/tx/"**TransceiverName**".conf The syntax of the file is simple. 
A comment is a line that begins with **#**. Empty lines are permitted.
To declare or set an option you simply use one of these form (depending on the option) ::

  **option <value>**
  **option <value1,value2,...>**
  **option <value1 value2 ...>**

GENERAL CONFIGURATION OPTIONS
=============================

**type keyword (default: none)**

::
  This option defines the sender type... keyword is one of:
    aftn             - AFTN   protocol socket


**extension string (default:  MISSING:MISSING:MISSING:MISSING:)**

::
  The extension is a text to be added to the end of a file name to make it suitable for ingest into metpx.
  Five fields separated by four colons.  keyword substitutions are supported:

  -CCCC           - replaced by the bulletin origin site
  -TT             - replaced by the bulletin type (first 2 letters)
  -PRIPRIOTY      - replaced by the bulletin priority found in the routing table
  -NAME           - replaced by the receiver's name

For bulletins, the convention is: extension -NAME:-CCCC:-TT:-CIRCUIT:Direct

In general, we choose the extension's fields to be: originSystem:originSite:dataType:priority:dataFormat
This extension is suffixed with a timestamp (20051116212028) will be added to the ingested file or bulletin.

**noduplicates boolean (default:True )**

if set to true, the transceiver computes the MD5 checksum of the product to send. 
It compares this number with its cached MD5 checksum of products already delivered.
If a match is found, the product is not sent.

When a client asks for a product to be retransmitted, if this option is enabled,
the product must be placed under the priority 0 directory of the transmission queue.

**validation boolean (default:False )**

Validate if the filename have the following form:
SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339
The priority field and the timestamp field are checked for validity.


**timeout integer (default:10 )**

Time between each tentative to establish a connexion


PRODUCT ROUTING OPTIONS
=======================

**routingTable filename (default: pxRouting.conf)**

When the transceiver receive bulletins, the routing table is always used (man pxRouting, man pxRouting.conf)
At the reception, the processing is exactly the same that is done by a pxReceiver (man pxReceiver) process
except that no directives like accept, reject, imask and emask can be applied on the incoming bulletins.

PRODUCT SELECTION OPTIONS (only for transmission, not reception)
================================================================

**accept <regexp pattern> [<keyword>]**
**reject <regexp pattern>**

The products' file name is matched against the **accept** and **reject** regexp patterns of
the transceiver's configuration file.  **reject** (exclusion) can be used to suppress the delivery
of files with a certain pattern. **accept** options validate filenames that are sent to the client.



**emask/imask <filepattern>**
**emask/imask** are an older version of **accept/reject** and use filepattern instead of regexp pattern.
They are still working for now  but are deprecated.

FILE TRANSMISSION OPTIONS
=========================


**batch integer (default:100 )**
The maximum number of files to be sent/written in one polling cycle. 


TYPE AFTN SPECIFIC OPTIONS
==========================

**subscriber Boolean (default: True)**
in practice, we are always a subscriber. when we do some testing,
we need a provider (MHS), so we configure a transceiver with 
subscriber False


**host remoteHostOrIP (mandatory)**
the hostname or IP with which we will establish a connexion 


**portR integer (mandatory)**
port that will be used to receive data


**portS integer (mandatory)**
port that will be used to send data


**stationID id (mandatory)**
Three capital letters defining the local id
ex: stationID DOA


**otherStationID id (mandatory)**
Three capital letters defining the "remote" id
ex: otherStationID ODA


**address 8_CAP_LETTERS (mandatory)**
Local AFTN address composed of 8 capital letters.
ex: address CWAOABCD


**otherAddress 8_CAP_LETTERS (mandatory)**
"Remote" AFTN address composed of 8 capital letters.
ex: address CWAOEFGH


**digits integer (default: 4)**
Number of digit use for the channel sequence number (CSN)
Use what your provider told you.

DEVELOPER SPECIFIC OPTIONS
==========================

**sorter keyword (Default: MultiKeysStringSorter)**
other keyword could be None, StandardSorter.  Determine which type of sorter will be used. In practice, never used.

**mtime integer (default:0 )**
Number of seconds a file must not have been modified before we process it. 
If set to 0, this is equivalent to not checking the modification time.
