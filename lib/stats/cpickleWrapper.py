"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##########################################################################
##  
## Name   : cpickleWrapper.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 06-07-2006 
##
##
## Description : Small wrapper to cpickle. cPickle is much faster than standard
##               pickle so it is very usefull in this library. 
##
##               This wrapper allows for folder creation when save is called. 
##         
##               It also has exception handling in case of non existing file in 
##               load call.
##                 
##############################################################################


import cPickle
import os 
import sys
import PXPaths

PXPaths.normalPaths()



def save( object, filename ):
    """
        Saves an object to disk using cpickle.
        
        Filename needs to be an absolute filename ie
        /apps/px/lib/PICKLES/SATNET/SATNET-PICKLE-2006-06-08
    
        User must have permission to write to the specified folder. 
        
        Raises exception if 
    """
    
    if filename[0] == "/" : 
        
        splitName = filename.split( "/" ) 
        directory = "/"
        
        for i in range( 1, len(splitName)-1 ):
            directory = directory + splitName[i] + "/"
        
        if not os.path.isdir( directory ):
            os.makedirs( directory, mode=0777 )    
            
        file = open( filename, 'wb' )
        file.write( cPickle.dumps( object, True ) )
        file.close()
    
    else:
    
        raise Exception( "Error occured in cpickleWrapper.save().Filename used : %s, needs to be an absolute path to the file." %filename )
        
    
    
        

def load( filename ):
    """
        
        Loads ands returns an object saved with cpickle.
        
        Pre-condition : file must exist. File must have been created 
                        using cpickle. 
    """
    
    if os.path.isfile( filename ): 
        
        file = open( filename, 'rb' )
           
        object = cPickle.load( file )
        
        file.close()
    
    else:
        
        raise Exception ( "Error occured in cpickleWrapper.load().Filename used : %s, does not exist." %filename)
        
          
    return object

    
    
if __name__ == "__main__":
    
    """
        Small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    #standard test case 
    x = "Hello world!"
    save( x, PXPaths.STATS +"x" )
    x = load ( PXPaths.STATS +"x" ) 
    print x
    
    #trouble cases 
    save (x,"y")#non absolute file name not yet implemented.... 
    y = load( PXPaths.STATS + "nonexistingfile" )
    
    