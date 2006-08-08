"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
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
##          It needs the file DirectoryFileCollector.py to collect all the file entries. 
##          
##          It needs the FileStatsCollector.py to collect the stats from each file   
##          that DirectoryFileCollector.py finds. 
## 
##          Specified directory needs to contain only valid files.  
##
#######################################################################################


#important files
import os 
import pickle
import cPickle
import DirectoryFileCollector
import cpickleWrapper
import PXPaths
from   Logger                 import *
from   Numeric                import *
from   FileStatsCollector     import *
from   random                 import *
from   DirectoryFileCollector import *
from   FileStatsCollector     import *
from   MyDateLib              import *

PXPaths.normalPaths()


class ClientStatsPickler:
    """
        Contains all the methods needed to pickle stats for a certain client.
    """
    
    def __init__( self, client = "", directory = "", statsTypes = None, statsCollection = None, pickleName = "", logger = None, machine = "pds5"  ):
        """ 
            Constructor.
            -Builds a ClientStatsPickler with no entries.   
        
        """
        
        self.client           = client                              #Name of the lcient for whom were collecting data 
        self.pickleName       = ""                                  #Pickle 
        self.directory        = directory                           #Name of the directory containing stats files.
        self.statsTypes       = statsTypes or []                    #Types we'll search for stats. 
        self.machine          = machine                             #Machine on wich the data resides.
        self.fileCollection   = DirectoryFileCollector( directory = directory ) #List of all the test files. 
        self.statsCollection  = statsCollection or FileStatsCollector()#All fileStats collected. 
        self.loggerName       = 'pickling'
        self.logger           = logger
        
        if logger is None: # Enable logging
            self.logger = Logger( PXPaths.LOG + 'stats_' + self.loggerName + '.log', 'INFO', 'TX' + self.loggerName ) 
            self.logger = self.logger.getLogger()
           


    def buildThisHoursFileName(  client = "satnet", offset = 0, currentTime = "", fileType = "tx", machine = "pds5" ):
        """ 
            Builds a filename using current currentTime.
            
            The format will be something like this :
            /apps/px/lib/stats/pickles/clientName/date/hour
            Ex :/apps/px/lib/stats/pickles/clientName/20060707/12:00:00
            
            offset can be used to find a file from an hour close to the current one 
            
            tempcurrentTime can also be used to build a filename from another hour. 
            
            
            To be used with pickles created hourly.
                
        """    
        
        fileName = PXPaths.PICKLES +  client + "/"
        
        
        if currentTime == "":
            currentTime = time.time()
        else:
            currentTime = MyDateLib.getSecondsSinceEpoch( currentTime )    
        
        currentTime = currentTime + ( offset * MyDateLib.HOUR )
        splitTime = time.gmtime( currentTime )    
        
        for i in range( 3 ):
            
            if int( splitTime[i] ) < 10 :
                fileName = fileName + "0" + str( splitTime[i] )
            else:
                fileName = fileName + str( splitTime[i] )          
        
                
        hour = MyDateLib.getHoursFromIso( MyDateLib.getIsoFromEpoch( currentTime ) )
        
        fileName = fileName + "/" + fileType + "/" + machine + "_" + hour
        
        
        return fileName 
    
    buildThisHoursFileName = staticmethod( buildThisHoursFileName )    
    
    
    
    def collectStats( self, types, directory, fileType = "tx", startTime = '2006-05-18 00:00:00', endTime = "", interval = 60*MINUTE, save = True  ):
        """
            This method is used to collectstats for a directory.
            
            Types is the type of dats to be collected. 
            
            Pickle is th ename of the file to be used. If not specified will be generated
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
        self.fileCollection =  DirectoryFileCollector( startTime  = startTime , endTime = endTime, directory = directory, lastLineRead = "", fileType = fileType, client = self.client )   
        self.fileCollection.collectEntries()          #find all entries from the folder
        
                
        if os.path.isfile( self.pickleName ): #We use whatever pickle the user specified.
            
            self.logger.warning( "User tried to modify allready filled pickle file." )
            self.logger.warning( "Pickle was named : %s" %self.pickleName )      
            
        else: 
            # Creates a new FileStats collector wich spans from the very 
            # start of the hour up till the end. 
            
            if self.pickleName == "":
                self.pickleName = ClientStatsPickler.buildThisHoursFileName( client = self.client, currentTime = startTime, machine = self.machine )
            
            self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, statsTypes = types, startTime = MyDateLib.getIsoWithRoundedHours( startTime ), endTime = endTime, interval = interval, totalWidth = 1*HOUR )
            
            self.statsCollection.collectStats( endTime )    

        try :    
            if save == True :
                temp =  self.statsCollection.logger
                del self.statsCollection.logger
                cpickleWrapper.save ( object = self.statsCollection, filename = self.pickleName ) 
                self.statsCollection = temp
                self.logger.info( "Saved pickle named : %s " %self.pickleName )  
        
        except:   
            (type, value, tb) = sys.exc_info()
            self.logger.error( "Error trying to save pickle named : %s" %self.pickleName )
            self.logger.error( "Type: %s, Value: %s, tb: %s ..." % (type, value,tb) )        
        
    
             
    def printStats( self ) :       
        """
            This method prints out all the stats concerning each files. 
            Mostly usefull for debugging.
            
            file is printed in currentWorkingDirectory/CSC_output_file
        """    
        
        absoluteFilename = str( PXPaths.STATS ) + "CSP_output_file "
        print "Absolute filename : %s" %absoluteFilename
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
        
    types = [ "latency","errors","bytecount" ]    
      
    cs = ClientStatsPickler( client = "satnet", directory = PXPaths.LOG )
    
    cs.collectStats( types, directory = PXPaths.LOG, fileType = "tx", startTime = '2006-07-16 01:00:12', endTime = "2006-07-16 01:59:12", interval = 1*MINUTE )  
            
    cs.printStats()        
    
    print ClientStatsPickler.buildThisHoursFileName()     
       

if __name__ == "__main__":
    main()    