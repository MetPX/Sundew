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
        self.currentTime  = time.time()       # Time when stats were queried.
        self.timespan     = timespan          # Number of hours we want to gather the data from 
    
        
            
    def getStartTimes( self, currentTime = 0 ,  timespan = 0 ):
        """ 
            Returns startime for each day we need to look up for 
            Allows users to get stats from numeroous past days. 
            
        """ 
        
        startTimes = [] 
        startTime  = ""
        
        
        #fixes start Time for furthest past day 
        width = timespan*60*60
        
        tempTime = currentTime-width
        
        startTimes.append ( MyDateLib.getOriginalDate(tempTime)  )
        
        #All these days will start at 00:00:00
        remainingDays = range( 0, int( timespan/24 ) )
        remainingDays.reverse()
        
        
        for i in remainingDays:
            
            tempTime = ( currentTime - (i*24*60*60) )
            dateWoHour = MyDateLib.getOriginalDate( tempTime ).split( " ")[0]
            startTime = dateWoHour + " 00:00:00"
            startTimes.append( startTime  )
            
        
       
        return startTimes 
    
        
    getStartTimes = staticmethod( getStartTimes )
    
    
    
    def getStatsFromPickle( self, pickleName , dataCollector, startTime = "2006-06-8 00:00:00"  ):
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
                dataCollector.statsCollection.fileEntries.append( statsCollection.fileEntries [i] )

            return dataCollector.statsCollection.fileEntries
            
            
        except:
            print "Error reading the %s pickle file.\nProgram terminated."
            sys.exit()
        
    
    
    def fillWithEmptyEntries(self, nbEmptyEntries, entries):
        """
            append empty entries to the entries
        
        """
        
        
        for i in range( nbEmptyEntries ):
            entries.append( _FileStatsEntry() )       
     
    
        return entries



    def getCurrentHour(self):
        """
            returns only the hour field of the current time transformed in 
            iso date 
            
        """
        
        currentHour = MyDateLib.getOriginalDate( self.currentTime )
        currentHour = currentHour.split( " " )
        currentHour = currentHour[1]
        currentHour = currentHour.split(":")
        currentHour = currentHour[0]
        
        return currentHour 
    
        
        
    def getDaysToSearch( self, currentHour ):
        """
            Returns a list of days to search for data. If 3 days are needed will return
            [2,1,0] 
            
        """
        
      
        if ( ( int(currentHour) - self.timespan ) >= 0 ):
           
            nbDaysToSearch = 1
        
        else:    
           
            nbDaysToSearch = 2 + (( self.timespan - int(currentHour) )/24)   #number of past days we need to look up
            
 
        
        days  = range( nbDaysToSearch )
        days.reverse()
        
        return days
        
        
        
    def getStatsFromDsCollector( self, entries, dataCollector , startTime = "2006-06-8 00:00:00"  ) :
        """
            This method returns a list of all the stats found in a dataCollector, 
            from the starting point set up by startTime up to the very end.
            This is used for current day where data collected might not yet have been pickled.
            
            ***warning***We take for granted here that buckets were allready made for every minute.... 
            
        """ 

        numberOfMinutes = MyDateLib.getMinutesSinceStartOfDay( startTime )
        
        for i in range( numberOfMinutes, len( dataCollector.statsCollection.fileEntries) ):
            entries.append( dataCollector.statsCollection.fileEntries [i] )

        return entries
        
 
        
            
    def produceGraphic( self, types ):
        """
            This higher-level method is used to produce a graphic based on the data found in log files
            concerning a certain client. Data will be searched according to the .clientName and timespan
            attributes of a ClientGraphicProducer.  
            
            This method will gather the data starting from current time - timespan up to the time of the call.   
                      
        """ 
        
        collectorsList = []        
        #Find how data will be spread between within different days and hours....   
        startTimes = self.getStartTimes( self, currentTime = self.currentTime ,  timespan = self.timespan ) 
        startTimes.reverse()
        
        currentHour = self.getCurrentHour()
        days = self.getDaysToSearch( currentHour )    
        
        
        for i in range( len( self.clientNames ) ):
            
            #Create empty entries that are properly cut in buckets....
            statsCollection = FileStatsCollector( statsTypes = types, startTime = startTimes[ len(startTimes)-1 ] , width = (self.timespan* MyDateLib.HOUR), interval = MyDateLib.MINUTE, totalWidth = (self.timespan* MyDateLib.HOUR) )
            
            lastCronJob = pickleUpdater.getLastCronJob( self.clientNames[i],self.currentTime,self.clientNames,update = False )
            
            #collect today's missing data since last pickle occured....
            dataCollector  = DirectoryStatsCollector( startTime = startTimes[0], statsCollection = statsCollection )
            dataCollector.startTime = startTimes[0]
            dataCollector.statsCollection.fileEntries = []
            
            timeSinceLastCron = self.currentTime -  lastCronJob 
            
            ds = DirectoryStatsCollector( directory = pickleUpdater.getfilesIntoDirectory( self.clientNames[i] ) )
            ds.collectStats( types, startTime = MyDateLib.getOriginalDate(lastCronJob) , width = timeSinceLastCron, interval = 1*MyDateLib.MINUTE,pickle = DirectoryStatsCollector.buildTodaysFileName( self.clientNames[i] ),save = False )
            
            
            for j in days : #Now gather all usefull info that was previously treated.
                
                
                thatDaysPickle = DirectoryStatsCollector.buildTodaysFileName( self.clientNames[i], offset = j - ( 2*j ) )
                
                if j == 0 :
                    dataCollector.statsCollection.fileEntries = self.getStatsFromDsCollector(  entries = dataCollector.statsCollection.fileEntries, dataCollector = ds, startTime = startTimes[j] )  
                    
                elif os.path.isfile( thatDaysPickle ) :#check to see if that days pickle exist. 
        
                    dataCollector.statsCollection.fileEntries =  self.getStatsFromPickle( pickleName = thatDaysPickle, dataCollector = dataCollector, startTime = startTimes[j] ) 
                
                else:#fill up gap with empty entries 
                    
                    MINUTES_PER_DAY = 60*24 
                    
                    if i!= 0 :#find how many empty entries we need 
                        nbEmptyEntries = MINUTES_PER_DAY - MyDateLib.getMinutesSinceStartOfDay( startTimes[j] )
                    else:    
                        nbEmptyEntries = MyDateLib.getMinutesSinceStartOfDay( MyDateLib.getOriginalDate(self.currentTime) )- MyDateLib.getMinutesSinceStartOfDay( startTimes[j] )
                    
                    dataCollector.statsCollection.fileEntries = self.fillWithEmptyEntries( nbEmptyEntries, dataCollector.statsCollection.fileEntries)
    
                collectorsList.append( dataCollector )
                         
        #Finally we use stats plotter to produce graphic.
        plotter = StatsPlotter( stats = collectorsList, clientNames = self.clientNames, timespan = self.timespan,currentTime = self.currentTime  ) 
        plotter.plot()                          
         

        
if __name__ == "__main__":
    """
        small test case to see proper use and see if everything works fine. 
        
    """
    gp = ClientGraphicProducer( clientNames = ['metpx'], timespan = 12 )  
    gp.produceGraphic( types = ["latency"] )
        