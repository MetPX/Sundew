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
## Goal   : This class' goal is to find all the interesting files within 
##          a certain directory. 
##
##          Usefull in the library to sort out the numerous log files found 
##          on a machine
##
##
#############################################################################


import os,sys,glob #important files 
import backwardReader 

from FileStatsCollector import *

class DirectoryFileCollector: 
    """ 
        This class' goal is to find all the interesting files within a certain directory. 
        
        It offers a data structure wich contains the directory's name and all the interesting
        information to make such a search.   
        
        Data structure that holds all the found files is a list.
        
                 
    """
    
    def __init__( self, startTime = "2006-06-06 01:00:00", endTime = "2006-06-06 02:00:00", directory = "/apps/px/log", lastLineRead = "", lineType = "[INFO]", fileType = "tx", client = "satnet" ):
       """ 
           Constructor.
           -Builds a directoryFileCollector with no entries.   
       
       """
       
       startTime = MyDateLib.getSecondsSinceEpoch( startTime )
       endTime   = MyDateLib.getSecondsSinceEpoch ( endTime ) 
       
       self.directory    = directory    # Name of the directory where we collect entries 
       self.startTime    = startTime    # Starting time of the data wich interests us. 
       self.endTime      = endTime      # Width of time for wich we are interested to collec data. 
       self.lastLineRead = lastLineRead # Last line read during a previous collection of data.  
       self.lineType     = lineType     # Type said last line. Needed to be able to deal with data found on that line.
       self.fileType     = fileType     # Type of file we will be searching for here. tx,rx etc...
       self.client       = client       # Name of the client for wich we are searching files.  
       self.entries = []                # List containing filenames of all interesting files found. 
  
    
    
    def containsUsefullInfo( self, fileName ):
        """
            This method returns whether or not a certain file contain any data wich is within 
            the range we want.
            
        """
        
        i = 0
        departure = ""
        usefull = False    
              
        
        #This method might be dangerous in case of huge file....
        fileHandle = open( fileName , 'r' ) 
        line = fileHandle.readline()
        print "************************"
        print line 
        if line != "":
            
            departure =  FileStatsCollector.findValue( "departure" , line )       
            
            if departure <= self.endTime  :
                
                line == ""
                fileSize = os.stat(fileName)[6]
                line,offset  = backwardReader.readLineBackwards( fileHandle, offset = -1, fileSize = fileSize  )
                print line 
                lastDeparture = FileStatsCollector.findValue( "departure" , line )        
                
                if lastDeparture  >= self.startTime :
                    print "usefull : %s" %fileName
                    usefull = True
        
        if usefull == True :
            print "usefull : %s" %fileName    
            
        print "************************"                            
        return usefull                   



    def collectEntries( self ):
        """ 
            If the directory is valid, this method will add all the valid  
            directory entries to the DirectoryFileCollector's entries field. 
            
            This means all files wich are not directories and whose names don't 
            start with '.'
        
        """      
              
        entries = []
         
        if os.path.isdir( self.directory ):
            
            filePattern = self.directory + "/%s_%s.log*" %( self.fileType, self.client )
            
            fileNames = glob.glob( filePattern )
            
            print fileNames
            
            for fileName in fileNames: #verify every entries.
                usefull = self.containsUsefullInfo( fileName )
                
                if usefull == True :
                    print "usefull : %s" %fileName
                    self.entries.append( fileName )



                    
if __name__ == "__main__":
    """
        Small test case. Tests if everything works plus gives an idea on proper usage.
    
    """
   
    dc = DirectoryFileCollector( startTime = "2006-07-20 01:00:00", endTime= "2006-07-20 02:00:00", directory = "/apps/px/lib/stats/files", lastLineRead = "", lineType = "", fileType = "tx", client = "satnet"  )
    dc.collectEntries()            
    print dc.entries            
