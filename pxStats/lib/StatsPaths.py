#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: StatsPaths.py
#
# Author      : Nicholas Lemay, 
#
# Date        : 2007-05-14
#
# Description : This class file contains all the needed paths within the differents 
#               stats library programs. This will prevent the programs to have hard-coded 
#               paths and make path changes simple by having to change a path that is used 
#               x number of times only once. 
# 
#############################################################################################
"""

import os, sys
"""
    Small function that adds pxlib to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    PXPaths requires pxlib 
"""
 
import PXPaths


class StatsPaths:
    
    
    """
        PDS RELATED PATHS
    """
    PDSCOLGRAPHS = '/apps/pds/tools/Columbo/ColumboShow/graphs/'
    PDSCOLLOGS   = '/apps/pds/tools/Columbo/ColumboShow/log/'
    PDSCOLETC    = '/apps/pds/tools/Columbo/etc/'
    
    
    """
        MetPX related paths
    """
    PXPaths.normalPaths()
    PXROOT   = PXPaths.ROOT
    PXLIB    = PXPaths.LIB
    PXLOG    = PXPaths.LOG
    PXETC    = PXPaths.ETC 
    PXETCRX  = PXPaths.RX_CONF
    PXETCTX  = PXPaths.TX_CONF
    PXETCTRX = PXPaths.TRX_CONF
    
    
    """
        Stats specific paths.
        pxStats must be checked-out in a pxStats folder.
    """ 
    
    STATSROOT   =  os.path.dirname( sys.argv[0] )   
    while(os.path.basename(STATSROOT) != "pxStats" ):
        STATSROOT = os.path.dirname(STATSROOT)
    
    STATSROOT = STATSROOT + "/"   
       
     
    STATSBIN     = STATSROOT + 'bin/'
    STATSDATA    = STATSROOT + 'data/'
    STATSDOC     = STATSROOT + 'doc/'
    STATSETC     = STATSROOT + 'etc/'
    STATSLIB     = STATSROOT + 'lib/'
    STATSLOGGING = STATSROOT + 'logs/'
    STATSMAN     = STATSROOT + 'man/'
     
    
    STATSPXCONFIGS    = STATSETC + 'pxConfigFiles/' 
    STATSPXRXCONFIGS  = STATSPXCONFIGS + 'rx/'
    STATSPXTXCONFIGS  = STATSPXCONFIGS + 'tx/'
    STATSPXTRXCONFIGS = STATSPXCONFIGS + 'trx/'
        
    STATSLIBRARY = STATSLIB
    
    STATSDB               = STATSDATA + 'databases/'
    STATSCURRENTDB        = STATSDB   + 'currentDatabases/'
    STATSCURRENTDBUPDATES = STATSDB   + 'currentDatabasesTimeOfUpdates/'
    STATSDBBACKUPS        = STATSDB   + 'databasesBackups/'
    STATSDBUPDATESBACKUPS = STATSDB   + 'databasesTimeOfUpdatesBackups/'    
    
    
    STATSFILEVERSIONS     = STATSDATA + 'fileAcessVersions/'
    STATSMONITORING       = STATSDATA + 'monitoring/'
    STATSPICKLES          = STATSDATA + 'pickles/'
    STATSLOGS             = STATSDATA + 'logs/'
    STATSWEBPAGES         = STATSDATA + 'webPages/'
    STATSGRAPHS           = STATSDATA + 'graphics/'
    STATSWEBGRAPHS        = STATSGRAPHS + 'webGraphics/'
    STATSCOLGRAPHS        = STATSWEBGRAPHS + 'columbo/'
    
    STATSPICKLESTIMEOFUPDATES    = STATSDATA + 'picklesTimeOfUpdates'
    STATSFILEACCESSVERSIONS      = STATSDATA + 'fileAccessVersions'
    
    
    
def main():
    """
        Small test case. 
        
        Shows current path settings.
        
        Shows user wheter or not paths are
        what they are expected to be.
    
    """
    
    print "pds/px pathssection : "
    print "StatsPaths.PDSCOLETC :%s" %StatsPaths.PDSCOLETC
    print "StatsPaths.PDSCOLGRAPHS :%s" %StatsPaths.PDSCOLGRAPHS
    print "StatsPaths.PDSCOLLOGS :%s" %StatsPaths.PDSCOLLOGS
    print "StatsPaths.PXETC :%s" %StatsPaths.PXETC
    print "StatsPaths.PXETCRX :%s" %StatsPaths.PXETCRX
    print "StatsPaths.PXETCTRX :%s" %StatsPaths.PXETCTRX
    print "StatsPaths.PXETCTX :%s" %StatsPaths.PXETCTX
    print "StatsPaths.PXLIB :%s" %StatsPaths.PXLIB
    print "StatsPaths.PXLOG :%s" %StatsPaths.PXLOG
    print "StatsPaths.PXROOT :%s" %StatsPaths.PXROOT
    
    print 
    print 
    print "Stats paths section : "
    print "StatsPaths.STATSBIN %s" %StatsPaths.STATSBIN
    print "StatsPaths.STATSCOLGRAPHS %s" %StatsPaths.STATSCOLGRAPHS
    print "StatsPaths.STATSCURRENTDB %s" %StatsPaths.STATSCURRENTDB
    print "StatsPaths.STATSCURRENTDBUPDATES %s" %StatsPaths.STATSCURRENTDBUPDATES
    print "StatsPaths.STATSDATA %s" %StatsPaths.STATSDATA
    print "StatsPaths.STATSDB %s" %StatsPaths.STATSDB
    print "StatsPaths.STATSDBBACKUPS %s" %StatsPaths.STATSDBBACKUPS
    print "StatsPaths.STATSDBUPDATESBACKUPS %s" %StatsPaths.STATSDBUPDATESBACKUPS
    print "StatsPaths.STATSDOC %s" %StatsPaths.STATSDOC
    print "StatsPaths.STATSETC %s" %StatsPaths.STATSETC
    print "StatsPaths.STATSFILEVERSIONS %s" %StatsPaths.STATSFILEVERSIONS
    print "StatsPaths.STATSGRAPHS %s" %StatsPaths.STATSGRAPHS
    print "StatsPaths.STATSLIB %s" %StatsPaths.STATSLIB
    print "StatsPaths.STATSLIBRARY %s" %StatsPaths.STATSLIBRARY
    print "StatsPaths.STATSLOGS %s" %StatsPaths.STATSLOGS
    print "StatsPaths.STATSLOGGING %s" %StatsPaths.STATSLOGGING
    print "StatsPaths.STATSMAN %s" %StatsPaths.STATSMAN
    print "StatsPaths.STATSMONITORING %s" %StatsPaths.STATSMONITORING
    print "StatsPaths.STATSPICKLES %s" %StatsPaths.STATSPICKLES
    print "StatsPaths.STATSPXCONFIGS %s" %StatsPaths.STATSPXCONFIGS
    print "StatsPaths.STATSPXRXCONFIGS %s" %StatsPaths.STATSPXRXCONFIGS
    print "StatsPaths.STATSPXTRXCONFIGS %s" %StatsPaths.STATSPXTRXCONFIGS
    print "StatsPaths.STATSPXTXCONFIGS %s" %StatsPaths.STATSPXTXCONFIGS
    print "StatsPaths.STATSROOT %s" %StatsPaths.STATSROOT
    print "StatsPaths.STATSWEBGRAPHS %s" %StatsPaths.STATSWEBGRAPHS
    print "StatsPaths.STATSWEBPAGES %s" %StatsPaths.STATSWEBPAGES
    
    
    
        
if __name__ == "__main__":
    main()    
    
    
    
    
    
    
    
    
