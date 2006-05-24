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
from array import *


#Constants can be removed once we add methods to the datelibrary and include it 
MINUTE = 60
HOUR   = 60 * MINUTE
DAY    = 24 * HOUR

   
class _Matrix:
    """
        This class is usefull to deal with two dimensional arrays. 
    """
    
    def __init__( self, columns =0, rows=0 ):
        """ Constructor.
           By default builds a 0*0 matrix.
           Matrix is always empty, values need to be added after creation.  
        """
        
        self.columns = columns       #number of columns of the matrix 
        self.rows = rows             #number of rows 
        self.matrix =  [[0 for column in range(columns)] for row in range(rows)] #matrix containing values
         


class _FileStatsEntry:
    """
        This class is used to contain all the info on a particular file entry.     
    """
    
    def __init__( self, values = _Matrix() , means = None , medians = None, totals = None, minimums =None, maximums = None, startTime = '2005-08-30 20:06:59', endTime ='2005-08-30 20:06:59'  ):
        
        self.startTime = startTime       # Start time on an entry.
        self.endTime   = endTime         # End time of an entry.                      
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
    
    def __init__(self, files = None , statsTypes = None, startTime = '2005-08-30 20:06:59', width = DAY, interval=20*MINUTE   ):
        """ 
            Constructor. All values can be set from the constructor by the user but recommend usage
            is to set sourceFile and statsType. The class contains other methods to set the other values
            properly.  
            
            Precondition : Interval should be smaller than width !
        """    
        
        startTime = FileStatsCollector.getSecondsSinceEpoch( startTime )
        
        self.files          = files or []     # Source files we will use. 
        self.statsTypes     = statsTypes or []# List of types we need to manage.
        self.fileEntries    = []              # list of all entries wich are parsed using time seperators.
        self.nbEntries      = 0               # number of entries within a file 
        self.startTime      = startTime       # Beginning of the timespan used to collect stats.
        self.width          = width           # Width of said timespan.
        self.interval       = interval        # Interval at wich we separate stats entries 
        self.timeSeperators = FileStatsCollector.getSeparatorsWithStartTime( self.startTime, self.width, self.interval )                     # Time separators used to parse the log file  
        
        
        
    
    
    """
        This section should be put in date library 
    """
    def getSecondsSinceEpoch(date='2005-08-30 20:06:59'):
        try:
            timeStruct = time.strptime(date, '%Y-%m-%d %H:%M:%S')
            
        except:
            print date
            
        return time.mktime(timeStruct)
    
    getSecondsSinceEpoch = staticmethod( getSecondsSinceEpoch )
            
    

    def getNumericMonthFromString( month ) :
        """
            This method takes a month in the string format and returns the month.
            Returns 00 if month is unknown.
        """    
        
        value = '00'
        
        if month == 'Jan'   : 
            value = '01'    
        elif month == 'Feb' :
            value = '02'
        elif month == 'Mar' :
            value = '03'
        elif month == 'Apr' :
            value = '04'
        elif month == 'May' :
            value = '05'
        elif month == 'Jun' :
            value = '06'
        elif month == 'Jul' :
            value = '07'
        elif month == 'Aug' :
            value = '08'
        elif month == 'Sep' :
            value = '09'
        elif month == 'Oct' :
            value = '10'
        elif month == 'Nov' :
            value = '11'
        elif month == 'Dec' :
            value = '12'
        
        return value   
    
    getNumericMonthFromString = staticmethod( getNumericMonthFromString )
        
    
    
    def getOriginalDate( seconds ):
        """
            Take a number of seconds built with getSecondsSinceEpoch
            and returns a date in the format of '2005-08-30 20:06:59'
            Thu May 18 13:00:00 2006     
        """
        
        timeString = time.ctime( seconds )
        splitTimeString = timeString.split( " " )
        
        originalDate = splitTimeString[4] + '-' + FileStatsCollector.getNumericMonthFromString ( splitTimeString[1] ) + '-' + splitTimeString[2] + ' ' + splitTimeString[3]   
        
        return originalDate
    
    getOriginalDate = staticmethod ( getOriginalDate )
    
    
    
    def getSeparators( width=DAY, interval = 20*MINUTE ):
        
        separators = []
        
        for value in range( interval, width+interval, interval ):
            separators.append( value )
        
        return separators 
    
    getSeparators = staticmethod( getSeparators )
    
    
    def getSeparatorsWithStartTime( startTime = 0, width=DAY, interval=60*MINUTE ):
        """
            This method works exactly like getSeparators but it uses a start time to set 
            the separators
        """    
        separators = []
        if interval <= width :
            for value in range( int(interval+startTime), int( width+interval+startTime ), int( interval ) ):
                separators.append(value)
            
            if separators[ len(separators)-1 ] > width+startTime :
                separators[ len(separators)-1 ] = width+startTime    
            
        return separators 
        
    getSeparatorsWithStartTime = staticmethod( getSeparatorsWithStartTime )
    
    """ 
        End of section that needs to be in date library 
    """



    def setMeans( self ):
        """
            This method takes all the values set in the values matrix, finds the means for every
            types found and sets them in a list of means. This means if statsTypes = [latency, bytecount]
            we will store the means in the same order :[ latencyMean,bytecountMean ] 
            
            precondition : Values matrix should have been built and filled prior to using this method.
              
        """
        
        total = 0
        
        
        for i in range ( self.nbEntries ): #for all entries 
            
            self.fileEntries[i].means = []
            
            
            for j in range( len( self.statsTypes ) ) :# for all datatypes        
           
                for line in range( self.fileEntries[i].values.rows  ) : 
                    total = total + self.fileEntries[i].values.matrix[line][j]
                
                if self.fileEntries[i].values.rows != 0:
                    mean = total / self.fileEntries[i].values.rows
                else:#this entry had no rows 
                    mean = 0
                    total = 0         
                
                self.fileEntries[i].means.append( mean )    
                self.fileEntries[i].totals.append( float(total) )
                total = 0 #resets values 
                mean  = 0        
            
            
            
    
    def setMinMaxMedians( self ):
        """
            This method takes all the values set in the values matrix, finds the media for every
            types found and sets them in a list of medians. This means if statsTypes = [latency, bytecount]
            we will store the medians in the same order :[ latencyMedian, bytecountMedian ] 
            
            precondition : Values matrix should have been built and filled prior to using this method.
        
        """
        
        minimum = 0  # Minimum of a certain field from an entry.  
        maximum = 0  # Maximum of a certain field from an entry.
        median  = 0  # Median of a certain field from a entry.
        values  = [] # Used to sort value to find median. 
        
        for i in range( self.nbEntries  ): #for each file entries 
            self.fileEntries[i].medians  = []
            self.fileEntries[i].minimums = []
            self.fileEntries[i].maximums = []
            
            for j in range( len( self.statsTypes ) ) :#for each datatype        
                
                for line in range( self.fileEntries[i].values.rows ) : # for each line in the entry 
                    values.append( self.fileEntries[i].values.matrix[line][j] )#add to new array
            
                if self.fileEntries[i].values.rows != 0:
                    values.sort()   
                    minimum = values[0]
                    maximum = values[ self.fileEntries[i].values.rows - 1 ]  
                    median  = values[ int( int(self.fileEntries[i].values.rows) / 2 ) ]    
                else: #this entry has no values 
                    minimum = 0
                    median  = 0
                    maximum = 0
                
                    
                self.fileEntries[i].medians.append( median )    # appending values to a list    
                self.fileEntries[i].minimums.append( minimum )  # permits user to use this class to collect
                self.fileEntries[i].maximums.append( maximum )  # as many datatypes as he wishes
                values = []
    
    
    def findValue( statsType, line = "" ):
        """
            This method is used to find a particular entry within a line. 
            Line format should be : timeofarrival;timeofdeparture;bytecount
            
            This method will return the value according to the type received as a parameter. 
            
            If type is unknown, method will return "". 
        
        """
        
        value = "" #in case of an unknown type
        parsedLine = line.split( ";" )
       
        
        if statsType == "latency":
            value = int( FileStatsCollector.getSecondsSinceEpoch( parsedLine[1] ) ) - int( FileStatsCollector.getSecondsSinceEpoch( parsedLine[0] ) ) 
            
        elif statsType == "arrival":
            value = int( FileStatsCollector.getSecondsSinceEpoch( parsedLine[0] ) )     
        
        elif statsType == "bytecount":
            value = parsedLine[2] 
            value = float( value.replace( '\n', '' ) )
        
        return value
    
    findValue = staticmethod( findValue )
    
    
    
    def setValues(self):
        """
            This method opens a file and finds sets all the values found in the file in the appropriate entry's value matrix.
            -Values searched depend on the datatypes asked for by the user.
            -Number of entries is based on the time separators wich are found with the startTime, width and interval.  -Only entries with arrival time comprised between startTime and startTime + width will be saved in matrixes
            -Entries wich have no values will have 0 as value for means, minimum maximum and median     
        """
        
        value = []
        entryCount = 0
        
        
        #we fill up fileEntries with empty entries with proper time labels 
        for i in range( len ( self.timeSeperators ) ):
        
            self.fileEntries.append( _FileStatsEntry() )       
            
            if i == 0 :
                self.fileEntries[0].startTime = FileStatsCollector.getOriginalDate( self.startTime )
            else:
                self.fileEntries[i].startTime = FileStatsCollector.getOriginalDate( self.timeSeperators[i-1] )
            
            self.fileEntries[i].endTime = FileStatsCollector.getOriginalDate( self.timeSeperators[i] )
            self.fileEntries[i].values  = _Matrix( len( self.statsTypes ), 0 )
            
        
        try:#read everyfile and append data found to matrixes 
            
            for file in range( len( self.files ) ) :
                
                fileHandle = open( self.files[file] , 'r' )
            
                lines = []
                lines = fileHandle.readlines() #read all lines from the file 
                
                # At this point lines should be sorted.  
                # If file is not allready sorted, apply some sort of sorting method HERE.
                
                nbLines = 0
                entryCount = 0
                
                #find the first line entry in the file wich is within the timespan we want
                while nbLines < len(lines) and FileStatsCollector.findValue( "arrival" , lines[nbLines] )  < self.startTime : 
                    nbLines = nbLines + 1
                    
                # read lines untill eof or untill we're out of range
                while  nbLines < len(lines) and FileStatsCollector.findValue( "arrival" , lines[nbLines] ) < self.startTime + self.width : 
                    
        
                    #go to next time separator until we find the right one. 
                    while FileStatsCollector.findValue( "arrival" , lines[nbLines] ) > self.timeSeperators[entryCount]:
                        entryCount = entryCount + 1 
                    
                    #find values to append 
                    for j in range( len( self.statsTypes ) ) :                  
                        value.append( FileStatsCollector.findValue( self.statsTypes[j] , lines[nbLines] ) )
                    
                    # add values at the right place  
                    self.fileEntries[ entryCount ].values.matrix.append( value )
                    self.fileEntries[ entryCount ].values.rows = self.fileEntries[ entryCount ].values.rows + 1
                    
                    nbLines = nbLines + 1
                    value = []      
                    
        except:
            print "Error. There was an error reading source file named %s" %( self.files )
            print "Program terminated."
            sys.exit()                     
            
        self.nbEntries =  len ( self.timeSeperators )
    
    
    
    def collectStats( self ):
        """
            This is the main method to use with a FileStatsCollector. 
            It will collect the values from the file and set them in a matrix.
            It will use that matrix to find the totals and means of each data types wanted. 
            It will also use that matrix to find the minimum max andmedians of 
            each data types wanted. 
               
        """
        
        self.setValues()        #fill matrix with values
        self.setMeans()         #finds means 
        self.setMinMaxMedians() #find medians  
        
                         

if __name__ == "__main__":
    """
        small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    types = [ 'latency', 'bytecount']
    filename = '/users/dor/aspy/lem/metpx/sundew/lib/stats/files/test1'
    
    stats = FileStatsCollector( files = [filename], statsTypes = types , startTime = '2006-05-18 00:00:00', width = 1*HOUR, interval = 22*MINUTE  )
    
    stats.collectStats()
    
    print "\nNb entries : %s" %stats.nbEntries 
    for i in range ( stats.nbEntries ) :
        print "\nStart time : %s    end time : %s" %( stats.fileEntries[i].startTime, stats.fileEntries[i].endTime ) 
        print "Values : %s"   %stats.fileEntries[i].values.matrix
        print "means :%s "    %stats.fileEntries[i].means
        print "medians : %s"  %stats.fileEntries[i].medians    
        print "minimums : %s" %stats.fileEntries[i].minimums
        print "maximums : %s" %stats.fileEntries[i].maximums
        
        
