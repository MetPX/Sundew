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



import array,time,sys,os #important files 
import copy
from   array     import *
import MyDateLib
from   MyDateLib import *
import commands
import copy 
import backwardReader

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
        self.rows         = rows     # Number of rows 
        self.dictionary   = {}       # Contains value for each data type collected.
        self.productTypes = []       # For each line read, we save up what product type it was   


class _FileStatsEntry:
    """
        This class is used to contain all the info on a particular file entry.     
    
    """
    
    def __init__( self, values = _ValuesDictionary() , means = None , medians = None, totals = None, minimums =None, maximums = None, startTime = 0, endTime = 0 ):
        
        
        self.startTime = startTime       # Start time IN SECONDS SINCE EPOCH.
        self.endTime   = endTime         # End time IN SECONDS SINCE EPOCH.                      
        self.values    = values          # List of values from all the types. 
        self.minimums  = minimums or {}  # List of the minimums of all types.
        self.nbFiles   = 0               # Number of files dealt with during this entry.
        self.filesWhereMinOccured =  {}  # Dict of files where min appened for each type  
        self.timesWhereMinOccured =  {}  # Dict of times where min appened for each type 
        self.maximums  = maximums or {}  # Maximum of all types.   
        self.filesWhereMaxOccured =  {}  # Dict of files where max appened for each type
        self.timesWhereMaxOccured =  {}  # Dict of times where max appened for each type 
        self.filesOverMaxLatency  =  0   # Number of files per entry whos latency are too long.  
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
    
    def __init__(self, files = None , statsTypes = None, startTime = '2005-08-30 20:06:59', endTime = '2005-08-30 20:06:59', interval=20*MINUTE, totalWidth = 24*HOUR, firstFilledEntry = 0, lastFilledEntry = 0, lastFilledLine = "", maxLatency = 15,fileEntries = None ):
        """ 
            Constructor. All values can be set from the constructor by the user but recommend usage
            is to set sourceFile and statsType. The class contains other methods to set the other values
            properly.  
            
            constructor receives date in an iso format wich is conveniant for users but transforms is in a seconds since epoch format for ease of use during the program.   
            
            Precondition : Interval should be smaller than width !
        
        """    
        
        startTimeInSeconds = MyDateLib.getSecondsSinceEpoch( startTime )
        endTimeInSeconds   = MyDateLib.getSecondsSinceEpoch( endTime )
        if fileEntries == None :
            fileEntries = []    
         
        self.files          = files or []        # Source files we will use. 
        self.statsTypes     = statsTypes or []   # List of types we need to manage.
        self.fileEntries    = copy.deepcopy(fileEntries)# list of all entries wich are parsed using time seperators.
        self.startTime      = startTimeInSeconds # Beginning of the timespan used to collect stats.
        self.endTime        = endTimeInSeconds   # End of saidtimespan.
        self.interval       = interval           # Interval at wich we separate stats entries .
        self.totalWidth     = totalWidth         # used to build timesperators.
        self.maxLatency     = maxLatency         # Acceptable limit for a latency.  
        self.timeSeperators = (MyDateLib.getSeparatorsWithStartTime( self.startTime, self.totalWidth, self.interval ) )
        self.nbEntries        = len ( self.timeSeperators )# Nb of "buckets" or entries  
        self.firstFilledEntry = firstFilledEntry        # Last entry for wich we calculated mean max etc....
        self.lastFilledEntry  = lastFilledEntry         # Last entry we filled with data. 
        self.lastFilledLine   = lastFilledLine          # Last line filled in this stats collection.
        
        if fileEntries == []:
            self.createEmptyEntries()                              # Create all empty buckets right away
         


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
                         
        
        for i in xrange( self.firstFilledEntry , self.lastFilledEntry + 1 ): #for each entries we need to deal with 
            
            
            self.fileEntries[i].medians  = {}
            self.fileEntries[i].minimums = {}
            self.fileEntries[i].maximums = {}
            
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
                            
                            values.append(self.fileEntries[i].values.dictionary[aType][row] )#add to new array
                            files.append( self.fileEntries[i].files[row]  )
                            times.append( self.fileEntries[i].times[row]  )
                        
                        else:
                            if aType == self.statsTypes[0] : #Lower number of file only if first time we check it.
                                self.fileEntries[i].nbFiles = self.fileEntries[i].nbFiles -1
                            if aType == "latency":
                                if self.fileEntries[i].values.dictionary[aType][row] > self.maxLatency:  
                                    self.fileEntries[i].filesOverMaxLatency = self.fileEntries[i].filesOverMaxLatency - 1  
                     
                                           
                    if len( values ) != 0 :
                        minimum = values[0]
                        maximum = values[0]
                    else:
                        minimum =0
                        maximum =0
                    
                    for k in range( len( values ) ) :
                        
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
   
                    
                                        
                    #median  = values[ int( int(self.fileEntries[i].values.rows) / 2 ) ]    
                    median  = 0 
                    try :
                        total   = sum( values )
                    except :
                        print "exception"
                        print "i: %s" %i
                        print "type : %s" %aType
                        print "values :%s " %values 
                        
                        
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
                self.fileEntries[i].totals[aType] =  float(total)
                

                    
        self.lastEntryCalculated = self.lastFilledEntry
        
        return self
    
    
    def findValue( statsType, line = "", lineType = "[INFO]" ):
        """
            This method is used to find a particular entry within a line. 
            Used with line format used in tx_satnet.logxxxxxxxxxx
        
            To be modified once line format is decided upon. 
            
        """
        
        value = "" #in case of an unknown type
        
        if line != "" and line != "\n" :
            
            if statsType == "departure" :
                
                departure = line.split( ",")
                departure = departure[0] 
                value     = MyDateLib.getSecondsSinceEpoch( departure )
            
            elif lineType == "[INFO]" :
            
                parsedLine = line.split( " " )
                
                if statsType == "latency":
                    
                    try:
                        lastPart  = parsedLine[6] 
                        lastPart  = lastPart.split(":") 
                        arrival   = MyDateLib.isoDateDashed( lastPart[6] )
                        departure = line.split( ",")
                        departure = departure[0]
                        value     = MyDateLib.getSecondsSinceEpoch( departure ) - MyDateLib.getSecondsSinceEpoch( arrival)
                        
                    except Exception,e:
                        print line 
                        print e 
                        sys.exit()
                        
                elif statsType == "arrival":
                    
                    try : # for debugging....lines passed should always be valid in final versions.      
                        
                        lastPart = parsedLine[6] 
                        lastPart = lastPart.split(":") 
                        arrival  = MyDateLib.isoDateDashed( lastPart[6] )
                        value    = MyDateLib.getSecondsSinceEpoch( arrival)    
                    
                    except Exception,e :
                        print line 
                        print e 
                        sys.exit()
                        
                elif statsType == "bytecount":
                    value = parsedLine[3]
                    value = value.replace( '(', '' )
                    value = int(value)
                    
                elif statsType == "fileName":
                    value = parsedLine[6]
                    value = value.split( ":" )
                    value = value[0]
                
        
                
                elif statsType == "productType":
                    splitLine = line.split( " " )
                    value = splitLine[6]
                    
                elif statsType == "errors" :
                    value = 0    
                
            elif lineType == "[ERROR]":
            
                if statsType == "errors" :
                    value = 1                   
    
                
                elif statsType == "productType" :     
                    value = ""
                else:
                    value = 0
            
            #elif lineType == "[OTHER]" :               

         
        return value

    
    
    findValue = staticmethod( findValue )
    
    
    
        
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
            
            If files were previously read,stops if we find
            the last line we read the other time.
            
            Otherwise, we stop at the first interesting line within the range
            of the data we want to collect.
        
        """
        
        print "Temps avant find first: %s" %time.gmtime( time.time() )
        print "self.startTime :%s" %MyDateLib.getIsoFromEpoch( self.startTime )
        print "self.endTime : %s" %MyDateLib.getIsoFromEpoch( self.endTime )
        line = ""
        backupLine = ""
        lineFound = False 
        firstLine      = fileHandle.readline()
        firstDeparture = FileStatsCollector.findValue( "departure" , firstLine )
        
        lastLine,offset  = backwardReader.readLineBackwards( fileHandle, offset = -1, fileSize = fileSize  )
        lastDeparture    = FileStatsCollector.findValue( "departure" , lastLine )
#         print "startTime dans fid first interesting : %s" %MyDateLib.getIsoFromEpoch(self.startTime)
#         print "endtime dans fid first interesting : %s" %MyDateLib.getIsoFromEpoch(self.endTime)
#         print "firstDeparture dans find first interesting : %s" %MyDateLib.getIsoFromEpoch(firstDeparture)
#         print "lastDeparture dans find first interesting : %s" %MyDateLib.getIsoFromEpoch(lastDeparture)
        
              
                
        if abs( firstDeparture - self.startTime ) < 2*(abs( lastDeparture - self.startTime )) :
            fileHandle.seek(0,0)
            
            print "+++++find forwards++++++++"    
            while lineFound == False :     
                
                departure =  FileStatsCollector.findValue( "departure" , line )
                if self.lastFilledLine != "" : 
                    if line == self.lastFilledLine :       
                        isInteresting,lineType = self.isInterestingLine( line )
                        if isInteresting == True :
                            position = fileHandle.tell()
                            lineFound = True  
                
                elif departure >= self.startTime and departure <=  self.endTime :
                    isInteresting,lineType = self.isInterestingLine( line )
                    
                    if isInteresting == True :
                        position = fileHandle.tell()
                        lineFound = True 
                   
                if lineFound == False :
                    line = fileHandle.readline ()        
                        
                        
                        
               
        else:#read backwards till we are in the range we want 
            fileHandle.seek(0,0)
            print "***find backwards"
            line = lastLine 
            departure = lastDeparture
            
            while line != "" and line != self.lastFilledLine and departure >= self.startTime :
                line,offset = backwardReader.readLineBackwards( fileHandle = fileHandle, offset = offset , fileSize = fileSize )
                #print line 
                if line != "":
                    departure =  FileStatsCollector.findValue( "departure" , line )
                if departure > self.startTime:#save line ,or else well lose it at last turn
                    backupLine = line             
            
            if backupLine != "" :        
                line = backupLine      
                isInteresting,lineType = self.isInterestingLine( line ) #go back the other way and find first of the good type 
                while isInteresting == False  :
                    line = fileHandle.readline()
                    isInteresting,lineType = self.isInterestingLine( line )     
                    position = fileHandle.tell()
                    
        print "Temps apres find first line  : %s" %time.gmtime( time.time() )                  
       
        print "####line : %s" %line  
        
        
        
        
        return line, lineType, position 



    def setValues( self, endTime = "" ):
        """
            This method opens a file and sets all the values found in the file in the appropriate entry's value dictionary.
            -Values searched depend on the datatypes asked for by the user.
            -Number of entries is based on the time separators wich are found with the startTime, width and interval.  -Only entries with arrival time comprised between startTime and startTime + width will be saved in dicts
            -Entries wich have no values will have 0 as value for means, minimum maximum and median     
        
            -Precondition : stats type specified in self must be valid. 
        
        """
        
        #try:        

        filledAnEntry = False
        self.firstFilledEntry = 0
        self.lastFilledEntry  = 0
        
        if endTime == "" :                                        
            endTime = self.endTime
        else:
            endTime = MyDateLib.getSecondsSinceEpoch( endTime )
        
        print "self.files : %s" %self.files
        
        
        for file in self.files :#read everyfile and append data found to dictionaries
            
            print "currently used file : %s" %file              
            nbErrors      = 0 
            entryCount    = 0
            
            fileHandle = open( file, "r" )
            fileSize = os.stat(file)[6]
            line,lineType,position  = self.findFirstInterestingLine( fileHandle, fileSize )                                        
            fileHandle.seek(position)
                       
            departure   = self.findValue( "departure" ,  line, lineType )
            productType = self.findValue( "productType", line, lineType )
             
            
            while str( departure ) != "" and  departure < self.endTime : #while in proper range 
                #print "departure : %s endtime : %s " %( MyDateLib.getIsoFromEpoch(departure), MyDateLib.getIsoFromEpoch( endTime ) )
                
                while long( departure ) >= long(self.timeSeperators[ entryCount ]):#find appropriate bucket
                    entryCount = entryCount + 1                         
                
#                 print len( self.fileEntries    )
#                 print entryCount 
                #add values general to the line we are treating 
                self.fileEntries[ entryCount ].files.append( self.findValue( "fileName" , line ) )
                self.fileEntries[ entryCount ].times.append( self.findValue( "departure" , line ) )
                self.fileEntries[ entryCount ].values.productTypes.append( self.findValue( "productType",line, lineType ) )
                self.fileEntries[ entryCount ].values.rows = self.fileEntries[ entryCount ].values.rows + 1
                
                
                if filledAnEntry == False :
                    self.firstFilledEntry = entryCount 
                    filledAnEntry = True 
                elif entryCount < self.firstFilledEntry:
                    self.firstFilledEntry = entryCount    
                
                for statType in self.statsTypes : #append values for each specific data type needed  
                    
                    newValue = self.findValue( statType , line, lineType )
                    
                    if statType == "latency":
                        if newValue > self.maxLatency :      
                            self.fileEntries[ entryCount ].filesOverMaxLatency = self.fileEntries[entryCount ].filesOverMaxLatency + 1                          
                    
                    self.fileEntries[ entryCount ].values.dictionary[statType].append( newValue )                                  
                
                
                if lineType != "[ERROR]" :
                    self.fileEntries[ entryCount ].nbFiles = self.fileEntries[ entryCount ].nbFiles + 1        
                
                #Find next interesting line     
                line    = fileHandle.readline()
                isInteresting,lineType = self.isInterestingLine( line )
                while isInteresting == False and line != "":
                          
                    line = fileHandle.readline()# we read again 
                    isInteresting,lineType = self.isInterestingLine( line )
                    
                
                        
                departure   = self.findValue( "departure" , line, lineType )
                productType = self.findValue( "productType",line, lineType )
                               
                   
                if entryCount > self.lastFilledEntry : # in case of numerous files....
                    self.lastFilledEntry = entryCount                  
                    self.lastFilledLine  = line 
            
            
            fileHandle.close()                 
            print "goes after filehandle.close"                        
#         
#         except Exception,e:
#             
#             print "*************************************************************************"
#             print "Exception : %s" %e
#             print "Error. There was an error reading source file named %s" %( self.files )
#             print "Program terminated."
#             sys.exit()                     
            
    
    
    def createEmptyEntries( self ):    
        """
            We fill up fileEntries with empty entries with proper time labels 
        
        """
        
        if len ( self.timeSeperators ) > 0 : 
            
            #treat special 0 case apart
            self.fileEntries.append( _FileStatsEntry() )
            self.fileEntries[0].startTime = self.startTime 
            self.fileEntries[0].endTime   = self.timeSeperators[0] 
            self.fileEntries[0].values    = _ValuesDictionary( len( self.statsTypes ), 0 )
            for statType in self.statsTypes:
                self.fileEntries[ 0 ].values.dictionary[statType] = []
            
            #other cases     
            for i in xrange( 1, len ( self.timeSeperators ) ):
            
                self.fileEntries.append( _FileStatsEntry() )       
                self.fileEntries[i].startTime =  self.timeSeperators[ i-1 ] 
                self.fileEntries[i].endTime   =  self.timeSeperators[ i ]  
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
        print "goes into setMinMaxMeanMedians "
        self.setMinMaxMeanMedians() #use values to find these values.   


                         

if __name__ == "__main__":
    """
            small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    types = [ "latency","errors","bytecount" ]
    filename = '/apps/px/lib/stats/files/tx_satnet.log'
     
    stats = FileStatsCollector( files = [ filename ], statsTypes = types , startTime = '2006-07-20 01:00:00', endTime = '2006-07-20 02:00:00', interval = 1*MINUTE  )
    
    stats.collectStats()   
    
    for i in range(60):
        print stats.fileEntries[i].means
     