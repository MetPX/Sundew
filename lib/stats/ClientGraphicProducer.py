"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##############################################################################
##
##
## Name   : ClientGraphicProducer.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 06-07-2006 
##
##
## Description : Contains all the usefull classes and methods to produce a graphic 
##               for a certain client. Main use is to build latency graphics
##               for one or many clients. Can also produce graphics on
##               bytecounts and errors found in log files. 
##
##
##############################################################################


#important files 
import os, time, sys
import cpickleWrapper
import MyDateLib
import pickleUpdater
import pickleMerging
import logging 
import StatsPaths
import generalStatsLibraryMethods

from Logger import *
from MyDateLib import MyDateLib
from StatsPlotter import StatsPlotter
from ClientStatsPickler import *
from FileStatsCollector import FileStatsCollector, _FileStatsEntry
from generalStatsLibraryMethods import *


LOCAL_MACHINE = os.uname()[1]


class ClientGraphicProducer:
        
    def __init__( self, directory, fileType, clientNames = None , groupName = "",  timespan = 12, currentTime = None, productTypes = ["All"], logger = None, machines = ["pds000"]  ):
        """
            ClientGraphicProducer constructor. 
            
            CurrentTime format is ISO meaning "2006-06-8 00:00:00". Will use current
            system time by default.   
            
            CurrentTime is to be used if a different time than sytem time is to be used. 
            
            Very usefull for testing or to implement graphic request where user can choose start 
            time.  
    
        
        """
        
        if currentTime != None :
            currentTime = currentTime 
        else:
            currentTime = time.time()
            
        self.directory    = directory          # Directory where log files are located. 
        self.fileType     = fileType           # Type of log files to be used.    
        self.machines     = machines           # Machines for wich to collect data. 
        self.clientNames  = clientNames or []  # Client name we need to get the data from.
        self.groupName    = groupName          # Name for a group of clients to be combined.
        self.timespan     = timespan           # Number of hours we want to gather the data from. 
        self.currentTime  = currentTime        # Time when stats were queried.
        self.productTypes  = productTypes      # Specific data types on wich we'll collect the data.
        self.loggerName   = 'graphs'           # Name of the logger
        self.logger       = logger             # Enable logging
        
        if self.logger is None: # Enable logging
            if not os.path.isdir( StatsPaths.PXLOG ):
                os.makedirs( StatsPaths.PXLOG , mode=0777 )
            self.logger = Logger( StatsPaths.PXLOG  + 'stats_' + self.loggerName + '.log.notb', 'INFO', 'TX' + self.loggerName, bytes = True  ) 
            self.logger = self.logger.getLogger()
                
            
    def getStartTimeAndEndTime( self, collectUptoNow = False ):
        """
            Warning : collectUptoNow not yet supported in program !
            
            Returns the startTime and endTime of the graphics.
        """
        
        
        #Now not yet implemented.
        if collectUptoNow == True :
            endTime = self.currentTime
            
        else :
            endTime = MyDateLib.getIsoWithRoundedHours( self.currentTime )
            
        startTime = MyDateLib.getIsoFromEpoch( MyDateLib.getSecondsSinceEpoch( endTime ) - (self.timespan * MyDateLib.HOUR) )  
         
        return startTime, endTime
    
    
    def collectDataForIndividualGraphics( self, startTime, endTime, types ):
        #find parameters
        
        """
            Returns a list of ClientStatsPicklers
            instances, each of wich contains data
            for all the individual graphics.
            
        """
        
        
        
        dataCollection = [] 
        
         
        for client in self.clientNames : # 
               
            #Gather data from all previously created pickles....      
            if self.logger != None :                 
                self.logger.debug( "Call to mergeHourlyPickles." )
                self.logger.debug( "Parameters used : %s %s %s" %( startTime, endTime, client ) )
            
            if len( self.machines ) > 1 :   
                clientArray = []
                clientArray.append(client) 
                statsCollection = pickleMerging.mergePicklesFromDifferentSources( logger = self.logger , startTime = startTime, endTime = endTime, clients = clientArray, fileType = self.fileType, machines = self.machines, groupName = self.groupName  )
                                    
            else:#only one machine, only merge different hours together
               
                statsCollection = pickleMerging.mergePicklesFromDifferentHours( logger = self.logger , startTime = startTime, endTime = endTime, client = client, fileType = self.fileType, machine = self.machines[0] )
                
            
            combinedMachineName = ""
            for machine in self.machines:
                combinedMachineName = combinedMachineName + machine
                
            dataCollection.append( ClientStatsPickler( client = self.clientNames, statsTypes = types, directory = self.directory, statsCollection = statsCollection, machine = combinedMachineName ) )
                            
        
        return dataCollection
         
               
            
    def collectDataForCombinedGraphics( self, startTime, endTime, types ):
        """
        
            Returns a list of one ClientStatsPicklers
            instance wich contains the combined data
            of all the individual graphics.
            
        """ 
        
        
        dataCollection = []        
       
        statsCollection = pickleMerging.mergePicklesFromDifferentSources( logger = None , startTime = startTime, endTime = endTime, clients = self.clientNames, fileType = self.fileType, machines =  self.machines, groupName = self.groupName )
        
        combinedMachineName = ""
        for machine in self.machines:
            combinedMachineName = combinedMachineName + machine
                
        #Verifier params utiliser par cette ligne
        dataCollection.append( ClientStatsPickler( client = self.clientNames, statsTypes = types, directory = self.directory, statsCollection = statsCollection, machine = combinedMachineName ) )
        
        return dataCollection
               
        
            
    def recalculateData( self, dataCollection ):
        """
            Recalculates the mean max min and median 
            of all the entries of the dataCollection.
            
            Usefull when using a specific productType 
        """
        
        
        
        for item in dataCollection: 
                item.statsCollection.setMinMaxMeanMedians(  productTypes = self.productTypes, startingBucket = 0 , finishingBucket = len(item.statsCollection.fileEntries) -1 )
                
        return  dataCollection 
        
        
        
    def produceGraphicWithHourlyPickles( self, types , now = False, createCopy = False, combineClients = False  ):
        """
            This higher-level method is used to produce a graphic based on the data found in log files
            concerning a certain client. Data will be searched according to the clientName and timespan
            attributes of a ClientGraphicProducer.  
            
            This method will gather the data starting from current time - timespan up to the time of the call.   
        
            Now option not yet implemented.
            
            Every pickle necessary for graphic production needs to be there. 
            Filling holes with empty data not yet implemented.              
            
        """         
        
        dataCollection = [] #                  
        startTime, endTime = self.getStartTimeAndEndTime()
        
        if combineClients == True :
            dataCollection = self.collectDataForCombinedGraphics(  startTime, endTime, types )              
        else: 
            dataCollection = self.collectDataForIndividualGraphics( startTime, endTime, types )       
                         
                   
        if self.productTypes[0] != "All":
            dataCollection = self.recalculateData( dataCollection )               
        
        if self.logger != None :         
            self.logger.debug( "Call to StatsPlotter :Clients:%s, timespan:%s, currentTime:%s, statsTypes:%s, productTypes:%s :" %( self.clientNames, self.timespan, self.currentTime, types, self.productTypes ) )
        
        #print "Call to StatsPlotter :Clients:%s, timespan:%s, currentTime:%s, statsTypes:%s, productTypes:%s :" %( self.clientNames, self.timespan, self.currentTime, types, self.productTypes )
        
        plotter = StatsPlotter( stats = dataCollection, clientNames = self.clientNames, groupName = self.groupName, timespan = self.timespan, currentTime = endTime, now = False, statsTypes = types, productTypes = self.productTypes, logger = self.logger, machines = self.machines, fileType = self.fileType  )
        
        plotter.plot( createCopy )
                                  
        print "Plotted graph."
        
        if self.logger != None :
            self.logger.debug( "Returns from StatsPlotter." )
            
            self.logger.info ("Created Graphics for following call : Clients : %s, timespan : %s, currentTime : %s, statsTypes : %s, productTypes : %s :" %( self.clientNames, self.timespan, self.currentTime, types, self.productTypes ) )         
            
        

if __name__ == "__main__":
    """
        small test case to see proper use and see if everything works fine. 
        
    """
    
    pathToLogFiles = generalStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, LOCAL_MACHINE )
    
    gp = ClientGraphicProducer( clientNames = [ 'amis' ], timespan = 24, currentTime = "2006-08-01 18:15:00",productTypes = ["All"], directory = pathToLogFiles, fileType = "tx" )  
    
    gp.produceGraphicWithHourlyPickles( types = [ "bytecount","latency","errors" ], now = False   )
    



    
