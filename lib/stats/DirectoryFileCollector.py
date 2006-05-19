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


import os,sys 



class DirectoryFileCollector: 
    """ This class use is to find all the files within a certain directory. 
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
        """ If the directory is valid, this method will add all 
            the directories entries to the DirectoryFileCollector's entries field. 
        """
        
        try:
            if os.path.isdir( self.directory ) :
                self.entries = os.listdir( self.directory )
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