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


MINUTE = 60
HOUR   = 60 * MINUTE
DAY    = 24 * HOUR

class _Matrix:
    """
        This class is usefull to deal with two dimensional arrays. 
    """
    
    def __init__( self, columns =0, rows=0 ):
        """ 
           Constructor.
           By default builds a 0*0 matrix.
           Matrix is always empty, values need to be added after creation.  
        
        """
        
        self.columns = columns       #number of columns of the matrix 
        self.rows = rows             #number of rows 
        self.matrix =  [[0 for column in xrange(0,columns)] for row in xrange(0,rows)] #matrix containing values
         


class _FileStatsEntry:
    """
        This class is used to contain all the info on a particular file entry.     
    """
    
    def __init__( self, values = _Matrix() , means = None , medians = None, totals = None, minimums =None, maximums = None, startTime = 0, endTime = 0 ):
        
        
        self.startTime = startTime       # Start time IN SECONDS SINCE EPOCH.
        self.endTime   = endTime         # End time IN SECONDS SINCE EPOCH.                      
        self.values    = values          # List of values from all the types. 
        self.minimums  = minimums or []  # List of the minimums of all types.
        self.maximums  = maximums or []  # Maximum of all types.   
        self.means     = means    or []  # Means for all the values of all the files.
        self.medians   = medians  or []  # Medians for all the values of all the files.
        self.totals    = totals   or []  # Total for all values of each files.                
        


class FileStatsCollector:
    """
       This class contains the date structure and the functions needed to collect stats from 
       a certain file.
    
    """
    
    def __init__(self, files = None , statsTypes = None, startTime = '2005-08-30 20:06:59', width = DAY, interval=20*MINUTE, totalWidth = 24*HOUR, lastEntryCalculated = 0, lastFilledEntry = 0 ):
        """ 
            Constructor. All values can be set from the constructor by the user but recommend usage
            is to set sourceFile and statsType. The class contains other methods to set the other values
            properly.  
            
            constructor receives date in an iso format wich is conveniant for users but transforms is in a seconds since epoch format for ease of use during hte program.   
            
            Precondition : Interval should be smaller than width !
        
        """    
        
        startTimeInSeconds = MyDateLib.getSecondsSinceEpoch( startTime )
        
        self.files          = files or {}        # Source files we will use. 
        self.statsTypes     = statsTypes or []   # List of types we need to manage.
        self.fileEntries    = []                 # list of all entries wich are parsed using time seperators.
        self.startTime      = startTimeInSeconds # Beginning of the timespan used to collect stats.
        self.width          = width              # Width of said timespan.
        self.interval       = interval           # Interval at wich we separate stats entries 
        self.totalWidth     = totalWidth         # used to build timesperators
        self.timeSeperators = (MyDateLib.getSeparatorsWithStartTime( self.startTime, self.totalWidth, self.interval ) )
        
        self.nbEntries            = len ( self.timeSeperators )# Nb of "buckets" or entries  
        self.lastEntryCalculated  = lastEntryCalculated        # Last entry for wich we calculated mean max etc....
        self.lastFilledEntry      = lastFilledEntry            # Last entry we filled with data. 
        self.maximum              = {}                         # Dict. containg value of the maximum.
        self.filesWhereMaxOccured = {}                         # Dict. containing file name where max occured. 
        self.timeOfMax            = {}                         # Dict. containing time where maximum value occured
        self.createEmptyEntries()                              # Create all empty buckets right away
        



    
    
    def setMinMaxMeanMedians( self ):
        """
            This method takes all the values set in the values matrix, finds the media for every
            types found and sets them in a list of medians. This means if statsTypes = [latency, bytecount]
            we will store the medians in the same order :[ latencyMedian, bytecountMedian ] 
            
            All values are set in the same method as to enhance performances slightly.
            
            precondition : Values matrix should have been built and filled prior to using this method.
        
        """
        
        total   = 0  # Total of the values of acertain field within an entry.
        mean    = 0  # Mean of a certain field within an entry.
        minimum = 0  # Minimum of a certain field within an entry.  
        maximum = 0  # Maximum of a certain field within an entry.
        median  = 0  # Median of a certain field within a entry.
        values  = [] # Used to sort value to find median. 
        
        for i in xrange( self.lastEntryCalculated , self.lastFilledEntry + 1 ): #for each entries we need to deal with 
            
            self.fileEntries[i].medians  = []
            self.fileEntries[i].minimums = []
            self.fileEntries[i].maximums = []
            
            
            if self.fileEntries[i].values.rows != 0 :
                
                for j in xrange( 0,len( self.statsTypes ) ) :#for each datatype        
                    
                    for line in xrange( 0, self.fileEntries[i].values.rows ) : # for each line in the entry 
                        values.append( self.fileEntries[i].values.matrix[line][j] )#add to new array
                
                    
                    if self.fileEntries[i].values.rows != 0:
                        #set values for each bucket..... 
                        
                        #is in commented block now for performance testing....
#                       values.sort()   
#                       minimum = values[0]
#                       maximum = values[ self.fileEntries[i].values.rows - 1 ]  
#                       median  = values[ int( int(self.fileEntries[i].values.rows) / 2 ) ]    
                        total   = sum( values )
                        mean    = float( total / len(values) )
                    
                    else: #this entry has no values 
                        minimum = 0
                        median  = 0
                        maximum = 0
                        total   = 0
                        mean    = 0
                        
                    self.fileEntries[i].medians.append( median )     # appending values to a list    
                    self.fileEntries[i].minimums.append( minimum )   # permits user to use this class to collect
                    self.fileEntries[i].maximums.append( maximum )   # as many datatypes as he wishes
                    self.fileEntries[i].means.append( mean )         #
                    self.fileEntries[i].totals.append( float(total) )
                    values = []
        
        self.lastEntryCalculated = self.lastFilledEntry
    
    
#     def findValue( self, statsType, line = "" ):
#         """
#             This method is used to find a particular entry within a line. 
#             Line format should be : timeofarrival;timeofdeparture;bytecount
#             
#             This method will return the value according to the type received as a parameter. 
#             
#             If type is unknown, method will return "". 
#         
#         """
#         
#         value = "" #in case of an unknown type
#         
#         if line != "" and line != "\n" :
#             
#             parsedLine = line.split( ";" )
#         
#             
#             if statsType == "latency":
#                 value =  MyDateLib.getSecondsSinceEpoch( parsedLine[1] ) -  MyDateLib.getSecondsSinceEpoch( parsedLine[0] ) 
#                 
#             elif statsType == "arrival":
#                 
#                 value =  MyDateLib.getSecondsSinceEpoch( parsedLine[0] )      
#             
#             elif statsType == "bytecount":
#                 value = parsedLine[2]
#                 value = value.replace( '\n', '' )
#                 value = int(value)
#         
#         return value
    
    
    
    def findValue( self, statsType, line = "" ):
        """
            This method is used to find a particular entry within a line. 
            Used with line format used in tx_satnet.logxxxxxxxxxx
        
        """
        
        value = "" #in case of an unknown type
        
        if line != "" and line != "\n" :
            
            parsedLine = line.split( " " )
        
            if statsType == "latency":
                lastPart  = parsedLine[6] 
                lastPart  = lastPart.split(":") 
                arrival   = MyDateLib.isoDateDashed( lastPart[6] )
                departure = line.split( ",")
                departure = departure[0]
                value     = MyDateLib.getSecondsSinceEpoch( departure ) - MyDateLib.getSecondsSinceEpoch( arrival)
                
            elif statsType == "arrival":
                lastPart = parsedLine[6] 
                lastPart = lastPart.split(":") 
                arrival  = MyDateLib.isoDateDashed( lastPart[6] )
                value    = MyDateLib.getSecondsSinceEpoch( arrival)    
            
            elif statsType == "bytecount":
                value = parsedLine[3]
                value = value.replace( '(', '' )
                value = int(value)
                
            elif statsType == "fileName":
                value = parsedLine[6]
                value = value.split( ":" )
                value = value[0]
            
                
        
        return value


    
    def containsUsefullInfo( self, file ):
        """
            This method returns whether or not a certain file contain any data wich is within 
            the range we want 
        """
        
        status,firstLine = commands.getstatusoutput( 'head -n 1  %s'%file) 
        
        arrival =  self.findValue( "arrival", firstLine )
        
        if arrival <= (self.startTime + self.totalWidth)  :
            status,lastLine = commands.getstatusoutput( 'tail -n 1 %s' %file) 
            arrival = self.findValue( "arrival", lastLine )
            
            if arrival >= self.startTime :
            
                usefull = True
            else:
                usefull = False
        else:
            print "not usefull"
            usefull = False 
        
        return usefull            
        
    
    
    def setMaximums(self):
        """
            if maximum values were'nt previously set, set default value 
            for every data type. 
        
        """
        
        if self.maximum == {}:
            for statType in self.statsTypes:
                self.maximum[statType]              = 0
                self.filesWhereMaxOccured[statType] = "" 
                self.timeOfMax[statType]            = 0 
    
    
    def findFirstInterestingLine( self,file ):
        """
            Finds the first interesting line in a file, starting where we last read the file.
            If file was never read, will of course satrt from start of file. 
            
            returns the first line 
        """
        
        offset = self.files[file][0]#if file was previously read, we'll know where we last stopped
        entryCount = self.files[file][1]
        filehandle = open( file , 'rb' )
            
        filehandle.seek( offset , 0 )
        
        line = filehandle.readline()# we need first line 
        
        #here we should call a isvalid(line) once we know what makes up a valid line.... 
        while line != "" and( line.replace( ' ', '' ) == "\n" or line[0] != '2' or "sent" in line or "Speed" in line or "Caching" in line  or "Initialisation " in line or "Cache" in line or "reloaded" in line ):
            line = filehandle.readline()# we read again 
            
        return entryCount,line,filehandle
    
    
    
    def setValues( self ):
        """
            This method opens a file and finds sets all the values found in the file in the appropriate entry's value matrix.
            -Values searched depend on the datatypes asked for by the user.
            -Number of entries is based on the time separators wich are found with the startTime, width and interval.  -Only entries with arrival time comprised between startTime and startTime + width will be saved in matrixes
            -Entries wich have no values will have 0 as value for means, minimum maximum and median     
        
            -Finding a way to speed up file reading would be nice....
        """
        
        #try:
        
        value = []
        files =  self.files.keys()    
        self.setMaximums( ) 
        
        
        for file in files :#read everyfile and append data found to matrixes 
            
            #if self.containsUsefullInfo( file ) == True :    
            entryCount,line,filehandle  = self.findFirstInterestingLine( file )
            
                                                    
            endTime = self.width + self.startTime #set them values so they dont have to be reevaluated at every step 
            arrival = self.findValue( "arrival" , line )
            
            while arrival != "" and arrival < endTime : 
                
                #go to next time separator until we find the right one. 
                while  arrival > self.timeSeperators[ entryCount ]:
                    entryCount = entryCount + 1 
                
                #find values to append 
                for statType in self.statsTypes :                  
                    newValue = self.findValue( statType , line )
                    value.append( newValue )
                    
                    if newValue > self.maximum[statType] : 
                        self.maximum[statType]              = newValue
                        self.filesWhereMaxOccured[statType] = self.findValue( "fileName", line  ) 
                        self.timeOfMax[statType]            = self.findValue( "arrival" , line ) 
                
                #add values at the right place  
                self.fileEntries[ entryCount ].values.matrix.append( value )
                self.fileEntries[ entryCount ].values.rows = self.fileEntries[ entryCount ].values.rows + 1
                

                offset  = filehandle.tell()
                line    = filehandle.readline()
                
                #add a is valid method once we know what a valid line is ....
                while line != "" and( line.replace( ' ', '' ) == "\n" or line[0] != '2' or "sent" in line or "Speed" in line or "Caching" in line or "erased" in line or "Initialisation " in line or "Cache" in line or "reloaded" in line)  :
                    line = filehandle.readline()# we read again 
                
                arrival = self.findValue( "arrival" , line )
                value   = []
              
                
            # We won't change offset if last line read isnt within range or else we'll lose it 
            # in the next reading.
            if arrival == "" or arrival < endTime :
                offset = filehandle.tell()
                
            
            self.files[file][0] = offset         
            self.files[file][1] = entryCount + 1 
            self.lastFilledEntry = entryCount
            filehandle.close()
                
#             else:
#                 print "useless file : %s " %file                     
#         except:
#             
#             print "Error. There was an error reading source file named %s" %( self.files )
#             print "Program terminated."
#             sys.exit()                     
            
    
    
    def createEmptyEntries( self ):    
        """
            Needs to be in a separate method 
            we fill up fileEntries with empty entries with proper time labels 
        
        """
        
        if len ( self.timeSeperators ) > 0 : 
            #treat special 0 case apart
            self.fileEntries.append( _FileStatsEntry() )
            self.fileEntries[0].startTime = self.startTime 
            self.fileEntries[0].endTime   = self.timeSeperators[0] 
            self.fileEntries[0].values    = _Matrix( len( self.statsTypes ), 0 )
            
            #other cases     
            for i in xrange( 1, len ( self.timeSeperators ) ):
            
                self.fileEntries.append( _FileStatsEntry() )       
                self.fileEntries[i].startTime =  self.timeSeperators[ i-1 ] 
                self.fileEntries[i].endTime   =  self.timeSeperators[ i ]  
                self.fileEntries[i].values    = _Matrix( len( self.statsTypes ), 0 )

    
    
    def collectStats( self ):
        """
            This is the main method to use with a FileStatsCollector. 
            It will collect the values from the file and set them in a matrix.
            It will use that matrix to find the totals and means of each data types wanted. 
            It will also use that matrix to find the minimum max andmedians of 
            each data types wanted. 
               
        """
        
        self.setValues()            #fill matrix with values
        self.setMinMaxMeanMedians() #use values to find these values.   

        
        
                         

if __name__ == "__main__":
    """
        small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    types = [ 'latency']
    filename = '/a/lib/stats/files/log'
     
    stats = FileStatsCollector( files = dict( [("/apps/px/lib/stats/files/log", [0,0]) ] ), statsTypes = types , startTime = '2006-05-18 00:00:00', width = 1*HOUR, interval = 1*MINUTE  )
    
    stats.collectStats()
    
#     print "\nNb entries : %s" %stats.nbEntries 
#     
#     for i in xrange ( 0, stats.width/stats.interval ) :
#         print "\nStart time : %s    end time : %s" %( FileStatsCollector.getOriginalDate(stats.fileEntries[i].startTime), FileStatsCollector.getOriginalDate(stats.fileEntries[i].endTime ) ) 
#         print "Values : %s"   %stats.fileEntries[i].values.matrix
#         print "means :%s "    %stats.fileEntries[i].means
#         print "medians : %s"  %stats.fileEntries[i].medians    
#         print "minimums : %s" %stats.fileEntries[i].minimums
#         print "maximums : %s" %stats.fileEntries[i].maximums
#         
        
