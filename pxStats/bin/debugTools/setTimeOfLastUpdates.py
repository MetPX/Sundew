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
# Description: This program is to be used in case of a problem with pickle/updater to set back 
#              the time of the the last updates prior to the errors. That way at the next 
#              update the pickling will be redone and might produce the right pickles if 
#              the problem was corrected. 
#
#   Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  pickleCleaner -h | --help
#
#
##############################################################################################
"""

import os, commands, time, sys, pickle
sys.path.insert(1, sys.path[0] + '/../../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib



def updatePickledTimes( dateToSet = "2006-10-23 09:00:00"  ):
    """
          Get all the keys then set all of them to the desired date.
    """
    
    fileName = StatsPaths.STATSROOT +"PICKLED-TIMES"

    if os.path.isfile( fileName ):

        fileHandle   = open( fileName, "r" )
        pickledTimes = pickle.load( fileHandle )
        fileHandle.close()
        
        
        keys = pickledTimes.keys()
        for key in keys:
            pickledTimes[key] = dateToSet
            
        fileHandle  = open( fileName, "w" )

        pickle.dump( pickledTimes, fileHandle )

        fileHandle.close()



    
def removePickledFilePositions(  ):
    """
        Deletes pickle file containing the position where we last read 
        a certain file for each source/client.
    """
    
    if os.path.isfile( StatsPaths.STATSROOT +  "PICKLED_FILE_POSITIONS" ) :
        status, output = commands.getstatusoutput("rm %s " %( StatsPaths.STATSROOT +  "PICKLED_FILE_POSITIONS" ) )
                
    
    
def main():
    """
        Deletes pickle file containing the position where we last read 
        a certain file for each source/client.
        
        Set date of last update in StatsPaths.STATSROOT +"PICKLED-TIMES"
        
    """
    
    dateToSet = "2006-10-23 09:00:00"
    
    if len( sys.argv ) == 2:
        
        try:
            
            dateToSet =  sys.argv[1]
            t =  time.strptime( dateToSet, '%Y-%m-%d %H:%M:%S' )#will raise exception if format is wrong.
            split = dateToSet.split()
            dateToSet = "%s %s" %( split[0], split[1] )
            removePickledFilePositions()
            updatePickledTimes( dateToSet )
        
        except:
            print 'Date must be of the following format "YYYY-MM-DD HH:MM:SS"'
            print "Program terminated."     
            sys.exit()
                
    
    else:
        print "You must specify date to set."
        print "Date must be of the folowing format YYYY-MM-DD HH:MM:SS"
        print "Program terminated."        
            


    
if __name__ == "__main__":
    main()                
                
                
                
                
                
                
                