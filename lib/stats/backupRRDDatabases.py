#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : backupRRDDatabases.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-10-25
#
# Description: This program is to be used to backup rrd databases and their corresponding
#              time of update files. Backing up rrd databases at various point in time is a
#              recommended paractice in case newly entered data is not valid. 
#
#              RRD does not offer any simple database modifying utilisties so the best way
#              to fix a problem is to used a backed up database and to restart the update 
#              with the newly corrected data. 
#              
#
#   Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  backupRRDDatabases.py -h | --help
#
#
##############################################################################################
"""

import os, commands, time, sys, pickle, glob
import MyDateLib,PXPaths 
from   MyDateLib import * 

PXPaths.normalPaths()


def backupDatabases( timeOfBackup ):
    """
       Copy all databases into a folder sporting the data of the backup.
       
       Limits the number of backups to 5
    """
    
    
    source = PXPaths.STATS + "databases"
    destination = PXPaths.STATS + "databases" + ".%s" %timeOfBackup
    status, output = commands.getstatusoutput( "cp -r %s %s" %( source, destination ) )
    
    
    #limit number of backup
    filePattern = PXPaths.STATS + "databases*"           
    fileNames = glob.glob( filePattern )  
    fileNames.sort()       
    newList = [fileNames[0]]
    fileNames.reverse()
    newList = newList + fileNames[:-1]
    
    if len( newList) > 5 :
        for i in range( 5, len(newList) ):
            status, output = commands.getstatusoutput( "rm -r %s " %( newList[i] ) ) 
    
    
    
def backupDatabaseUpdateTimes( timeOfBackup ):
    """
        Copy all databases into a folder sporting the data of the backup.
        
        Limits the number of database backups to 3.
    """
    
    source = PXPaths.STATS + "DATABASE-UPDATES"
    destination = PXPaths.STATS + "DATABASE-UPDATES" + ".%s" %timeOfBackup
    status, output = commands.getstatusoutput( "cp -r %s %s" %( source, destination ) )
    
    #limit number of backups         
    filePattern = PXPaths.STATS + "DATABASE-UPDATES*"          
    fileNames = glob.glob( filePattern )  
    fileNames.sort()       
    newList = [fileNames[0]]
    fileNames.reverse()
    newList = newList + fileNames[:-1]
    
    if len( newList) > 5 :
        for i in range( 5, len(newList) ):
            status, output = commands.getstatusoutput( "rm -r %s " %( newList[i] ) )
    
def main():
    """
        This program is to be used to backup rrd databases and their corresponding
        time of update files. Backing up rrd databases at various point in time is a
        recommended paractice in case newly entered data is not valid. 
        
    """
    currentTime = time.time()        
    currentTime = MyDateLib.getIsoFromEpoch( currentTime )
    currentTime = MyDateLib.getIsoWithRoundedSeconds( currentTime )
    currentTime = currentTime.replace(" ", "_")
    backupDatabaseUpdateTimes( currentTime )
    backupDatabases( currentTime )
    
if __name__ == "__main__":
    main()                