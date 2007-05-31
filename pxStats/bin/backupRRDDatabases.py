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
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib


def backupDatabases( timeOfBackup, backupsToKeep ):
    """
       @summary: Copy all databases into a folder sporting the data of the backup.
       
       @param timeOfBackup : Used to tag the database backup folder. 
       
       @param backupsToKepp : Limits the number of backups to the specified value.
    
    """
    
    
    source = StatsPaths.STATSCURRENTDB
    #destination = StatsPaths.STATSDBBACKUPS + "%s" %timeOfBackup
    
    if not os.path.isdir( destination ):
        os.makedirs( destination )
    status, output = commands.getstatusoutput( "cp -r %s/* %s" %( source, destination ) )
    print output    
    
    #limit number of backup
    filePattern = StatsPaths.STATSDBBACKUPS + "*"           
    fileNames = glob.glob( filePattern )  
    fileNames.sort()       
    
    if len( fileNames ) > 0:
        newList = [fileNames[0]]
        fileNames.reverse()
        newList = newList + fileNames[:-1]
    
        if len( newList) > backupsToKeep :
            for i in range( backupsToKeep, len(newList) ):
                status, output = commands.getstatusoutput( "rm -r %s " %( newList[i] ) ) 
    
    
    
def backupDatabaseUpdateTimes( timeOfBackup, backupsToKeep ):
    """
    
       @summary: Copy all databases update times into a folder sporting
                 the data of the backup.
       
       @param timeOfBackup : Used to tag the database backup folder. 
       
       @param backupsToKeep : Limits the number of backups to the 
                              specified value.
    
    """
    
    source = StatsPaths.STATSCURRENTDBUPDATES
    destination = StatsPaths.STATSDBUPDATESBACKUPS + "%s" %timeOfBackup
    
    if not os.path.isdir( destination ):
        os.makedirs( destination )
    status, output = commands.getstatusoutput( "cp -r %s/* %s" %( source, destination ) )
    print output 

    #limit number of backups         
    filePattern = StatsPaths.STATSDBUPDATESBACKUPS + "*"          
    fileNames = glob.glob( filePattern )  
    fileNames.sort()       
    
    if len( fileNames ) > 0 :
    
        newList = [fileNames[0]]
        fileNames.reverse()
        newList = newList + fileNames[:-1]
    
        if len( newList) > backupsToKeep :
            for i in range( backupsToKeep, len(newList) ):
                status, output = commands.getstatusoutput( "rm -r %s " %( newList[i] ) )
    

    
def main():
    """
        This program is to be used to backup rrd databases and their corresponding
        time of update files. Backing up rrd databases at various point in time is a
        recommended paractice in case newly entered data is not valid. 
        
    """
    
    currentTime = time.time()        
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    currentTime = StatsDateLib.getIsoWithRoundedSeconds( currentTime )
    currentTime = currentTime.replace(" ", "_")
    
    backupsToKeep = 20
    
    if len( sys.argv ) == 2:
        try:
            backupsToKeep =  int( sys.argv[1] )
        except:
            print "Days to keep value must be an integer. For default 20 backups value, type nothing."
            sys.exit()
                      
    backupDatabaseUpdateTimes( currentTime, backupsToKeep )
    backupDatabases( currentTime, backupsToKeep )
    
    
if __name__ == "__main__":
    main()                
