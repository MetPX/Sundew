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

sys.path.append("../")
sys.path.insert(1, '/apps/px/lib/importedLibs')
import PXPaths; PXPaths.normalPaths()

def headerToLocation(self, header):
    """
    Transform a bulletin filename (header) into its location in the database.
    """
    
    headerParts = header.split(":")
    dbPath = PXPaths.DB
    date = headerParts[-1][0:8] # First eight caracters of the timestamp 
    tt = headerParts[0][0:2] # First two letters of the TTAAii
    target = headerParts[1]
    cccc = headerParts[2]

    return "%s%s/%s/%s/%s/%s" % (dbPath, date, tt, target, cccc, header)
