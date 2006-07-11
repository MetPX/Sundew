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
import gzippickle
import MyDateLib
from MyDateLib import MyDateLib
import DirectoryStatsCollector
from DirectoryStatsCollector import DirectoryStatsCollector
import StatsPlotter
from StatsPlotter import StatsPlotter
import FileStatsCollector
from FileStatsCollector import FileStatsCollector, _FileStatsEntry
import pickleUpdater


class ClientGraphicProducer:
    
    
    
    def __init__( self, clientNames = None ,  timespan = 12, currentTime = None  ):
        """
            ClientGraphicProducer constructor. 
            
            CurrentTime format is ISO meaning "2006-06-8 00:00:00". Will use current
            system time by default.   
            
            CurrentTime is to be used if a different time than sytem time is to be used. 
            Very usefull for testing or to implement graphic request where user can choose start 
            time.  
    
        
        """
        
        if currentTime != None :
            currentTime = MyDateLib.getSecondsSinceEpoch( currentTime ) 
        else:
            currentTime = time.time()
            
            
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        self.timespan     = timespan          # Number of hours we want to gather the data from. 
        self.currentTime  = currentTime       # Time when stats were queried.
        
            
    
    def getStartTimes( self, currentTime = 0 ,  timespan = 0 ):
        """ 
            Returns startime for each day we need to look up for 
            Allows users to get stats from numerous past days. 
            
        """ 
        
        startTimes = []  # list of all startTimes 
        startTime  = ""  # Temporary variable used to calculate particular startTime
        
        width = timespan*60*60 #fixes start Time for furthest past day 
        startTime = currentTime - width
        startTimes.append ( MyDateLib.getIsoFromEpoch( startTime ) )
        
        daysInBetween = MyDateLib.getNumberOfDaysBetween( MyDateLib.getIsoFromEpoch( currentTime ), MyDateLib.getIsoFromEpoch( startTime ) ) 
        
        remainingDays = range( daysInBetween )
        remainingDays.reverse()
        
        
        for i in remainingDays:
            
            startTime  = ( currentTime - (i*24*60*60) )
            dateWoHour = MyDateLib.getIsoFromEpoch( startTime ).split( " ")[0]
            startTime  = dateWoHour + " 00:00:00"
            startTimes.append( startTime  )
            
        
       
        return startTimes 
    
        
    getStartTimes = staticmethod( getStartTimes )
    
    
    
    def getStatsFromPickle( self, type, pickleName , graphEntries, startTime = "2006-06-8 00:00:00" ):
        """
            This method returns a list of all the stats found in a pickle, 
            from the starting point up to the very end of the file.
            
            This is usefull for pickles from past days where all the data has previously been 
            collected. 
            
            ***warning***We take for granted here that buckets were allready made for every minute.... 
            
        """ 
        
        
        try:
            statsCollection = gzippickle.load( pickleName )
            
            numberOfMinutes = MyDateLib.getMinutesSinceStartOfDay( startTime )
    
            for i in range( numberOfMinutes, len( statsCollection.fileEntries) ):
                graphEntries.append( statsCollection.fileEntries[i] )
                
            
            return graphEntries
        
            
        except Exception, e :
        
            print "Exception %s.\nProgram terminated." %e
            sys.exit()
        
    
    
    def fillWithEmptyEntries( self, nbEmptyEntries, entries ):
        """
            Append certain number of empty entries to the entry list. 
        
        """
        
        
        for i in range( nbEmptyEntries ):
            entries.append( _FileStatsEntry() )       
     
    
        return entries


    
    def getDaysToSearch( self, currentHour ):
        """
            Returns a list of days to search for data.
            If 3 days are needed will return [2,1,0] 
            
        """
        
      
        if ( ( int(currentHour) - self.timespan ) >= 0 ):
            nbDaysToSearch = 1
        else:    
            nbDaysToSearch = 2 + (( self.timespan - int(currentHour) ) /24 ) #number of past days we need to look up
            
        
        days  = range( nbDaysToSearch )
        days.reverse()
        
        return days
        
        
        
    def getStatsFromDsCollector( self, type, graphEntries, todaysEntries, startTime = "2006-06-8 00:00:00", pickleStartTime = 0 ) :
        """
            This method returns a list of all the stats found in a dataCollector, 
            from the starting point set up by startTime up to the very end.
            This is used for current day where data collected might not yet have been pickled.
            
            ***warning***We take for granted here that buckets were allready made for every minute.... 
            
        """ 
        
        entryCount = 0 
        
        emptyEntry = _FileStatsEntry( means = [0.0], maximums = [0.0] )
        
        numberOfMinutesStart  = MyDateLib.getMinutesSinceStartOfDay( startTime )
        numberOfMinutesEnd    = MyDateLib.getMinutesSinceStartOfDay( MyDateLib.getIsoFromEpoch( self.currentTime ) )
        
        while entryCount < len( todaysEntries ) and MyDateLib.getMinutesSinceStartOfDay( MyDateLib.getIsoFromEpoch(todaysEntries[entryCount].startTime)) < numberOfMinutesStart: 
	    
            entryCount =  entryCount + 1
        
        
        # Verify that it's within range of todays pickle.
        # Important in case we started pickling later for some reason...
        # like a new server or down server or whatever.    
        for i in range( numberOfMinutesStart, numberOfMinutesEnd ):
            
            if i < MyDateLib.getMinutesSinceStartOfDay(  MyDateLib.getIsoFromEpoch( pickleStartTime ) ):
                #in case pickling started AFTER the graphics start.....    
                graphEntries.append( emptyEntry )
            
            else:#Append only data wich is within boundaries.Pickle probably started before the graph starts...  
                graphEntries.append( todaysEntries[ entryCount] )    
                entryCount = entryCount + 1
                
        return graphEntries
        
 
        
    def produceGraphic( self, types , now = False):
        """
            This higher-level method is used to produce a graphic based on the data found in log files
            concerning a certain client. Data will be searched according to the .clientName and timespan
            attributes of a ClientGraphicProducer.  
            
            This method will gather the data starting from current time - timespan up to the time of the call.   
            
            Note : Quite long for my likings.
                   Would be nice if it could be trimmed up a little or split into different part.          
        
        """ 
        
        collectorsList = [] #     
        minutesToAppend = 0 # In case we need to collect up to now 
        
        #Find how data will be spread between within different days and hours.... 
        currentIsoHour = MyDateLib.getIsoWithRoundedHours( MyDateLib.getIsoFromEpoch( self.currentTime ) )
        currentIsoHour = MyDateLib.getSecondsSinceEpoch( currentIsoHour ) 
        
        startTimes = self.getStartTimes( self, currentTime = currentIsoHour ,  timespan = self.timespan ) 
        startTimes.reverse()
        
        
        currentHour = MyDateLib.getHoursFromIso( MyDateLib.getIsoFromEpoch( self.currentTime ) )
        days = self.getDaysToSearch( currentHour )    
        
        if now == True :
            endTime =  MyDateLib.getIsoWithRoundedSeconds( MyDateLib.getIsoFromEpoch( self.currentTime ) )
            minutesToAppend = int(MyDateLib.getMinutesFromIso( endTime )  )
        
        else :     
            endTime = MyDateLib.getIsoWithRoundedHours( MyDateLib.getIsoFromEpoch( self.currentTime ) )
            minutesToAppend = 0
            
            
        for i in range( len( self.clientNames ) ):
            
            
            #Create collection that's properly cut in buckets....
            statsCollection = FileStatsCollector( statsTypes = types, startTime = startTimes[ len(startTimes)-1 ] , width = ( self.timespan* MyDateLib.HOUR ), interval = MyDateLib.MINUTE, totalWidth = ((self.timespan* MyDateLib.HOUR ) + 60 * minutesToAppend ) )
            
            
            lastCronJob = pickleUpdater.getLastCronJob( self.clientNames[i], MyDateLib.getIsoFromEpoch(self.currentTime) )
            
            timeSinceLastCron = self.currentTime -  MyDateLib.getSecondsSinceEpoch( lastCronJob )
            

            #do a pickleUpdater like job without saving pickle....
            ds = DirectoryStatsCollector( directory = pickleUpdater.getfilesIntoDirectory( self.clientNames[i] ) )
            
            
            if endTime != lastCronJob : #collect data that was not collected
            
                ds.collectStats( types, startTime = lastCronJob , endTime = endTime, width = timeSinceLastCron, interval = 1*MyDateLib.MINUTE, pickle = DirectoryStatsCollector.buildTodaysFileName( self.clientNames[i], tempTime = MyDateLib.getIsoFromEpoch(self.currentTime )) , save = False )         
            
            else:#skip collecting 
                
                pickleName = DirectoryStatsCollector.buildTodaysFileName( self.clientNames[i], tempTime = MyDateLib.getIsoFromEpoch(self.currentTime ))
                ds.statsCollection = gzippickle.load( pickleName )
                      
            
            #Build a directory stats collector with todays info.. stats collection has allready been cut in bucket 
            #corresponding to the ones needed in the graphic
            dataCollector  = DirectoryStatsCollector( startTime = startTimes[0], statsCollection = statsCollection )
            dataCollector.startTime = startTimes[0]
            dataCollector.statsCollection.fileEntries = []
            
           
             
            for j in days : #Now gather all usefull info that was previously treated.
                
                
                thatDaysPickle = DirectoryStatsCollector.buildTodaysFileName( self.clientNames[i],offset = j - ( 2*j ), tempTime = endTime )
                
                if j == 0 :
                
                    dataCollector.statsCollection.fileEntries = self.getStatsFromDsCollector( type = types[0], graphEntries = dataCollector.statsCollection.fileEntries, todaysEntries = ds.statsCollection.fileEntries, startTime = startTimes[0],pickleStartTime = ds.statsCollection.fileEntries[0].startTime )  
                    
                                    
                elif os.path.isfile( thatDaysPickle ) :#check to see if that days pickle exist. 
                    
                    dataCollector.statsCollection.fileEntries =  self.getStatsFromPickle( type = types[0], pickleName = thatDaysPickle, graphEntries = dataCollector.statsCollection.fileEntries, startTime = startTimes[j] ) 
                     
                
                else:#fill up gap with empty entries                
                    
                    if j != 0 :#j is allready tested fount out why im testing this....
                        nbEmptyEntries = MyDateLib.MINUTES_PER_DAY - MyDateLib.getMinutesSinceStartOfDay( startTimes[j] )
                                                
                    else:    
                        nbEmptyEntries = MyDateLib.getMinutesSinceStartOfDay( MyDateLib.getIsoFromEpoch(self.currentTime) )- MyDateLib.getMinutesSinceStartOfDay( startTimes[j] )
                    
                    
                    dataCollector.statsCollection.fileEntries = self.fillWithEmptyEntries( nbEmptyEntries, dataCollector.statsCollection.fileEntries)
                   
                        
            collectorsList.append( dataCollector )                        
        
       
        plotter = StatsPlotter( stats = collectorsList, clientNames = self.clientNames, timespan = self.timespan, currentTime = self.currentTime, now = False, statsTypes = types  )
        plotter.plot()                          
         


        
if __name__ == "__main__":
    """
        small test case to see proper use and see if everything works fine. 
        
    """
    
    gp = ClientGraphicProducer( clientNames = [ 'satnet' ], timespan = 24, currentTime = "2006-07-01 18:15:00"  )  
    gp.produceGraphic( types = [ "errors","latency" ], now = False   )


    
