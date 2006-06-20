import time,sys,os
    
MINUTE = 60
HOUR   = 60 * MINUTE
DAY    = 24 * HOUR

class MyDateLib:
    
    #Constants can be removed once we add methods to the datelibrary and include it 
    MINUTE = 60
    HOUR   = 60 * MINUTE
    DAY    = 24 * HOUR


    
    """
        This section should be put in date library upon approval. 
    
    """
    
    def getSecondsSinceEpoch( date='2005-08-30 20:06:59' ):
        
        
        try:

            timeStruct = time.strptime( date, '%Y-%m-%d %H:%M:%S' )
            return time.mktime( timeStruct )
        
        except:
            print "Cannot convert %s in getSecondsSinceEpoch. " %date 
            sys.exit()
        
    
    getSecondsSinceEpoch = staticmethod( getSecondsSinceEpoch )
    
    
    
    def getSeconds(string):
        # Should be used with string of following format: hh:mm:ss
        hours, minutes, seconds = string.split(':')
        return int(hours) * HOUR + int(minutes) * MINUTE + int(seconds)
    
    getSeconds = staticmethod( getSeconds )
    
    
    def getHoursSinceStartOfDay( date='2005-08-30 20:06:59' ):
        """
            This method takes an iso style date and returns the number 
            of hours that have passed since 00:00:00 of the same day.
        
        """
        
        try:
            splitDate = date.split( " " )
            splitDate = splitDate[1]
            splitDate = splitDate.split( ":" )
            
            hoursSinceStartOfDay = int( splitDate[0] )  
            
            
            return hourssSinceStartOfDay
        
        except:
        
            print "Cannot convert %s in getMinutesSinceStartOfDay. " %date 
            sys.exit()
    
    
    
    def isoDateDashed( date = "20060613162653" ):
        """
            This method takes in parameter a non dashed iso date and 
            returns the date dashed and the time with : as seperator. 
            
        """    
        
        dashedDate = date[0:4] + "-" + date[4:6] + "-" + date[6:8] + " "  + date[8:10] + ":"  + date[10:12] + ":" + date[12:14]
          
        return dashedDate
        
    isoDateDashed = staticmethod( isoDateDashed )  
    
    
    
    def getMinutesSinceStartOfDay( date='2005-08-30 20:06:59' ):
        """
            This method receives an iso date as parameter and returns the number of minutes 
            wich have passed since the start of that day.            
        
        """
     
        
        try:
            
            splitDate = date.split( " " )
            splitDate = splitDate[1]
            splitDate = splitDate.split( ":" )
            
            minutesSinceStartOfDay = int( splitDate[0] ) * 60 + int( splitDate[1] ) 
            
            
            return minutesSinceStartOfDay
        
        except:
            
            print "Cannot convert %s in getMinutesSinceStartOfDay. " %date 
            sys.exit()
    

    getMinutesSinceStartOfDay = staticmethod( getMinutesSinceStartOfDay )        
    
    
    
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
        timeString = timeString.replace( "  ", " " )#in speicla case there may be two spaces 
        splitTimeString = timeString.split( " " )
        
        if int(splitTimeString[2]) < 10 :
            splitTimeString[2] = "0" + splitTimeString[2]     
         
        originalDate = splitTimeString[4] + '-' + MyDateLib.getNumericMonthFromString ( splitTimeString[1] ) + '-' + splitTimeString[2] + ' ' + splitTimeString[3]   
        return originalDate
    
    getOriginalDate = staticmethod ( getOriginalDate )
  
    
    
    def getOriginalHour( seconds ):
        """
            Take a number of seconds built with getSecondsSinceEpoch
            and returns a date in the format of '2005-08-30 20:06:59'
            Thu May 18 13:00:00 2006     
        
        """
        
        timeString = time.ctime( seconds )
        splitTimeString = timeString.split( " " )
        
        originalHour = splitTimeString[3]   
        
        return originalHour
    
    getOriginalHour = staticmethod ( getOriginalHour )  
    
    
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
    

       