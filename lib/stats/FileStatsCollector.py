"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

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



import array,time,sys,os,pickle,datetime #important files 
import copy
from   array     import *
import MyDateLib
from   MyDateLib import *
import commands
import copy 
import backwardReader
import cpickleWrapper
import logging 
import PXPaths
from   Logger                 import *

PXPaths.normalPaths()


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
    
    def __init__( self, files = None, statsTypes = [ "latency", "errors","bytecount" ], startTime = '2005-08-30 20:06:59', endTime = '2005-08-30 20:06:59', interval=1*MINUTE, totalWidth = HOUR, firstFilledEntry = 0, lastFilledEntry = 0, lastReadPosition = 0, maxLatency = 15, fileEntries = None, logger = None ):
        """ 
            Constructor. All values can be set from the constructor by the user but recommend usage
            is to set sourceFile and statsType. The class contains other methods to set the other values
            properly.  
            
            constructor receives date in an iso format wich is conveniant for users but transforms is in a seconds since epoch format for ease of use during the program.   
            
            Precondition : Interval should be smaller than width !
        
        """    

        if fileEntries == None :
            fileEntries = []    
        
        
        self.files            = files or []               # Source files we will use. 
        self.statsTypes       = statsTypes or []          # List of types we need to manage.
        self.fileEntries      = copy.deepcopy(fileEntries)# list of all entries wich are parsed using time seperators.
        self.startTime        = startTime                 # Beginning of the timespan used to collect stats.
        self.endTime          = endTime                   # End of saidtimespan.
        self.interval         = interval                  # Interval at wich we separate stats entries .
        self.totalWidth       = totalWidth                # used to build timesperators.
        self.maxLatency       = maxLatency                # Acceptable limit for a latency. 
        self.firstFilledEntry = firstFilledEntry          # Last entry for wich we calculated mean max etc....
        self.lastFilledEntry  = lastFilledEntry           # Last entry we filled with data. 
        self.lastReadPosition = lastReadPosition          # Last line filled in this stats collection.
        self.loggerName       = 'fileStatsCollector'      #
        self.logger           = logger                    #
        
        timeSeperators = [ startTime ]
        timeSeperators.extend( MyDateLib.getSeparatorsWithStartTime( startTime, self.totalWidth, self.interval ) ) 
        self.timeSeperators = timeSeperators
        self.nbEntries        = len ( self.timeSeperators ) -1 # Nb of entries or "buckets" 
        
        if self.logger == None: # Enable logging
           
            self.logger = Logger( PXPaths.LOG + 'stats_' + self.loggerName + '.log.notb', 'DEBUG', 'TX' + self.loggerName ) 
            self.logger = self.logger.getLogger()
            
        
        if fileEntries == []:
            self.createEmptyEntries()   # Create all empty buckets right away    
        
        # sortingneeds to be done to make sure first file we read is the oldest,thus makes sure
        # that if we seek the last read position we do it in the right file. 
           
        self.files.sort()                
        
        if len( self.files ) > 1 and files[0].endswith("log"):
            print 
            firstItem     = self.files[ 0 ]
            print "firstItem : %s" %firstItem
            remainingList = self.files[ 1: ]
            print "remainingList : %s" %remainingList
            self.files    = remainingList
            self.files.append( firstItem )                            
            print "self.files has been modified to %s." %self.files

            
            
    def setMinMaxMeanMedians( self, productType = "", startingBucket = 0 , finishingBucket = 0  ):
        """
            This method takes all the values set in the values dictionary, finds the media for every
            types found and sets them in a list of medians. This means if statsTypes = [latency, bytecount]
            we will store the medians in the same order :[ latencyMedian, bytecountMedian ] 
            
            All values are set in the same method as to enhance performances slightly.
           
            Product type starting bucket and finishing bucket can be quite usefull to recalculate a days data 
            for only selected products names.  
            
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
        
        if startingBucket != 0 :
            self.firstFilledEntry  = startingBucket
        if finishingBucket !=0 : 
            self.lastFilledEntry = finishingBucket -1
        
        if self.logger != None :    
            self.logger.debug( "Call to setMinMaxMeanMedians received." )
            self.logger.debug( "ProductType : %s, firstFilledEntry : %s, lastFilledEntry : %s  ." %( productType, self.firstFilledEntry, self.lastFilledEntry ) )     
                   
        for i in xrange( self.firstFilledEntry , self.lastFilledEntry + 1 ): #for each entries we need to deal with 
            
            
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
                        
                        if productType in self.fileEntries[i].values.productTypes[row] :
                        
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
                        mean    = float( total / len(values) )
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
                    
                self.fileEntries[i].medians[aType]= median     # appending values to a list   
                self.fileEntries[i].means[aType] = mean
                #if aType  == "latency":
                    #print "latency mean : %s" %mean
      
                self.fileEntries[i].totals[aType] =  float(total)
                

                    
        self.lastEntryCalculated = self.lastFilledEntry
        
        return self
    
    
        
    def findValues( statsTypes, line = "", lineType = "[INFO]" ):
        """
            This method is used to find a particular entry within a line. 
            Used with line format used in tx_satnet.logxxxxxxxxxx
        
            To be modified once line format is decided upon. 
            
        """
        
        values = {} #in case of an unknown type
        
        splitLine = line.split( " " )
        
        if line != "" and line != "\n" :
            
            for statsType in statsTypes :   
                #print statsType 
                if statsType == "departure" :
                    values[statsType] =  line.split( ",")[0]   
                    
                
                elif lineType == "[INFO]" :
                    
                    if statsType == "latency":
                        
                        d1 = line[:19]
                        d2 = splitLine[6].split(":")[6] 
                        values[statsType]=(datetime.datetime( int(d1[0:4]), int(d1[5:7]), int(d1[8:10]), int(d1[11:13]), int(d1[14:16]), int(d1[17:19])) -datetime.datetime( int(d2[0:4]),int(d2[4:6]),int(d2[6:8]),int(d2[8:10]),int(d2[10:12]),int(d2[12:14]) ) ).seconds
                        
                            
                    elif statsType == "arrival":                  
                    
                        arrival   = MyDateLib.isoDateDashed( splitLine[6].split(":")[6] )    

                            
                    elif statsType == "bytecount":
                        values[statsType] = int( splitLine[3].replace( '(', '' ) )
                       
                    elif statsType == "fileName":
                        values[statsType] = splitLine[6].split( ":" )[0]
                    
                    elif statsType == "productType":
                        values[statsType] = splitLine[6].split(":")[0]
                        
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
        else:
            for type in statsTypes :
                values[type] = 0
        
        return values

    
    
    findValues = staticmethod( findValues )
    
    
    
        
    def isInterestingLine( self, line ):
        """
            This method returns whether or not the line is interesting 
            according to the types ask for in parameters. 
            
            Also returns for what type it's interesting.   
            
            To be modified when new log file format comes in.   
        
        """
        
        lineType = ""
        isInteresting = False 
        
        
        if line != "" :
            
            if "errors" in self.statsTypes and "[ERROR]" in line:
                isInteresting = True
                lineType = "[ERROR]" 
            
            elif "[INFO]" in line and "Bytes" in line and "/sec" not in line and " Segment " not in line : 
                isInteresting = True             
                lineType = "[INFO]"
                
        return isInteresting,lineType
    
    
    
    def findFirstInterestingLine( self, fileHandle, fileSize ):
        """
            Finds the first interesting line in a file.
            
            If files were previously read, stops if we find
            the last line we read the other time.
            
            Otherwise, we stop at the first interesting line within the range
            of the data we want to collect.
        
        """
        
        line = ""
        backupLine = ""
        lineFound = False 
        firstDeparture = 0
        lastDeparture  = 0 
        firstDepartureInSecs = 0
        startTimeinSec       = 0
        lastDepartureInSecs  = 0
        
        if self.logger != None :
            self.logger.debug( "Call to findFirstInterestingLine received." )
            self.logger.debug( "Parameters were self.lastReadPosition : %s, filesize : %s" %( self.lastReadPosition, fileSize )) 
        
        
        if self.lastReadPosition != 0:
            
            fileHandle.seek( self.lastReadPosition, 0 )
            firstLine = fileHandle.readline()
            position = fileHandle.tell()
        
        else:
            
            firstLine      = fileHandle.readline()
            position       = fileHandle.tell()
            firstDeparture = FileStatsCollector.findValues( ["departure"] , firstLine )["departure"]
            
            lastLine,offset  = backwardReader.readLineBackwards( fileHandle, offset = -1, fileSize = fileSize  )
            lastDeparture    = FileStatsCollector.findValues( ["departure"] , lastLine )["departure"]
            
            firstDepartureInSecs = MyDateLib.getSecondsSinceEpoch( firstDeparture )
            startTimeinSec       = MyDateLib.getSecondsSinceEpoch( self.startTime )
            lastDepartureInSecs  = MyDateLib.getSecondsSinceEpoch( lastDeparture )
      
        print "self.lastReadPosition : %s" %self.lastReadPosition
        if self.lastReadPosition != 0 or abs( firstDepartureInSecs - startTimeinSec ) < 2*(abs( lastDepartureInSecs - startTimeinSec)) :
            
            fileHandle.seek( position,0 )
            line = firstLine 
               
            while lineFound == False :     
                
                departure =  FileStatsCollector.findValues( ["departure"] , line )["departure"]
                if departure >= self.startTime and departure <=  self.endTime :
                    isInteresting, lineType = self.isInterestingLine( line )
                    
                    if isInteresting == True :
                        position = fileHandle.tell()
                        lineFound = True 
                   
                if lineFound == False :
                    line = fileHandle.readline ()        
                        
        else:#read backwards till we are in the range we want 
            #might want to log here....
            fileHandle.seek(0,0)
            print "goes backwards!?"
            line = lastLine 
            departure = lastDeparture
            
            while line != "" and departure >= self.startTime :
                line,offset = backwardReader.readLineBackwards( fileHandle = fileHandle, offset = offset , fileSize = fileSize )
                
                if line != "":
                    departure =  FileStatsCollector.findValues( ["departure"] , line )["departure"]
                if departure > self.startTime:#save line ,or else well lose it at last turn
                    backupLine = line             
            
            if backupLine != "" :        
                line = backupLine      
                isInteresting,lineType = self.isInterestingLine( line ) #go back the other way and find first of the good type 
                while isInteresting == False  :
                    line = fileHandle.readline()
                    isInteresting,lineType = self.isInterestingLine( line )     
                    position = fileHandle.tell()
                    
                        
       
        print "####line : %s" %line  
        
        return line, lineType, position 



    def setValues( self, endTime = "" ):
        """
            This method opens a file and sets all the values found in the file in the appropriate entry's value dictionary.
            -Values searched depend on the datatypes asked for by the user.
            -Number of entries is based on the time separators wich are found with the startTime, width and interval.  -Only entries with arrival time comprised between startTime and startTime + width will be saved in dicts
            -Entries wich have no values will have 0 as value for means, minimum maximum and median     
        
            -Precondition : stats type specified in self must be valid. 
        
            - performance bottleneck...needs to be optimized badly.   
        """
        
             
        try:
                
            filledAnEntry         = False
            self.firstFilledEntry = 0
            self.lastFilledEntry  = 0
            baseTypes             = [ "fileName", "productType" ]
            neededTypes           = baseTypes 
            
            if self.logger != None :        
                self.logger.debug( "Call to setValues received."  )
                self.logger.debug( "Parameters were self.lastReadPosition : %s, endTime : %s" %(self.lastReadPosition,endTime)) 
                
            
            for statType in self.statsTypes :    
                neededTypes.append(statType)
            
            if endTime == "" :                                        
                endTime = self.endTime
            else:
                endTime = endTime 
        
            print "self.files : %s" %self.files
    
            for file in self.files :#read everyfile and append data found to dictionaries
                
                #print "currently used file : %s" %file              
                nbErrors      = 0 
                entryCount    = 0
                
                fileHandle = open( file, "r" )
                fileSize = os.stat(file)[6]
                line, lineType, position  = self.findFirstInterestingLine( fileHandle, fileSize )                                        
                fileHandle.seek( position )
                        
                departure   = self.findValues( ["departure"] ,  line, lineType )["departure"]
                
                
                while str(departure)[:-2] < str(endTime)[:-2] and line  != "" : #while in proper range 
                    
                    #print line 
                    while departure[:-2] > self.timeSeperators[ entryCount ][:-2]:#find appropriate bucket
                        entryCount = entryCount + 1                         
                        #print "entryCount : %sdeparture : %s,endTime :%s" %(entryCount,departure,endTime)
    
                    neededValues = self.findValues( neededTypes, line, lineType )    
                    
                    #add values general to the line we are treating 
                    self.fileEntries[ entryCount ].files.append( neededValues[ "fileName" ] )
                    self.fileEntries[ entryCount ].times.append( departure )
                    self.fileEntries[ entryCount ].values.productTypes.append( neededValues[ "productType" ] )
                    self.fileEntries[ entryCount ].values.rows = self.fileEntries[ entryCount ].values.rows + 1
                    
                    
                    if filledAnEntry == False :
                        self.firstFilledEntry = entryCount 
                        filledAnEntry = True 
                    elif entryCount < self.firstFilledEntry:
                        self.firstFilledEntry = entryCount    
                    
                    for statType in self.statsTypes : #append values for each specific data type needed  
                        
                        
                        if statType == "latency":
                        
                            if neededValues[ statType ] > self.maxLatency :      
                                self.fileEntries[ entryCount ].filesOverMaxLatency = self.fileEntries[entryCount ].filesOverMaxLatency + 1                          
                
                        self.fileEntries[ entryCount ].values.dictionary[statType].append( neededValues[ statType ] )
                    
                        
                    
                    
                    if lineType != "[ERROR]" :
                        self.fileEntries[ entryCount ].nbFiles = self.fileEntries[ entryCount ].nbFiles + 1        
    #                 
    #                 #Find next interesting line     
                    line    = fileHandle.readline()
                    isInteresting,lineType = self.isInterestingLine( line )
                    
                    while isInteresting == False and line != "":
                            
                        line = fileHandle.readline()# we read again 
                        isInteresting,lineType = self.isInterestingLine( line )
                    
                    
                    departure   = self.findValues( ["departure"] , line, lineType )["departure"]
                    
                    
                    #print "file : %s,entryCount :%s,self.lastFilledEntry :%s " %( file, entryCount, self.lastFilledEntry)
                    #if entryCount > self.lastFilledEntry : # in case of numerous files....
                    
                    if line != "" :
                        self.lastFilledEntry = entryCount                  
                        self.lastReadPosition= fileHandle.tell() 
                    else:
                        self.lastFilledEntry = entryCount                  
                        self.lastReadPosition= 0
                        print "found end of file "
                            
                if self.logger != None :        
                    self.logger.debug( "Last line read in setValues: %s" %line  )
                    self.logger.debug( "Departure of that line : %s endtime :%s " %( str(departure)[:-2], str(endTime)[:-2]) )  
                
                if line == "\n":       
                    print "last line read : %s" %line
                elif line == "":
                    print "youve found it "
                elif line.replace( " ","") == "":
                    print "you had to remove space"
                elif line.replace( " ","") =="\n":
                    print "you need to rmeove space then you get backslash n"            
                else:
                    print "line : %s" %line
                    print "you still need to find what that last line is !"    
                
                fileHandle.close()                 
              
        
        except:
            (type, value, tb) = sys.exc_info()
            self.logger.error( "Unexpected exception in FileStatsCollector.setValues." ) 
            self.logger.error( (type, value, tb) ) 
            self.logger.debug( "Line being read was : %s" %line )                    
            self.logger.debug( "Parameters were : endtime : %s entryCount : %s" %((endTime)[:-2], entryCount) ) 
            
    
            
            
    def createEmptyEntries( self ):    
        """
            We fill up fileEntries with empty entries with proper time labels 
        
        """
        
        if self.logger != None :
            self.logger.debug(" Call to createEmptyEntries received.")
            self.logger.debug(" len ( self.timeSeperators )-1 = %s." %(len ( self.timeSeperators )-1 ) )
            self.logger.debug(" Call to createEmptyEntries received.")
        
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
        
#         try:
            
        self.setValues( endTime )   #fill dictionary with values
        self.setMinMaxMeanMedians() #use values to find these values.   
        
#         except:
#             (type, value, tb) = sys.exc_info()
#             self.logger.error( "Unexpected exception in FileStatsCollector.collectSats." ) 
#             self.logger.error("Type: %s, Value: %s, tb: %s ..." % (type, value,tb))                        
             

                         

if __name__ == "__main__":
    """
            small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    types = [ "latency", "errors","bytecount" ]
    
    filename = PXPaths.LOG +'tx_amis.log'
    
    startingHours=["00:00:00","01:00:00","02:00:00","03:00:00","04:00:00","05:00:00","06:00:00","07:00:00","08:00:00","09:00:00","10:00:00","11:00:00","12:00:00","13:00:00","14:00:00","15:00:00","16:00:00","17:00:00","18:00:00","19:00:00","20:00:00","21:00:00","22:00:00","23:00:00" ]
    
    endingHours = ['00:59:00', '01:59:00', '02:59:00', '03:59:00', '04:59:00', '05:59:00', '06:59:00', '07:59:00', '08:59:00', '09:59:00', '10:59:00', '11:59:00', '12:59:00', '13:59:00', '14:59:00', '15:59:00', '16:59:00', '17:59:00', '18:59:00', '19:59:00', '20:59:00', '21:59:00', '22:59:00', '23:59:00' ]
     
     
    for i in xrange(1, 8) : #len(startingHours)
              
        stats = FileStatsCollector( files = [ filename ], statsTypes = types , startTime = '2006-08-01 %s' %startingHours[i], endTime = '2006-08-01 %s' %endingHours[i], interval = 1*MINUTE  )
        stats.collectStats()
        saveFile = PXPaths.STATS + "test/%s" %startingHours[i]
        del stats.logger
        cpickleWrapper.save( object = stats, filename = saveFile )
       

     
