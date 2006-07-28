"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##########################################################################
##  Original author is Bill McNeill <billmcn@speakeasy.net>
##
##  His code was taken from the following source :
##  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/189972
##
##
##  Modified by Nicholas Lemay to make it faster by using cPickle instead of 
##  the usual Pickle. 
##
##  Save modified by Nicholas Lemay so that it creates missing directories 
##  if needed. 
##
##  Original header by Bill Mcneill was :
##
##  Generic object pickler and compressor
##
##  This module saves and reloads compressed representations of generic Python
##  objects to and from the disk.
##
##
##############################################################################


#Original author's name as was written in original file... 
__author__ = "Bill McNeill <billmcn@speakeasy.net>"
__version__ = "1.0"


import pickle
import gzip
import cPickle
import os 
import sys

def save( object, filename ):
    """
        Saves a compressed object to disk.
        
        Filename needs to be an absolute filename ie
        /apps/px/lib/PICKLES/SATNET/SATNET-PICKLE-2006-06-08
    
        User must have permission to write to the specified folder. 
        
    """
    
    if filename[0] == "/" : 
        
        splitName = filename.split( "/" ) 
        directory = "/"
        
        for i in range( 1, len(splitName)-1 ):
            directory = directory + splitName[i] + "/"
        
        if not os.path.isdir( directory ):
            os.makedirs( directory, mode=0777 )    
            
        file = gzip.GzipFile( filename, 'wb' )
        file.write( cPickle.dumps( object, True ) )
        file.close()
    
    else:
    
        print "Error occured in gzippickle.save()."
        print "Filename used : %s, needs to be an absolute path to the file." %filename
        
        sys.exit()  
    
        

def load( filename ):
    """
        Loads a compressed object from disk.
        
        If file does not exist application will be terminated. 
    
        Pre-condition file used must be a file that was saved using the 
        gzippickle.save() method.
        
    """
    
    if os.path.isfile( filename ): 
        
        file = gzip.GzipFile( filename, 'rb' )
        
        buffer = ""
        
        while 1:
            
            data = file.read()
            if data == "":
                break
            buffer += data
            
        object = cPickle.loads( buffer )
        
        file.close()
    
    else:
        print "Error occured in gzippickle.load()."
        print "Filename used : %s, does not exist." %filename
        
        sys.exit()  
    
    return object

    
    
if __name__ == "__main__":
    
    """
        Small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    #standard test case 
    x = "Hello world!"
    save( x, "/apps/px/lib/stats/x" )
    x = load ("/apps/px/lib/stats/x") 
    print x
    
    #trouble cases 
    save (x,"y") 
    y = load("/apps/px/lib/stats/nonexistingfile")
    
    