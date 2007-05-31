#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : picklesTimeOfUpdatesViewer.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-06-19
#
# Description: This method allows user to quicly see all the update times stored in the 
#              time of updates file.
#
#   Usage:   This program can be called from command-line. 
#
#   For informations about command-line:  picklesTimeOfUpdatesViewer.py -h | --help
#
#
##############################################################################################
"""

import os, sys, pickle 
sys.path.insert(1, sys.path[0] + '/../../../')

from pxStats.lib.StatsPaths import StatsPaths


def printPickledTimes( pickledTimes, fileName ):
    """
        This method prints the content of the pickled-times file. 
        
        pre condition : pickledTimes must be a dictionary instance. 
    
    """
    
    keys = pickledTimes.keys()
    keys.sort()
    
    
    os.system( 'clear' )
    print "############################################################"
    print "# Times found in %-42s#" %fileName
    print ("#                                                          #")
    
    for key in keys:
        
        print("#%-27s : %-28s#") %(key,pickledTimes[key] )
    
    print ("#                                                          #")    
    print "############################################################"
    


def loadPickledTimes( fileName ):
    """
        This method loads a standard non-gzip pickle file.
        
        Returns object found in pickle. 
        
        Filename must exist or else application is terminated. 
        
    """
    
    if os.path.isfile( fileName ):
        
        fileHandle   = open( fileName, "r" )
        pickledTimes = pickle.load( fileHandle )
        fileHandle.close()       
  
    else:
    
        print "Error. Pickled file named : %s does not exist." %fileName
        print "Modify content of this program to use another file."
        print "Program terminated."
        sys.exit()    

    
    return pickledTimes  
    
    
    
        
def main():
    """
        Main method.
    """
    
    #standard use.
    os.system( 'clear' )
    fileName = StatsPaths.STATSPICKLESTIMEOFUPDATES
    pickledTimes = loadPickledTimes( fileName )
    printPickledTimes( pickledTimes, fileName  )

#     #tests unexisting file 
#     fileName = "nonexistingfile"
#     pickledTimes = loadPickledTimes( fileName )
#     printPickledTimes( pickledTimes, fileName ) 

if __name__ == "__main__":
    main()