"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: SearchResendUtils.py
#
# Author: Dominik Douville-Belanger
#
# Description: This module contain utility function for
#              the search and resend processes.
#              THIS IS A WORK IN PROGRESS
#              (it was added late in the product lifecycle)
#
# Date: 2006-08-16
#
###########################################################
"""

import sys
sys.path.insert(1,sys.path[0] + '/../')
sys.path.append(sys.path[1] + "/importedLibs")
import PXPaths; PXPaths.normalPaths()

def headerToLocation(header):
    """
    Transform a bulletin filename (header) into its location in the database.
    ex: SACN31_CWAO_151300__CYXX_75340    ncp2    CWAO    SA    3    Direct    20060815130152
                    [0]                    [1]     [2]   [3]   [4]     [5]       [6] or [-1]
    """
    
    headerParts = header.split(":")
    dbPath = PXPaths.DB
    date = headerParts[-1][0:8] # First eight caracters of the timestamp 
    tt = headerParts[3]
    target = headerParts[1]
    cccc = headerParts[2]

    return "%s%s/%s/%s/%s/%s" % (dbPath, date, tt, target, cccc, header)
