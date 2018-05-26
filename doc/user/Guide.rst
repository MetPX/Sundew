======================
A Guide to Using MetPX 
======================


.. contents::

Front Matter
-------------
:Authors: 
    Peter Silva, Michel Grenier, Daniel Lemay,
    and many more to come...:-)

:Version: 
     $Rev$
     $Date$

PRE-DRAFT, not even ready for revision yet! Missing:

* amb - explanation of file naming convention & extension.
* mg - explanation of DESTFN stuff in general terms (details for man page.)
* lp - WMO monitoring feed, little blather about METDATA thingum...
* amb - several recipes: choosing among WMO feeds...
* several incomplete sections marked FIXME.
* description of required cron jobs.


:Copyright: MetPX Copyright (C) 2004-2006  Environment Canada



About This Guide
---------------- 
´A Guide to Using MetPX´ describes the principles and features of the MetPX TCP/IP WMO switching
application.  The Guide introduces many the facets of the package, to get the user started.
For fully detailed reference material, the manual pages are available on each of the commands used.

This document begins with a trivial switching system to illustrate the basic concepts and activities.
Various aspects of routing and special effects (aka filtering) are gradually unveiled.  
Towards the end, an overview of a typical clustering/HA configuration is given.

While Metpx consists of at least three separate modules (sundew, columbo, and stats), 
this guide currently concerns itself only with the real-time switching component (sundew)
Columbo is the web monitoring interface for an entire cluster from a 
single screen.  For now there is not much about columbo in this guide.  As
the module installation methods mature, information about Columbo will be added.


Fundamentals
------------
`MetPX <http://metpx.sourceforge.net/>`_ is a high speed, high reliability, 
low-latency meteorological message switching application.  Another term in
wide use for this type of application is a Message Handling System (MHS).
Regardless of the term, the purpose is to handle message traffic for the 
`World Meteorological Organization <http://www.wmo.int>`_'s GTS, as described in the 
Manual on the Global Telecommunications System WMO386, 
(there will be many references to *WMO386* in this guide) or GTS.  MetPX 
originated at the Canadian Meteorological Centre (CMC), which 
in WMO386 Part I terminology is both a Regional Specialized Meteorological 
Centre for Volcanic Ash advisories as well as environmental emergencies, 
in addition to being the National Meteorological Centre for Canada. The 
system is also the gateway between the GTS in Canada and the Canadian 
portion of the International Civil Aviation Organization's (ICAO) 
Aviation Fixed Telecommunications Network (AFTN) operated within Canada
by NavCanada.

At the CMC, Metpx runs on a cluster of Debian Linux systems configured for high 
availability.   As such, configuration requires a basic knowledge of linux 
shell commands (such as ls, rm, cp, cat, and grep), and use of text editor, 
(vi is used, but any text editor will do.)  Lastly python 
( http://www.python.org ) regular expression are heavily used in the 
configuration files. 

All px configuration occurs when running as the px user. So one
needs to begin by opening a shell as the px user.  The ways to accomplish
this are many and varied, and beyond the scope of this manual. however,
throughout the manual, commands are assumed to be typed from this acocunt.


.. image:: BigPicture.png

figure 1: The Overall view of Sources, Filters, and Clients.

Above is an overview of the data switching problem which metpx addresses.
Data can come from many sources.  Often, one can obtain the same (or
similar) data from multiple sources.   Data filters are processes
which transform data in some manner, sometimes they are completely
external, such as the RADAR processing cluster, and sometimes they 
are internal, such as the GIF to PNG converter.  Delivering data to 
clients is complicated because different clients need different
data, some clients want data we are not permitted to send to them,
and many clients are limited in the amount of bandwidth which
can be used to send them data.

One cannot control the wide variety of hardware and software in use
by other entities, or even when it comes to COTS systems for various 
functions (WMO monitoring, GOES acquisition, etc...) Today, MetPX can receive:

 * Alpha-Manager Protocol sockets (A Canadian proprietary protocol.)
 * WMO GTS socket data.
 * files dropped in a directory on the server (we accept them via scp, ftp, cp, and rcp today.)
 * files dropped in a remote directory accessible via a file transfer protocol (ftp only for now)

MetPX can Send:

 * Alpha-Manager Protocol sockets (A Canadian proprietary protocol.)
 * AMIS Protocol sockets (mimics a deceased 25 year old Canadian digital satellite broadcast.)
 * WMO GTS socket data.
 * via AMQP socket (emerging standard: www.amqp.org)
 * via FTP 
 * via SFTP

MetPX's switching component (sundew) functions, succinctly, as follows:  

 * data is received by pxReceiver processes, 
 * each pxReceiver destermines the routing key for the data.
 * The receivers then *switch* or *route* the data based on the label, (that is, they queue the data for the appropriate Filters and Senders. Steps:

    * look up the key in pxRouting.conf
    * a table entry gives the list of destinations, as well as a sending priority.

 * pxSenders send the data which is waiting in their queues.  
 * pxFilters read data from their queue like a sender, transform data in some 
   fashion, and then name and switch the result like a receiver.

Receivers (also called *Sources*) and Senders (also called *Clients*), as 
their names imply, are uni-directional data channels.  A receiver will only 
receive data, and a sender will only send it.   While there are two broad 
categories of data,  bulletin and file,  there is only one internal 
representation of data in metPX: files.  On receipt, every bulletin is 
turned into a file, and stored in a directory hierarchy.  The queue for a 
sender is just another directory tree.

The traditional form of data for the GTS is the bulletin.  What is a bulletin?
In general, bulletins are defined by `WMO386 attachment II
<http://www.wmo.ch/web/www/ois/Operational_Information/WMO386/Volume1/AttachmentII_5.pdf>`_ .  
For our purposes, however, a WMO bulletin is a stream of 
bytes.  The stream always begins with an Abbreviated Header line (as defined in WMO386), or AHL, for the bulletin, expressed in 7-bit ASCII characters.  
MetPX uses the AHL to route bulletin data.  An AHL is of the general form:

  *TTAAii* *CCCC* *DDHHMM*  ... example: SACN31 CWAO 091300

Sample information from an AHL:
 * SA - Surface observation, from
 * CN - Canada, (the AA is not always a country code, depends on TT)
 * 31.. a number indicating the scope of distribution, local, national, regional, wordwide.
 * CWAO bulletin originated at the Canadian Meteorological centre,
 * 091300 - on the ninth day of the month, 13h00 (1:00 pm) in UTC timezone.

The above is a very brief introduction the topic of AHL's. For a proper discussion, 
please consult WMO386.  For Metpx, the fundamental point is that it extracts 
TTAAii_CCCC to create a routing key.

The second category of data which metpx understands is files. A file is a stream
of bytes, with a name.  Metpx extracts a key from the name of a file and
perform the same switching function used for bulletins.

Regardless of how data is received, as bulletins or files, metpx turns
it into invidual files, one product per file, with a file name that
gives enough information to be able to route it. so one may find the words 
file and bulletin used interchangeably.


As an aside: there is also a third hybrid reception type: bulletin-file.
A bulletin-file receives files like a file receiver, but ignores their names. 
Instead, it treats all files as if they were a byte stream 
received on a socket connection. The bulletin-file receiver looks for 
the first AHL in a file, routes the contents accordingly.




Installation
------------

Download the .deb package from the download area on metpx.sf.net.
Then install it using Debian standard methods:

| dpkg -i metpx-sundew-xx-yy.dpkg

installs the package itself.

|  apt-get install -f

installs the missing dependencies, if any.

A First Run
-----------

In this section, a minimal configuration is built and run.
The reader is introduced to the directory tree, how to start
and stop circuits, and check their status.

First construct a small pool of sample bulletins
(copy thes commands and pasting them into a shell will build the files 
on your server.)

| mkdir sample_bulletins
| 
| cat >sample_bulletins/s1 <<EOT
| SACN31 CWAO 300651
| METAR
| BGBW 131550Z 21010KT 8000 -RADZ BKN006 OVC012 03/00 Q1009 RMK 5SC
|      8SC=
| EOT
| cat >sample_bulletins/s2 <<EOT
| SANT31 CWAO 300651
| METAR
| BGBX 131550Z 21010KT 8000 -RADZ BKN006 OVC012 03/00 Q1009 RMK 5SC
|      8SC=
| EOT
| cat >sample_bulletins/s3 <<EOT
| SICN25 CWAO 300651
| AAXX 04154
| 71255 36/// /0202 11078 21089 333 60001=
| EOT
| 
| cat >sample_bulletins/s4 <<EOT
| SICN25 CWAO 300651
| AAXX 04154
| 71255 36/// /0202 11078 21089 333 60001=
| EOT
| 
| cat >sample_bulletins/s5 <<EOT
| SMCN37 CWAO 300651
| AAXX 20184
| 71784 16/// /0000 10036 20031 39903 40107 53021 60001 333 10040
| 20020 70305=
| EOT
| 
| cat >sample_bulletins/s6 <<EOT
| SMCN37 CWAO 300651
| AAXX 20184
| 71783 16/// /0000 10036 20031 39903 40107 53021 60001 333 10040
| 20020 70305=
| EOT

Now build a sample configuration: 

|
| PXETC=/etc/px

| cat >${PXETC}/rx/file.conf <<EOT
|   type bulletin-file
|   extension file\:-CCCC:-TT:-PRIORITY:Direct
| EOT
|
| cat >${PXETC}/rx/loop.conf <<EOT
|   type wmo
|   port 5002
|   extension pxatx\:-CCCC:-TT:-PRIORITY:Direct
| EOT
|
| cat >${PXETC}/tx/loop.conf <<EOT
|   type wmo
|   destination wmo://localhost:5002
|   accept .*:.*:.*:.*:.*:.*:.*
| EOT
|
| cat >${PXETC}/pxRouting.conf <<EOT
|   key_accept .* loop 3
| EOT
|

FIXME: default 'extension' should be set in /etc/px/px.conf as a sitewide
setting. 

As the above series of commands show, configuration files for metpx
reside in the /etc/px directory.  Configuration which applies to multiple
channels is in this directory.  Individual channels are created by
placing an appropriate .conf file in an rx, fx, or tx sub-directory.
The above configuration creates two receivers and one sender.
The pxRouting.conf file specifies a central table consulted by all 
receivers and filters. The routing table above routes any and all data 
received to the loop sender.  Start it up to see what happens.

| px@laptop:~/$ px start

The above will start all the configured recievers and senders, it will
also build the queuing directories for each defined channel.

laptop% ls -lr rxq txq
txq:
total 4
drwxr-xr-t 2 px px 4096 2006-10-08 23:03 loop

rxq:
total 8
drwxr-xr-t 2 px px 4096 2006-10-08 23:03 loop
drwxr-xr-t 2 px px 4096 2006-10-08 23:04 file
laptop%   

Now, Let's have a look at the processes:

| px@laptop:~/$ ps ax | grep px
| 15897 pts/2    S      0:00 su - px
| 16848 pts/2    S      0:00 python /usr/sbin/pxReceiver loop start
| 16849 pts/2    S      0:00 python /usr/sbin/pxReceiver file start
| 16856 pts/2    R      0:04 python /usr/sbin/pxSender loop start
| 16863 pts/2    R+     0:00 grep px
| px@laptop:~/$  

So the Receivers have started.  Let us given them some data to route.

| cp sample_bulletins/* /var/spool/px/rxq/file

That will copy a selection of bulletins into the file receiver's input queue.  What happens next?:

 1. The bulletins are ingested and queued for transmission via the loop sender.   
 2. The loop sender sends the bulletins to the loop receiver.
 3. The loop receiver ingests and queues the data for transmission via loop sender.
 4. The loop sender sends the bulletins to the loop receiver.
 5. The loop receiver detects that these are duplicate messages and discards them.

Lets have a look at the log files in the /var/log/px, directory and examine the results.
There should be three log files, and they should indicate normal startup.  Look at rx_file.log first:

| 2006-10-08 00:23:31,060 [INFO] Receiver file has been started
| 2006-10-08 00:23:31,061 [INFO] Initialisation of source file
| 2006-10-08 00:23:31,064 [INFO] Ingestor (source file) can link files to clients: ['loop']
| 2006-10-08 00:23:31,290 [INFO] Initialisation of client loop
| 2006-10-08 00:23:31,506 [INFO] Routing table used: /etc/px/pxRouting.conf
| 2006-10-08 00:24:36,553 [INFO] 6 bulletins will be ingested
| 2006-10-08 00:24:36,556 [INFO] (107 Bytes) Ingested in DB as /var/spool/px/db20061008/SM/file/CWAO/SMCN37_CWAO_300651___0001:file\:CWAO:SM:3:Direct:20061008042436
| 2006-10-08 00:24:36,557 [INFO] Queued for: loop


Then the rest of the bulletins are ingested once, and each in turn is queued 
for transmission on the loop wmo sender.  Note what has been done to name 
the file corresponding to the bulletin received.  The file name begins with 
the complete AHL, then the a randomizing counter is added, followed by the 
string given in the extension directive, and a reception timestamp.   The 
following line, 'Queued for' indicates whose transmission queues the file 
will be linked to.

Now have a look at the log of the sender:

| 2006-10-08 00:23:31,278 [INFO] Sender loop has been started
| 2006-10-08 00:23:31,316 [INFO] Initialisation of client loop
| 2006-10-08 00:23:31,543 [INFO] Trying to connect remote host localhost
| 2006-10-08 00:23:31,547 [INFO] Connexion established with localhost
| 2006-10-08 00:24:36,615 [INFO] 6 new bulletins will be sent
| 2006-10-08 00:24:36,616 [INFO] (130 Bytes) Bulletin SACN31_CWAO_300651___0006:file\:CWAO:SA:3:Direct:20061008042436  delivered
| 2006-10-08 00:24:36,617 [INFO] (130 Bytes) Bulletin SANT31_CWAO_300651___0005:file\:CWAO:SA:3:Direct:20061008042436  delivered
| 2006-10-08 00:24:36,618 [INFO] (103 Bytes) Bulletin SICN25_CWAO_300651___0003:file\:CWAO:SI:3:Direct:20061008042436  delivered
| 2006-10-08 00:24:36,618 [INFO] suppressed duplicate send SICN25_CWAO_300651___0004\:file\:CWAO:SI:3:Direct:20061008042436
| 2006-10-08 00:24:36,619 [INFO] (141 Bytes) Bulletin SMCN37_CWAO_300651___0001:file\:CWAO:SM:3:Direct:20061008042436  delivered
| 2006-10-08 00:24:36,620 [INFO] (141 Bytes) Bulletin SMCN37_CWAO_300651___0002:file\:CWAO:SM:3:Direct:20061008042436  delivered
| 2006-10-08 00:24:36,722 [INFO] 5 new bulletins will be sent
| 2006-10-08 00:24:36,722 [INFO] suppressed duplicate send SACN31_CWAO_300651___00001:localhost:CWAO:SA:3:Direct:20061008042436
| 2006-10-08 00:24:36,723 [INFO] suppressed duplicate send SANT31_CWAO_300651___00002:localhost:CWAO:SA:3:Direct:20061008042436
| 2006-10-08 00:24:36,723 [INFO] suppressed duplicate send SICN25_CWAO_300651___00003:localhost:CWAO:SI:3:Direct:20061008042436
| 2006-10-08 00:24:36,723 [INFO] suppressed duplicate send SMCN37_CWAO_300651___00004:localhost:CWAO:SM:3:Direct:20061008042436
| 2006-10-08 00:24:36,724 [INFO] suppressed duplicate send SMCN37_CWAO_300651___00005:localhost:CWAO:SM:3:Direct:20061008042436

The loop receiver log will show the messages being ingested, and sent, as in 
the file receiver.  So from this you can see a very simple installation 
configuration self-test.  Complete the excercise:

| px@laptop:~/log$ px stop
| px@laptop:~/log$ px status
| * receiver loop is not running
| * receiver file is not running
| * sender loop is not running
| px@laptop:~/log$ ps ax | grep px
| 15897 pts/2    S      0:00 su - px
| 18704 pts/2    S+     0:00 grep px
| px@laptop:~/log$    


So now one can:
  * Build a basic configuration. 
  * Start them all up as a group, and stop them.
  * See what is going on in the log files.

experiments:

 * Do *px start*, then *pxSender loop stop*, then feed the data from sample 
   bulletins into the file receiver.  Look at txq/loop.  What do you see?
 * Replace wmo by am in the loop receiver and sender. You can now exchange data 
   with Canadian MetManager, or AM software.
 * Make the test run forever by *noduplicates false* to the loop sender's config 


Configuring VSFTPD for File Reception
-------------------------------------

Being careful, one can likely use any FTP server.  However,
use of VSFTPD makes configuration quite simple.  It is available from 
standard Debian repositories via *apt-get install vsftpd*.  

Here is a complete /etc/vsftpd.conf: 

| cat >/etc/vsftpd.conf <<EOT
| # These are Debian/Ubuntu Defaults ...
| listen=YES
| dirmessage_enable=YES
| xferlog_enable=YES
| connect_from_port_20=YES
| secure_chroot_dir=/var/run/vsftpd
| pam_service_name=vsftpd
| rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
| rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
| ascii_upload_enable=YES
| ascii_download_enable=YES
| 
| # Do not want users logging in without pw.
| anonymous_enable=NO
| # will specify which users can log in in /etc/vsftpd.user_list
| userlist_enable=YES
| userlist_deny=NO
| userlist_file=/etc/vsftpd.user_list
| write_enable=YES
| 
| # all the authenticated users are 'guests' of the px account.
| # when they log in, they will be placed in the right reception queueing directory.
| local_enable=YES
| guest_enable=YES
| guest_username=px
| virtual_use_local_privs=YES
| user_sub_token=$USER
| local_root=/var/spool/px/rxq/$USER
| EOT
|

NOTE:
   vsftpd has a very picky parser for it's configuration files:

   * it cares about capital letters versus lower case, and spaces.
   * Do not put spaces before or after directives, or around the = sign.
   * Do not apply trailing comments, they will be considered part of the value setting.  
   * Comments need their own line. 

For each *guest* user, vsftp will chroot the session into a directory given
by the local_root pattern, so the *file* will have /var/spool/px/rxq/file as 
the working directory on login.

Now that we have a vsftpd configuration, also need to prep for guest users.
This is because of an oddity in vsftpd's PAM setup on ubuntu (same on Deb?), 
where it refuses to approve a login unless the account has a valid shell.  
/bin/false was already used as a login shell for many users, but it is not
in /etc/shells.  Worrying that this was on purpose, and not wanting to 
assign a useful shell to 'guests', added a bogus one to /etc/shells instead.

| echo "/bin/true" >>/etc/shells

Of note, vsftpd has the virtual user / guest user concept.  This makes it easier
to set up ftp receivers.  For example, to configure ftp reception for 
the 'file' receiver defined in the first run above, just do the following:

|
| useradd  -s /bin/true file   # create the 'file' user.
| echo "file" >>/etc/vsftpd.user_list  # permit him to ftp into the server.
| passwd file  # set his password.
|    # assume it is ILuvData

Send username and password to the technical contact at your data source, 
and your work is done!


Setup FTP Sender
-----------------

Change the sender loop configuration:

| cat >${PXETC}/tx/loop <<EOT
| type single-file
| destination ftp://file:ILuvData@localhost
| accept .*
| EOT

So there you have a basic FTP sender!


Now if you want to play around with the filename once at its destination,
there is an option "filename" in the configuration that you can use.
The option can be uses  ::


  NONE        deliver with the complete metpx filename (its the default)

  WHATFN      the first part of the metpx filename (string before first :)
  HEADFN      HEADER part of the metpx filename (bulletin only)
  TIME        time stamp appended to filename. Example of use: WHATFN:TIME
  DESTFN=str  direct filename declaration str

  SENDER       the metpx filename may end with a string SENDER=<string>
               in this case the <string> will be the remote filename
               This is borrowed from the PDS application...

  DESTFNSCRIPT=script.py  invoke a script that will process the input filename
                          and generate the remote filename. The script must be
                          found in $PXROOT/etc/scripts



Basic Routing
-------------

FIXME: Add a second router, create per bulletin pxRouting file.


* file naming requirements and conventions.

* source 
  apply accept to extract key.

* pxRouting.conf

  * list of keys with clients to route to.
  * find key, queue up for those clients.

* client.

  * looks in it´s queue
  * applies reject/accept, sends as directed.


Advanced Routing
----------------

use Nws, ukmet & noaaport triple GTS feed routing as example.
receiving same bulletins from multiple sources, suppressing some sources
for some destinations, using reject/accept.

FIXME: input from amb




Filters
-------
When you need to modify/convert a product prior to its shipping, the
user should make use of a pxFilter.  Products routing to the filter works 
exactly like routing to a client.  And the converted products are routed 
from the filter exactly like if the filter was a receiver. 
In the pxFilter configuration file, use option fx_script followed by the name
the python script file.  The user must provide this python script in
$PXROOT/etc/scripts. 

The python script receives the input filename and the process'logger object.
The script is expected to return one of the following values ::

    None           : which means the input file was incorrect
    input filepath : which means the input file is already in the proper fashion
    output filepath: which is the path for the newly created product.

The following example is a filter that change the origin of a bulletin from
CWNT to CWAO (absolute nonsense). The output file name (if we succeed) is the
same as the input file except that it has its field :Direct: replaced by
:Converted:.  It is a good practice to implement the three return cases 
explained earlier. ::

   import sys,os,time,stat,string

   class Transformer(object):

      def __init__(self):
          pass

      def renamer(self,ipath):
          opath = ipath.replace('Direct','Converted')
          return opath

      def perform(self, ipath, logger ):

          # file already converted

          parts =  ipath.split(':')
          if parts[-2] == 'Converted' : return ipath

          # read in the file

          data=''
          try :     
                    f = open(ipath, 'r')
                    data = f.read()
                    f.close()
          except :  
                    # problem with file return None
                    return None

          # change header

          data = data.replace('CWNT','CWAO')

          # write the file into its proper name

          opath = self.renamer(ipath)
          f = os.open( opath, os.O_CREAT | os.O_WRONLY )
          os.write( f , data )
          os.close( f )

          # log a message

          return opath

   transformer=Transformer()
   self.fx_script=transformer.perform

The very last line is very important. It sets the fx_script with
the module perform that does the filtering work.

(NOTE  dx_script... should be covered too MG)


Recommendations
----------------


Use revision control on configuration files.
  systems such as RCS, CVS, and Subversion are very helpful for maintaining
  configuration files. One of the primary advantages of text based configuration
  files is being able to compare different configurations easily via diff.
  tracking who made what change, when, can be invaluable when troubleshooting.

Use separate reception directories to clarify sources of data.
  One could configure a single reception directory for all data. Sorting
  through such a directory to determine which files are which data will be
  more cumbersome and error prone than if the reception is separate at least
  for each entity delivering data to a MetPX instance.  This will also reduce
  processing overhead, because fewer masking patterns will be in place for each
  reception directory, and for each file, one will have to go through fewer patterns.

Use key directive (in preference over key_accept) and comments copiously in pxRouting.conf
  MetPX provides the ability to use broad patterns to perform very simple routing.
  In an NMC, or other environment where delivering the wrong data to the wrong 
  client can have important consequences, one uses such patterns very 
  sparingly.  Instead, very detailed, specific routing tables are common.  
  CMC uses approximately 30,000 bulletin data routing entries and 60,000 
  entries for file data in their routing tables.  A major goal in MetPX's 
  design was to efficiently operate with very large routing tables.
 
  MetPX is not designed as an indiscriminate weather broadcasting tool
  where the main constraint is client need for data, rather than provider
  constraints (such as permissions)  

|   key SACN37_CWAO NWP,Archive 3  # Private stations from provincial Hydro 
|   key SICN25_CWAO NWP,Archive,GTS_main 3 # our stations in Northern Province of Hoser
|   key SANT31_CWAO NWP,Archive,GTS_main,GTS_backup 3
|   key SMCN37_CWAO NWP,Archive,GTS_main,GTS_backup 3

  When sending data, one always must be cognizant of the channel over which the
  data is being sent.  Sending radar data over a phone line, for example, will 
  often result in not being able to get weather warnings through, because the 
  line will be clogged.  Metpx provides precise routing in order for users to
  be able to control exactly what is sent on a communications link at any
  given time.  

  Beyond the practical necessity of controlling bandwidth, there is the need
  to assure data providers of appropriate distribution of their data.  Key
  to obtaining many sorts of data is the promise not to distribute it.  Systems
  which are oriented towards weather broadcasting are thus ill-suited for
  our needs.

  With all this in mind, It is anathema to permit users to easily be able to 
  request re-transmission of large amounts of data or different types of
  data.  Manual oversight, as a management function, is *a good thing*. 


WMO Monitoring 
--------------
FIXME: input needed LP, write up a little configuration...
 * promote the DWD package, provide a link...
 * Give a sample circuit configuration.


Feeding LDM
-----------

Unidata's Local Data Manager ( http://www.unidata.ucar.edu/software/ldm/ ) is well known
in the meteorological community.  There is no special configuration needed to feed ldm using METPX.
A simple scenario could be, from METPX, send the product into a directory.
Periodically run pqinsert on each file... thats it.
Refer to LDM's documentation for more details.

Receiving from LDM
------------------
LDM uses a configuration file called pqact.conf. It defines action to take
the product selected (pattern matching on product names). The directive also
defines an output directory (or a filter with an output directory as argument).
To feed metpx from LDM's output products you simply specify the output
directory to be an rxq directory (or it could be a link to it). The
filename of an LDM output product consist of 1 word. The receiver will have
to define the extension to use on that file.

An example of pqact.conf directives ::

  #
  # NCEP Extended Range Model (MRF model)
  #
  HRS     ^H.E[L-Y][0-9][0-9] KWB. ([0-3][0-9])([0-2][0-9])
	  FILE    data/GRIB/(\1:yyyy)(\1:mm)\1\2_mrf_nh.grb
  HRS     ^H.F[L-Y][0-9][0-9] KWB. ([0-3][0-9])([0-2][0-9])
	  FILE    /apps/px/rxq/from_ldm/(\1:yyyy)(\1:mm)\1\2_mrf_sh.grb

where /home/ldm/data/GRIB is a link to /apps/px/rxq/from_ldm for example

And here is a possible receiver for these products (from_ldm.conf) ::

  #
  #  receive and treat all grib products coming from ldm
  #
  type single-file

  batch 1000

  routemask        true
  routing_version  1
  routingTable     /apps/px/etc/LDM_ROUTING.conf

  mtime 300

  extension LDM:MRF:GRIB:BIN:

  accept ^.........._(.*grb:LDM:MRF:GRIB:BIN).*

AMQP
----
The Advanced Message Queueing Protocol (AMQP, www.amqp.org) is an emerging standard from
the financial sector which strives to be interoperable and vendor, language, and transport neutral.
There is a very close conceptual alignment between traditional WMO messages, and AMQP.  For MetPX in particular, the affinities are very clear.  Terminology mapping:  

========== ==========
   Concept Mapping
---------------------
  AMQP       MetPx
========== ==========
Exchange   Receiver
Binding	   Routing
Queue      Sender
Broker     MHS, Switch
========== ==========

So if you read AMQP literature about an Exchange, it is basically referring to a Receiver in MetPx.
Current work in MetPX is aimed at bridging to AMQP. a amqp Sender can feed metpx data to an AMQP broker. An AMQP receiver, similarly connects to an amqp broker, and accepts data from it.  There is currently no plan to implement full AMQP broker functionality.

In order to demonstrate AMQP usage, please visit the rabbitmq.com web site, and install that broker.  Debian packages are readily available for installation via apt-get after adding rabbitmq´s repository.  The following examples assume that rabbitmq has been installed on localhost.  No further configuration is assumed.

Feeding AMQP
------------

Following the simple loopback examples above.  the loop transmitter can be 
re-cast as an amqp sender. 

| pxSender loop stop
| cat >${PXETC}/tx/loop.conf <<EOT
|   type amqp
|   destination amqp://guest:guest@localhost//data
|   accept .*
| EOT
| pxSender loop start

you can then repeat the 






AFTN
----

The AFTN over TCP/IP Gateway in MetPX is an end-node implemention, which expected 
to talk to to a AFTN Message Handling System.  It is not a complete AFTN MHS on 
its own.  The protocol implemented was specified by NavCanada for use with their 
MHS, which should be quite similar to the interface supported by AFTN MHS's from 
vendor FIXME: XYZ.

AFTN is well, necessarily completely different from WMO protocols.  Instead of 
unidirectional channels, AFTN requires bi-directional channels.   Instead of using 
WMO headers, there are AFTN envelopes to remove, and inside are WMO messages., 
there are mappings, and WMO bulletins are encapsulated within AFTN messages.  

Typical configuration file for a transceiver::
    
    # Note: In a real metpx configuration file, comment cannot be added at the end
    # of the line (only at the beginning)

    type             aftn         # At this time, only possible type for a transceiver
    subscriber       True         # False if it is a provider (in practice, always subscriber)
    host             192.168.1.1  # Remote host name (or ip) where to send files
    portR            12345        # Receiving port
    portS            12346        # Sending port
    stationID        TLA          # Three letter ID of this party
    otherStationID   LTA          # Three letter ID of the other party
    address          CWAOYYYY     # AFTN address of this process
    otherAddress     CWBOZZZZ     # AFTN address of the other party
    digits           4            # Number of digits used in the Channel Sequence Number (CSN)
    timeout          10           # Time we wait between each tentative to connect

    # Extension to be added to the ingest name
    extension aftn:-CCCC:-TT:-CIRCUIT:Direct 

    emask *:aftn:*:*:*:*          # Do not return on AFTN link what was received on AFTN  
    imask *:*:*:*:*:Direct:*      # Accept everything else with "Direct" well placed 

|
| Routing table is used at reception of a message and also for transmission of a message.
| Same routing table directives (*key, clientAlias*) as for receivers are used for transceiver of type aftn.

In addition, two other directives are used:

**subclient <client>  <subclient1, subclient2,...,subclientN>**

    This directive is used to define the subclients to which a given client can refers.  The following clients can be used in *key* and *clientAlias*
    directives:

    | <client.subclient1>
    | <client.subclient2>
    | <client.subclientN>

    | On reception, the bulletin will be linked in the tx queue of <client>.
    | On transmission, the <client> must know how to use the <subclient?> part
      to do appropriate delivery.

    At this moment, the subclient directive is only used for a transceiver of type aftn.

    ex: We will use a "client" with the name "toto" that is a transceiver of type aftn

    ::

        subclient toto AAAAAAAA,BBBBBBBB,CCCCCCCC
        clientAlias ab toto.AAAAAAAA toto.BBBBBBBB
        clientAlias abc AB,toto.CCCCCCCC
        key AACN01_ANIK ab,client1,client2
        key AACN02_ANIK client3,abc

        When a px receiver receive an AACN01_ANIK bulletin, it will be linked 
        in the tx queue of the transceiver named toto.

        The transceiver named toto will delivers the AACN01_ANIK bulletin to the following address:
        AAAAAAAA and BBBBBBBB (because the transceiver toto know how to use these subclient (in our
        example, these are AFTN addresses))

**aftnMap     <address|DEFAULT>     <prefix_header>**

    This directive is **only used on reception** of message by a transceiver of type aftn.
    If the text part of the message has no WMO Header, one will be created (thanks to the
    aftnMap entries) for each destination address in the message.

    If a destination address present in the message has no associated aftnMap directive,
    the prefix_header defined by aftnMap DEFAULT will be used.

    ex::

        aftnMap DEFAULT AACN30
        aftnMap AAAAAAAA AACN30
        aftnMap BBBBBBBB UANT30

        A transceiver (type aftn) receive a message with no WMO header and the destinaton addresses are: AAAAAAAA, BBBBBBBBB, CCCCCCCC
        Bulletins with following header will be created, ingested in the DB and linked to appropriate (following key directives) clients:

        AACN30 AAAA  (AAAA is the last 4 characters of AAAAAAAA)
        UANT30 BBBB  (BBBB is the last 4 characters of BBBBBBBB)
        AACN30 CCCC  (CCCC is the last 4 characters of CCCCCCCC)


Basic High Availability
-----------------------

The first step in improving availability over running a single system on it´s own
is to pair servers up, and have some provision for failover between the paired machines.
If servers A and B are configured in HA mode, then typically it is in an active/passive
way, where Server A is active, while B is idle.  In the case of failure of the server A, 
B is ready to take over processing for Server A.  To do that, it needs to assure itself that 
server A is down, and then take over the disk data from A so that it knows which operations are pending.

The need to take over disk space means that some form of shared storage is needed
so that both servers can access it.   There are many ways of doing this, from DRBD running over
ethernet, to myriad cluster file systems, to simple file system failover over fibre channel using heartbeat.
Regardless of the method of shared storage, the impact on sundew is the same.

One does not typically share /var across an HA cluster, but have separate application file systems
which transition to the active server.  So configuration of sundew needs to use this shared
space.

Example... assume /apps is a path where storage is moved between peers in an HA cluster. 
Assuming sundew is already installed the instructions for moving application data onto 
shared space would be something like below:

|
| px stop
| mkdir /apps/px
| mv /var/log/px /apps/px/logs
| ln -s /apps/px/logs /var/log/px
| mv /var/spool/px/* /apps/px
| ln -s /apps/px /var/spool
| mv /etc/px /apps/px/etc
| ln -s /apps/px/etc /etc/px
| chown -R px.px /apps/px
| px start
|


Product eXchange Array
----------------------

Beyond running in simple failover pairs which are still limited to the performance of a single
server, one can scale performance to an arbitrary level 
by moving to a fully scalable configuration. Normally, Sundew is an application which runs 
on a single computer.  This is an express decision to ensure focus in application development, 
and to maximally leverage existing technologies.  Sundew is not limited to running on a single 
system, and at the Canadian Meteorological Centre, it is deployed across at least four 
servers, fronted by load balancers, to increase processing capacity, and provide 
reliability beyond what is possible to do with a single server.  Because the approach 
is to leverage existing technologies, those technologies are treated as 
interchangeable components, to be substituted when it makes sense to do so.

To provide higher reliability than a single server, one configures servers in pairs, 
with a sort of shared storage (where the application stores data in transit.)  
Usually, one server has access to the storage at a time, when the primary server 
fails, the secondary server has to notice, and then take over the shared
storage, and continue operations.  To scale beyond a single server, one requires
a technology which accepts requests for service, and distributes them across
an array of identically configured servers.

So there are the three commodity technologies required:  failover monitoring, 
shared storage, and load balancing.  There is a wide variety of different products 
which accomplish some or all of the functions above.  We have not attempted to 
do a formal survey and evaluation of all of them, and the field is rapidly 
evolving in any event.  The technologies were chosen in 2004 and have served us 
well.  For more information on high availability and clustering products with 
linux, there is: http://lcic.org.  Besides Free Software solutions, there are
many other solutions such as proprietary software, and hardware (load balancers, 
and fibre channel SAN equipment.)  It is simplest to say, YMMV.

With that said, At the CMC, all systems are deployed in pairs (twins).  Each twin
has large internal disks and two data partitions.  One partition is for local 
storage, the other partition mirrors the local storage of the twin.  Such a solution
is adequate when one can consider retaining only the information that fits on 
internal disks.  http://www.drbd.org does the mirroring , and failure of the other 
twin, is recognized using heartbeat (http://www.linux-ha.org/.)  For load balancing,
ldirectord ( http://www.vergenet.net/linux/ldirectord) controls the linux virtual 
server load balancer twins.

.. image:: PXA.png

In terms of configuration, an address published for the load balancer is used by all incoming connections (socket or file based.)  An array of processing nodes 
sits behind the load balancer, each taking a portion of the incoming requests as 
assigned by the load balancer.  The processing nodes also perform transformations 
as configured. There are some operations which are necessarily "global" in that a single system needs to have an understanding of all relevant data.  examples of such 
systems are 

collected observations 
   for forwarding to the WMO.  To determine the revision level of a collected 
   bulletin, or indeed collect all reports for a given bulletin, the contituent 
   reports may have been received on any number of array processing nodes.  To
   produce a colelcted bulletins all the individual reports need to be forwarded to
   a single server.
   
socket senders.  
   Peer organizations typically do not look kindly on opening a large number of 
   identical sockets (1 from each array processors), so the appropriate data is 
   concentrated on a single node, and then the single node can open a single 
   socket and transmit all requisite data.

pull receivers.
   Pull receivers which do not delete files on the source need to maintain a global
   state of files already pulled, to prevent multiple retrivals of the same data.

Besides the actual data routing, processing, and delivery, there is another pair
of servers dedicated to monitoring.  This pair of servers runs the columbo module
and a web server, as well as the statistics module.  This minimizes the load for
statistics and monitoring on nodes which need to do processing.


Retransmission
--------------

It is possible to retransmit a product, or several products to a client.
The metpx package provides two utilities for that namely pxRetransmit and
pxRetrans. pxRetrans is a more complete utility searching for the user 
through the database for the products and retransmitting to various combination
of clients. pxRetransmit is a simple shell script with at least 2 arguments.
The first argument is the client (sender) name, the second is the absolute path
of the product you want to retransmit. You can put as many products as you want
Here is an example which retransmit all SXVX45 bulletins to the navcan client:

|
|  cd $PXROOT/db/20080604/SX/pds6/KWNB
|  pxRetransmit  navcan  ./SXVX45*
|

You can list more than one product for the last command line arguments.
A detailed description of the pxRetrans program is found here (Daniel...!!!)

Columbo
-------

Need to install it on the laptop first... get packaging out of the way.



Miscellany
----------

OK, there is also mr-clean, which eliminates unwanted empty directories, 
as well as pxChecker which restarts any channels which may have failed.  Those 
processes generally need no attention.  

bandwidth control using vsftpd ... at least for reception.



