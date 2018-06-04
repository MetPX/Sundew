======
Sundew
======

WMO-GTS switch on TCP/IP protocols (largely obsolete, legacy code.)

History
-------

This was started in 2004, entered full production 2007. Approximately a dozen 
different developers contributed over it's life.  This application is 25 klocs
of python, that replaced Tandem/Apps 450 klocs + PDS (45 klocs) (20:1) reduction
in application code.  Provided most Meteorological switching for Canada from 
about 2006 until about 2017. Still in service but being gradually supplanted
by Sarracenia.  Same code base support both message and file transfer (was 
innovative at the time.)

Sundew is too constrained by early requirements to be modernized, so started
a fresh code base to work with modern needs: Sarracenia will eventually replace 
Sundew for (modernized versions of) the same use cases.  Suggest you look 
`there <http://github.com/MetPX/sarracenia>`_ if looking for something new to
deploy.

Features
--------

- Implements the WMO-GTS TCP/IP socket protocol (which is now deprecated by WMO.)
- Does not implement any X.25 (also deprecated by WMO.)
- Does implement a specific implementation of AFTN over TCP/IP.
- Does not handle dialup data collection (seems many expect a *wmo switch* to do that.)
- Whatever products it acquires, it stores it in a file, and then links the 
  file to queue directories to be sent on to a destination based on a routing 
  table. 

Documentation
-------------

Docs are `here <doc>`_

Installation
------------

On Ubuntu 14.04/16.04/17.10/18.04 and derivatives of same::

  sudo add-apt-repository ppa:ssc-hpc-chp-spc/metpx
  sudo apt-get update
  sudo apt-get install python-metpx-sundew  

To run Sundew, it is critical to install the cron cleanup jobs (mr-clean) since otherwise the
server will slow down continuously over time until it slows to a crawl.
It is recommended to subscribe to the mailing list and let us know what is stopping you from
trying it out, it could inspire us to work on that bit faster to get some collaboration
going.

Building From Source
--------------------

If not running on ubuntu, one must build from source code.  Please refer to 
`Sundew developer guide <DevGuide.rst>`_ for instructions on how to build 
*Metpx-Sundew*. Currently internal installations are done, one at a time, from
source. Development is done on the trunk release.  When we install 
operationally, the process consists of creating a branch, and running the branch
on a staging system, and then implementing on operational systems.  There are
README and INSTALL files that can be used for installation of sundew. One can
follow those instructions to get an initial installed system.

Sundew Binaries
---------------

MetPx-Sundew is available for download from our `Launchpad PPA <https://launchpad.net/~ssc-hpc-chp-spc/+archive/ubuntu/metpx>`_.
Please follow the instructions on in our PPA site on how to add the PPA to your
Ubuntu system and install the latest vesrion of MetPx-Sundew::

   sudo add-apt-repository ppa:ssc-hpc-chp-spc/metpx
   sudo apt-get update
   sudo apt-get install python-metpx-sundew 



