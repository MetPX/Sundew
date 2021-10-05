
==========
 PXSender
==========

----------------------------------------
Metpx program to manage sender processes
----------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite


SYNOPSIS
========

**pxSender** *sender_name* [ *start|stop|restart|reload|status* ]...

DESCRIPTION
===========

A sender, in the METPX suite, is a program that deliver products to a client. 
The products it processes usually comes from a METPX receiver (or a filter). Once 
a receiver databased a product and determined that a sender should transmit that 
product, it links the database file in the sender's transmission directory tree...  
namely under $PXROOT/txq/"sender_name"/priority/YYYYMMDDHH where YYYYMMDDHH is 
the current date and time. The receiver will create the directory if it does not exist.

The sender scans endlessly all directories under $PXROOT/txq/"sender_name" in 
search of products.  When products are present, the sender processes them according 
to its configuration, and delivers them to the client defined in its configuration file.
The products file are finally unlinked from its transmission directory tree.

The priority is either 0,1,2,3,4,5.  A receiver will never create a 0 priority 
directory.  The 0 priority directory is used for retransmission. Any product put 
under the 0 priority directory will be sent to the client (without duplicate checking) 
if it meets the routing criteria.

The configuration of a sender is a simple ascii file. It must be placed in 
directory $PXROOT/etc/tx (PXROOT is usually /apps/px). The file's name must be
the sender_name with the suffix .conf. For example if the 
file $PXROOT/etc/tx/am-bulletins.conf exists and is syntactically correct, then 
the following commands are valid ::

   pxSender am-bulletins start
   pxSender am-bulletins restart
   pxSender am-bulletins reload
   pxSender am-bulletins status
   pxSender am-bulletins stop

The action arguments do simply what they mean. 

**reload**
reloads the sender configuration. After reloading, the program resumes to its normal state.
   
**restart**
restarts the sender. It is equivalent to a stop followed by a start.
   
**start**
starts the sender program. It includes : saving the process id in the lock file $PXROOT/txq/"sender_name"/.lock,
loading its configuration, and starting the sending process which depends of the sender type in its config.
   
**status**
returns the state of sender (running, locked or stopped). It gets the process id in the lock file $PXROOT/txq/"sender_name"/.lock (if not found the sender is assumed to be stopped), than check to see if the pid is a running process... If the pid is found but the process is not, the sender is assumed to be locked
   
**stop**
stops the sender program. It includes a proper handling of the socket writing buffer (if any), the termination of file processing (if any) and it removes the lock file $PXROOT/txq/"sender_name"/.lock.

SENDER TYPES
============

The possible types are :
   
**am**
open/write a socket using Alpha Manager (AM) protocol (Environment Canada proprietary). The output data are bulletins
   
**amis**
open/write a socket using AES Meteorological Information System (AMIS) protocol (Environment Canada proprietary.) The output data are bulletins.
   
**amqp**
open/write a socket using Advanced Message Queing Protocol. For the moment, its supports exclusively bulletins but there is no constraint on the message's content and other file types could be supported in the future.
   
**wmo**
open/write a socket using WMO protocol. The output data are bulletins.
     
**single-file**
When products are available, a single-file sender opens a connection to a remote 
host using the information in its configuration file (protocol, host, user,password, 
mode... etc ). It sends the files to their proper remote destination, and closes 
the connection.

CONFIGURATION
=============
   
As said earlier, the configuration file for a sender resides 
in $PXROOT/etc/tx/"**SenderName**".conf The syntax of the file is simple. 
A comment is a line that begins with **#**. Empty lines are permitted.
To declare or set an option you simply use one of these form (depending on the option) ::
   
  **option <value>**
  **option <value1,value2,...>**
  **option <value1 value2 ...>**

   
GENERAL CONFIGURATION OPTIONS
=============================
   
**type keyword (default: none)**
   
This option defines the sender type... keyword is one of::

    am              - AM   protocol socket
    amis            - AMIS protocol socket
    amqp            - AMQP protocol socket
    wmo             - WMO  protocol socket
    single-file     - user defined the protocol to use for delevery (Ex.FTP)
   
**destfn_script script (default:None)**
For senders that do not use sockets, one can define a script to modify the remote 
filename.  The script must be in python and reside in $PXROOT/etc/scripts.  The 
destfn_script must end with the line ::

         self.destfn_script = module

where the module is a valid python module having 1 argument : ipath.
ipath is the path of the incoming file to rename at destination.
The module must return a valid none empty string.

**dx_script script (default:None)**
For AM type senders, one can define a script to create derived products.  
The script must be in python and reside in $PXROOT/etc/scripts. The dx_script
must end with the line ::

         self.dx_script = module

where the module is a valid python module having 2 arguments : data, logger.
data is the incoming bulletinAm data class to apply the script to.  logger is 
an internal metpx class that can be used to log messages to the sender's log 
file.  It supports 3 levels of messages ::

        logger.debug  ("message1")
        logger.warning("message2")
        logger.error  ("message3")

The module must return one of the following :: 

        inBulletinAm  return the incoming BulletinAm data class object
        outBulletinAm return the derived  BulletinAm data class object
        None          return the python   None  keyword

If **None** is returned, nothing is sent to the client. If a BulletinAm data class object is returned (inBulletinAm or outBulletinAm), that data only is sent to the client. The incoming file is unlinked and the derived data is not retained.


**fx_script script (default:None)**
For senders that do not use sockets, it is possible to define a script to create derived products.
The script must be in python and reside in $PXROOT/etc/scripts. The fx_script must end with the line ::

         self.fx_script = module

where the module is a valid python module having 2 arguments : ipath, logger.
ipath is the path of the incoming file to apply the fx on.  logger is an internal 
metpx class that can be used to log messages to the sender's log file.  It 
supports 3 levels of messages ::

        logger.debug  ("message1")
        logger.warning("message2")
        logger.error  ("message3")

The module must return one of the following :: 

        ipath         return the incoming filename path
        opath         return the derived  filename path
        None          return the python   None  keyword

If **None** is returned, nothing is sent to the client. If a filename path is returned (ipath or 
opath), that file only is sent to the client. The incoming file and the derived file (if created)
are unlinked.

**include <filename>**

The **include** option inserts all the configuration lines present in 
**$PXROOT/etc/tx/filename** as if they were present in the sender's configuration 
file. This might be usefull when several senders in a cluster use almost exactly the
same configuration. By convention, include file is suffixed with .inc but not requiered.
(Avoid .conf, px programs would think that this file is a sender and would
result in logging errors)


**noduplicates boolean (default:True )**

if set to true, the sender computes the MD5 checksum of the product to send. 
It compares this number with its cached MD5 checksum of products already delivered.
If a match is found, the product is not sent.

When a client asks for a product to be retransmitted, if this option is enabled,
the product must be placed under the priority 0 directory of the transmission queue.


**validation boolean (default:True )**

Validate if the filename have the following form:
SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339
The priority field and the timestamp field are checked for validity.
In practice, never used for sources. But turned off if you want to
behave like the PDS.


**purgeAlias alias purgeInstructions (no default)**

::
  Used to define purge alias (illimited number of them)

  ex: purgeAlias OLD_AND_OLDER 10H,4+:16H,3 
  The existence of alias OLD_AND_OLDER will permit to use the following
  directive:

  purge OLD_AND_OLDER

**purge <purgeInstructions | alias>  (default:None)**

Used to delete old files of a given priority

ex: purge 5H,3:10H,3+ (delete files 5 hours old (and more) of priority 3 and also,
delete files 10 hours old (and more) of priority 3,4,5
ex: purge OLD_AND_OLDER (purge instructions defined by OLD_AND_OLDER will be used)

Note: if you want to delete old (5 hours and more in the following example) files no matter what the priority is, use 1+
ex: purge 5H,1+

PRODUCT SELECTION OPTIONS
=========================

::
  **accept <regexp pattern> [<keyword>]**
  **reject <regexp pattern>**

The products' file name is matched against the **accept** and **reject** regexp patterns of
the sender's configuration file.  **reject** (exclusion) can be used to suppress the delivery
of files with a certain pattern. **accept** options validate filenames that are sent to the client.
If the sender is 'single-file' than a product accepted will be placed in the nearest directory
declared before the matching **accept** declaration. The **accept** declaration has an
optional **keyword**. It overwrites the **filename** option value for the accepted products only.
As an example the two following sequence are equivalent.::

         filename WHATFN
         accept   .*:JPEG:.*

is exactly equivalent to::

         accept   .*:JPEG:.*  WHATFN

FILE TRANSMISSION OPTIONS
=========================

**batch integer (default:100 )**
The maximum number of files to be sent/written in one polling cycle. 

TYPE AM/AMIS/AMQP/WMO SPECIFIC OPTIONS
======================================

**maxLength integer**
maximum length in bytes of a bulletin to be sent. If the bulletin's length exceeds
this limit, it is segmented before being sent. (does not apply to AMQP)::

         AM's   default maxLength is 32768
         AMIS's default maxLength is 14000
         WMO's  default maxLength is 500000
         AMQP   unknown



**port integer (default:None)**
Port to connect to for the transmission.

**am_dest_thread type number**
When am type is used, the default am thread number encoded in the bulletin is 255,
which means send it to all thread. A specific thread number can be set for specific
bulletin types using this option. The * can be used to specify all bulletin types.
A valid usage example could be ::

       am_dest_thread SA 17
       am_dest_thread IS 48
       am_dest_thread * 255

TYPE SINGLE-FILE SPECIFIC OPTIONS (see note)
============================================

***** Nota Bene: amqp protocol **
When using a sender of type amqp, a subset of the single-file options are used.
Options that relate to the authentication (protocol,host,user,password,port) are
used. The directory option defines the realm (URL declaration of the directory
can set them all... see the directory option)

**protocol name (Default: ftp )**
The following protocols are supported :  file, ftp, and sftp.
The ftp and sftp protocols are use to send file on a remote host.
They require the use of options host, user, password, directory
(sftp and amqp also support user defined port number through the port option).
If there is only one directory the option destination can replace
the others.  When using sftp the option key_file must be provided.

The file protocol is used to put the files in local directories. 

**host remotehost (Default: None )**
the host where we are going to put the files

**port portnumber (Default: None )**
the port used by the protocol. Currently, only sftp supports user defined port.

**user username (Default: None )**
the user on the remote host where we are going to use to put the files

**password pw (Default: None )**
the password for the user  on the remote host

**key_file path (Default: None )**
When sftp is used, key_file gives the path to the ssh key
for the username given by the user option.

**binary (Default: True )**
ftp mode type is binary by default.
When binary is set to false the ftp mode type is ascii.

**kbytes_ps (default: -1 )**
By default, for protocol ftp, the file is send without
any speed check (no bandwidth limiting).  When kbytes_ps 
is set to a positive integer the file sending are limited
to that speed.

**directory dir (Default:'.')**
defines the directory where the files are going to be sent
When amqp is used the directory corresponds to the realm::

      directory //absolute/directory
      directory /relative/directory

**filename keyword (default: WHATFN)**
A filename in Metpx is a five fields strings separted by four colons.
The option filename defines the remote host's filename. (This option 
is not used when protocol is amqp).
The following keywords are valid::

      WHATFN      the first part of the metpx filename (string before first :)
      HEADFN      HEADER part of the metpx filename
      SENDER      the metpx filename may end with a string SENDER=<string>
                  in this case the <string> will be the remote filename
      NONE        deliver with the complete metpx filename (without :SENDER=...)
      NONESENDER  deliver with the complete metpx filename (with :SENDER=...)
      TIME        time stamp appended to filename. Example of use: WHATFN:TIME
      DESTFN=str  direct filename declaration str
      SATNET=1,2,3,A  cmc internal satnet application parameters

      DESTFNSCRIPT=script.py  invoke a script (same as destfn_script) to generate the
                              remote filename.

**destination url [filename-keyword] (Default: None )**
**url** stands for Uniform Resource Locator and can be used to designate where
a sender should connect to.  All the previous single-file options, if used only once,
can be set in one **destination** declaration.  Here **filename-keyword** refer to
the keywords of the **filename** option defined above.::

  The url syntax is   protocol://user:password@remotehost//absolute_path
                 or   protocol://user:password@remotehost/relative_path
  Ex. :

       destination ftp://toto:totospw@totosmachine//data/for/toto WHATFN

       is equivalent to

       filename WHATFN
       destination ftp://toto:totospw@totosmachine//data/for/toto

**The remaining of the file options is irrelevant to the amqp protocol**

**ftp_mode mode (Default: passive )**
the ftp mode is either **active** or **passive**.

**chmod integer (default: 666)**

This option defines the permission given to the file when completely delivered.

**lock string (default: .tmp)**

This option should be set in agreement with the manager of the remote host to which
files are being delivered (irrelevant for amqp). It is used to prevent the remote
system from picking up the product while transfer is in progress.  There are two 
ways to use this option.

Usualy the **lock** option defines a suffix given to the file during transfer.
When the file is completely transfered, the suffix is removed by renaming the file.

The second usage is to use the string **umask** to set it. Ex.: **lock umask**
In this case the file has permission 000 during transfer. When the transfer is done,
the permission changes to the value given to the option **chmod**.

Note that umask is not a supported command under SFTP. To implement that
functionality, the sender opens the file in write mode, and than sets its
permission to 000. The two successive calls to the remote server cause the
file to be created and empty without the 000 permission for a short period.
The remote server could, at this precise moment decide, based on its default 
permission, that it can process the file... The file hence processed would be
empty. The sender would get an error and resend the file.

**dir_mkdir boolean (default: False)**
When this option is enabled, the directories where the products are delivered
are created if they do not exist. 

**dir_pattern boolean (default:False)**
If this option is enabled, the following patterns placed anywhere in the directory name
are going to be systematicaly replaced ::

  ${T1}    replace by bulletin's T1
  ${T2}    replace by bulletin's T2
  ${A1}    replace by bulletin's A1
  ${A2}    replace by bulletin's A2
  ${ii}    replace by bulletin's ii
  ${CCCC}  replace by bulletin's CCCC
  ${YY}    replace by bulletin's YY   (obs. day)
  ${GG}    replace by bulletin's GG   (obs. hour)
  ${Gg}    replace by bulletin's Gg   (obs. minute)
  ${BBB}   replace by bulletin's bbb
  ${RYYYY} replace by reception year
  ${RMM}   replace by reception month
  ${RDD}   replace by reception day
  ${RHH}   replace by reception hour
  ${RMN}   replace by reception minutes
  ${RSS}   replace by reception second

**timeout_send seconds (default:0)**
set the elapsed time after which a product sending will be considered timed out.
A value of 0 means do not check for timeout.

DEVELOPER SPECIFIC OPTIONS
==========================

**sorter keyword (Default: MultiKeysStringSorter)**
other keyword could be None, StandardSorter.  Determine which type of sorter will be used. In practice, never used.

**keepAlive boolean (Default:True)**
This option set the unix socket option SO_KEEPALIVE to the value of that option

**mtime integer (default:0 )**
Number of seconds a file must not have been modified before we process it. 
If set to 0, this is equivalent to not checking the modification time.

**patternMatching boolean  (Default: True)**

If the option **patternMatching** is True by default. But if it is set to False, the products' file name
will not be matched against the **accept** and **reject** regexp patterns of the sender's configuration file.
For sender of type single-file, no product is processed. For senders of type am or wmo, all products are processed.

**emask/imask <filepattern>**
**emask/imask** are an older version of **accept/reject** and use filepattern instead of regexp pattern.
They are still working for now  but are deprecated.
