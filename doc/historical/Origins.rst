
================
Origins of MetPX
================

:Authors:
    Peter Silva

:Version: $Revision: $
:Copyright: MetPX Copyright (C) 2004-2006  Environment Canada


.. contents::

Purpose
--------

The purpose of this document is to provide some background terminology and historical
context for terms which might be found elsewhere in the documentation and source code.


Direct Ancestors
----------------


NCS 
 * National Communications System  (And National Central Communications System) aka APPS
 * a predecessor of MetPX.
 * applications written in a proprietary language for a proprietary OS, non-portable.
 * for bulletin switching.
 * excellent features for intended purpose, but decades old and now obsolete.

PDS
 * Product Distribution System.
 * a predecessor of MetPX.  Still in heavy use within Environment Canada.
 * only intended for file transfers, not bulletins.
 * application in C, no plans to release it.
 * metpx has lower switching latency, higher delivery performance, and lower overhead.
 * was the design point from which metpx arose.

Originally, MetPX-Sundew was called pds-nccs, with the idea being to create small modules
that would permit a standard PDS to send and receive over sockets.  At this point, the
receivers and senders were called NCSamReceiver, or NCSWmoReceiver.
This was brought into a full-scale mockup configuration, and it proved complex to configure
and was too slow.  The socket drivers worked well but the latency and performance of the PDS
was not upto the task.  At that point, a trial project was initiated to re-implement
a minimal subset of the PDS to support the PDS-NCCS project.  The tiny (500 line)
prototype was the File Exchange Tracker (FET).  Those trials were successful (order(s)
of magnitude improvements in latency and performance.) It lived only a month or
two as an independent module.

The separate individual configuration of many, many individual components was cumbersome
and fraught with chances for error by administrators. In order to make the package easier
to configure, a standardized file tree was designed, and FET and pds-nccs were thus merged
with a common, simpler configuration. The result of that was the original product exchanger
(PX.)


Why Sundew is Faster than PDS
-----------------------------

Why is it faster? One reason: PDS uses a central ingest process, and IPC for reception to 
communicate with a dispatcher. The dispatcher is a single process that does all routing and access 
to it is serialized using IPC.  As volume grows, the small individual synchronization delays accumulate,
and all routing is limited to a single CPU, in spite of multiple cpu systems now being common.
MetPX receivers do the routing themselves, with no hand-off to a dispatcher, so 10 receivers 
can be performing receipt and routing in parallel with no waiting, and making use of upto 10 processors.
So routing is fundamentally done by multiple independent processes, instead of one.

The second major difference is the routing algorithim. PDS routing means taking an input file 
and comparing to all configurations for all senders, applying all regular expressions for 
each destination. MetPX adopted the routing table from the Tandem Apps, a lookup table 
to do initial routing.  Regular expressions are only evaluated after that initial look up 
is done, which usually means 10x fewer regular expressions to compare.

So, on a configuration with 150 inputs and 150 outpus, Sundew has 150 processes doing 
the routing instead of one, and each of those is about 10x faster than the single central 
dispatcher in PDS.


Where AM Sockets Come From
---------------------------

Other systems in use in Environment Canada, are packages such as Alpha-Manager / Image Manager,
also called IM/AM. This is the system which first implemented what is termed *AM sockets*.
This package originated in the early 90's and was deployed in all regional offices. The 
application is largely retired from environment Canada, except for a few special 
applications such as a raw bulletin filtering system, known as CODECON.

MetManager, the son of IM/AM, has a greatly improved feature set. It also uses AM sockets
as the primary means of circulating bulletin information. It's configuration is very
similar from the bulletin point of view. MM also has a unique protocol 
for passing images, which is not implemented in MetPX (we deliver by FTP.)


Where Columbo Came From
------------------------

An operator interface for the PDS, called Columbo, had been created in the early 2000's by
Daniel. This existing interface was extended to support both PDS and PX.  Eventually, the 
interface was subsumed as part of the overall MetPX project, so the switching component 
was renamed from px to Sundew.

Original Specification of FET, parent of metpx
-----------------------------------------------

The first spec for what eventually became PX... pds-nccs existed, but
each individual circuit was completely independent.  Needed to minimize 
configuration work.  Also, PDS had proved far too slow as a switching system.

| 
| FET - File Exchange Tracker, specification
| 
|   - philosphical change:  
|      Current PDS uses one or a few accounts for ingest.  Instead,
|      All sources should use distinct accounts to deliver data.
|      -- provides clearer tracking of data, easier identification of sources.
|      -- allows simpler processing of data, if you know the kind of data
|         there, how to modify it becomes simpler to figure out.
|      -- allows for some security on input (joe cannot put in fake Jane data)
| 
|   - as per Anne-Marie's letter:
|      -- integrate into existing pds-nccs
|      -- no pdsswitch.
|      -- ingestor figures out how to link to clients.
| 
|   - Add a file-hierarchy standard, so that the whole hangs together.
|     Have a master which starts all the requisite senders and receivers 
|     in one go. (A pds startup script, and another to shutdown)
| 
|   - add PDS functionality to the pds-nccs code.
| 
|       file ingestor:
| 
|         - have it scan a directory or series of them (no priorities), 
| 	  and ingest files.
| 
| 	  no sample code available, perhaps adapt ncsSender code.
| 
| 
|         - add integrated whattopds functionality (file renaming)
| 
| 	  sample code: fet.ingestName(
| 
| 
| 	- make the grammar in configuration files similar, so that
| 	  it looks like a single application. 
| 
| 	  sample code: pds2fetconf converter...
| 
| 
| 	- have it parse imasks etc... to know how to link to clients.
|   	  & ingest into a database: 
| 
| 	  sample code: fet.ingest( do all the above...
| 	     uses:
| 	     	dbname -- maps an ingest name to a db path
| 		clientmatches -- checks all the imask entries to find hits.
| 		clientQdirname -- figure out what clientQdirectory to use
| 				(takes ingestname priority as an argument.)
| 	     
| 
| 
|       file sender:
|         - use curl for file delivery (provides multi-protocol support,
| 	  bandwidth limiting.)
| 
| 	  no sample available.
| 
| 
|         - have a parseable log for .sent when performing resends,
| 	  use the sent log to look for file names, then re-link from the db.
| 
| 	  no sample available.
| 
| 
|         - have a parseable log for :old, per circuit logic for :old
| 	  and scheduling.
| 
| 	  examples of conflicting algorithms:
| 	  	-- if it's older than 60 minutes, it's useless so
| 		    drop it (log to .old and delete)
| 		-- if there's a backlog, send the newest first.
| 		-- No matter what the age and backlog, ensure they are 
| 		   sent them in chronological order.
|           role of 'resender' is to recover files from the log, and
| 	  re-link from the db (only schedules for resend, does not resend.)
| 
| 	  The really interesting bit is having pluggable next file
| 	  selection routine.  The routine could read a whole directory
| 	  tree for a single tx client, and create prioritized list
| 	  of what to send (perhaps using a priority queue), then
| 	  fire off a curl process to do the sending,logging, & unlinking.
| 
| 	  no sample available.
| 
| 
| 
|   - Do it in a non-commital way, ie. keep pds-nccs PDS compatible,
|     so that we can mix and match.
|     put in a global setting 'use_pds' 1
|     will be 'obsoleted' later.  use_pds setting will turn off fet
|     integration.
| 
|     no sample available.
| 
| 
| 
|   - add to NCS socket protocol receivers the missing parameters for
|     routing.  in old PDS, there are two passes passed the config file.
|     first pass, is to pick the client, and deposit in the client q.
|     the second pass, is within the sender to figure out the destination
|     characteristics.  PDS-NCCS adds 'direct routing' which applies the
|     matching based on specific names (ie.  header2client.conf)
| 
|     so still need logic in the am protocol ingestor to figure out
|     the ingestname is (the name of the file to be placed in the db
|     and client directory, and used to match imasks for destination
|     characteristics... hm...)
| 
|     need some thinking... 
|       ... figure out the ingestname. (why? client imasks... you'll see)
|       ... do we still need patterns that match per client?
|       ... what about per client rejection of files (no match on second pass?)
| 
| 
| removing/changing configuration options:
| 
|   - there should be no options to support debugging, or if there
|     are such options, they should be clearly marked as such, and
|     not be required in config files for normal use.
| 
|   - there should be reasonable defaults for options, wherever possible.
| 
|   - client_id from the pds client config file names the config file
|     in the transmission directory trees for configuration and spooling
| 
|   - eliminate file path directives in configuration files, by defining
|     a standard hierarchy.
|     
|     if you start something like:
| 
|     ncsreceiver <source>
| 
|     it will have:
| 
|     config file is in /apps/fet/etc/rx/<source>.conf 
|     log file is in /apps/fet/log/rx/fetrx_<source>.<timestamp>
|     input q file is in /apps/fet/rx/<source>/<pri>_jjjHH/
|   
|     log_file will be separate per client.  same as rollover 
|     (daily,weekly,monthly) not a per client option, but a 
|     global one. (no need for setting in config file.
| 
|   - host/usr/pw moved into main configuration file.
|     (host removed from imask settings.) 
| 
|   - add destination directory setting replaces per line pattern.
|     Determines the destination directory to be used for patterns
|     on succeeding lines.
|     directory /........... 
| 
|   - protocol directive, determines the protocol used for deliveries
|     on succeeding lines.
| 
|   - add destination setting, which accepts URL style format.
|       destination http://usr:passwd@host/directory/WHATFN
| 
|   - allow any mix of host,user,password,protocol,directory, & destination
|     directives on succceeding lines.
| 
|   - no pdsswitch.conf or clientlist needed.
| 
|   - perhaps add 'include' directive so files can share parts.
| 
|   - add the 'active' directive.   turning a client or source on
|     or off should be a matter of toggling this setting, and -HUP
|     the master process.
| 
| 
| file hierarchy:
| 
| the nice thing about standards is there are so many to choose from...
| There is a linux file hierarchy standard (FHS - http://www.pathname.com/fhs/)
| normally applications which are installed into the system follow that.
| but there is also a standard of installing things under /opt, where
| an entire tree is encapsulated.   Then there is thre /apps tradition.
| to preserve the ability to accomodate all three file hierarchies, the
| application is split into three:
| 
| 	FET_DATA/ -- is where all the data is.  db, tx, etc...
| 		subdirectories: db, tx, rx
| 	FET_ETC/ -- is where all the configuration information is
| 
| 	FET_BIN/ -- is the binary run tree.  bin/ lib/ should be under there.
| 
| for maximum compatibility with history...
| FHS builtin style:   FET_DATA=/var/sppol/px,   FET_ETC=/etc/px, FET_BIN=/usr
| FHS opt style:   FET_DATA=/opt/px,   FET_ETC=/opt/px/etc, FET_BIN=/opt/px
| PDS style:   FET_DATA=/apps/px,   FET_ETC=/apps/px/etc, FET_BIN=/apps/px
| 
|         FET_DATA= /apps/px
| 	FET_DATA/db/<date>/
| 
| 	FET_DATA/rx/<source>/
| 
| 	FET_DATA/tx/<client>/[1..5] '_' YYYYMMDDHH
|         FET_DATA/log/		-- logs for statistics, monitoring etc...
| 	             rx/<client> -- is same logs for resending?
| 		     tx/<source>
| 
| 	eventually:
|         FET_ETC/
| 		fet.conf
| 		  -- global settings.
| 		     like 
| 		     'use_pds yes'
| 	        tx/<client>.conf
| 		rx/<source>.conf
| 
|      model logs on existing ones.
| 
| -------------------------------------
|      sample rx/<source>.conf
| 
| type dumb
| priority 3
| 
| 
| active yes
| ingest fill_missing
| priority 3
| system AMTCP2FILE
| site   DADS
| type   BULLETIN
| format ASCII
| routing direct
| 
| type am
| 
| -----------------------------
|     sample etc/tx/ppp1_wmo.conf
| 
| active yes
| log_roll_over  daily
| sleep_timer    10
| debug_level    3
| chmod          000
| 
| protocol https
| user am
| password Pr2namPW
| host ppp1.cmc.ec.gc.ca
| directory /tmp/data_wmo
| filename  WHATFN
| imask *:nwsA:*:*:* 
| destination https://fred:fredpass@fredwether.com/disk1/WHATFN
| imask *:nwsG:*:*:* 
| 
| destination NULL -- special meaning, just leave it there.. (in: /apps/fet/tx/<client>/<whatever> )
| .........................................
| 'include'
| 
| deferred:
|   - use sticky bit for reasonable security on input.
| 
|   - what does RASTER do?
|   - what does COMPRESS do? (mechanism)
|   - what do the other input threads do (pdschkrcis)
|   - conversion on input (compress, togif, 
