"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

##############################################################################
##
##
## Name   : StatsDateLib.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 29-05-2006 
##
##
## Description : Contains many usefull date manipulation methods wich are 
##               to be used throughout the stats library. 
##
##############################################################################

"""

import time, sys, os
    
    
"""   
    Globals
"""
MINUTE = 60
HOUR   = 60 * MINUTE
DAY    = 24 * HOUR
MINUTES_PER_DAY = 24*60


class StatsDateLib:
    
    #Constants can be removed once we add methods to the datelibrary and include it 
    MINUTE = 60
    HOUR   = 60 * MINUTE
    DAY    = 24 * HOUR
    MINUTES_PER_DAY = 24*60

       
    def getStartEndFromPreviousDay( currentTime, nbDays = 1  ):
        """
            Returns the start and end time of
            the day prior to the currentTime. 
            
            currentTime must be in iso format.       
            start and end are returned in iso format. 
            
        """
        
        end       = StatsDateLib.getIsoTodaysMidnight( currentTime )
        yesterday = StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch( currentTime ) - (24*60*60)  ) 
        start     = StatsDateLib.getIsoTodaysMidnight( yesterday ) 
        
        return start, end 
    
    getStartEndFromPreviousDay = staticmethod( getStartEndFromPreviousDay )    
        
    
    
    def getStartEndFromPreviousWeek( currentTime, nbWeeks = 1 ):
        """
            Returns the start and end time of
            the week prior to the currentTime. 
            
            currentTime must be in iso format.       
            start and end are returned in iso format. 
            
        """
        
        currentTimeInSecs = StatsDateLib.getSecondsSinceEpoch( currentTime )
        weekDay     = int(time.strftime( "%w", time.gmtime( currentTimeInSecs ) ))
        endInSecs   = currentTimeInSecs - ( weekDay*24*60*60 )
        startInSecs = endInSecs - ( 7*24*60*60 )
        start       = StatsDateLib.getIsoTodaysMidnight( StatsDateLib.getIsoFromEpoch( startInSecs ) ) 
        end         = StatsDateLib.getIsoTodaysMidnight( StatsDateLib.getIsoFromEpoch( endInSecs ) )   
        
        return start, end 
    
    getStartEndFromPreviousWeek = staticmethod( getStartEndFromPreviousWeek )      
        
    
    
    def getStartEndFromPreviousMonth( currentTime ):
        """
            Returns the start and end time of
            the month prior to the currentTime. 
            
            currentTime must be in iso format.       
            start and end are returned in iso format. 
            
        """
        
        
        date    = currentTime.split()[0]
        splitDate = date.split("-")
        end   = splitDate[0] + "-" + splitDate[1] + "-" + "01 00:00:00"       
        
        splitTime   = currentTime.split()
        date        = splitTime[0]
        splitDate   = date.split("-")
        
        if int( splitDate[1] ) != 1 :
            month = int( splitDate[1] ) - 1
            if month < 10 :
                month = "0" + str( month ) 
            splitDate[1] = month
        
        else:
            year = int( splitDate[0] ) - 1
            splitDate[0] = str(year)      
            splitDate[1] = "01"
        
        firstDayOfPreviousMonth = str( splitDate[0] ) + "-" + str( splitDate[1] ) + "-01" 
        start = firstDayOfPreviousMonth + " 00:00:00"           
        
        return start, end 
    
    getStartEndFromPreviousMonth = staticmethod( getStartEndFromPreviousMonth )         
        
    
    
    def getStartEndFromPreviousYear( currentTime ):
        """
            Returns the start and end time of
            the day prior to the currentTime. 
            
            currentTime must be in iso format.       
            start and end are returned in iso format. 
            
        """      
        
        year = currentTime.split("-")[0]
        year = str( int(year)-1 )
        start = year + "-01-01 00:00:00"    
        
        year = currentTime.split("-")[0]
        end  = year + "-01-01 00:00:00"    
        
        return start, end         
        
    getStartEndFromPreviousYear = staticmethod( getStartEndFromPreviousYear )        
        
    
    
    def getStartEndFromCurrentDay( currentTime ):
        """
            Returns the start and end time of
            the current day. 
            
            currentTime must be in iso format.       
            start and end are returned in iso format. 
            
        """       
        
        start    = StatsDateLib.getIsoTodaysMidnight( currentTime )
        tomorrow = StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch( currentTime ) + 24*60*60 )
        end      = StatsDateLib.getIsoTodaysMidnight( tomorrow )
        
        return start, end 
            
    getStartEndFromCurrentDay = staticmethod( getStartEndFromCurrentDay )            
        
    
    
    def getStartEndFromCurrentWeek( currentTime ):
        """
            Returns the start and end time of
            the currentweek. 
            
            currentTime must be in iso format.       
            start and end are returned in iso format. 
            
        """       
        
        currentTimeInSecs = StatsDateLib.getSecondsSinceEpoch( currentTime )
        weekDay     = int(time.strftime( "%w", time.gmtime( currentTimeInSecs ) ))
        
        endInSecs   = currentTimeInSecs + ( ( 7 - weekDay)*24*60*60 )
        end         = StatsDateLib.getIsoTodaysMidnight( StatsDateLib.getIsoFromEpoch( endInSecs ) )   
        
        
        startInSecs = currentTimeInSecs - ( weekDay*24*60*60 )
        start       = StatsDateLib.getIsoTodaysMidnight( StatsDateLib.getIsoFromEpoch( startInSecs ) ) 
        
        
        return start, end         
            
    getStartEndFromCurrentWeek = staticmethod( getStartEndFromCurrentWeek )        
            
    
    
    def getStartEndFromCurrentMonth( currentTime ):
        """
            Returns the start and end time of
            the currentDay. 
            
            currentTime must be in iso format.       
            start and end are returned in iso format. 
            
        """       
        
        splitTime   = currentTime.split()
        date        = splitTime[0]
        splitDate   = date.split( "-" )
        start       = splitDate[0] + "-" + splitDate[1] + "-01 00:00:00"
        
        if int( splitDate[1] ) != 12 :
            month = int( splitDate[1] ) + 1
            if month < 10: 
                month = "0" + str( month ) 
            splitDate[1] = month
        
        else:
            year = int( splitDate[0] ) + 1
            splitDate[0] = str(year)      
            splitDate[1] = "01"
            
            
        firstDayOfMonth = str( splitDate[0] ) + "-" + str( splitDate[1] ) + "-01" 
        end = firstDayOfMonth + " 00:00:00" 
            
        return start, end         
            
    getStartEndFromCurrentMonth = staticmethod( getStartEndFromCurrentMonth )            
        
    
    
    def getStartEndFromCurrentYear( currentTime ):
        """
            Returns the start and end time of
            the currentDay. 
            
            currentTime must be in iso format.       
            start and end are returned in iso format. 
            
        """       
        
        year = currentTime.split("-")[0]
        start  = year + "-01-01 00:00:00" 
        
        year = currentTime.split("-")[0]
        year = str( int(year)+1 )
        end = year + "-01-01 00:00:00"    
            
        return start, end                              
    
    getStartEndFromCurrentYear = staticmethod( getStartEndFromCurrentYear )     

        
    def getHoursFromIso( iso = '2005-08-30 20:06:59' ):
        """
            Returns the hours field from a iso format date. 
        
        """
        
        
        iso = iso.split(" ")[1]
        hours, minutes, seconds = iso.split(':')
        
        return hours
    
    getHoursFromIso = staticmethod( getHoursFromIso )
    
    
    
    def getMinutesFromIso( iso = '2005-08-30 20:06:59' ):
        """
            Returns the minute field from a iso format date. 
        
        """
        
        hours, minutes, seconds = iso.split(':')
        
        return minutes
    
    getMinutesFromIso = staticmethod( getMinutesFromIso )
    
    
    
    def rewindXDays( date  = '2005-08-30 20:06:59' , x = 0 ):
        """
            Takes an iso format date and substract the number 
            of days specified by x.
            
        """
        
        seconds = StatsDateLib.getSecondsSinceEpoch( date )  
        seconds = seconds - ( x * 24*60*60 )
        
        rewindedDate = StatsDateLib.getIsoFromEpoch( seconds )    
          
        return rewindedDate
        
        
        
    rewindXDays = staticmethod( rewindXDays )         
    
    
    
    def getNumberOfDaysBetween( date1 = '2005-08-30 20:06:59', date2 = '2005-08-30 20:06:59'   ):
        """
            
            Takes two iso format dates and returns the number of days between them 
        
        """
    
        seconds1 = StatsDateLib.getSecondsSinceEpoch( date1 ) - StatsDateLib.getSecondsSinceStartOfDay( date1 )
        seconds2 = StatsDateLib.getSecondsSinceEpoch( date2 ) - StatsDateLib.getSecondsSinceStartOfDay( date2 )
        
        numberOfDays = abs( float( (seconds1-seconds2) /( 24*60*60 ) ) )
        
	numberOfDays = int( numberOfDays )
	
        return numberOfDays
    
    
    
    getNumberOfDaysBetween = staticmethod( getNumberOfDaysBetween )
    
    
    
    def areDifferentDays( date1 = '2005-08-30 20:06:59', date2 = '2005-08-30 20:06:59'   ):
        """
            
            Takes two iso format dates and returns whether or not both date are on different days.  
           
        """
    
        day1 = date1.split( " " )[0]
        day2 = date2.split( " " )[0]
        
        return day1 != day2
        
    areDifferentDays = staticmethod( areDifferentDays )    
    
    
    
    def getSecondsSinceEpoch(date='2005-08-30 20:06:59', format='%Y-%m-%d %H:%M:%S'):
        
        try:
            timeStruct = time.strptime(date, format)
        except:
            print "date tried : %s" %date
            
        return time.mktime(timeStruct)
            
    
    getSecondsSinceEpoch = staticmethod( getSecondsSinceEpoch )
    
    
    
    def getIsoLastMinuteOfDay( iso = '2005-08-30 20:06:59' ):
        """
            Takes an iso format date like 2005-08-30 20:06:59.
            Replaces hour, minutes and seconds by last minute of day.
            Returns 2005-08-30 23:59:59.
        
        """
        
        iso = iso.split( " " )
        iso = iso[0]
        iso = iso + " 23:59:59"
        
        return iso 
        
    
    getIsoLastMinuteOfDay = staticmethod( getIsoLastMinuteOfDay )
    
    
    
    def getIsoTodaysMidnight( iso ):
        """
            Takes an iso format date like 2005-08-30 20:06:59.
            Replaces hour, minutes and seconds by 00.
            Returns 2005-08-30 00:00:00.
        
        """
        
        iso = iso.split( " " )
        iso = iso[0]
        iso = iso + " 00:00:00"
        
        return iso 
        
    getIsoTodaysMidnight = staticmethod( getIsoTodaysMidnight ) 
    
        
    
    def getIsoWithRoundedHours( iso ):
        """
            Takes an iso format date like 2005-08-30 20:06:59.
            Replaces minutes and seconds by 00.
            Returns 2005-08-30 20:00:00.
        
        """
        
        iso = iso.split( ":" )
        iso = iso[0]
        iso = iso + ":00:00"
        
        return iso 
        
    getIsoWithRoundedHours = staticmethod( getIsoWithRoundedHours ) 
    
    
    
    def getIsoWithRoundedSeconds( iso ):
        """
            Takes a numbers of seconds since epoch and tranforms it in iso format
            2005-08-30 20:06:59. Replaces minutes and seconds by 00 thus returning
            2005-08-30 20:00:00.
        
        """
        
        #print "iso before modif : %s" %iso 
        iso = iso.split( ":" )
        iso = iso[0] + ":" + iso[1] + ":00"
        
        return iso 
        
    getIsoWithRoundedSeconds = staticmethod( getIsoWithRoundedSeconds ) 
    
    
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
        
        dashedDate = '%Y-%m-%d %H:%M:%S' %date
          
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
    
    
    def getSecondsSinceStartOfDay( date='2005-08-30 20:06:59' ):
        """
            This method receives an iso date as parameter and returns the number of seconds 
            wich have passed since the start of that day.            
        
        """
     
        
        try:
            
            splitDate = date.split( " " )
            splitDate = splitDate[1]
            splitDate = splitDate.split( ":" )
            
            minutesSinceStartOfDay = ( int( splitDate[0] ) * 60 *60 ) + ( int( splitDate[1] ) *60 ) + int( splitDate[2] ) 
            
            return minutesSinceStartOfDay
        
        except:
            
            print "Cannot convert %s in getMinutesSinceStartOfDay. " %date 
            sys.exit()
    

    getSecondsSinceStartOfDay = staticmethod( getSecondsSinceStartOfDay ) 
    
    
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
        
    
    
    def getIsoFromEpoch( seconds ):
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
         
        originalDate = splitTimeString[4] + '-' + StatsDateLib.getNumericMonthFromString ( splitTimeString[1] ) + '-' + splitTimeString[2] + ' ' + splitTimeString[3]   
        
        return originalDate
    
    getIsoFromEpoch = staticmethod ( getIsoFromEpoch )
  
    
    
    
    def getOriginalHour( seconds ):
        """
            Take a number of seconds built with getSecondsSinceEpoch
            and returns a date in the format of '2005-08-30 20:06:59'
            Thu May 18 13:00:00 2006     
        
        """
        
        timeString = time.ctime( seconds )
        splitTimeString = timeString.split( " " )
        originalHour = splitTimeString[3]
        
        originalHour = originalHour.split( ":" )
        originalHour = originalHour[0]
        
        return originalHour
    
    getOriginalHour = staticmethod ( getOriginalHour )  
    
    
    
    def getSeparators( width=DAY, interval = 20*MINUTE ):
        
        separators = []
        
        for value in range( interval, width+interval, interval ):
            separators.append( value )
        
        return separators 
    
    getSeparators = staticmethod( getSeparators )
    
    
    
    def getSeparatorsWithStartTime( startTime = "2006-06-06 00:00:00", width=DAY, interval=60*MINUTE ):
        """
            This method works exactly like getSeparators but it uses a start time to set 
            the separators
        
        """    
        
        separators = []
        
        startTime = StatsDateLib.getSecondsSinceEpoch(startTime)
        
        if interval <= width :
            
            for value in range( int(interval+startTime), int( width+interval+startTime ), int( interval ) ):
                separators.append( StatsDateLib.getIsoFromEpoch(value) )
            
            if separators[ len(separators)-1 ] > width+startTime :
                separators[ len(separators)-1 ] = StatsDateLib.getIsoFromEpoch(width+startTime)
            
        return separators 
        
    getSeparatorsWithStartTime = staticmethod( getSeparatorsWithStartTime )


if __name__ == "__main__":

    print "StatsDateLib.getIsoFromEpoch() : %s" %StatsDateLib.getIsoFromEpoch( 0)
    print "StatsDateLib.getNumberOfDaysBetween( ) : %s" %StatsDateLib.getNumberOfDaysBetween( '2005-08-31 00:00:01','2005-08-30 23:59:59' )
    
    
    
    
       