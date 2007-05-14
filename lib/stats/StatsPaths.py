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

import os 
import PXPaths

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
    Stats-only paths.
"""
STATSROOT   =  PXROOT + 'stats/'

STATSPXCONFIGS    = STATSROOT + 'pxConfigs/' 
STATSPXRXCONFIGS  = STATSPXCONFIGS + 'rx/'
STATSPXTXCONFIGS  = STATSPXCONFIGS + 'tx/'
STATSPXTRXCONFIGS = STATSPXCONFIGS + 'trx/'

STATSLIBRARY    = PXLIB + 'stats/'
STATSGRAPHS     = STATSROOT + 'graphs/'
STATSDB         = STATSROOT + 'databases/'
STATSDBBACKUPS  = STATSROOT + 'databases_backups/'
STATSDBUPDATES  = STATSROOT + 'DATABASE-UPDATES/'
STATSMONITORING = STATSROOT + 'statsMonitoring/'
STATSPICKLES    = STATSROOT + 'pickles/'
STATSWEBPAGES   = STATSROOT + 'webPages/'
STATSDBUPDATESBACKUPS = STATSROOT + 'DATABASE-UPDATES_BACKUPS/'
