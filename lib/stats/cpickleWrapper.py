#! /usr/bin/env python
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
        
        Will create folder up to destination if folders don't exist. 
   
        User must have permission to write to the specified folder. 
        
        Raises exception if application is unable to save file.
        
        Warning : Objects containing opened files, such as log files,
                  cannot be saved. Remember to close file or delete
                  file property from object prior to saving. 
    """
        
    splitName = filename.split( "/" ) 
    
    if filename[0] == "/":
        directory = "/"
    else:
        directory = ""
        
        
    for i in range( 1, len(splitName)-1 ):
        directory = directory + splitName[i] + "/"
    
    if not os.path.isdir( directory ):
        os.makedirs( directory, mode=0777 )    
        
    file = open( filename, 'wb' )
    file.write( cPickle.dumps( object, True ) )
    file.close()



def load( filename ):
    """
        
        Loads ands returns an object saved with cpickle.
        
        Pre-condition : file must exist. File must have been created 
                        using cpickle. 
                        
    """
    
    object = None  
    
    if os.path.isfile( filename ): 
        
        try :
            file = open( filename, 'rb' )
            
            object = cPickle.load( file )
            
            file.close()
            
        except:
            print  "Error occured in cpickleWrapper.load()"
            
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
    
    