"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : directoryFileCollector.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006
##
## Goal   : This method is used to collect all the file entries from  
##          a specified directory.
##
##
#############################################################################


import os,sys #important files 



class DirectoryFileCollector: 
    """ This class' goal is to find all the files within a certain directory. 
        It offers a date structure wich contains the directory name and all it's 
        entries. 
    """
    
    def __init__( self, directory = "" ):
       """ Constructor.
           builds a directoryFileCollector with no entries.   
       """
       self.directory = directory 
       self.entries = []
       
    
    def collectEntries(self):
        """ If the directory is valid, this method will add all the valid  
            directorie entries to the DirectoryFileCollector's entries field. 
        """
        
        entries = []
        
        try:
            if os.path.isdir( self.directory ):
                entries = os.listdir( self.directory )
                for i in range( len(entries ) ): # for everyfiles
                    fileName = ( str( self.directory ) + str( entries[i] ) )
                    if not os.path.isdir( fileName ) and str( entries[i] ).startswith( '.' ) == False:
                        self.entries.append( fileName )
                
            
        except:
            print "Error. %s is not a valid directory" %self.directory
            print "Program terminated"
            sys.exit() 
                
                
if __name__ == "__main__":
    """small test case. Tests if everything works plus gives an idea on proper usage.
    """
   
    dc = DirectoryFileCollector( "/users/dor/aspy/" )
    dc.collectEntries()            
    print dc.entries            