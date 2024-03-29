
==========================
MetPX Contributors Guide
==========================

.. contents::


Front Matter
------------

:Authors:
  Peter Silva,
  Daniel Lemay

:Version: 
  $Rev$ 
  $Date$
  Drafty Draft...

:Copyright::
  MetPX Copyright (C) 2004-2006  Environment Canada.
  MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
  named COPYING in the root of the source directory tree.
  or the *Licensing* section of this document.    



Making Better Software Together
---------------------------------

People are welcome to make changes to MetPX.  We are especially pleased
if those who make changes choose to contribute them back to the project
so that all users can benefit from the improvements.  The WMO messaging
community is very, very, small.  Cooperative development of a reference
switch implementation will benefit everyone.

If the reader is unfamiliar with open source methods, then some aspects
of this project may seem unusual.  Metpx strives to be a relatively standard 
open source development project.  The goal of open source is to reduce the overhead
of collaborating with people in other organizations to as near zero as
feasible, so people can work together to reduce costs and improve quality
of the tools available to the community.

As a collaborative development project, it tries to use the best practices
of open source projects as observed over the past decade.  

  * The most common open source license (GPLv2) is used for the project. This 
    license is used in approximately 60% of all open source projects, and when 
    multiple competitive projects with different licensing schemes have been 
    seen (ie. \*BSD vs. Linux) The GPL license has tended to build a more 
    cohesive community, and therefore developed a stronger product, than 
    applications built with other types of licenses.

  * the source code repository is on a public site, rather than one belonging 
    to the primary sponsor and rights holder.  This is to emphasize that the project
    is open to everyone, and that the primary rights holder has no particular
    privilege beyond those of potential contributors.

  * Other nations' met services, other government users, and industrial
    producers and consumers of met data, rather than being considered clients 
    or customers, are hoped to be collaborators in development, with an aim 
    of reducing costs for all over the long term. 

  * Companies and contractors are welcome to include the application in 
    their offerings, even bundling it with their own products, provided they do 
    not sell the software itself, or any derived products or improvements.  
    They must also include the source code for the application, including
    their modifications, when distributing the code.  Charging for support 
    of the products they integrate is perfectly reasonable and expected.  
    Actions which build up the collaborative development community are 
    welcome and encouraged.

    (tha above paragraph is not part of any licensing agreement, but an attempt
    to describe GPLv2 in layman's terms.  GPLv2 presents the complete 
    licensing terms.)

    Here are some examples of companies distributing GPLv2 software on a 
    commercial basis:  `RedHat <http://www.redhat.com>`_, 
    `Novell <http://www.novell.com>`_, `Ubuntu <http://www.canonical.com>`_, 
    `MySQL <http://www.mysql.com>`_, 
    `JBOSS <http://www.jboss.com>`_ (now a division of RedHat), 
    `SugarCRM <http://www.sugarCRM.com>`_.
    Well established integrators also profitably perform support roles without 
    being necessarily associated with the product itself, such as 
    `IBM <http://www.ibm.com>`_.  

    An example of a niche might be to provide turnkey solutions to clients
    which have little to no inhouse technical expertise.  A contract based
    on support costs would probably have little difference in it's cost vs.
    a conventional software sale.  For many vendors, creating the software
    is simply a cost for being in the integration niche.  The bigger
    the user base, the more likely other contributors will appear.  The
    use of GPL'd software is a net benefit for system integrators.



Contributor Background
------------------------

Leaving aside the community aspirations of an open source development project,
we can now turn to application development itself.  

The main development web-site is http://sourceforge.net/projects/metpx
where one can use can browse the git source tree over the web,
as well as examine the list of known bugs, and feature requests.
There are also two mailing lists which ought to be of interest to potential
contributors:

* `metpx-devel <https://lists.sourceforge.net/lists/listinfo/metpx-devel>`_ for
  discussions about development, and general support questions.
* `metpx-commit <https://lists.sourceforge.net/lists/listinfo/metpx-commit>`_
  which mails out the change descriptions created by developers as they
  commit changes to the repository.

Taking the time to read and comment on the documentation and commenting on 
bugs, participating on the mailing list submitting feature requests
are all very helpful activities to guide us in future development.
The kinds of skills What you might want to know to be able to help:

 * Basic knowledge of the Python programming language. 
 * Basic knowledge of Linux shell commands (ls, ps, cat, vi (or other editor)) etc...
 * Basic knowledge of Make (build automation tool.)
 * Basic knowledge of Subversion (source code management system.)
 * For documentation, ReStructured Text is your friend.  Dia for Diagrams.

If your knowledge of python is not encyclopedic, no worries, collaborating
means learning together too.  Collaboration is also a means for people
to collectively improve their skils.   


This manual describes ideal working methods we strive for.  Sometimes we do 
not manage to live up to our ideals.  If you find parts of the code that do not follow the 
prescriptions here, then it is either an oversight or code which existed 
before this guide was created, and not a license to deviate.  Please strive 
to follow the guide's principles.  If you really feel the need to 
violate the principles here, mail to metpx-devel for discussion first.



Development Platform: Any Old Linux Laptop Will Do
---------------------------------------------------

While MetPX runs at the CMC on highly redundant servers in a large cluster 
in a climate controlled room with a small army of highly trained 
specialists, it can run pretty much on any PC available on the market today.
A good development environment is to remotely login to a server in a machine
room, where real WMO bulletin and RADAR data streams are available, but 
the application does not expect or require any sort of cluster infrastructure,
and is not aware of one if it is in place.  It is blissfully ignorant of
anything beyond a single system.

One developer works exclusively on a vintage 2004 laptop running Kubuntu offsite,
with no connectivity the WMO or any weather centre.  With a faster system 
and/or more nodes, ultimate performance and reliability improve, but the 
application itself is identical.

You need to install a reasonably modern (i.e. Debian Sarge=3.1 or better, anything 
released later than 2005/06) linux distribution.  It will be easiest if you
use Debian, or Debian Derived operating system such as kubuntu on your laptop, 
as well as the necessary development tools (principally git, and 
several python modules) all of which are available from standard repositories.


Getting Source Code
-------------------

MetPX http://metpx.sourceforge.net is developed and used on Debian Linux Systems.  
There are no special dependencies on this linux distribution, but no testing 
of others is done.  Users of other Debian derived distributions should also have 
no trouble (Ubuntu and Kubuntu will work fine.)  

The simplest method of obtaining the source code is to open a shell window on
a linux system, and execute the command:

git clone git://git.code.sf.net/p/metpx/git metpx-git

Assuming it works, You will see a trunk directory. and you can set up
a loop back environment by:

Building a Package
------------------

Debian standard packaging used::

   dch

fill in debian/changelog with information about changes in latest release::

   debuild -us uc

build a package locally. Make sure it builds properly.
Only after that::

   git tag -a "0.YY.x" -m "something helpful"

YY is the last two digits of the year. x is the ordinaly number of releases in the year
or it could be the month...  After it is tagged::

   git push

Then proceed to Launchpad.net.  Need credentials for this account:

https://launchpad.net/~ssc-hpc-chp-spc

and the recipe is: metpx-sundew.  the next step is to "Request build(s)"
As no version of paramiko for python2 is not currently available on ubuntu 20.04
the last stable OS release for which a release can be built is therefore 18.04.





Running A Loopback Test as a Developer
----------------------------------------

Once you have the source code. go into the trunk/sundew directory.

| cd trunk/sundew
| export PXROOT=`pwd`
| export PATH="`pwd`/bin:${PATH}"
| echo "user=*<your user name>*" > etc/px.conf   
 
By setting PXROOT, PATH, as well putting the current user name in etc/px.conf,
you can now run the application in a 'developer' mode.  To try it out,
use the procedure from *A First Run* in the User's Guide, but use the PXETC 
setting from here. You might also need to create a few directories first.
something like:

| mkdir etc/rx etc/tx txq rxq db
| export PXETC=etc
| 

then the need to run all cat commands.

This should work as it did in the user guide.  Another way of working would
be to install the package normally, but set the path for the px user to
search your development path ahead of the default versions of metpx.


Changing the Documentation
-----------------------------

Editing Documentation Source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To edit the documentation, checkout the source code normally. then change
directory into the one containing the source of the manual you with
to modify. ie.. doc/dev.  Once there, you can use a text editor
to modify DevGuide.txt to make your own additions to the Contributor Guide.
The document is in *ReStructured Text* see http://docutils.sourceforge.net/rst.html
for details about that.  Once you have made your modifications to the .txt
save your changes, and run make to see create the corresponding html.
Review the html, and when satisfied, you can commit your changes back
to the repository just as one would do with source code.

Debian packages needed:
  * python-docutils  (includes rst2html)
  * dia (for editing diagrams & creating png's from .dia)
  * groff (for processing man pages.)  systems include groff-base by default, need full groff for html output.


Updating the Web Site
^^^^^^^^^^^^^^^^^^^^^^^^

The website content is generated from the doc/html directory.  There is a 
Makefile there, type make, and it will pull in HTML documentation from 
the rest of the project.  There is also master indexe.html and indexf.html 
which must be edited manually.
(English and French) after all the HTML is produced,  Review the site
by pointing a browser at this distory on your local system (file: url)

Once reviewed, one should commit the changes to the repository.
After the changes are committed, one can then update the actual web site.

From the doc/html directory, update the web site using a sourcforge 
account access:

  % scp * <user>,metpx@web.sourceforge.net:htdocs

General Information About Contributions
-----------------------------------------


additional features for the user community to share.  The goal is
 * subscribe to metpx-devel.
 * Visit metpx.sf.net, and then go to the sourceforge site.  Look at the bugs 
   and feature requests which are pending.  Feel free to add feature requests
   there. 
 * Propose/discuss your ideas on metpx-devel.
 * You can always use anonymous checkout to obtain the code and play with it.
 * Read this manual first !
 * do not add configuration options without discussion. (Principle 5)
 * consider performance when adding features. (Principle 4)
 * Apply Python Style Guide (even though some of the existing modules do not.)
 * Comments in the code should say what the goal of code is, rather than how 
   it is being done (code itself says how.) example to avoid (similar spots 
   in the code in multiple places):

		# process the bulletin
                self.processBulletin()
 
 * to become a project member email, one of the project admins. 
   FIXME: Cathedral vs. Bazaar... We are cathedral, striving for Bazaar :-)
   * please subscribe to metpx-commit and metpx-devel first.
   * probably will want to see some sample fixes, submitted as patches first.
 * once you have commit privileges:
 * develop happens mostly on the trunk 
 * commit working code.  Occasional breakage is normal, but try to avoid it.
   when committing code:
   * git pull
   * run a loopback test (read the logs to confirm basic functionality is still there.)
   * everything is OK?  clean up
   * git pull again, to make sure nothing else happenned.
   * git push.
 * Commit early, commit often:  This is a generally understood principle
   of distributed development, and is common practice in open source projects.
   Strive to commit small, self-contained, easily described fixes.  Before you
   start, think about what the description of the patch will be when you commmit.  
   If you can make a short single sentence that describes the intent of the patch,
   then you are on the right track.  Keep each modification to a single topic 
   (do not include several unrelated changes in a single commit.)  Keep changes 
   incremental.
 
   When working on longish features.  Try to break it down into individually
   useful (or at least harmless) changes, and commit each one sequentially as 
   they are implemented. 

   Some references for this point:

   http://jspwiki.org/wiki/CommitEarlyCommitOften
   http://dev.tikiwiki.org/3Rules
   http://wiki.winehq.org/GitWine

 * If you really need to break something, and it will have to stay broken for
   a long time, then create a branch.  They are easy and cheap in git.  
   Apply updates from the trunk while on a development branch, and perform as
   much merging as possible on the branch as you go, to minimize the integration
   work then a project gets folded back into the trunk.
   
		




MetPX Principles
------------------

The above practices are the same for most open source projects.  This section
presents the general approach behind code in MetPX.  Beyond what is in 
the basic Python Style Guide (80 column width, indenting and capitalization.)
There are some principles to how the application is meant to be 
built.  Principles do not have to be followed in every case, but it is
most often a good idea to follow them, and deviating without a good reason
will most often lead to unwanted outcomes.


1. Principle: Each message is stored in one file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first application design principle is to use files as an application 
storage method.  The contention is that storing messages in files 
provides sufficient performance, and will make the application 
simpler to implement, and generally applicable to a unification of
traditionally short messages and larger items as RADAR or satellite data 
for switching purposes.  


2. Principle: Avoid IPC
^^^^^^^^^^^^^^^^^^^^^^^^^^
combined with the above principle is to a principle of eliminating 
other forms of inter-process communications (IPC) relying only on the inherent 
locking provided by the file system.  If there is a lock in an algorithm, 
then that indicates where there are race conditions or potential 
contention.  The application is to be designed such that no such 
conditions arise, and avoid the need for performance altering synchronization.

for example:  
     * a message is received, all messages/files received are to have unique
       names such that there are no name clashes.
     * Since there are no name clashes, all processes can place files
       into the database and client queues in parallel.  Since there are
       no queues which need to be explicitly added to by the programs,
       there is no IPC needed to moderate access to the queues (five
       sources can simultaneously be adding items to a single client queue)
     * serialization of access to file system directories is taken care of by 
       operating system mechanisms, no code is required to support them.
       As these mechanisms are already heavily used, their reliability is assumed.   

Note::
  This is not a generalized slur against IPC, merely a statement that it is
  a very complex tool.  IPC, by it's nature, co-ordinates processes, and
  coordinating processes is going to make some of them wait some of the time.
  In cases where deadlocks are real and inevitable, IPC is invaluable.  However,
  if sufficient care and thought is taken, it is preferable to have processes work 
  a completely independently (without any co-ordination.), meaning no process
  ever has to wait for any other.  We have managed to do this in every case
  so far, why stop now?


3. Principle: Minimize File System Interactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Even if file system performance has been deemed adequate, it is still 
the element which limits  application performance, so optimization 
of interactions with the file system may provide significant benefits.

examples:

   * If we can pack all the routing information in the name, 
     we are better off. (avoid a stat call per file to route.)
     example here: better to have an ascii encoded date in the file name
     than perform a stat call.  (FIXME: TEST THIS!)

   * Want to minimize the number of times we touch a file
     initial creation (open), close (commits all writes), link, unlink, chmod.

   * PDS method of file protection (chmod 000 during xfer) is more
     expensive than renaming (FIXME: TEST THIS!)
     FIXME: wanted test confirming/denying the cost of these calls.

   * file and directory manipulation time is directly proportional to the
     lengths of the file names. (FIXME: reference long file name results.)
     so do not lengthen them beyond what you need.

   * When there is more than a few tens of thousands  of files in a 
     single directory, it becomes cumbersome to manage.  Plan out the
     directory tree to avoid having directories which exceed 100,000
     entries. (FIXME: figure out the test data to back this up.)


4. Principle:  No Performance critical coding without experimental data.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Whenever adding features one should start by evaluating how often the 
    feature will be called in the normal course of execution.

    Usually, performance in code is not an issue, because it will not be
    called often enough to warant optimization.  If the feature will be 
    used very frequently hoever, careful consideration to it's efficiency 
    is needed.  When programmers try to create efficient algorithms,
    they often guess wrong, so do not just guess.
    
    To examine performance, make some guesses.  Then make some small test 
    programs to verify the guesses.   Keep the testing hypothesis, and the 
    tests done to verify it by adding them to this Guide.  If the results 
    make sense, then start looking at how to modify things to be in 
    accordance with the hypothesis.

    Consult the Efficiency Tests Chapter for examples.


5. Principle: Minimize Configuration Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    
    A configuration setting should be created when there are multiple cases
    which are reasonably common.  When the same configuration string is present
    many times, that indicates a need for review.

    example problem:  The *batch* setting on senders is required in order to 
    compensate for different transfer rates.  On high speed channels, the 
    batch can be set quite high.  On low speed channels, it needs to be 
    set low.  Ideally an adaptive algorithm would do better than the current
    manual settings.  It would be nice to eliminate batch eventually.
    

6. Principle: Try not to decode the data (aka: We don't want to know.)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Sometimes it is un-avoidable, but normally, for metpx itself, we make
    a reasonable effort never to decode data when we have no need to.
    The reason for this is to simplify the code.  This way,
    it does not have to follow changes to formats as they evolve, does
    not have to decode data in order to route it (such as looking in
    the meta data of a GIF file for routing information.)
 
    It is also more efficient to look only at the name, than to have
    to parse all the data in a file (like, say a GRIB, or a RADAR volume scan.)

    In practice, with bulletin data, there are numerous cases where one
    is forced to parse the data.  MetPX does parse where necessary, but
    it does so reluctantly.  This is not a scientific research data
    management application, but a communications system.  The goal is to
    shuttle data between producers and consumers of data, with a minimum
    of knowledge about the data itself.

    This principle relates to metpx itself.  It is nonsense when applied
    to filters.  Filters, by their very nature need to decode data in order
    to transform it.  They are not subject to this principle.


7. Principle: There is no Cluster (metpx)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    This application will typically be deployed in a cluster.  Don't
    worry about it.  Pretend it isn't true.  The cluster architecture
    for metpx is an array of identically configured nodes, none of whom
    is aware that there is a cluster.  This is something of a corollary
    to *Principle 2: Avoid IPC*


8. Principle: Language is Important.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    If you find us using ornate phraseology in order to convey a concept,
    call us on it.  We will re-ify our definitions and phrasing methodology
    to...  um... We'll find a simpler way to say it, OK? We try to pick
    'le mot juste' (poor translation: The right word) so that the meaning
    of directives, log messages, and displays are self-evident.  We value
    clarity and brevity. (if you prefer: we like things short and clear!)


Efficiency Tests
----------------



Efficiency of date calls. PS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    I was worried calls to format strings of the time would be 
    expensive, because on some systems, they are (unfortunately acquire a lock
    to read the time, makes stuff slow.) wrote a loop below to try it out:

    |
    |    import time
    | 
    |    t=time.time()
    |    i=0
    |    den=100000
    |    while i < den:
    |      tl=time.time()
    |      today = time.strftime( "%Y%m%d", time.gmtime(tl) )
    |      i=i+1
    | 
    |    print tl, t, den, (tl-t)/den
    |

    and ran it on my laptop (linux 2.6.10 from kernel.org.) :
    1106969450.64 1106969449.84 100000 8.01682949066e-06

    in other words, it takes 8 microseconds per loop iteration.  So if performance 
    is limited to a few hundred or even a few thousand calls per second (as is 
    likely the case), then this call will account for only 0.1 % of execution time.  
    Not worth optimizing.  Avoids having to wonder when to check if the date changed.  

Disk Reader Tests 
^^^^^^^^^^^^^^^^^

    tests wanted:
    For whatever priority schemes we come up with, need to have methods
    to verify their behaviour in revovery situations...

     * large numbers of files, with lower priorities, and
     * and small numbers of files with high priorities.

    review results for messages per second, and data.

      * our normal peak 5/second
      * application rate few hundred per second.
      * recovery from failure is the performance driver.



File Name Verification 
^^^^^^^^^^^^^^^^^^^^^^

2005-02-09 (DL)

Note: These tests have been done on my personal computer, not a server.

A filename verification function has been added to the directory sorting
ingestor. The pattern to verify is written as a regex.

The verification is not included directly in the class that extracts the "keys"
from a filename. It implies that a first pass has to be done to eliminate the
"bad" files. It's better for the design and the overhead is negligible.

Testing has been done on ingestion of 12000 filenames. Here are the results:

    Time to ingest the 12000 filenames: ~16 seconds
    Time to verify the correctness of each filename: ~ 1 second
    Time to sort the good filenames (12000): ~ 1 second

Conclusion: The time spent for name verification is negligible in comparison
to the time passed to ingest.

We choose design over performance on this item.


File Creation Speed.
^^^^^^^^^^^^^^^^^^^^

2005-03-01 (DL)

Tests have been done on pds5.

We were able to create 20000 links in 0.75 second. This observation has
for consequence that we have let down worklists.


Validate and Sort File Names.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2005-03-01 (DL)

Tests have been done on pds5.

The tests consist in reading and validating filenames contained in a
directory and sorting the filenames (according to priority and timestamp). 


    ======= ============ =========
    Number  Time to read Sorting 
     of     and validate Time
    Files   filenames   
            (seconds)    (seconds)
    ======= ============ =========
    20000   ~ 1          ~ 1 
    40000   ~ 3          ~ 1 
    200000  ~ 15         ~ 8 
    ------- ------------ ---------
    100000  ~ 29         ~ 4 
    200000  ~ 60         ~ 8 
    ------- ------------ ---------
    100000  ~ 26         ~ 4 
    200000  ~ 52         ~ 8 
    ------- ------------ ---------
    40000   ~ 3          ~ 1 
    100000  ~ 7          ~ 4 
    200000  ~ 15         ~ 7 
    ======= ============ =========
    
    
Conclusion: There is a linear relathionship in both reading and sorting.
The sort times are very consistent (25000 files/second).  The read
times vary with system load,  even when the load was not percetible via
the 'uptime' command.  In all the above tests, system load was below 1.
The overall read rate varies from 3333 to 13333 files/second.





A Map of Files and Modules
---------------------------

This section gives a brief overview of the many pathnames in the running
tree, and breaks down the source code into functional groups of files.

Here is the running tree:

| initial file hierarchy:
|         PX_ROOT= /apps/px
| 	PX_ROOT/db/<date>/
| 	PX_ROOT/rxq/<source>/[1..5]_<YYYYMMDDHH>
| 	PX_ROOT/txq/<client>/[1..5]_<YYYYMMDDHH>
|       PX_ROOT/log/rx_<source>
|       PX_ROOT/log/tx_<client>
|        PX_ROOT/log/trx_<sourlient>
|        
|        PX_ROOT/etc/
|		px.conf
|		pxRouting.conf
|		stations.conf
|	        tx/<client>.conf
|	        trx/<sourlient>.conf
|		rx/<reception>.conf


What all the files are doing, generally, in the source...

================= ==========================================================================================
 path	          Explanation
================= ==========================================================================================
bin/              All the runnable scripts

                  px          : Send a command (start, stop, reload, status) to all receivers and senders
                  pxReceiver  : Send a command (start, stop, reload, status) to a receiver
                  pxSender    : Send a command (start, stop, reload, status) to a sender
                  pxTranceiver : Send a command (start, stop, reload, status) to a Transceiver 
                  (Tranceivers are rare... only there for AFTN.)
                  paplat      : Used to make latencies stats
                  pxChecker   : Restart a sender/receiver that should be running (cron each minute)
                  pxDBCleaner : Keep a certain amount of days in DB (cron each day)
----------------- ------------------------------------------------------------------------------------------
etc/              Configuration files for senders and receivers are put there
                  etc/rx/titi.conf  (example for a receiver)
                  etc/tx/toto.conf  (example for a sender)
                  pxRouting.conf (direct routing file)
                  stations.conf (map stations to bulletin headers (for collections & header completion.)
                  px.conf - sitewide settings, such as default extension, user names, PXROOT, etc...
----------------- ------------------------------------------------------------------------------------------
[r,t]xq/ 
                  Reception queues:     rxq/titi/  (example for a source titi)
                  Transmission queues:  txq/toto/3/2005110815/ (example for a client toto)
----------------- ------------------------------------------------------------------------------------------
db/               The database.
                  The file SAUY_SUMU_280100_00005:nws-alph:SUMU:SA:5:Direct:20051107210952
                  will be put in /apps/px/db/20051107/SA/nws-alph/SUMU/
----------------- ------------------------------------------------------------------------------------------
/apps/px/log/     Log files.
                  Log of source titi: /apps/px/log/rx_titi.log
                  Log of client toto: /apps/px/log/tx_toto.log
================= ==========================================================================================

The scripts in bin are basically stubs which all the appropriate routines in the lib directory.
The guts of the application are in lib.   Here is an introduction to the 

============================  ============================================================
Purpose                       Files
----------------------------  ------------------------------------------------------------
Bulletin Processing           bulletin.py
                              bulletinPlain.py
                              bulletinAm.py
                              bulletinWmo.py
                              bulletinManager.py
                              bulletinManagerAm.py
                              bulletinManagerWmo.py
----------------------------  ------------------------------------------------------------
Socket Management             socketManager.py
                              socketManagerAm.py
                              socketManagerWmo.py
----------------------------  ------------------------------------------------------------
General utilities             PDSPaths.py         : Useful paths for PDS   
                              PXPaths.py          : Useful paths for PX
                              SystemManager.py   
                              PDSManager.py
                              PXManager.py
                              CacheManager.py
                              Logger.py
                              mailLib.py
                              dateLib.py
----------------------------  ------------------------------------------------------------
Start, stop, restart, reload  Igniter.py
                              PXIgniter.py
----------------------------  ------------------------------------------------------------
Receivers and Senders         gateway.py
                              receiverAm.py
                              receiverWmo.py
                              senderAm.py
                              senderWmo.py
                              senderAMIS.py
                              SenderFTP.py
----------------------------  ------------------------------------------------------------
Configuration file parsing    Client.py
and ingestion                 Source.py
                              Ingestor.py
                              URLParser.py
----------------------------  ------------------------------------------------------------
Reading and Sorting           DiskReader.py
                              SortableString.py
                              StandardSorter.py
                              MultiKeysStringSorter.py
----------------------------  ------------------------------------------------------------
Switchover Procedure          SwitchoverCopier.py
                              SwitchoverDeleter.py
----------------------------  ------------------------------------------------------------
paplat                        LatMessage.py
                              Latencies.py
                              PXLatencies.py
                              PDSLatencies.py
                              Plotter.py
----------------------------  ------------------------------------------------------------
AFTN                          MessageAFTN.py
                              MessageManager.py
                              TransceiverAFTN.py
                              TextSplitter.py
============================  ============================================================






Terminology/Glossary
----------------------------------


Circuits
     Circuits are established relationships with other machines.
     Circuits are unidirectional and can be divided into two types:
     We receive products from 'source' circuits and deliver products
     to 'client' circuits.   For bi-directional connections, the trx
     configuration directory includes 'sourlient' circuit definitions.
   
     The term circuit is used loosely, as in this case it applies
     to file reception and delivery as well as traditional permanent
     connections.
   
Directions
     all directions are relative to the entire machine, not any sub-component.
     if files are on their way into the machine, they are rx (reception) files.
     if they are on their way out from the machine, they are tx (transmission) files.
   
     sample confusion to be avoided:
     ie. in PDS, the 'incoming' directory is where one places files which are outgoing from the server,
     because they are 'incoming' to the client.  Such a directory name is very confusing.
     in PX, the analogous files are under the transmit txq directory hierarchy.

Clients
     locations to which products are delivered.
     same terminology as the PDS.

sources 
     one (or more, depends on priority setting in config.)
     places where files can be received.

Sourlient
     Combined source & client... Tranceiver type channels.  Bi-directional.

Reception Name
     Files are received with a "reception name" in the rxq.
     To the reception name, receivers typically add an extension, to create
     the ingest name.

Ingest Name
     Ingest name is used to store the file in the DB, as is.

     for soon to be deprecated patterned routing (see below):
     ingest name is mapped against patterns to find clients who 
     will be sent the file.

Destination File Name
     destination file name, destfn, is calculated:
     default is first field of ingest name.
     add suffixes according to DESTFN parameter setting in pattern.

Version1 Routing
     combines Direct Routing with patterns and caching...
     coming soon (version1/rx_algorithm.txt)

Direct Routing
     routing using a lookup table, tandem style, with direct correspondence
     between source and client.  Used by almost all receivers.

Pattern Routing
     traditional PDS routing, via emasks & imasks
     Single-file receiver accurately reproduces PDS routing.
     just looks at imasks/emasks in clients.  Expect latencies to grow 
     longer as more clients and patterns are added to a configuration.
     This method is to be deprecated in favour of the, as yet only in
     discussion phase, version1/rx_algorithm.txt

Derived Products, Filters, Transformations, post_ingest_processing
     once a product has been received, create another one based on it. 


Licensing
----------
The primary license for distribution of this software is the General Public 
License, Version 2.  For individuals or groups wishing to license the application 
under other terms, they may approach the copyright holders and negotiate a different 
license more appropriate for their needs.

For now, the only rights holder on the application is the Government of Canada.
However, contributors retain the rights to their contributions.  So when major
contributions arrive, any potential licensee will have to negotiate with all 
appropriate rights holders.

The Text of the GPLv2, as reference material, follows:

| 
| 		    GNU GENERAL PUBLIC LICENSE
| 		       Version 2, June 1991
| 
|  Copyright (C) 1989, 1991 Free Software Foundation, Inc.
|      59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
|  Everyone is permitted to copy and distribute verbatim copies
|  of this license document, but changing it is not allowed.
| 
| 			    Preamble
| 
|   The licenses for most software are designed to take away your
| freedom to share and change it.  By contrast, the GNU General Public
| License is intended to guarantee your freedom to share and change free
| software--to make sure the software is free for all its users.  This
| General Public License applies to most of the Free Software
| Foundation's software and to any other program whose authors commit to
| using it.  (Some other Free Software Foundation software is covered by
| the GNU Library General Public License instead.)  You can apply it to
| your programs, too.
| 
|   When we speak of free software, we are referring to freedom, not
| price.  Our General Public Licenses are designed to make sure that you
| have the freedom to distribute copies of free software (and charge for
| this service if you wish), that you receive source code or can get it
| if you want it, that you can change the software or use pieces of it
| in new free programs; and that you know you can do these things.
| 
|   To protect your rights, we need to make restrictions that forbid
| anyone to deny you these rights or to ask you to surrender the rights.
| These restrictions translate to certain responsibilities for you if you
| distribute copies of the software, or if you modify it.
| 
|   For example, if you distribute copies of such a program, whether
| gratis or for a fee, you must give the recipients all the rights that
| you have.  You must make sure that they, too, receive or can get the
| source code.  And you must show them these terms so they know their
| rights.
| 
|   We protect your rights with two steps: (1) copyright the software, and
| (2) offer you this license which gives you legal permission to copy,
| distribute and/or modify the software.
| 
|   Also, for each author's protection and ours, we want to make certain
| that everyone understands that there is no warranty for this free
| software.  If the software is modified by someone else and passed on, we
| want its recipients to know that what they have is not the original, so
| that any problems introduced by others will not reflect on the original
| authors' reputations.
| 
|   Finally, any free program is threatened constantly by software
| patents.  We wish to avoid the danger that redistributors of a free
| program will individually obtain patent licenses, in effect making the
| program proprietary.  To prevent this, we have made it clear that any
| patent must be licensed for everyone's free use or not licensed at all.
| 
|   The precise terms and conditions for copying, distribution and
| modification follow.
| 
| 		    GNU GENERAL PUBLIC LICENSE
|    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
| 
|   0. This License applies to any program or other work which contains
| a notice placed by the copyright holder saying it may be distributed
| under the terms of this General Public License.  The "Program", below,
| refers to any such program or work, and a "work based on the Program"
| means either the Program or any derivative work under copyright law:
| that is to say, a work containing the Program or a portion of it,
| either verbatim or with modifications and/or translated into another
| language.  (Hereinafter, translation is included without limitation in
| the term "modification".)  Each licensee is addressed as "you".
| 
| Activities other than copying, distribution and modification are not
| covered by this License; they are outside its scope.  The act of
| running the Program is not restricted, and the output from the Program
| is covered only if its contents constitute a work based on the
| Program (independent of having been made by running the Program).
| Whether that is true depends on what the Program does.
| 
|   1. You may copy and distribute verbatim copies of the Program's
| source code as you receive it, in any medium, provided that you
| conspicuously and appropriately publish on each copy an appropriate
| copyright notice and disclaimer of warranty; keep intact all the
| notices that refer to this License and to the absence of any warranty;
| and give any other recipients of the Program a copy of this License
| along with the Program.
| 
| You may charge a fee for the physical act of transferring a copy, and
| you may at your option offer warranty protection in exchange for a fee.
| 
|   2. You may modify your copy or copies of the Program or any portion
| of it, thus forming a work based on the Program, and copy and
| distribute such modifications or work under the terms of Section 1
| above, provided that you also meet all of these conditions:
| 
|     a) You must cause the modified files to carry prominent notices
|     stating that you changed the files and the date of any change.
| 
|     b) You must cause any work that you distribute or publish, that in
|     whole or in part contains or is derived from the Program or any
|     part thereof, to be licensed as a whole at no charge to all third
|     parties under the terms of this License.
| 
|     c) If the modified program normally reads commands interactively
|     when run, you must cause it, when started running for such
|     interactive use in the most ordinary way, to print or display an
|     announcement including an appropriate copyright notice and a
|     notice that there is no warranty (or else, saying that you provide
|     a warranty) and that users may redistribute the program under
|     these conditions, and telling the user how to view a copy of this
|     License.  (Exception: if the Program itself is interactive but
|     does not normally print such an announcement, your work based on
|     the Program is not required to print an announcement.)
| 
| These requirements apply to the modified work as a whole.  If
| identifiable sections of that work are not derived from the Program,
| and can be reasonably considered independent and separate works in
| themselves, then this License, and its terms, do not apply to those
| sections when you distribute them as separate works.  But when you
| distribute the same sections as part of a whole which is a work based
| on the Program, the distribution of the whole must be on the terms of
| this License, whose permissions for other licensees extend to the
| entire whole, and thus to each and every part regardless of who wrote it.
| 
| Thus, it is not the intent of this section to claim rights or contest
| your rights to work written entirely by you; rather, the intent is to
| exercise the right to control the distribution of derivative or
| collective works based on the Program.
| 
| In addition, mere aggregation of another work not based on the Program
| with the Program (or with a work based on the Program) on a volume of
| a storage or distribution medium does not bring the other work under
| the scope of this License.
| 
|   3. You may copy and distribute the Program (or a work based on it,
| under Section 2) in object code or executable form under the terms of
| Sections 1 and 2 above provided that you also do one of the following:
| 
|     a) Accompany it with the complete corresponding machine-readable
|     source code, which must be distributed under the terms of Sections
|     1 and 2 above on a medium customarily used for software interchange; or,
| 
|     b) Accompany it with a written offer, valid for at least three
|     years, to give any third party, for a charge no more than your
|     cost of physically performing source distribution, a complete
|     machine-readable copy of the corresponding source code, to be
|     distributed under the terms of Sections 1 and 2 above on a medium
|     customarily used for software interchange; or,
| 
|     c) Accompany it with the information you received as to the offer
|     to distribute corresponding source code.  (This alternative is
|     allowed only for noncommercial distribution and only if you
|     received the program in object code or executable form with such
|     an offer, in accord with Subsection b above.)
| 
| The source code for a work means the preferred form of the work for
| making modifications to it.  For an executable work, complete source
| code means all the source code for all modules it contains, plus any
| associated interface definition files, plus the scripts used to
| control compilation and installation of the executable.  However, as a
| special exception, the source code distributed need not include
| anything that is normally distributed (in either source or binary
| form) with the major components (compiler, kernel, and so on) of the
| operating system on which the executable runs, unless that component
| itself accompanies the executable.
| 
| If distribution of executable or object code is made by offering
| access to copy from a designated place, then offering equivalent
| access to copy the source code from the same place counts as
| distribution of the source code, even though third parties are not
| compelled to copy the source along with the object code.
| 
|   4. You may not copy, modify, sublicense, or distribute the Program
| except as expressly provided under this License.  Any attempt
| otherwise to copy, modify, sublicense or distribute the Program is
| void, and will automatically terminate your rights under this License.
| However, parties who have received copies, or rights, from you under
| this License will not have their licenses terminated so long as such
| parties remain in full compliance.
| 
|   5. You are not required to accept this License, since you have not
| signed it.  However, nothing else grants you permission to modify or
| distribute the Program or its derivative works.  These actions are
| prohibited by law if you do not accept this License.  Therefore, by
| modifying or distributing the Program (or any work based on the
| Program), you indicate your acceptance of this License to do so, and
| all its terms and conditions for copying, distributing or modifying
| the Program or works based on it.
| 
|   6. Each time you redistribute the Program (or any work based on the
| Program), the recipient automatically receives a license from the
| original licensor to copy, distribute or modify the Program subject to
| these terms and conditions.  You may not impose any further
| restrictions on the recipients' exercise of the rights granted herein.
| You are not responsible for enforcing compliance by third parties to
| this License.
| 
|   7. If, as a consequence of a court judgment or allegation of patent
| infringement or for any other reason (not limited to patent issues),
| conditions are imposed on you (whether by court order, agreement or
| otherwise) that contradict the conditions of this License, they do not
| excuse you from the conditions of this License.  If you cannot
| distribute so as to satisfy simultaneously your obligations under this
| License and any other pertinent obligations, then as a consequence you
| may not distribute the Program at all.  For example, if a patent
| license would not permit royalty-free redistribution of the Program by
| all those who receive copies directly or indirectly through you, then
| the only way you could satisfy both it and this License would be to
| refrain entirely from distribution of the Program.
| 
| If any portion of this section is held invalid or unenforceable under
| any particular circumstance, the balance of the section is intended to
| apply and the section as a whole is intended to apply in other
| circumstances.
| 
| It is not the purpose of this section to induce you to infringe any
| patents or other property right claims or to contest validity of any
| such claims; this section has the sole purpose of protecting the
| integrity of the free software distribution system, which is
| implemented by public license practices.  Many people have made
| generous contributions to the wide range of software distributed
| through that system in reliance on consistent application of that
| system; it is up to the author/donor to decide if he or she is willing
| to distribute software through any other system and a licensee cannot
| impose that choice.
| 
| This section is intended to make thoroughly clear what is believed to
| be a consequence of the rest of this License.
| 
|   8. If the distribution and/or use of the Program is restricted in
| certain countries either by patents or by copyrighted interfaces, the
| original copyright holder who places the Program under this License
| may add an explicit geographical distribution limitation excluding
| those countries, so that distribution is permitted only in or among
| countries not thus excluded.  In such case, this License incorporates
| the limitation as if written in the body of this License.
| 
|   9. The Free Software Foundation may publish revised and/or new versions
| of the General Public License from time to time.  Such new versions will
| be similar in spirit to the present version, but may differ in detail to
| address new problems or concerns.
| 
| Each version is given a distinguishing version number.  If the Program
| specifies a version number of this License which applies to it and "any
| later version", you have the option of following the terms and conditions
| either of that version or of any later version published by the Free
| Software Foundation.  If the Program does not specify a version number of
| this License, you may choose any version ever published by the Free Software
| Foundation.
| 
|   10. If you wish to incorporate parts of the Program into other free
| programs whose distribution conditions are different, write to the author
| to ask for permission.  For software which is copyrighted by the Free
| Software Foundation, write to the Free Software Foundation; we sometimes
| make exceptions for this.  Our decision will be guided by the two goals
| of preserving the free status of all derivatives of our free software and
| of promoting the sharing and reuse of software generally.
| 
| 			    NO WARRANTY
| 
|   11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
| FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
| OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
| PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
| OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
| MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
| TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
| PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
| REPAIR OR CORRECTION.
| 
|   12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
| WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
| REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
| INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
| OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
| TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
| YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
| PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
| POSSIBILITY OF SUCH DAMAGES.
| 
| 		     END OF TERMS AND CONDITIONS
| 
| 	    How to Apply These Terms to Your New Programs
| 
|   If you develop a new program, and you want it to be of the greatest
| possible use to the public, the best way to achieve this is to make it
| free software which everyone can redistribute and change under these terms.
| 
|   To do so, attach the following notices to the program.  It is safest
| to attach them to the start of each source file to most effectively
| convey the exclusion of warranty; and each file should have at least
| the "copyright" line and a pointer to where the full notice is found.
| 
|     <one line to give the program's name and a brief idea of what it does.>
|     Copyright (C) <year>  <name of author>
| 
|     This program is free software; you can redistribute it and/or modify
|     it under the terms of the GNU General Public License as published by
|     the Free Software Foundation; either version 2 of the License, or
|     (at your option) any later version.
| 
|     This program is distributed in the hope that it will be useful,
|     but WITHOUT ANY WARRANTY; without even the implied warranty of
|     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
|     GNU General Public License for more details.
| 
|     You should have received a copy of the GNU General Public License
|     along with this program; if not, write to the Free Software
|     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
| 
| 
| Also add information on how to contact you by electronic and paper mail.
| 
| If the program is interactive, make it output a short notice like this
| when it starts in an interactive mode:
| 
|     Gnomovision version 69, Copyright (C) year  name of author
|     Gnomovision comes with ABSOLUTELY NO WARRANTY; for details type \`show w'.
|     This is free software, and you are welcome to redistribute it
|     under certain conditions; type \`show c' for details.
| 
| The hypothetical commands \`show w' and \`show c' should show the appropriate
| parts of the General Public License.  Of course, the commands you use may
| be called something other than \`show w' and \`show c'; they could even be
| mouse-clicks or menu items--whatever suits your program.
| 
| You should also get your employer (if you work as a programmer) or your
| school, if any, to sign a "copyright disclaimer" for the program, if
| necessary.  Here is a sample; alter the names:
| 
|   Yoyodyne, Inc., hereby disclaims all copyright interest in the program
|   \`Gnomovision' (which makes passes at compilers) written by James Hacker.
| 
|   <signature of Ty Coon>, 1 April 1989
|   Ty Coon, President of Vice
| 
| This General Public License does not permit incorporating your program into
| proprietary programs.  If your program is a subroutine library, you may
| consider it more useful to permit linking proprietary applications with the
| library.  If this is what you want to do, use the GNU Library General
| Public License instead of this License.
