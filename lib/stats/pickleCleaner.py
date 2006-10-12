#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : pickleCleaner.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-10-12
#
# Description: 
#
#   Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  pickleCleaner -h | --help
#
#
##############################################################################################
"""

import os, commands, time
import MyDateLib 
from   MyDateLib import * 

DAYS_TO_KEEP = 10 #Global constant



def getDirListToKeep():
    """
          Gets the list of directories to keep. Based on DAYS_TO_KEEP constant.
    """
    
    dirlist = []
    secondsSinceEpoch = time.time()
    
    for i in range( DAYS_TO_KEEP ):
        dirlist.append( MyDateLib.getIsoFromEpoch( secondsSinceEpoch - ( i*60*60*24) ).split()[0].replace( '-','') )
         
    return dirlist
    

    
def cleanPickles( dirsToKeep ):
    """
        Deletes every pickle directory that is not within the list to keep.
    """
    
    clientdirs = os.listdir( "/apps/px/stats/pickles/" )
    
    
    for clientDir in clientdirs :
        upperDir = "/apps/px/stats/pickles/" + clientDir 
        innerList = os.listdir( upperDir )
        for innerFolder in innerList:
            completePath = upperDir + "/" + innerFolder
            
            if innerFolder not in dirsToKeep:
                status, output = commands.getstatusoutput("rm -rf %s " %completePath )
                #print "deleted : %s " %completePath
                
    
    
def main():
    """
        Gets the list of directories to keep. Based on DAYS_TO_KEEP constant.
        Deletes every pickle directory that is not within the list to keep.
        
    """

    dirsToKeep = getDirListToKeep()
    cleanPickles( dirsToKeep )

    
if __name__ == "__main__":
    main()                
                
                
                
                
                
                
                