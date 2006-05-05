# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: CollectionUtils.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           
# Date: 2006-02-09
#
# Description:  This module holds various functions which serve as collection utilities
#
# Revision History: 
#               
#############################################################################################
"""
__version__ = '1.0'

import sys, os, os.path, string, commands, re, signal, fnmatch
import PXPaths
PXPaths.normalPaths()              # Access to PX paths


def calculateBBBDirName(bulletin):
    """ calculateBBBDirName(bulletin)

        Given a bulletin, this method calculates the directory path for the 
        bulletin including the BBB field in the path.
    """
    #-----------------------------------------------------------------------------------------
    # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
    #-----------------------------------------------------------------------------------------
    dirName = calculateBulletinDir(bulletin.getTwoLetterType(), \
                                   bulletin.getTimeStampWithMinsSetToZero(), \
                                   bulletin.getOrigin(), bulletin.getFullType())

    #-----------------------------------------------------------------------------------------
    # Returns the true BBB such as 'RRX1' or 'RRA'
    #-----------------------------------------------------------------------------------------
    BBB = bulletin.getCollectionBBB()

    #-----------------------------------------------------------------------------------------
    # Add the BBB field to the path (/apps/px/collection/SA/041200/CYOW/SACNxx/RRA)
    #-----------------------------------------------------------------------------------------
    dirName = "%s/%s" % (dirName, BBB)
    return dirName.strip()


def calculateOnTimeDirName(bulletin,collectionConfigParser):
    """ calculateOnTimeDirName(bulletin,collectionConfigParser)

        Given a bulletin, this method calculates the on time directory path for the 
        bulletin. Note that since all bulletins are considered on time, the
        directory's minute field will be force to 00 indicating that all 
        items in this directory are on time and meant for the top of the hour.
    """
    #-----------------------------------------------------------------------------------------
    # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
    #-----------------------------------------------------------------------------------------
    dirName = calculateBulletinDir(bulletin.getTwoLetterType(), \
                                   bulletin.getTimeStampWithMinsSetToZero(), \
                                   bulletin.getOrigin(), bulletin.getFullType())

    reportType = bulletin.getTwoLetterType()
    validTime = collectionConfigParser.getReportValidTimeByHeader(reportType)
    #-----------------------------------------------------------------------------------------
    # Append the on-time dir name to the path (/apps/px/collection/SA/041200/CYOW/SACNXX/7min)
    #-----------------------------------------------------------------------------------------
    dirName = "%s/%smin" % (dirName, validTime)
    return dirName.strip()


def calculateBulletinDir(reportType, timeStamp, origin, fullType):
    """ This method calculates the directory name of a collection, given the above parameters
        reportType  string
                    the 2 letter code for the bulletin type, such as SA or SI or SM.

        timeStamp   string
                    The timestamp from the bulletin header.

        origin      string
                    The orgin of the bulletin

        fullType    string
                    The full Type of the bulletin (SACNXX)
    """
    #-----------------------------------------------------------------------------------------
    # Find the basic collection path (/apps/px/collection/SA/041200/CYOW/SACNXX)
    #-----------------------------------------------------------------------------------------
    dirName = "%s%s/%s/%s/%s" % (PXPaths.COLLECTION_DB, reportType, timeStamp, origin, fullType)
    return dirName



def calculateControlDestPath(collectionDirPath):
    """ calculateControlDestPath(collectionDirPath)

        collectionDirPath:  string  Path such as (/apps/px/collection/SA/041200/CYOW/SACNXX)

        This method calculates and returns the directory name of the lock directory, 
        given the regular path
    """
    #-----------------------------------------------------------------------------------------
    # convert the given path of (/apps/px/collection/SA/041200/CYOW/SACNXX) into 
    # (/apps/px/collection/control/SA/041200/CYOW/SACNXX)
    #-----------------------------------------------------------------------------------------
    collectionDirPath = collectionDirPath.split('/')
    collectionIndex = collectionDirPath.index('collection')
    collectionDirPath.insert(collectionIndex+1,'control')
    dirName = ''
    for element in collectionDirPath:
        dirName = os.path.join(dirName,element)
    return os.path.join('/',dirName)


