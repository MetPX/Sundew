"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
#######################################################################################
##
## Name   : ClientStatsCollector.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006
##
## Goal   : This class is used to collect stats from all the files from a directory.
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
import gzippickle
from   Numeric import *
from   FileStatsCollector     import *
from   random                 import *
from   DirectoryFileCollector import *
from   FileStatsCollector     import *
from   MyDateLib              import *


class ClientStatsCollector:
    """
        Contains all the methods needed to collect stats from a certain directory.
    """
    
    def __init__( self, client = "", directory = "", statsTypes = None, startTime = "2006-05-18 21:45:30",statsCollection = None ):
        """ 
            Constructor.
            -Builds a directoryFileCollector with no entries.   
        
        """
        self.client           = client                              #Name of the lcient for whom were collecting data  
        self.directory        = directory                           #Name of the directory containing stats files.
        self.statsTypes       = statsTypes or []                    #Types we'll search for stats. 
        self.fileCollection   = DirectoryFileCollector( directory = directory ) #List of all the test files. 
        self.statsCollection  = statsCollection or FileStatsCollector(startTime = startTime)#All fileStats collected. 
        
        
        
    
    def buildTodaysFileName(  clientName = "", offset = 0, tempTime = "" ):
        """ 
            Builds a filename using current time.
            The format will be clientNameDate
	    Ex: satnet20060707
                     
            offset can be used to find a file from a day close to the current one 
            
            tempTime can also be used to build a filename from another day. 
            
            
        """    
        
        fileName = str( os.getcwd() ) #will probably need a better path eventually.... 
        fileName = fileName +  "/pickles/%s" %( clientName )
        
        if tempTime == "" :
        
            tempTime = time.time() 
            tempTime = tempTime + (offset*24*60*60)
        
        else:
            
            tempTime = MyDateLib.getSecondsSinceEpoch( tempTime )
            tempTime = tempTime + (offset*24*60*60)
            
            
        for i in range(3):
            
            if i == 1 and int(i) < 10:
                fileName = fileName + "0" + str( time.gmtime( tempTime )[i] )
            else:
                fileName = fileName + str( time.gmtime( tempTime )[i] )        
        
        return fileName 
        
    buildTodaysFileName = staticmethod( buildTodaysFileName )
    
    
    
    def isReadableFile( file ):
        """ 
            This method receives the absolute path to a file.
            It checks if it can be read.If so returns True otherwise 
            returns false. 
        
        """
    
        readable = True 
        
        try:
            fileHandle = open( file, 'r' )
        except:
            readable = False
        else:#since opening file went fine     
            fileHandle.close()                 
        
        return readable    



    def collectStats( self, types, pickle, directory,fileType = "tx", startTime = '2006-05-18 00:00:00', endTime = "",  width=DAY, interval = 60*MINUTE, save = True, dailyPickling = True ):
        """
            This method collects the stats for all the files found in the directory. 
        """
        print "in collect stats " 
        print "startTime :%s" %startTime
        print "endtime : %s" %endTime
        print "fileType : %s" %fileType
        print "self.client : %s"  %self.client
        
        self.fileCollection =  DirectoryFileCollector( startTime  = startTime , endTime = endTime, directory = directory, lastLineRead = "", lineType = "[INFO]", fileType = fileType, client = self.client )   
        self.fileCollection.collectEntries()          #find all entries from the folder
        
        print "self.fileCollection.entries %s" %self.fileCollection.entries
        
        
        if os.path.isfile( pickle ):
                    
            self.statsCollection = gzippickle.load( pickle )            
           
            #update fields who need to be updated like list of file .
            #we dont allow someone to change interval during the day so we dont even look it up
            self.statsCollection.files = self.fileCollection.entries 
            self.statsCollection.startTime = MyDateLib.getSecondsSinceEpoch( startTime )
            self.statsCollection.width = width 
            
            self.statsCollection.collectStats( endTime  )           
            
           
        elif dailyPickling == True :  
            
            self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, statsTypes = types, startTime = MyDateLib.getIsoTodaysMidnight( startTime ), width = width, interval = interval, totalWidth = 24*HOUR )
            
            self.statsCollection.collectStats( endTime )
            
        
        elif dailyPickling == False:

            self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, statsTypes = types, startTime = MyDateLib.getIsoWithRoundedSeconds(startTime), width = width, interval = interval, totalWidth = 24*HOUR )
            self.statsCollection.collectStats( endTime )         
        
        
        if save == True :
            gzippickle.save ( object = self.statsCollection, filename = pickle ) 
           
        
        
    def collectStatsWithoutPickling( self, types, startTime = '2006-05-18 00:00:00', width=DAY, interval = 60*MINUTE, totalWidth = 24*HOUR, totalwidth = DAY  ):
        """
            This method collects the stats for all the files found in the directory. 
        
        """
    
        self.fileCollection.collectEntries() # find all entries from the folder
        
        self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, statsTypes = types, startTime = startTime , width = width, interval = interval, totalWidth = totalWidth )
        
        self.statsCollection.width = totalWidth
        self.statsCollection.collectStats()           
    

    
    def printStats( self ) :       
        """
            This method prints out all the stats concerning each files. 
            Mostly usefull for debugging.
        
        """    
        
        absoluteFilename = str( os.getcwd() ) + "/CSC_output_file "
        print "Absolute filename : %s" %absoluteFilename
        fileHandle = open( absoluteFilename , 'w' )
        old_stdout = sys.stdout 
        sys.stdout = fileHandle 
        
        print "\n\nFiles used : %s" %self.fileCollection.entries
        print "Starting date: %s" % MyDateLib.getIsoFromEpoch(self.statsCollection.startTime)
                                    
        print "Interval: %s" %self.statsCollection.interval
        print "Time Width: %s" %self.statsCollection.width

        for j in range( self.statsCollection.nbEntries ):
            print "\nEntry's interval : %s - %s " %( MyDateLib.getIsoFromEpoch(self.statsCollection.fileEntries[j].startTime), MyDateLib.getIsoFromEpoch(self.statsCollection.fileEntries[j].endTime ) )
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
        print "printed %s " %absoluteFilename
    
    
 
def main():
    """
            small test case. Tests if everything works plus gives an idea on proper usage.
    """
        
    types = [ 'latency']
    
    print "Temps avant : % s" %time.gmtime( time.time() )
    
    cs = ClientStatsCollector( client = "satnet", directory = "/apps/px/lib/stats/files/" )
    cs.collectStats( types, directory = "/apps/px/lib/stats/files/", fileType = "tx", pickle = "/apps/px/lib/stats/PICKLES/satnetTestpickle", startTime = '2006-07-20 05:00:12', endTime = "2006-07-20 06:00:12",width = 10*HOUR, interval = 1*MINUTE )
    
    print "Temps apres : % s" %time.gmtime( time.time() )
    print "call to collect stats done"
    
    cs.printStats()        
        

if __name__ == "__main__":
    main()    