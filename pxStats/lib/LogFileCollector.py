"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##########################################################################
##
## Name   : LogFileCollector.py ( formely DirectoryFileCollector.py ) 
##  
## Author : Nicholas Lemay  
##
## Date   : December 12th 2006
##
## Goal   : This class' goal is to find all the interesting log files within 
##          a certain directory. 
##
##          Usefull in the library to sort out the numerous log files found 
##          on a machine.
##
##
#############################################################################
"""
import os, sys
"""
    Small function that adds pxlib to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    Logger requires pxlib 
"""
import glob #important files 
from   Logger                     import * 

from   pxStats.lib.BackwardReader             import BackwardReader 
from   pxStats.lib.FileStatsCollector         import FileStatsCollector
from   pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from   pxStats.lib.StatsPaths                 import StatsPaths


LOCAL_MACHINE = os.uname()[1]   

class LogFileCollector: 
    """ 
        This class' goal is to find all the interesting files within a certain directory. 
        
        It offers a data structure wich contains the directory's name and all the interesting
        information to make such a search.   
        
        Data structure that holds all the found files is a list.
        
                 
    """
    
    def __init__( self, startTime = "2006-06-06 01:00:00", endTime = "2006-06-06 02:00:00", directory = None, lastLineRead = "", logType = "tx", name = "satnet", logger = None ):
        """ 
            Constructor.
            -Builds a directoryFileCollector with no entries.   
        
        """

        self.directory    = directory       # Name of the directory where we collect entries 
        self.startTime    = startTime       # Starting time of the data wich interests us. 
        self.endTime      = endTime         # Width of time for wich we are interested to collec data. 
        self.lastLineRead = lastLineRead    # Last line read during a previous collection of data.  
        self.logType      = logType         # Type of file we will be searching for here. tx,rx etc...
        self.name         = name            # Name for wich we are searching files.  
        self.entries      = []              # List containing filenames of all interesting files found. 
        self.logger       = logger          # Used to log warning error infos etc.
        self.loggerName   = 'fileCollector' # Name used for the logger if none was specified.
       
        
        if logger is None: # Enable logging
            if not os.path.isdir( StatsPaths.STATSLOGGING  ):
                os.makedirs( StatsPaths.STATSLOGGING , mode=0777 )
            self.logger = Logger( StatsPaths.STATSLOGGING + 'stats_' + self.loggerName + '.log.notb', 'INFO', 'TX' + self.loggerName, bytes = True  ) 
            self.logger = self.logger.getLogger()
            
            
    
    def containsUsefullInfo( self, fileName ):
        """
            This method returns whether or not a certain file contain any data wich is within 
            the range we want.
            
            Pre-condition : self.startTime must be <= self.endTime            
                       
        """
        
        i = 0
        departure = ""
        usefull = False   
                     
                
        fileHandle = open( fileName , 'r' ) 
        line = fileHandle.readline()
        
        if line != "":
            
            departure =  FileStatsCollector.findValues( ["departure"], line )["departure"]       
            
                                             
            if departure <= self.endTime  :
                
                line == ""
                fileSize = os.stat( fileName )[6]
                
                line,offset  = BackwardReader.readLineBackwards( fileHandle, offset = -1, fileSize = fileSize  )
                
                isInteresting, lineType = FileStatsCollector.isInterestingLine( line, usage = "departure" ) 
                
                while isInteresting == False and line != "" : #in case of traceback found in file
                    line, offset  = BackwardReader.readLineBackwards( fileHandle, offset = offset, fileSize = fileSize )
                    isInteresting, lineType = FileStatsCollector.isInterestingLine( line, usage = "departure" ) 
                
                lastDeparture = FileStatsCollector.findValues( ["departure"] , line )["departure"]
               
                                                                                            
                if lastDeparture  >= self.startTime :
                    usefull = True
                    
                    
        fileHandle.close()
                         
        return usefull                   



    def collectEntries( self ):
        """ 
            If the directory is valid, this method will add all the valid  
            directory entries to the LogFileCollector's entries field. 
            
            Pre-condition : Files in the specified directory must all be of the valid 
                            log file format. 
        
        """      
              
        entries = []
        
           
        if os.path.isdir( self.directory ):            
            
            filePattern = self.directory + "%s_%s.log*" %( self.logType, self.name )                  
            fileNames = glob.glob( filePattern )                        
                                  
            for fileName in fileNames: #verify every entries.
                usefull = self.containsUsefullInfo( fileName )
                
                if usefull == True :
                    self.entries.append( fileName )
                
        else:
            
            if self.logger != None :
                self.logger.warning( "Warning in LogFileCollector. Folder named %s does not exist."%self.directory )

                          
                    
if __name__ == "__main__":
    """
        Small test case. Tests if everything works plus gives an idea on proper usage.
    
    """
    
    pathToLogFiles = GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, LOCAL_MACHINE )

    lfc = LogFileCollector( startTime = "2006-07-20 01:00:00", endTime= "2006-07-20 02:00:00", directory = pathToLogFiles, lastLineRead = "", logType = "tx", name = "satnet"  )
    lfc.collectEntries() 
    
    print "Files returned : %s " %lfc.entries            
