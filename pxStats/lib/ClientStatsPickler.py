"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#######################################################################################
##
## Name   : ClientStatsPickler.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006
##
## Goal   : Introduces the data pickling option to the library.
##          This class is to be used to generate pickles for a certain client.
##         
##          Stats will be collected for this client using fileStatsCollector.
##       
##          It needs the file LogFileCollector.py to collect all the file entries. 
##          
##          It needs the FileStatsCollector.py to collect the stats from each file   
##          that LogFileCollector.py finds. 
## 
##          Specified directory needs to contain only valid files.  
##
#######################################################################################
"""


import os , sys, time
sys.path.insert(1, sys.path[0] + '/../../')
"""
    Small function that adds pxlib to the environment path.  
"""
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    Logger requires pxlib 
"""
from   Logger                 import Logger

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.LogFileCollector import LogFileCollector
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.CpickleWrapper import CpickleWrapper
from pxStats.lib.FileStatsCollector import FileStatsCollector
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods


LOCAL_MACHINE = os.uname()[1]   
    

class ClientStatsPickler:
    """
        Contains all the methods needed to pickle stats for a certain client.
        
    """
    
    def __init__( self, client = "", directory = "", statsTypes = None, statsCollection = None, pickleName = "", logger = None, machine = "pdsCSP"  ):
        """ 
            Constructor.
            -Builds a ClientStatsPickler with no entries.           
        """
        
        self.client           = client                 # Name of the client for whom were collecting data 
        self.pickleName       = ""                     # Pickle 
        self.directory        = directory              # Name of the directory containing stats files.
        self.statsTypes       = statsTypes or []       # Types we'll search for stats. 
        self.machine          = machine                # Machine on wich the data resides.
        self.loggerName       = 'pickling'             # Name of the logger.             
        self.logger           = logger                 # Permits a logging system for this object.
        
        if logger is None: # Enable logging
            if not os.path.isdir( StatsPaths.STATSLOGGING ):
                os.makedirs( StatsPaths.STATSLOGGING , mode=0777 )
            self.logger = Logger( StatsPaths.STATSLOGGING + 'stats_' + self.loggerName + '.log.notb', 'INFO', 'TX' + self.loggerName, bytes = True  ) 
            self.logger = self.logger.getLogger()
           
        self.statsCollection  = statsCollection or FileStatsCollector( logger = self.logger )
        self.fileCollection   = LogFileCollector( directory = directory, logger = self.logger )       
        
        
        
    def buildThisHoursFileName(  client = "satnet", offset = 0, currentTime = "", fileType = "tx", machine = "pdsCSP" ):
        """ 
            Builds a filename using current currentTime.
            
            The format will be something like this :
            StatsPaths.STATSPICKLES/clientName/date/hour
            Ex : StatsPaths.STATSPICKLES/clientName/20060707/12:00:00
            
            offset can be used to find a file from an hour close to the current one 
            
            tempcurrentTime can also be used to build a filename from another hour. 
            
            
            To be used with pickles created hourly.
                
        """    
        
        
        fileName = StatsPaths.STATSPICKLES +  client + "/"
        
        
        if currentTime == "":
            currentTime = time.time()
        else:
            currentTime = StatsDateLib.getSecondsSinceEpoch( currentTime )    
        
        currentTime = currentTime + ( offset * StatsDateLib.HOUR )
        splitTime = time.gmtime( currentTime )    
        
        for i in range( 3 ):
            
            if int( splitTime[i] ) < 10 :
                fileName = fileName + "0" + str( splitTime[i] )
            else:
                fileName = fileName + str( splitTime[i] )          
        
                
        hour = StatsDateLib.getHoursFromIso( StatsDateLib.getIsoFromEpoch( currentTime ) )
        
        fileName = fileName + "/" + fileType + "/" + machine + "_" + hour
        
        
        return fileName 
    
    buildThisHoursFileName = staticmethod( buildThisHoursFileName )    
    
    
    
    def collectStats( self, types, directory, fileType = "tx", startTime = '2006-05-18 00:00:00', endTime = "", interval = 60*StatsDateLib.MINUTE, save = True  ):
        """
            This method is used to collect stats for a directory.
            
            Types is the type of dats to be collected. 
            
            Pickle is the name of the file to be used. If not specified will be generated
            according to the other parameters.
            
            FileType specifies what type of files to look for in the directory.
            
            StartTime and endtime specify the boundaries within wich we'll collect the data. 
            
            Interval the width of the entries in the stats collection 
                
            save can be false if for some reason user does not want to save pickle.            
                       
            If both  of the above are true, hourly pickles will be done.
            
            Pre-conditions : StarTime needs to be smaller than endTime.
                             
                             If Daily pickling is used,width between start 
                             and endTime needs to be no more than 24hours
                             
                             If Hourly pickling is used,width between start 
                             and endTime needs to be no more than 1hour.
                               
        
            If pre-conditions aren't met, application will fail.
            
        """     
        
        #Find up to date file list. 
        self.fileCollection =  LogFileCollector( startTime  = startTime , endTime = endTime, directory = directory, lastLineRead = "", logType = fileType, name = self.client, logger = self.logger )   
        
        
        temp  = self.logger#Need to remove current logger temporarily
        del self.logger
        self.fileCollection.collectEntries()          #find all entries from the folder
        self.logger = temp 
        
        
        if self.fileCollection.logger != None : #No longer need the logger 
            self.fileCollection.logger = None  
                
        if os.path.isfile( self.pickleName ):
            
            if self.logger != None :
                self.logger.warning( "User tried to modify allready filled pickle file." )
                self.logger.warning( "Pickle was named : %s" %self.pickleName )      
            
        
        # Creates a new FileStats collector wich spans from the very 
        # start of the hour up till the end. 
        
        if self.pickleName == "":
            self.pickleName = ClientStatsPickler.buildThisHoursFileName( client = self.client, currentTime = startTime, machine = self.machine, fileType = fileType )
    
            
        self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, fileType = fileType, statsTypes = types, startTime = StatsDateLib.getIsoWithRoundedHours( startTime ), endTime = endTime, interval = interval, totalWidth = 1*StatsDateLib.HOUR, logger = self.logger )
        
        #Temporarily delete logger to make sure no duplicated lines appears in log file.
        temp  = self.logger
        del self.logger
        self.statsCollection.collectStats( endTime )    
        self.logger = temp
        
    
    
        if save == True :# must remove logger temporarily. Cannot saved opened files.
            
            if self.statsCollection.logger != None:     
                temp = self.statsCollection.logger
                del self.statsCollection.logger
                loggerNeedsToBeReplaced = True 
            
            CpickleWrapper.save ( object = self.statsCollection, filename = self.pickleName ) 
            
            
            if loggerNeedsToBeReplaced :  
                self.statsCollection.logger = temp
            
            if self.logger != None:
                self.logger.info( "Saved pickle named : %s " %self.pickleName )                          
               
                
    
             
    def printStats( self ) :       
        """
            This utility method prints out all the stats concerning each files. 
            Mostly usefull for debugging.           
                     
        """    
        
        absoluteFilename = str( StatsPaths.STATSDATA ) + "CSP_output_file "
        print "Output filename used : %s" %absoluteFilename
        fileHandle = open( absoluteFilename , 'w' )
        old_stdout = sys.stdout 
        sys.stdout = fileHandle 
        
        print "\n\nFiles used : %s" %self.fileCollection.entries
        print "Starting date: %s" % self.statsCollection.startTime
                                    
        print "Interval: %s" %self.statsCollection.interval
        print "endTime: %s" %self.statsCollection.endTime

        for j in range( self.statsCollection.nbEntries ):
            print "\nEntry's interval : %s - %s " %(self.statsCollection.fileEntries[j].startTime,self.statsCollection.fileEntries[j].endTime)
            print "Values :"
            print self.statsCollection.fileEntries[j].values.dictionary
            print "Means :"
            print self.statsCollection.fileEntries[j].means
            print "Medians"    
            print self.statsCollection.fileEntries[j].medians
            print "Minimums"
            print self.statsCollection.fileEntries[j].minimums
            print "Maximums"
            print self.statsCollection.fileEntries[j].maximums
            print "Total"
            print self.statsCollection.fileEntries[j].totals
    

            
        fileHandle.close()      
        sys.stdout = old_stdout #resets standard output  
        print "Printed %s " %absoluteFilename
    
    
 
def main():
    """
            small test case. Tests if everything works plus gives an idea on proper usage.
    """
    pathToLogFiles =  GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, LOCAL_MACHINE )
   
    types = [ "latency","errors","bytecount" ]    
      
    cs = ClientStatsPickler( client = "satnet", directory = pathToLogFiles )
    
    cs.collectStats( types, directory = pathToLogFiles, fileType = "tx", startTime = '2006-07-16 01:00:12', endTime = "2006-07-16 01:59:12", interval = 1*StatsDateLib.MINUTE )  
            
    cs.printStats()        
    
    print ClientStatsPickler.buildThisHoursFileName()     
       

if __name__ == "__main__":
    main()    