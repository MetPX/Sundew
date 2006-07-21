"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : pickledTimesViewer.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-06-19
#
# Description: 
#
#   Usage:   This program can be called from command-line. 
#
#   For informations about command-line:  PickleTimesViewer.py -h | --help
#
#
##############################################################################################
"""

import os,pickle 

def printPickledTimes( pickledTimes, fileName ):
    """
    
    """
    
    print pickledTimes 
    keys       = pickledTimes.keys()
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
    
    """
    
    if os.path.isfile( fileName ):
        
        fileHandle   = open( fileName, "r" )
        pickledTimes = pickle.load( fileHandle )
        fileHandle.close()       
  
    else:
    
        print "Error. Pickled times file named : %s does not exist." %fileName
        print "Program terminated."
        sys.exit()    

    
    return pickledTimes  
    
    
    
        
def main():
    """
    
    """
    fileName = "/apps/px/lib/stats/PICKLED-TIMES"
    pickledTimes = loadPickledTimes( fileName )
    printPickledTimes( pickledTimes, fileName  )




if __name__ == "__main__":
    main()