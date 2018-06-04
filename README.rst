======
Sundew
======

WMO-GTS switch on TCP/IP protocols (largely obsolete, legacy code.)

History
-------

This was started in 2004, entered full production 2007.  about a dozen different developers over it's life.
This application is 25 klocs of python, that replaced Tandem/Apps 450 klocs + PDS (45 klocs) (20:1) reduction
in application code.  Provided most Meteorological switching for Canada from about 2006 until about 2017.  
Still in service but being gradually supplanted by Sarracenia.  Same code base support both message and
file transfer (was innovative at the time.)

Sundew is too constrained by early requirements to be modernized, so started a fresh code base
to work with modern needs: Sarracenia will eventually replace Sundew for (modernized versions of)
the same use case.

Suggest you look there if looking for something new to deploy: http://github.com/MetPX/sarracenia

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

Docs are `here <docs>`_

Installation
------------

On Ubuntu 14.04/16.04/17.10/18.04 and derivatives of same::

  sudo add-apt-repository ppa:ssc-hpc-chp-spc/metpx
  sudo apt-get update
  sudo apt-get install python-metpx-sundew  





