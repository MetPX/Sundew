"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
#######################################################################################
##
## Name   : DirectoryStatsCollector.py 
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


class DirectoryStatsCollector:
    """
        Contains all the methods needed to collect stats from a certain directory.
    """
    
    def __init__( self, directory = "", statsTypes = None, startTime = "2006-05-18 21:45:30",statsCollection = None ):
        """ 
            Constructor.
            builds a directoryFileCollector with no entries.   
        
        """
        
        self.dire             = directory                           #Name of the directory containing stats files.
        self.fileCollection   = DirectoryFileCollector( directory ) #List of all the test files. 
        self.statsCollection  = statsCollection or FileStatsCollector(startTime = startTime)#All fileStats collected. 
        self.statsTypes       = statsTypes or []                    #Types we'll search for stats. 
        
        
    
    def buildTodaysFileName(  clientName = "", offset = 0 ):
        """ 
            Builds a filename using current time
            The format will be 2006-10-31-19-15-53.txt
            Meaning October 31st 2006 at 19:15:53
            
            offset can be used to find a file from a day close to the current one 
        
        """    
        
        print "offset : %s" %offset
        fileName = str( os.getcwd() )
        fileName = fileName +  "/" + clientName +"-PICKLE-"
        
        tempTime = time.time() 
        
        tempTime = tempTime + (offset*24*60*60)
        
        
        for i in range(3):
            
            if i == 1 and int(i) < 10:
                fileName = fileName + "0" + str( time.gmtime( tempTime )[i] )
            else:
                fileName = fileName + str( time.gmtime( tempTime )[i] )
                
            if i != 2: 
                fileName = fileName + "-" 
        
        
        print "todaysfilename:%s" %fileName
        
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



    def collectStats( self, types, startTime = '2006-05-18 00:00:00', width=DAY, interval = 60*MINUTE, pickle = "todaysPickle", save = True ):
        """
            This method collects the stats for all the files found in the directory. 
        """
        
            
        self.fileCollection.collectEntries()          #find all entries from the folder
        
        try:
                    
            self.statsCollection = gzippickle.load( pickle )            
            
            #update fields who need to be updated
            #we dont allow someone to change interval during the day so we dont even look it up 
            self.statsCollection.startTime = MyDateLib.getSecondsSinceEpoch( startTime )
            self.statsCollection.width = width 
            
            #if any files were added since last time we add'em to the dictionary.
            for currentFile in self.fileCollection.entries.keys() :
                if currentFile not in self.statsCollection.files.keys():
                    self.statsCollection.fileEntries.append( (currentFile, [0, 0] ) )
            
            
            self.statsCollection.collectStats( )           
        
        except: # create new statscollection for the day 
            print"pas trouver le %s!?" %pickle
            self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, statsTypes = types, startTime = startTime, width = width, interval = interval, totalWidth = 24*HOUR )
            self.statsCollection.collectStats(  )         
         
        
        if save == True :
            print "Temps avant save : % s" %time.gmtime( time.time() )
            gzippickle.save ( object = self.statsCollection, filename = pickle ) 
            print "Temps apres save: % s" %time.gmtime( time.time() )
    
    
    
    def collectStatsWithoutPickling( self, types, startTime = '2006-05-18 00:00:00', width=DAY, interval = 60*MINUTE, totalWidth = 24*HOUR  ):
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
     
        print "\n\nFiles used : %s" %self.fileCollection.entries
        print "Starting date: %s" % MyDateLib.getOriginalDate(self.statsCollection.startTime)
                                    
        print "Interval: %s" %self.statsCollection.interval
        print "Time Width: %s" %self.statsCollection.width

        for j in range( self.statsCollection.nbEntries ):
            print "\nEntry's interval : %s - %s " %( MyDateLib.getOriginalDate(self.statsCollection.fileEntries[j].startTime), MyDateLib.getOriginalDate(self.statsCollection.fileEntries[j].endTime ) )
            print "Values :"
            print self.statsCollection.fileEntries[j].values.matrix
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
    

    
    def createLogFile( name = "log" ):
        """
            Creates a huge log file : 4 entries per seconds 24 hours file 345 600 lines....
            takes about 90 sec and weights ~15 megs
        
        """
        
         
        arrival   = "2006-06-16 00:00:00"
        departure = "2006-06-16 00:00:01"
        
        byteCount = 0
        
        file = open( name, "w")
        old_stdout = sys.stdout 
        sys.stdout = file 
        
        
        for i in range( 345600 ):
            
            byteCount = i
            
            departure = MyDateLib.getOriginalDate( MyDateLib.getSecondsSinceEpoch( arrival ) + randint( 1,30) )
            
            if i%4 == 1:
                arrival = MyDateLib.getOriginalDate( MyDateLib.getSecondsSinceEpoch( arrival ) + 1 )
            
            print "%s;%s;%s" %( arrival, departure, byteCount ) 
        
                  
        file.close()                 
        sys.stdout = old_stdout #resets standard output            

    createLogFile = staticmethod( createLogFile )



    def testCollectStats( self, types, startTime = '2006-05-18 00:00:00', width=DAY, interval = 60*MINUTE , pickle = "todaysPickle", save = True ):
        
        """
            This method collects the stats for all the files found in the directory. 
        """
        
           
        self.fileCollection.collectEntries()          #find all entries from the folder
        
        try:
             
            self.statsCollection = gzippickle.load( pickle )
            #update fields who need to be updated
            #we dont allow someone to change interval during the day so we dont even look it up 
            self.statsCollection.startTime = MyDateLib.getSecondsSinceEpoch( startTime )
            self.statsCollection.width = width 
            
            # Test sequence to pretend like we are using the same file all the time like we'll
            # usually do
            
            lastFile =  self.statsCollection.files.keys() # should only be one file there.... 
           
            
            lastValues = self.statsCollection.files[ lastFile[0] ]
           
                
            lastValues = self.statsCollection.files[ lastFile[0] ]
            
            del self.statsCollection.files[ lastFile[0] ]
            
            
            newFiles = self.fileCollection.entries.keys()
            
            self.statsCollection.files = dict( [( newFiles[0], lastValues )] )
            
            self.statsCollection.collectStats( )           
            
            
        except: # create new statscollection from skratch 
            self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, statsTypes = types, startTime = startTime, width = width, interval = interval, totalWidth = 24*HOUR )
            
            self.statsCollection.collectStats(  )         

        if save == True :
            gzippickle.save ( object = self.statsCollection, filename = todaysFile )
  

def main():
    """
            small test case. Tests if everything works plus gives an idea on proper usage.
    """
        
    # creates a 4 entry per seconds 24 hours file 345 600 lines.... in 90 sec wich weights ~15 megs
    #DirectoryStatsCollector.createLogFile( "/apps/px/lib/stats/files/2006-06-16" )
    
    types = [ 'latency']
#     #'bytecount' 
#         
#     ds = DirectoryStatsCollector( directory = "/apps/px/lib/stats/files/" )
#     ds.fileCollection.collectEntries()
#     ds.collectStatsWithoutPickling( types, startTime = '2006-05-18 00:00:00', width = 60*MINUTE, interval = 1*MINUTE ,totalWidth = 24 * HOUR )
        
    # simulate a crontab call at every hour. We use different files at every call to simulate an 
    #expanding file over 24 hours 
    
    print "Temps avant : % s" %time.gmtime( time.time() )
    ds = DirectoryStatsCollector( directory = "/apps/px/lib/stats/files/" )
    #ds.fileCollection.collectEntries()
    ds.collectStats( types, startTime = '2006-06-16 00:00:00', width = 14*HOUR, interval = 1*MINUTE,pickle = "metpx-PICKLE-2006-06-16" )
    print "Temps apres : % s" %time.gmtime( time.time() )
    print "call 1 to collect stats done"
#     
    print "len(ds.statsCollection.fileEntries) %s" %len(ds.statsCollection.fileEntries)  
    #ds.printStats()        
#    return ds         

if __name__ == "__main__":
    main()    