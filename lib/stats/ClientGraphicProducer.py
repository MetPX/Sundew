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
## Description : Contains all classes and methods usefull to produce a graphic 
##               for a certain client. Main use is to build latency graphics
##               for one or many clients. 
##
##
##               Implementation of other classes of this library used allow
##               for multi-data types.
##
##               Thus far this implentation is slightly too rigid to produce 
##               multi data types graphics but should be easily modified to do so.
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
    
    
    
    def __init__( self, clientNames = None ,  timespan = 12 ):
        """
            ClientGraphicProducer constructor.     
    
        """
        
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        #self.currentTime  = time.time()       # Time when stats were queried.
        self.currentTime  = MyDateLib.getSecondsSinceEpoch( "2006-06-29 08:25:00" )
        self.timespan     = timespan          # Number of hours we want to gather the data from. 
        
        
            
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
            
            startTime = ( currentTime - (i*24*60*60) )
            dateWoHour = MyDateLib.getIsoFromEpoch( startTime ).split( " ")[0]
            startTime = dateWoHour + " 00:00:00"
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
                graphEntries.append( statsCollection.fileEntries [i] )
                
            
            return graphEntries
        
            
        except Exception, e :
        
            print "Exception %s.\nProgram terminated." %e
            sys.exit()
        
    
    
    def fillWithEmptyEntries( self, nbEmptyEntries, entries ):
        """
            Append empty entries to the entries
        
        """
        
        
        for i in range( nbEmptyEntries ):
            entries.append( _FileStatsEntry() )       
     
    
        return entries



    def getCurrentHour( self ):
        """
            Returns only the hour field of the current time transformed in 
            iso date 
            
        """
        
        currentHour = MyDateLib.getIsoFromEpoch( self.currentTime )
        currentHour = currentHour.split( " " )
        currentHour = currentHour[1]
        currentHour = currentHour.split(":")
        currentHour = currentHour[0]
        
        return currentHour 
    
        
        
    def getDaysToSearch( self, currentHour ):
        """
            Returns a list of days to search for data.
            If 3 days are needed will return [2,1,0] 
            
        """
        
      
        if ( ( int(currentHour) - self.timespan ) >= 0 ):
            nbDaysToSearch = 1
        else:    
            nbDaysToSearch = 2 + (( self.timespan - int(currentHour) ) /24 )   #number of past days we need to look up
            
        
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
        
        
        emptyEntry = _FileStatsEntry( means = [0.0], maximums = [0.0] )
        
        numberOfMinutesStart  = MyDateLib.getMinutesSinceStartOfDay( startTime )
        numberOfMinutesEnd    = MyDateLib.getMinutesSinceStartOfDay(MyDateLib.getIsoFromEpoch(self.currentTime))
        
        
        entryCount = 0 
	while entryCount < len(todaysEntries) and MyDateLib.getMinutesSinceStartOfDay( MyDateLib.getIsoFromEpoch(todaysEntries[entryCount].startTime)) < numberOfMinutesStart: 
	    
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
                
        return  graphEntries
        
 
        
    def produceGraphic( self, types , now = False):
        """
            This higher-level method is used to produce a graphic based on the data found in log files
            concerning a certain client. Data will be searched according to the .clientName and timespan
            attributes of a ClientGraphicProducer.  
            
            This method will gather the data starting from current time - timespan up to the time of the call.   
                      
        """ 
        
        collectorsList = [] #     
        minutesToAppend = 0 # In case we need to collect up to now 
        
        #Find how data will be spread between within different days and hours.... 
        currentIsoHour = MyDateLib.getIsoWithRoundedHours( MyDateLib.getIsoFromEpoch( self.currentTime ) )
        currentIsoHour = MyDateLib.getSecondsSinceEpoch( currentIsoHour ) 
        
        startTimes = self.getStartTimes( self, currentTime = currentIsoHour ,  timespan = self.timespan ) 
        startTimes.reverse()
        
        
        currentHour = self.getCurrentHour()
        days = self.getDaysToSearch( currentHour )    
        
        if now == True :
            endTime =  MyDateLib.getIsoFromEpoch( self.currentTime ) 
            minutesToAppend = int(MyDateLib.getMinutesFromIso( endTime )  )
        
        else :     
            endTime = MyDateLib.getIsoWithRoundedSeconds( MyDateLib.getIsoFromEpoch( self.currentTime ) )
            minutesToAppend + 0
            
        for i in range( len( self.clientNames ) ):
            
            
            #Create empty entries that are properly cut in buckets....
            statsCollection = FileStatsCollector( statsTypes = types, startTime = startTimes[ len(startTimes)-1 ] , width = ( self.timespan* MyDateLib.HOUR ), interval = MyDateLib.MINUTE, totalWidth = ((self.timespan* MyDateLib.HOUR ) + 60 * minutesToAppend ) )
            
            
            lastCronJob = pickleUpdater.getLastCronJob( self.clientNames[i], MyDateLib.getIsoFromEpoch(self.currentTime),update = False )
            
            
            timeSinceLastCron = self.currentTime -  MyDateLib.getSecondsSinceEpoch( lastCronJob )
            
            
            #do a pickle update like job without saving pickle....
            ds = DirectoryStatsCollector( directory = pickleUpdater.getfilesIntoDirectory( self.clientNames[i] ) )
            ds.collectStats( types, startTime = lastCronJob , endTime = endTime, width = timeSinceLastCron, interval = 1*MyDateLib.MINUTE, pickle = DirectoryStatsCollector.buildTodaysFileName( self.clientNames[i],tempTime = MyDateLib.getIsoFromEpoch(self.currentTime )) , save = False )                   

            
            #Build a directory stats collector with todays info.... stats collection has allread been cut in bucket 
            #corresponding to the ones needed in the graphic
            dataCollector  = DirectoryStatsCollector( startTime = startTimes[0], statsCollection = statsCollection )
            dataCollector.startTime = startTimes[0]
            dataCollector.statsCollection.fileEntries = []
            
             
            for j in days : #Now gather all usefull info that was previously treated.
                
                
                thatDaysPickle = DirectoryStatsCollector.buildTodaysFileName( self.clientNames[i],offset = j - ( 2*j ), tempTime = endTime )
                
                if j == 0 :
                
                    print "***working on todays data"

                    print "pickle startTime avant getstats from ds collector : %s" %MyDateLib.getIsoFromEpoch( ds.statsCollection.fileEntries[0].startTime)   
                    dataCollector.statsCollection.fileEntries = self.getStatsFromDsCollector( type = types[0], graphEntries = dataCollector.statsCollection.fileEntries, todaysEntries = ds.statsCollection.fileEntries, startTime = startTimes[0],pickleStartTime = ds.statsCollection.fileEntries[0].startTime )  
                    
                    print "len apres : %s " %len(dataCollector.statsCollection.fileEntries)
                
                elif os.path.isfile( thatDaysPickle ) :#check to see if that days pickle exist. 
                     print "****from the pickle : %s" %thatDaysPickle
                     print "j : %s" %j 
                     print "offset : %s " % (j - ( 2*j ))
                     print "types : %s" %types
                     print "starttimes : %s" %startTimes
                     print "startime du pickle : %s" %startTimes[j]
                     dataCollector.statsCollection.fileEntries =  self.getStatsFromPickle( type = types[0], pickleName = thatDaysPickle, graphEntries = dataCollector.statsCollection.fileEntries, startTime = startTimes[j] ) 
                     
                     print "len data collector apres pickling : %s" %len(dataCollector.statsCollection.fileEntries)
                     
                         
                else:#fill up gap with empty entries 
                    print "***empty entries "
                    MINUTES_PER_DAY = 60*24 
                    
                    if j != 0 :#j is allready tested fount out why im testing this....
                        nbEmptyEntries = MINUTES_PER_DAY - MyDateLib.getMinutesSinceStartOfDay( startTimes[j] )
                        print "MINUTES_PER_DAY :%s " %MINUTES_PER_DAY
                        print "MyDateLib.getMinutesSinceStartOfDay( startTimes[j] ) : %s" %MyDateLib.getMinutesSinceStartOfDay( startTimes[j] )
                        
                    else:    
                        nbEmptyEntries = MyDateLib.getMinutesSinceStartOfDay( MyDateLib.getIsoFromEpoch(self.currentTime) )- MyDateLib.getMinutesSinceStartOfDay( startTimes[j] )
                    
                    print "nbEmptyEntries : %s" %nbEmptyEntries
                    dataCollector.statsCollection.fileEntries = self.fillWithEmptyEntries( nbEmptyEntries, dataCollector.statsCollection.fileEntries)
                    print "len apres empty entries %s" %len(dataCollector.statsCollection.fileEntries)
                        
            print "len avant append : %s " %len(dataCollector.statsCollection.fileEntries)
            
            collectorsList.append( dataCollector )
                         
        
       
        plotter = StatsPlotter( stats = collectorsList, clientNames = self.clientNames, timespan = self.timespan, currentTime = self.currentTime, now = now  )
        plotter.plot()                          
         

        
if __name__ == "__main__":
    """
        small test case to see proper use and see if everything works fine. 
        
    """
    
    
    gp = ClientGraphicProducer( clientNames = ['satnet'], timespan = 12 )  
    gp.produceGraphic( types = ["latency"], now = True  )
        