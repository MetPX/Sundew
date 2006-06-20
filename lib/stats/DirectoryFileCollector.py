"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : DirectoryFileCollector.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006
##
## Goal   : This class is used to collect all the file entries from  
##          a specified directory.
## 
##          Usefull in the stats library since interesting log files are to
##          be downloaded in a specific directory and we'll need this class 
##          make the connection between the data collectors and the previously
##          downloaded files.
##
##
##
#############################################################################


import os,sys #important files 



class DirectoryFileCollector: 
    """ 
        This class' goal is to find all the files within a certain directory. 
        It offers a data structure wich contains the directory name and all it's 
        entries. 
        
        Data structure is a dictionary. The key is the entry's name. Value is 
        a list wich has 2 entries.
        [0] contains the offset,wich mean the number of byte where we last read the file.
            Is really usefull for reading expanding files...
        [1] contains the entry count, meaning the last fileEntry of a FileStatsCollector instance 
            we were at while reading the file. 
            Is also really usefull for reading expanding files...
    
    """
    
    def __init__( self, directory = "" ):
       """ 
           Constructor.
           -Builds a directoryFileCollector with no entries.   
       
       """
       
       self.directory = directory  # Name of the directory where we collect entries 
       self.entries = {}           # Dictionary containings filenames,and up to what line we've read it 
       
    
    
    def collectEntries(self):
        """ 
            If the directory is valid, this method will add all the valid  
            directorie entries to the DirectoryFileCollector's entries field. 
            
            This means all files wich are not directories and whose names don't 
            start with '.'
        
        """
        
        entries = []
        validEntries = []
        
        try:
            
            if os.path.isdir( self.directory ):
                entries = os.listdir( self.directory )#gets every entries of the folder except . and .. 
                
                for i in range( len(entries ) ): #verify every entries.
                    fileName = ( str( self.directory ) + str( entries[i] ) )
                    
                    if not os.path.isdir( fileName ) and str( entries[i] ).startswith( '.' ) == False:
                        validEntries.append( fileName )
                
                
                self.entries = dict( [(x, [0,0]) for x in validEntries] ) # set offset and entryCount at 0.
                            
        except:
            
            (type, value, tb) = sys.exc_info()
            
            print("Type: %s, Value: %s" % (type, value))
            print "Error. %s is not a valid directory" %self.directory
            print "Program terminated"
            sys.exit() 



if __name__ == "__main__":
    """
        Small test case. Tests if everything works plus gives an idea on proper usage.
    
    """
   
    dc = DirectoryFileCollector( "/users/dor/aspy/lem/Desktop" )
    dc.collectEntries()            
    print dc.entries            
