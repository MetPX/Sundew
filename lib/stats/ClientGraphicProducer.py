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
## Description : Contains all usefullclasses and methods to produce a graphic 
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
import PXPaths
from   Logger                 import *


from MyDateLib import MyDateLib
from StatsPlotter import StatsPlotter
from ClientStatsPickler import *
from FileStatsCollector import FileStatsCollector, _FileStatsEntry

PXPaths.normalPaths()



class ClientGraphicProducer:
    
    
    
    def __init__( self, directory, fileType, clientNames = None ,  timespan = 12, currentTime = None, productType = "All", logger = None, machines = ["pds5"]  ):
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
            
        self.directory    = directory         # Directory where log files are located. 
        self.fileType     = fileType          # Type of log files to be used.    
        self.machines     = machines          #Machiens for wich to collect data. 
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        self.timespan     = timespan          # Number of hours we want to gather the data from. 
        self.currentTime  = currentTime       # Time when stats were queried.
        self.productType  = productType       # Specific data type on wich we'll collect the data.
        self.loggerName   = 'graphs'          #
        self.logger = logger
        
        if self.logger is None: # Enable logging
            self.logger = Logger( PXPaths.LOG + 'stats_' + self.loggerName + '.log', 'INFO', 'TX' + self.loggerName ) 
            self.logger = self.logger.getLogger()
                 

    

    def produceGraphicWithHourlyPickles( self, types , now = False ):
        """
            This higher-level method is used to produce a graphic based on the data found in log files
            concerning a certain client. Data will be searched according to the clientName and timespan
            attributes of a ClientGraphicProducer.  
            
            This method will gather the data starting from current time - timespan up to the time of the call.   
        
            Now option not yet implemented.
            
            Every pickle necessary for graphic production eeds to be there. Filling holes with empty data not yet implemented.  
            
            
        """ 
        
        collectorsList = [] #     
        minutesToAppend = 0 # In case we need to collect up to now 
        
        #Now not yet implemented.
        if now == True :
            endTime = self.currentTime
            
        else :
            endTime = MyDateLib.getIsoWithRoundedHours( self.currentTime )
            
        startTime = MyDateLib.getIsoFromEpoch( MyDateLib.getSecondsSinceEpoch( endTime ) - (self.timespan * MyDateLib.HOUR) )
        
        
         
        for client in self.clientNames : # 
               
            #Gather data from all previously creted pickles....                       
            self.logger.debug( "Call to mergeHourlyPickles." )
            self.logger.debug( " Parameters used : %s %s %s" %(startTime, endTime, client) )
            
            statsCollection = pickleMerging.mergePicklesFromDifferentMachines( logger = None , startTime = startTime, endTime = endTime, client = client, fileType = self.fileType, machines = self.machines )
            
            #print statsCollection.fileEntries[0].means      
            dataCollector =  ClientStatsPickler( client = client, statsTypes = types, directory = self.directory, statsCollection = statsCollection )
            
            collectorsList.append( dataCollector )         
             
        
        if self.productType != "All":
            
            for c in collectorsList: 
                c.statsCollection.setMinMaxMeanMedians(  productType = self.productType, startingBucket = 0 , finishingBucket = len(c.statsCollection.fileEntries)  )
#                     
        self.logger.debug( "Call to StatsPlotter :Clients:%s, timespan:%s, currentTime:%s, statsTypes:%s, productType:%s :" %( self.clientNames, self.timespan, self.currentTime, types, self.productType ) )
        
        plotter = StatsPlotter( stats = collectorsList, clientNames = self.clientNames, timespan = self.timespan, currentTime = endTime, now = False, statsTypes = types, productType = self.productType, logger = None  )
        
        plotter.plot()                          
        
        self.logger.debug( "Returns from StatsPlotter." )
        self.logger.info("Graphic(s) created.")
    


        

if __name__ == "__main__":
    """
        small test case to see proper use and see if everything works fine. 
        
    """
    
    gp = ClientGraphicProducer( clientNames = [ 'amis' ], timespan = 24, currentTime = "2006-08-01 18:15:00",productType = "All", directory = PXPaths.LOG , fileType = "tx" )  
    
    gp.produceGraphicWithHourlyPickles( types = [ "bytecount","latency","errors" ], now = False   )
    
    
    
    
#     gp = ClientGraphicProducer( clientNames = [ 'satnet' ], timespan = 12, currentTime = "2006-07-20 05:15:00",productType = "", directory =PXPaths.LOG, fileType = "tx" )  
#     
#     gp.produceGraphic( types = [ "bytecount","latency","errors" ], now = False   )


    
