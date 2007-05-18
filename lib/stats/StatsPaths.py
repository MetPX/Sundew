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
"""
STATSROOT   =  PXROOT + 'stats/'

STATSPXCONFIGS    = STATSROOT + 'pxConfigs/' 
STATSPXRXCONFIGS  = STATSPXCONFIGS + 'rx/'
STATSPXTXCONFIGS  = STATSPXCONFIGS + 'tx/'
STATSPXTRXCONFIGS = STATSPXCONFIGS + 'trx/'

STATSLIBRARY    = PXLIB + 'stats/'
STATSDBUPDATESBACKUPS = STATSROOT + 'DATABASE-UPDATES_BACKUPS/'
STATSDB         = STATSROOT + 'databases/'
STATSDBBACKUPS  = STATSROOT + 'databases_backups/'
STATSDBUPDATES  = STATSROOT + 'DATABASE-UPDATES/'
STATSMONITORING = STATSROOT + 'statsMonitoring/'
STATSPICKLES    = STATSROOT + 'pickles/'
STATSWEBPAGES   = STATSROOT + 'webPages/'
STATSGRAPHS     = STATSROOT + 'graphs/'
STATSWEBGRAPHS  = STATSGRAPHS + 'webGraphics/'
STATSCOLGRAPHS  = STATSWEBGRAPHS + 'columbo/'



