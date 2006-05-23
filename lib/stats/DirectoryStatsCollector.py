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
import os 
import DirectoryFileCollector
import FileStatsCollector
from   DirectoryFileCollector import *
from   FileStatsCollector     import *



class DirectoryStatsCollector:
    """
        Contains all the methods needed to collect 
    """
    
    def __init__( self, directory = "", statsTypes = None  ):
        """ Constructor.
            builds a directoryFileCollector with no entries.   
        """
        
        self.dire             = directory                           #Name of the directory containing stats files.
        self.fileCollection   = DirectoryFileCollector( directory ) #List of all the test files. 
        self.statsCollection  = []                                  #List of all the fileStats collected,1 per file. 
        self.statsTypes       = statsTypes or []                    #Types we'll search for stats. 
        
        
        
    def collectStats( self, types, startTime = 0, width=DAY, interval = 60*MINUTE  ):
        """
            This method collects the stats for all the files found in the directory. 
        """
        
        self.fileCollection.collectEntries()          #find all entries from the folder
        
        self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, statsTypes = types, startTime = startTime, width = width, interval = interval )
                    
        self.statsCollection.collectStats()           #collect stats from ALL files 
            
            
    def printStats( self ) :       
        """
            This method prints out all the stats concerning each files. 
            Mostly usefull for debugging. 
        """    
     
        print "\n\nFiles used : %s\n" %self.fileCollection.entries
        
        
        for j in range( self.statsCollection.nbEntries ):
            print "\nEntry's interval : %s - %s " %( self.statsCollection.fileEntries[j].startTime,self.statsCollection.fileEntries[j].endTime )
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
    
            
                    
if __name__ == "__main__":
    """small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    types = [ 'latency', 'bytecount' ]
    ds = DirectoryStatsCollector( directory = "/users/dor/aspy/lem/metpx/sundew/lib/stats/files/" )
    ds.fileCollection.collectEntries
    ds.collectStats( types, startTime = '2006-05-18 00:00:00', width = 24*HOUR, interval = 2*HOUR )
    ds.printStats()        
            