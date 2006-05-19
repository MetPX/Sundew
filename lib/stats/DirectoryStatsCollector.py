#######################################################################################
##
## Name   : DirectoryStatsCollector.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006
##
## Goal   : This file is used to collect stats from all the files from a directory.
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
import DirectoryFileCollector
import FileStatsCollector
from DirectoryFileCollector import *
from FileStatsCollector import *



class DirectoryStatsCollector:
    """
        Contains all the methods needed to collect 
    """
    
    def __init__( self, directory = "", statsTypes = []  ):
        """ Constructor.
            builds a directoryFileCollector with no entries.   
        """
        self.dire             = directory                           #Name of the directory containing stats files.
        self.fileCollection   = DirectoryFileCollector( directory ) #List of all the test files. 
        self.statsCollection  = []                                  #List of all the fileStats collected,1 per file. 
        
        
        
        
    def collectStats(self, types, startTime = 0, width=DAY, interval=60*MINUTE ):
        """
            This method collects the stats for all the files found in the directory. 
        """
        self.fileCollection.collectEntries()  #find all entries from the folder
        
        for i in range( len( self.fileCollection.entries ) ): # for everyfiles
            self.statsCollection.append( FileStatsCollector( sourceFile = ( str(self.dire) + str(self.fileCollection.entries[i] ) ), statsTypes = types, startTime = startTime, width = width, interval = interval ) )
            
            self.statsCollection[i].collectStats()
    
            
            
    def printStats(self) :       
        """
            This method prints out all the stats concerning each files. 
            Mostly usefull for debugging. 
        """    
        for i in range( len( self.statsCollection ) ):
            print "Nom fichier : %s" %self.fileCollection.entries[i]
            
            for j in range(  self.statsCollection[i].nbEntries +1 ):
                print "Entry #%s " %j
                print "Values :"
                print self.statsCollection[i].fileEntries[j].values.matrix
                print "Means :"
                print self.statsCollection[i].fileEntries[j].means
                print "Medians"    
                print self.statsCollection[i].fileEntries[j].medians
                print "Minimums"
                print self.statsCollection[i].fileEntries[j].minimums
                print "Maximums"
                print self.statsCollection[i].fileEntries[j].maximums
            
            
if __name__ == "__main__":
    """small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    types = [ 'latency', 'bytecount']
    ds = DirectoryStatsCollector( directory = "/users/dor/aspy/lem/metpx/sundew/lib/stats/files/" )
    ds.fileCollection.collectEntries
    ds.collectStats( types, startTime = '2006-05-17 13:00:00', width = 7*24*HOUR, interval = 24*HOUR )
    ds.printStats()        
            