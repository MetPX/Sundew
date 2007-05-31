"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


#######################################################################################
##
## Name   : FileStatsCollector.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006
##
## Goal   : This file contains all the usefull classes and methods needed to build stats  
##          regarding latencies text files.   
##          
##          For performance puposes, users of this class can get stats from as many
##          datatypes as desired. For exemple, if they choose ['latency','bytecount'] 
##          all the entries will have the following values
##          means = [latencyMean, bytecountMean ]
##          max   = [maxLatency, max bytecount ] etc...  
##          
##          
#######################################################################################
"""

import os, sys

"""
    Small function that adds pxlib to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    Logger requires pxlib 
"""
import commands, logging, time, sys, os, pickle, datetime, fnmatch #important files 

from fnmatch import  fnmatch
from Logger  import *

from pxStats.lib.CpickleWrapper import CpickleWrapper
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsPaths import StatsPaths 
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods


LOCAL_MACHINE = os.uname()[1]


MINUTE = 60
HOUR   = 60 * MINUTE
DAY    = 24 * HOUR


class _ValuesDictionary:
    """
        This class is usefull to store all the values collected. 
    
    """
    
    def __init__( self, columns =0, rows=0 ):
        """ 
           Constructor.
           By default builds a 0*0 dictionary.
           dictionary is always empty, values need to be added after creation.  
        
        """
        self.columns      = columns  # Number of columns of the dictionary 
        self.rows         = rows     # Number of rows,interesting or not,that were collected.
        self.dictionary   = {}       # Contains value for each data type collected.
        self.productTypes = []       # For each line read, we save up what product type it was   


        
class _FileStatsEntry:
    """
        This class is used to contain all the info on a particular file entry.     
    
    """
    
    def __init__( self, values = _ValuesDictionary() , means = None , medians = None, totals = None, minimums =None, maximums = None, startTime = 0, endTime = 0 ):
        
        
        self.startTime = startTime       # Start time of the entry.
        self.endTime   = endTime         # End time of the entry.                  
        self.values    = values          # List of values from all the types. 
        self.minimums  = minimums or {}  # List of the minimums of all types.
        self.nbFiles   = 0               # Number of interesting files dealt with during this entry.
        self.filesWhereMinOccured =  {}  # Dict of files where min appened for each type  
        self.timesWhereMinOccured =  {}  # Dict of times where min appened for each type 
        self.maximums  = maximums or {}  # Maximum of all types.   
        self.filesWhereMaxOccured =  {}  # Dict of files where max appened for each type
        self.timesWhereMaxOccured =  {}  # Dict of times where max appened for each type 
        self.filesOverMaxLatency  =  0   # Number of interesting files per entry whos latency are too long.  
        self.means     = means    or {}  # Means for all the values of all the files.
        self.medians   = medians  or {}  # Medians for all the values of all the files.
        self.totals    = totals   or {}  # Total for all values of each files.                
        self.files     = []              # Files to be read for data collection. 
        self.times     = []              # Time of departure of an entry 
        
        
                                         
                                            

class FileStatsCollector:
    """
       This class contains the date structure and the functions needed to collect stats from 
       a certain file.
    
    """
    
    def __init__( self, files = None, fileType = "tx", statsTypes = [ "latency", "errors","bytecount" ], startTime = '2005-08-30 20:06:59', endTime = '2005-08-30 20:06:59', interval=1*MINUTE, totalWidth = HOUR, firstFilledEntry = 0, lastFilledEntry = 0, maxLatency = 15, fileEntries = None, logger = None ):
        """ 
            Constructor. All values can be set from the constructor by the user but recommend usage
            is to set sourceFile and statsType. The class contains other methods to set the other values
            properly.  
            
            constructor receives date in an iso format wich is conveniant for users but transforms it in a seconds since epoch format for ease of use during the program.   
            
            Precondition : Interval should be smaller than width !
        
        """    

        if fileEntries == None :
            fileEntries = []    
        
        
        self.files            = files or []               # Source files we will use. 
        self.fileType         = fileType                  # Type of files. tx or rx.  
        self.statsTypes       = statsTypes or []          # List of types we need to manage.
        self.fileEntries      = fileEntries               # list of all entries wich are parsed using time seperators.
        self.startTime        = startTime                 # Beginning of the timespan used to collect stats.
        self.endTime          = endTime                   # End of saidtimespan.
        self.interval         = interval                  # Interval at wich we separate stats entries .
        self.totalWidth       = totalWidth                # used to build timesperators.
        self.maxLatency       = maxLatency                # Acceptable limit for a latency. 
        self.firstFilledEntry = firstFilledEntry          # Last entry for wich we calculated mean max etc....
        self.lastFilledEntry  = lastFilledEntry           # Last entry we filled with data. 
        self.loggerName       = 'fileStatsCollector'      # Name of the logger if none is specified.
        self.logger           = logger                    # Logger
        
        timeSeperators = [ startTime ]
        timeSeperators.extend( StatsDateLib.getSeparatorsWithStartTime( startTime, self.totalWidth, self.interval ) ) 
        self.timeSeperators = timeSeperators
        self.nbEntries        = len ( self.timeSeperators ) -1 # Nb of entries or "buckets" 
        
        if self.logger == None: # Enable logging
            self.logger = Logger( StatsPaths.STATSLOGGING + 'stats_' + self.loggerName + '.log.notb', 'INFO', 'TX' + self.loggerName, bytes = True  ) 
            self.logger = self.logger.getLogger()
            
        
        if fileEntries == []:            
            self.createEmptyEntries()   # Create all empty buckets right away    
        
            
        # sorting needs to be done to make sure first file we read is the oldest, thus makes sure
        # that if we seek the last read position we do it in the right file.           
        self.files.sort()                
        
        if len( self.files ) > 1 and files[0].endswith("log"):#.log file is always newest.
             
            firstItem     = self.files[ 0 ]
            remainingList = self.files[ 1: ]
            self.files    = remainingList
            self.files.append( firstItem )                            
            
            
             
               
    def isInterestingProduct( product = "", interestingProductTypes = ["All"] ):
        ''' 
        @param product: Product to verifry.
               
        @param interestingProductTypes: Array containing the list of valid product types to look for. 
                                        Product types can contain wildcard characters.
        
        '''
        
        isInterestingProduct = False
        #print "produt : %s   interested in : %s " %(product , interestingProductTypes )
        
        
        for productType in interestingProductTypes:
            
            if productType == "All":
                pattern = '*'
            else:    
                pattern = GeneralStatsLibraryMethods.buildPattern(productType)
            

            if fnmatch( product, pattern):
                isInterestingProduct = True
                break
            
                
        return isInterestingProduct   
        
        
    isInterestingProduct = staticmethod(isInterestingProduct)
    
    
    
    def setMinMaxMeanMedians( self, productTypes = ["All"], startingBucket = 0, finishingBucket = 0  ):
        """
            This method takes all the values set in the values dictionary, finds the minimum, maximum,
            mean and median for every types found and sets them in a dictionary.
            
            All values are set in the same method as to enhance performances slightly.
           
            Product type, starting bucket and finishing bucket parameters can be quite usefull
            to recalculate a days data for only selected products names.  
            
            Pre-condition : Values dictionary should have been built and filled prior to using this method.
        
        """
        
        total   = 0  # Total of the values of acertain field within an entry.
        mean    = 0  # Mean of a certain field within an entry.
        minimum = 0  # Minimum of a certain field within an entry.  
        maximum = 0  # Maximum of a certain field within an entry.
        median  = 0  # Median of a certain field within a entry.
        values  = [] # Used to sort value to find median. 
        files   = [] # Used to browse all files of an entry
        times   = [] # Used to browse all times of an entry 
        
        if finishingBucket == 0 :
            finishingBucket = -1
        
        if self.logger != None :    
            self.logger.debug( "Call to setMinMaxMeanMedians received." )
   
               
        for i in xrange( startingBucket , finishingBucket + 1 ): #for each entries we need to deal with 
                        
            self.fileEntries[i].medians  = {}
            self.fileEntries[i].minimums = {}
            self.fileEntries[i].maximums = {}
            self.fileEntries[i].nbFiles  = 0  
            self.fileEntries[i].filesOverMaxLatency = 0
            
            for aType in self.statsTypes :#for each datatype        
                
                self.fileEntries[i].minimums[aType] =  0.0    
                self.fileEntries[i].filesWhereMinOccured[aType] =  ""
                self.fileEntries[i].timesWhereMinOccured[aType]= 0 
                self.fileEntries[i].maximums[aType]= 0.0    
                self.fileEntries[i].filesWhereMaxOccured[aType] = "" 
                self.fileEntries[i].timesWhereMaxOccured[aType] = 0 
                
                values = []
                files  = []
                times  = []                        
                
                if self.fileEntries[i].values.rows != 0:
                    #set values for each bucket..... 
                    for row in xrange( 0, self.fileEntries[i].values.rows ) : # for each line in the entry 
                        
                        if FileStatsCollector.isInterestingProduct( self.fileEntries[i].values.productTypes[row], productTypes  ) == True :
                        
                            if aType == self.statsTypes[0] : #Lower number of file only if first time we check it.
                                self.fileEntries[i].nbFiles = self.fileEntries[i].nbFiles +1
                            
                            if aType == "latency":
                                if self.fileEntries[i].values.dictionary[aType][row] > self.maxLatency:  
                                    self.fileEntries[i].filesOverMaxLatency = self.fileEntries[i].filesOverMaxLatency + 1   
                                  
                            values.append(self.fileEntries[i].values.dictionary[aType][row] )#add to new array
                            files.append( self.fileEntries[i].files[row]  )
                            times.append( self.fileEntries[i].times[row]  )                     
                    
                    
                    if len( values ) != 0 :
                        minimum = values[0]
                        maximum = values[0]
                        
                        self.fileEntries[i].minimums[aType] = values[0]
                        self.fileEntries[i].filesWhereMinOccured[aType] = files[0]    
                        self.fileEntries[i].timesWhereMinOccured[aType] = times[0]
                        
                        self.fileEntries[i].maximums[aType]= values[0]
                        self.fileEntries[i].filesWhereMaxOccured[aType] = files[0]    
                        self.fileEntries[i].timesWhereMaxOccured[aType] = times[0]  
                                            
                    else:
                        minimum =0
                        maximum =0
                    
                        
                        
                    for k in xrange( len( values ) ) :
                        
                        if values[k] < minimum:
                            minimum = values[k]
                            self.fileEntries[i].minimums[aType] = values[k]
                            self.fileEntries[i].filesWhereMinOccured[aType] = files[k]    
                            self.fileEntries[i].timesWhereMinOccured[aType] = times[k]
                        
                        elif values[k] > maximum:
                            maximum = values[k]
                            self.fileEntries[i].maximums[aType]= values[k]
                            self.fileEntries[i].filesWhereMaxOccured[aType] = files[k]    
                            self.fileEntries[i].timesWhereMaxOccured[aType] = times[k]                      
                                        
                    
                    median  = 0 
                    
                    try :
                        total   = sum( values )
                    except :
                        total = 0
                        if self.logger != None :
                            self.logger.error("Could not compute sum in setMinMaxMeanMedians. Make sure values are numeric.")            
                        
                        
                    if len(values) != 0 :
                        mean    = float( float( total ) / float( len( values ) ) )                        
                    else:
                        mean = 0
                        
                        
                    if aType == "errors" :
                        if total > maximum :
                            maximum = total
                            self.fileEntries[i].maximums[aType] = total
                            self.fileEntries[i].filesWhereMaxOccured[aType] = files[k]    
                            self.fileEntries[i].timesWhereMaxOccured[aType] = times[k]
                            
                         
                else: #this entry has no values 
                    minimum = 0
                    median  = 0
                    maximum = 0
                    total   = 0
                    mean    = 0
                                  
                self.fileEntries[i].medians[aType]= median# appending values to a list   
                self.fileEntries[i].means[aType] = mean     
                self.fileEntries[i].totals[aType] =  float(total)
                                    
        self.lastEntryCalculated = self.lastFilledEntry
        
        return self
    
    
        
    def findValues( statsTypes, line = "", lineType = "[INFO]", fileType = "tx",logger = None ):
        """
            This method is used to find a particular entry within a line. 
            Used with line format used in tx_satnet.logxxxxxxxxxx
        
            To be modified once line format is decided upon. 
            
        """
       
        values = {} #in case of an unknown type
        
        splitLine = line.split( " " )
        
        if line != "" and line != "\n" :
            
            for statsType in statsTypes :   
                
                try:
                    if statsType == "departure" : #is at the same place for every lineType 
                        values[ statsType ] =  line.split( "," )[0]   
                        
                    
                    elif lineType == "[INFO]" :
                        
                        if statsType == "latency":
                                                            
                            d1 = line[:19]
                            d2 = splitLine[6].split(":")[6] 
    
                                    
                            values[statsType]= (datetime.datetime( int(d1[0:4]), int(d1[5:7]), int(d1[8:10]), int(d1[11:13]), int(d1[14:16]), int(d1[17:19])) - datetime.datetime( int(d2[0:4]),int(d2[4:6]),int(d2[6:8]),int(d2[8:10]),int(d2[10:12]),int(d2[12:14]) ) ).seconds                           
                            
                                    
                                
                        elif statsType == "arrival":                  
                        
                            arrival = StatsDateLib.isoDateDashed( splitLine[6].split( ":" )[6] )    
    
                                
                        elif statsType == "bytecount":
                            start = line.find( "(" )
                            end   = line.find( "Bytes" )  
                            start = start +1
                            end = end -1                           
                            
                            values[statsType] = int( line[start:end] )
                        
                            
                        elif statsType == "fileName":
                            
                            if fileType == "tx" :
                                values[statsType] = os.path.basename(splitLine[6])#.split( ":" )[0]
                            else:
                                split     = line.split( "/" )
                                lastPart  = split[ len( split ) -1 ]
                                values[ statsType ] = lastPart.split( ":" )[0] #in case something is added after line ends.
                            
                        elif statsType == "productType":
                            
                            if fileType == "tx":
                                values[statsType] = os.path.basename(splitLine[6])#.split( ":" )[0]
                            else: # rx has a very different format for product.
                                split     = line.split( "/" )
                                lastPart  = split[ len( split ) -1 ]
                                values[ statsType ] = lastPart.split( ":" )[0] #in case something is added after line ends.
                                
                        elif statsType == "errors" :
                            values[statsType] = 0  
                            
                        
                    elif lineType == "[ERROR]":
                    
                        if statsType == "errors" :
                            values[statsType] = 1                   
            
                        
                        elif statsType == "productType" :     
                            values[statsType] = ""
                        else:
                            values[statsType] = 0
                        
                        #elif lineType == "[OTHER]" :               
                except:                
                    
                    if logger != None :
                        logger.error("could not find %s value in line %s." %( statstype,line ) ) 
                        logger.error("value was replaced by 0.")
                    
                    values[statstype] = 0    
                    pass
        
        else:
            for type in statsTypes :
                values[type] = 0
        
        return values

    
    
    findValues = staticmethod( findValues )
    
    
    
        
    def isInterestingLine( line, usage = "stats", types = None ):
        """ 
            This method returns whether or not the line is interesting 
            according to the types asked for in parameters. 
            
            Also returns for what type it's interesting.   
            
            To be modified when new log file format comes in.   
        
        """
        
        lineType = ""
        isInteresting = False 
        
        if types == None :
            types = [] 
        
        if line != "" :
            
            if "errors" in types and line.find("[ERROR]") != -1:
                isInteresting = True
                lineType = "[ERROR]" 
            
            elif line.find("[INFO]") != -1 and line.find("Bytes") != -1 and line.find("/sec") == -1  and line.find(" Segment ") == -1 and line.find("SEND TIMEOUT") == -1 : 
                isInteresting = True             
                lineType = "[INFO]"          
              
                          
            elif usage != "stats" and ( line.find("[WARNING]") != -1 or line.find("[INFO]") != -1 or line.find("[ERROR]") != -1 ) :
                isInteresting = True 
                lineType = "[OTHER]"


#this line is useless. Previous elif covers this case                         
#             elif usage != "stats" and ( "[INFO]" in line and "SEND TIMEOUT" in line ):
#                 isInteresting = True 
#                 lineType = "[OTHER]"  
                    
                
        return isInteresting,lineType
    
    isInterestingLine = staticmethod( isInterestingLine )
    
    
    
    def findFirstInterestingLine( self, fileHandle, fileSize ):
        """
            Finds the first interesting line in a file.
            
            If files were previously read, stops if we find
            the last line we read the other time.
            
            Otherwise, we stop at the first interesting line within the range
            of the data we want to collect.
        
        """       
              
        line                 = ""
        lineType             = None 
        backupLine           = ""
        lineFound            = False 
        startTimeinSec       = 0

        
        if self.logger != None :
            self.logger.debug( "Call to findFirstInterestingLine received." )
        
        firstLine      = fileHandle.readline()
        position       = fileHandle.tell()
        
        #In case of traceback line
        isInteresting, linetype = FileStatsCollector.isInterestingLine( firstLine, usage = "departure", types = self.statsTypes ) 
        while isInteresting == False and firstLine != "" :  
            firstLine = fileHandle.readline()
            position  = fileHandle.tell()
            isInteresting, linetype = FileStatsCollector.isInterestingLine( firstLine, usage = "departure", types = self.statsTypes )               
            #print firstLine    
                                                 
        fileHandle.seek( position, 0 )
        line = firstLine 
        
        #print "before last while : %s" %line 
   
        while lineFound == False and line != "":     
            #print "enters last while "
            isInteresting, lineType = FileStatsCollector.isInterestingLine( line,types = self.statsTypes )
            
            if isInteresting  : #were still can keep on reading range 
                #print "***Usefull line : %s " %line
                
                departure =  FileStatsCollector.findValues( ["departure"] , line, fileType = self.fileType,logger= self.logger )["departure"]
                
                if departure <=  self.endTime and departure >= self.startTime :
                    position = fileHandle.tell()
                    lineFound = True                                                                       
                                    
                elif departure >  self.endTime:# there was no interesting data in that file                    
                    lineFound = True   
                
                else:
                    line = fileHandle.readline ()
                    
            else:#keep on readin 
                #print "useless line : %s" %(line)
                #print "self.statstypes : %s" %(self.statsTypes)
                line = fileHandle.readline()        
                
        #print "*****************%s****************" %line     

        return line, lineType, position 



    def setValues( self, endTime = "" ):
        """
            This method opens a file and sets all the values found in the file in the appropriate entry's value dictionary.
            -Values searched depend on the datatypes asked for by the user.
            -Number of entries is based on the time separators wich are found with the startTime, width and interval.  -Only entries with arrival time comprised between startTime and startTime + width will be saved in dicts
            -Entries wich have no values will have 0 as value for means, minimum maximum and median     
        
            -Precondition : stats type specified in self must be valid.         
              
        """
        #print "setValues"
        line                  = ""                 
        filledAnEntry         = False
        previousPosition      = 0        
        baseTypes             = [ "fileName", "productType" ]
        neededTypes           = baseTypes        
        self.firstFilledEntry = 0 # resets values 
        self.lastFilledEntry  = 0
        
        if self.logger != None :        
            self.logger.debug( "Call to setValues received."  )
           
        
        for statType in self.statsTypes :    
            neededTypes.append(statType)
        
        if endTime == "" :                                        
            endTime = self.endTime
        else:
            endTime = endTime 
    
        
        #print self.files
        for file in self.files :#read everyfile and append data found to dictionaries
                                  
            nbErrors      = 0 
            entryCount    = 0
            
            fileHandle = open( file, "r" )
            fileSize = os.stat(file)[6]
            
            line, lineType, position  = self.findFirstInterestingLine( fileHandle, fileSize )
            #print "endTime : %s" %endTime  
            #print "line returned : %s" %line
            #print "coming from file named : %s" %file

           
            if line != "" :                                        
                fileHandle.seek( position )
                departure   = self.findValues( ["departure"] ,  line, lineType, fileType = self.fileType,logger= self.logger )["departure"]
            
            
            while line  != "" and str(departure)[:-2] < str(endTime)[:-2]: #while in proper range 
                                
                while departure[:-2] > self.timeSeperators[ entryCount ][:-2]:#find appropriate bucket
                    entryCount = entryCount + 1                         
                    
                neededValues = self.findValues( neededTypes, line, lineType,fileType = self.fileType,logger= self.logger )    
                
                #print "neededValues : %s" %neededValues
                #print 
                #add values general to the line we are treating 
                self.fileEntries[ entryCount ].files.append( neededValues[ "fileName" ] )
                self.fileEntries[ entryCount ].times.append( departure )
                self.fileEntries[ entryCount ].values.productTypes.append( neededValues[ "productType" ] )
                self.fileEntries[ entryCount ].values.rows = self.fileEntries[ entryCount ].values.rows + 1
                
                
                if filledAnEntry == False :#in case of numerous files
                    self.firstFilledEntry = entryCount 
                    filledAnEntry = True 
                elif entryCount < self.firstFilledEntry:
                    self.firstFilledEntry = entryCount    
                
                for statType in self.statsTypes : #append values for each specific data type needed  
                    
                    
                    if statType == "latency":
                    
                        if neededValues[ statType ] > self.maxLatency :      
                            self.fileEntries[ entryCount ].filesOverMaxLatency = self.fileEntries[entryCount ].filesOverMaxLatency + 1                          
            
                    self.fileEntries[ entryCount ].values.dictionary[statType].append( neededValues[ statType ] )
                    #print self.fileEntries[ entryCount ].values.dictionary                             
                
                if lineType != "[ERROR]" :
                    self.fileEntries[ entryCount ].nbFiles = self.fileEntries[ entryCount ].nbFiles + 1        
                 
                #Find next interesting line     
                line    = fileHandle.readline()
                isInteresting,lineType = FileStatsCollector.isInterestingLine( line, types = self.statsTypes )
                
                while isInteresting == False and line != "":
                    previousPosition = fileHandle.tell() #save it or else we might loose a line.    
                    line = fileHandle.readline()# we read again 
                    isInteresting,lineType = FileStatsCollector.isInterestingLine( line, types = self.statsTypes )
                
                
                departure   = self.findValues( ["departure"] , line, lineType, fileType = self.fileType,logger= self.logger )["departure"]               
                
                
            if line == "" :
                #print "read the entire file allready"
                if entryCount > self.lastFilledEntry:#in case of numerous files
                    self.lastFilledEntry  = entryCount                  
                previousPosition      = 0
                
            else:
                if entryCount > self.lastFilledEntry :#in case of numerous files
                    self.lastFilledEntry  = entryCount                  
                
           
            fileHandle.close()             
                
    
    
            
    def createEmptyEntries( self ):    
        """
            We fill up fileEntries with empty entries with proper time labels 
        
        """
        
        if self.logger != None :
            self.logger.debug( "Call to createEmptyEntries received." )
        
        if len ( self.timeSeperators ) > 1 : 
    
            for i in xrange(0, len ( self.timeSeperators )-1 ):
                self.fileEntries.append( _FileStatsEntry() )       
                self.fileEntries[i].startTime =  self.timeSeperators[ i ] 
                self.fileEntries[i].endTime   =  self.timeSeperators[ i+1 ]  
                self.fileEntries[i].values    = _ValuesDictionary( len( self.statsTypes ), 0 )
                
                for statType in self.statsTypes:
                    self.fileEntries[i].values.dictionary[statType] = []



    def collectStats( self, endTime = "" ):
        """
            This is the main method to use with a FileStatsCollector. 
            It will collect the values from the file and set them in a dictionary.
            It will use that dictionary to find the totals and means of each data types wanted. 
            It will also use that dictionary to find the minimum max andmedians of 
            each data types wanted. 
               
        """
            
        self.setValues( endTime )   #fill dictionary with values
        self.setMinMaxMeanMedians( startingBucket = self.firstFilledEntry, finishingBucket = self.lastFilledEntry  )  
                     
             

                         

if __name__ == "__main__":
    """
        small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    types = [ "latency", "errors","bytecount" ]
    
    filename = StatsPaths.PXLOG + 'tx_amis.log'
    
    startingHours=["00:00:00","01:00:00","02:00:00","03:00:00","04:00:00","05:00:00","06:00:00","07:00:00","08:00:00","09:00:00","10:00:00","11:00:00","12:00:00","13:00:00","14:00:00","15:00:00","16:00:00","17:00:00","18:00:00","19:00:00","20:00:00","21:00:00","22:00:00","23:00:00" ]
    
    endingHours = ['00:59:00', '01:59:00', '02:59:00', '03:59:00', '04:59:00', '05:59:00', '06:59:00', '07:59:00', '08:59:00', '09:59:00', '10:59:00', '11:59:00', '12:59:00', '13:59:00', '14:59:00', '15:59:00', '16:59:00', '17:59:00', '18:59:00', '19:59:00', '20:59:00', '21:59:00', '22:59:00', '23:59:00' ]
     
     
    for i in xrange(1, 8) : #len(startingHours)
              
        stats = FileStatsCollector( files = [ filename ], statsTypes = types , startTime = '2006-08-01 %s' %startingHours[i], endTime = '2006-08-01 %s' %endingHours[i], interval = 1*MINUTE  )
        stats.collectStats()
        saveFile = StatsPaths.STATSDATA + "test/%s" %startingHours[i]
        del stats.logger
        CpickleWrapper.save( object = stats, filename = saveFile )
       

     
