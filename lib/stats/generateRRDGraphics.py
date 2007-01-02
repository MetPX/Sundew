#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#######################################################################################
##
## Name   : generateRRDGraphics.py 
##  
## Author : Nicholas Lemay  
##
## Date   : October 2nd 2006
##
## Goal   : This files contains all the methods needed to generate graphics using data  
##          found in RRD databases.
##          
##          
##          
#######################################################################################


import os, time, getopt, rrdtool, shutil  
import ClientStatsPickler, MyDateLib, pickleMerging, PXManager, PXPaths, transferPickleToRRD

from   ClientStatsPickler import *
from   optparse  import OptionParser
from   PXPaths   import *
from   PXManager import *
from   MyDateLib import *
from   Logger    import *     
from   Logger    import *       


PXPaths.normalPaths()

LOCAL_MACHINE = os.uname()[1]
    
    
class _GraphicsInfos:

    def __init__( self, fileType, types, totals, clientNames = None ,  timespan = 12, startTime = None, endTime = None, machines = ["pdsGG"], copy = False  ):            
        
        self.fileType     = fileType          # Type of log files to be used.    
        self.types        = types             # Type of graphics to produce. 
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        self.timespan     = timespan          # Number of hours we want to gather the data from.
        self.startTime    = startTime         # Time where graphic(s) starts 
        self.endTime      = endTime           # Time where graphic(s) ends.
        self.machines     = machines          # Machine from wich we want the data to be calculated.
        self.totals       = totals            # Make totals of all the specified clients 
        self.copy         = copy              # Whether or not to create copies of the images. 
        
        
        
#################################################################
#                                                               #
#############################PARSER##############################
#                                                               #
#################################################################   
def getStartEndFromPreviousDay( currentTime, nbDays = 1  ):
    """
        Returns the start and end time of
        the day prior to the currentTime. 
        
        currentTime must be in iso format.       
        start and end are returned in iso format. 
        
    """
    
    end       = MyDateLib.getIsoTodaysMidnight( currentTime )
    yesterday = MyDateLib.getIsoFromEpoch( MyDateLib.getSecondsSinceEpoch( currentTime ) - (24*60*60)  ) 
    start     = MyDateLib.getIsoTodaysMidnight( yesterday ) 
    
    return start, end 

    
    
def getStartEndFromPreviousWeek( currentTime, nbWeeks = 1 ):
    """
        Returns the start and end time of
        the week prior to the currentTime. 
        
        currentTime must be in iso format.       
        start and end are returned in iso format. 
        
    """
    
    currentTimeInSecs = MyDateLib.getSecondsSinceEpoch( currentTime )
    weekDay     = int(time.strftime( "%w", time.gmtime( currentTimeInSecs ) ))
    endInSecs   = currentTimeInSecs - ( weekDay*24*60*60 )
    startInSecs = endInSecs - ( 7*24*60*60 )
    start       = MyDateLib.getIsoTodaysMidnight( MyDateLib.getIsoFromEpoch( startInSecs ) ) 
    end         = MyDateLib.getIsoTodaysMidnight( MyDateLib.getIsoFromEpoch( endInSecs ) )   
    
    return start, end 


    
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
    
    
    
def getStartEndFromCurrentDay( currentTime ):
    """
        Returns the start and end time of
        the current day. 
        
        currentTime must be in iso format.       
        start and end are returned in iso format. 
        
    """       
    
    start    = MyDateLib.getIsoTodaysMidnight( currentTime )
    tomorrow = MyDateLib.getIsoFromEpoch( MyDateLib.getSecondsSinceEpoch( currentTime ) + 24*60*60 )
    end      = MyDateLib.getIsoTodaysMidnight( tomorrow )
    
    return start, end 
        
        
def getStartEndFromCurrentWeek( currentTime ):
    """
        Returns the start and end time of
        the currentweek. 
        
        currentTime must be in iso format.       
        start and end are returned in iso format. 
        
    """       
    
    currentTimeInSecs = MyDateLib.getSecondsSinceEpoch( currentTime )
    weekDay     = int(time.strftime( "%w", time.gmtime( currentTimeInSecs ) ))
    
    endInSecs   = currentTimeInSecs + ( ( 7 - weekDay)*24*60*60 )
    end         = MyDateLib.getIsoTodaysMidnight( MyDateLib.getIsoFromEpoch( endInSecs ) )   
    
    
    startInSecs = currentTimeInSecs - ( weekDay*24*60*60 )
    start       = MyDateLib.getIsoTodaysMidnight( MyDateLib.getIsoFromEpoch( startInSecs ) ) 
    
    
    return start, end         
        
        
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
    
    
    
def getOptionsFromParser( parser ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the infos variable.   
    
        If errors are encountered in parameters used, it will immediatly terminate 
        the application. 
    
    """ 
    
    date   = []
    
    ( options, args )= parser.parse_args()        
    timespan         = options.timespan
    machines         = options.machines.replace( ' ','').split(',')
    clientNames      = options.clients.replace( ' ','' ).split(',')
    types            = options.types.replace( ' ', '').split(',')
    date             = options.date.replace('"','').replace("'",'')
    fileType         = options.fileType.replace("'",'')
    individual       = options.individual
    totals           = options.totals
    daily            = options.daily
    weekly           = options.weekly
    monthly          = options.monthly
    yearly           = options.yearly    
    fixedCurrent     = options.fixedCurrent
    fixedPrevious    = options.fixedPrevious
    copy             = options.copy
    
    counter = 0  
    specialParameters = [daily, monthly, weekly, yearly]
    for specialParameter in specialParameters:
        if specialParameter:
            counter = counter + 1 
            
    if counter > 1 :
        print "Error. Only one of the daily, weekly and yearly options can be use at a time " 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
    
    elif counter == 1 and timespan != None :
        print "Error. When using the daily, the weekly or the yearly options timespan cannot be specified. " 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
        
    elif counter == 0:    
        if fixedPrevious or fixedCurrent:
            print "Error. When using one of the fixed options, please use either the -d -m -w or -y options. " 
            print "Use -h for help."
            print "Program terminated."
            sys.exit()
        
        if copy :
            if daily or not( weekly or monthly or yearly ):
                print "Error. Copying can only be used with the -m -w or -y options. " 
                print "Use -h for help."
                print "Program terminated."        
            
                
    if counter == 0 and timespan == None :
        timespan = 12
    if fixedPrevious and fixedCurrent:
        print "Error. Please use only one of the fixed options,either fixedPrevious or . " 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()  
    
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( date, '%Y-%m-%d %H:%M:%S' )
        split = date.split()
        date = "%s %s" %( split[0], split[1] )

    except:    
        print "Error. The date format must be YYYY-MM-DD HH:MM:SS" 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()    
        
     
    #fix timeSpan method???   
    if daily :
        timespan = 24
    elif weekly:
        timespan = 24 * 7
    elif monthly:
        timespan = 24 * 30     
    elif yearly:
        timespan = 24 * 365   
    
    #fix start and end method???    
    if fixedPrevious :
        if daily :
            start, end = getStartEndFromPreviousDay( date )  
        elif weekly:
            start, end = getStartEndFromPreviousWeek( date )
        elif monthly:
            start, end = getStartEndFromPreviousMonth( date )
        elif yearly:
            start, end = getStartEndFromPreviousYear( date )
            
    elif fixedCurrent:
        if daily :
            start, end = getStartEndFromCurrentDay( date )   
        elif weekly:
            start, end = getStartEndFromCurrentWeek( date )
        elif monthly:
            start, end = getStartEndFromCurrentMonth( date )    
        elif yearly:
            start, end = getStartEndFromCurrentYear( date ) 
    
    else:        
        start = MyDateLib.getIsoFromEpoch( MyDateLib.getSecondsSinceEpoch( date ) - timespan*60*60 ) 
        end   = date                        
                               
    try:    
        if int( timespan ) < 1 :
            raise 
                
    except:
        
        print "Error. The timespan value needs to be an integer one above 0." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
        
        
  
    if fileType != "tx" and fileType != "rx":
        print "Error. File type must be either tx or rx."
        print 'Multiple types are not accepted.' 
        print "Use -h for additional help."
        print "Program terminated."
        sys.exit()            
        
        
    if clientNames[0] == "ALL":
        rxNames, txNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machines[0] )
        #get rx tx names accordingly.         
        if fileType == "tx":    
            clientNames = txNames  
        else:
            clientNames = rxNames    
            
    
    try :
        
        if fileType == "tx":       
        
            validTypes = [ "latency", "bytecount", "errors", "filesOverMaxLatency", "filecount" ]
            
            if types[0] == "All":
                types = validTypes
            else :
                for t in types :
                    if t not in validTypes:
                        raise Exception("")
                        
        else:      
            
            validTypes = [ "bytecount", "errors", "filecount" ]
            
            if types[0] == "All":
                types = validTypes
            
            else :
                for t in types :
                    if t not in validTypes:
                        raise Exception("")

    except:    

        print "Error. With %s fileType, possible data types values are : %s." %( fileType, validTypes )
        print 'For multiple types use this syntax : -t "type1,type2"' 
        print "Use -h for additional help."
        print "Program terminated."
        sys.exit()
  
            
    if individual != True :        
        combinedMachineName = ""
        for machine in machines:
            combinedMachineName = combinedMachineName + machine
                    
        machines = [ combinedMachineName ]              
                
    
    
    end = MyDateLib.getIsoWithRoundedHours( end )
    
    infos = _GraphicsInfos( startTime = start, endTime = end, clientNames = clientNames, types = types, timespan = timespan, machines = machines, fileType = fileType, totals = totals, copy = copy  )   
            
    return infos                       


def createParser( ):
    """ 
        Builds and returns the parser 
    
    """
    
    usage = """

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************

Defaults :

- Default Client is the entire tx/rx list that corresponds to the list of machine passed in parameter.
- Default Date is current system time.  
- Default Types value is "bytecount", "errors", "filecount" for rx and 
  "latency", "bytecount", "errors", "filesOverMaxLatency", "filecount"
  for tx.
- Default span is 12 hours.
- Accepted values for types are the same as default types.
- To use mutiple types, use -t|--types "type1,type2"
 

Options:
 
    - With -c|--clients you can specify the clients names on wich you want to collect data. 
    - With -d|--daily you can specify you want daily graphics.
    - With --date you can specify the time of the request.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log fiels that will be used.  
    - With -m|--monthly you can specify you want monthly graphics.
    - With   |--machines you can specify from wich machine the data is to be used.
    - With -s|--span you can specify the time span to be used to create the graphic 
    - With -t|--types you can specify what data types need to be collected
    - With -y|--yearly you can specify you want yearly graphics.
            
    
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -e "2006-10-10 15:13:00" -s 12 
     --machines "pds1" -f tx                 --> Generate all avaibable graphic types for every tx 
                                                 client found on the machine named pds1. Graphics will
                                                 be 12 hours wide and will end at 15:00:00.  
Ex3: %prog -e "2006-10-10 15:13:00" -y 
     --machines "pds1"                       --> Generate all yearly graphics for all tx and rx clients
                                                 associated with the machine named pds1. 
                                                                                                
********************************************
* See /doc.txt for more details.           *
********************************************"""   
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """
        This method is used to add all available options to the option parser.
        
    """
    
    
    
    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default="ALL",
                        help="Clients' names")
    
    parser.add_option("-d", "--daily", action="store_true", dest = "daily", default=False, help="Create daily graph(s).")
    
    parser.add_option( "--date", action="store", type="string", dest="date", default=MyDateLib.getIsoFromEpoch( time.time() ), help="Decide end time of graphics. Usefull for testing.")
    
    parser.add_option("-f", "--fileType", action="store", type="string", dest="fileType", default='tx', help="Type of log files wanted.")                     
    
    parser.add_option( "--fixedPrevious", action="store_true", dest="fixedPrevious", default=False, help="Do not use floating weeks|days|months|years. Use previous fixed interval found.")
   
    parser.add_option( "--fixedCurrent", action="store_true", dest="fixedCurrent", default=False, help="Do not use floating weeks|days|months|years. Use current fixed interval found.")
    
    parser.add_option("-i", "--individual", action="store_true", dest = "individual", default=False, help="Dont combine data from specified machines. Create graphs for every machine independently")
    
    parser.add_option( "--copy", action="store_true", dest = "copy", default=False, help="Create a copy file for the generated image.")
        
    parser.add_option("-m", "--monthly", action="store_true", dest = "monthly", default=False, help="Create monthly graph(s).")
     
    parser.add_option( "--machines", action="store", type="string", dest="machines", default=LOCAL_MACHINE, help = "Machines for wich you want to collect data." )   
    
    parser.add_option("-s", "--span", action="store",type ="int", dest = "timespan", default=None, help="timespan( in hours) of the graphic.")
       
    parser.add_option("-t", "--types", type="string", dest="types", default="All",help="Types of data to look for.")   
    
    parser.add_option("--totals", action="store_true", dest = "totals", default=False, help="Create graphics based on the totals of all the values found for all specified clients or for a specific file type( tx, rx ).")
    
    parser.add_option("-w", "--weekly", action="store_true", dest = "weekly", default=False, help="Create weekly graph(s).")
    
    parser.add_option("-y", "--yearly", action="store_true", dest = "yearly", default=False, help="Create yearly graph(s).")
    
    
        
def buildTitle( type, client, endTime, timespan, minimum, maximum, mean  ):
    """
        Returns the title of the graphic based on infos. 
    
    """
    
    span = timespan
    timeMeasure = "hours"
    
    if span%(365*24) == 0 :
        span = span/(365*24)
        timeMeasure = "year(s)" 
    
    elif span%(30*24) == 0 :
        span = span/(30*24)
        timeMeasure = "month(s)" 
    
    elif span%24 == 0 :
        span = span/24
        timeMeasure = "day(s)" 
    
    type = type[0].upper() + type[1:] 
       
    return  "%s for %s for a span of %s %s ending at %s." %( type, client, span, timeMeasure, endTime )    

    
 
def getAbsoluteMin( databaseName, startTime, endTime, logger = None ):
    """
        This methods returns the minimum of the entire set of data found between 
        startTime and endTime within the specified database name.
        
        In most case this will be a different min than the visible min found
        on the graphic since the drawn points usually show the total or average of 
        numerous data entries.
        
    
    """
    
    minimum = None 
    
    try :  
    
        output = rrdtool.fetch( databaseName, 'MIN', '-s', "%s" %startTime, '-e', '%s' %endTime )
        minTuples = output[2]
        
        i = 0 
        while i < len( minTuples ):
            if minTuples[i][0] != 'None' and minTuples[i][0] != None  :       
                                
                if minTuples[i][0] < minimum or minimum == None : 
                    minimum = minTuples[i][0]
                    #print minimum
            i = i + 1 
       
         
    except :
        if logger != None:
            logger.error( "Error in generateRRDGraphics.getOverallMin. Unable to read %s" %databaseName )
        pass    
        
    return minimum
    
    
    
def getAbsoluteMax( databaseName, startTime, endTime, logger = None ):
    """
        This methods returns the max of the entire set of data found between 
        startTime and endTime within the specified database name.        
                
        In most case this will be a different max than the visible max found
        on the graphic since the drawn points usually show the total or average of 
        numerous data entries.
        
    """  
    
    maximum = None
    
    try:
    
        output = rrdtool.fetch( databaseName, 'MAX', '-s', "%s" %startTime, '-e', '%s' %endTime )      
        
        maxTuples = output[2]
        
        for maxTuple in maxTuples :
            if maxTuple[0] != 'None' and maxTuple[0] != None :
                if maxTuple[0] > maximum : 
                    maximum = maxTuple[0]

    
    except :
        if logger != None:
            logger.error( "Error in generateRRDGraphics.getOverallMin. Unable to read %s" %databaseName )
        pass    
    
    return maximum 
 
    
       
def getAbsoluteMean( databaseName, startTime, endTime, logger = None  ):
    """
        This methods returns the mean of the entire set of data found between 
        startTime and endTime within the specified database name.
        
                
        In most case this will be a different mean than the visible mean found
        on the graphic since the drawn points usually show the total or average of 
        numerous data entries.
        
    """
    
    sum = 0 
    avg = 0
    
    try :
        
        output = rrdtool.fetch( databaseName, 'AVERAGE', '-s', "%s" %startTime, '-e', '%s' %endTime )

        meanTuples = output[2]
        i = 0
        for meanTuple in meanTuples :            
            if meanTuple[0] != 'None' and meanTuple[0] != None :
                sum = sum + meanTuple[0]
                i = i + 1         
        
        avg = sum / len( meanTuples )  
        
    
    except :
        if logger != None:
            logger.error( "Error in generateRRDGraphics.getOverallMin. Unable to read %s" %databaseName )
        pass    
            
    return avg 


        
def getGraphicsMinMaxMean( databaseName, startTime, endTime, interval, logger = None  ):
    """
        This methods returns the min max and mean of the entire set of data that is drawn 
        on the graphic.
                
    """
    
    min = None
    max = None
    sum = 0 
    avg = 0
    
    try :
        
        output = rrdtool.fetch( databaseName, 'AVERAGE', '-s', "%s" %startTime, '-e', '%s' %endTime )
        meanTuples = output[2]

        for meanTuple in meanTuples :            
            if meanTuple[0] != 'None' and meanTuple[0] != None :
                realValue = ( float(meanTuple[0]) * float(interval) ) 
                if  realValue > max:
                    max = realValue
                if realValue < min or min == None :
                    min = realValue 
                sum = sum + realValue
            
        avg = sum / len( meanTuples )  
    
    except :
        if logger != None:
            logger.error( "Error in generateRRDGraphics.getOverallMin. Unable to read %s" %databaseName )
        pass    
            
    
    return min, max, avg
    
    
    
def buildImageName(  type, client, machine, infos, logger = None ):
    """
        Builds and returns the image name to be created by rrdtool.
        
    """

    span = infos.timespan
    timeMeasure = "hours"
    
    if infos.timespan%(365*24) == 0 :
        span = infos.timespan/(365*24)
        timeMeasure = "years" 
    
    elif infos.timespan%(30*24) == 0 :
        span = infos.timespan/(30*24)
        timeMeasure = "months" 
    
    elif infos.timespan%24 == 0 :
        span = infos.timespan/24
        timeMeasure = "days" 
       
                    
    date = infos.endTime.replace( "-","" ).replace( " ", "_")
    
    fileName = PXPaths.GRAPHS + "others/rrd/%s/%s_%s_%s_%s_%s%s_on_%s.png" %( client, infos.fileType, client, date, type, span, timeMeasure, machine )
    
    
    fileName = fileName.replace( '[', '').replace(']', '').replace(" ", "").replace( "'","" )               
    
    splitName = fileName.split( "/" ) 
    
    if fileName[0] == "/":
        directory = "/"
    else:
        directory = ""
    
    for i in range( 1, len(splitName)-1 ):
        directory = directory + splitName[i] + "/"
    
        
    if not os.path.isdir( directory ):
        os.makedirs( directory, mode=0777 ) 
           
    return fileName 


    
def getDatabaseTimeOfUpdate( client, machine, fileType ):
    """
        If present in DATABASE-UPDATES file, returns the time of the last 
        update associated with the databse name.      
        
        Otherwise returns None 
        
    """ 
    
    lastUpdate = 0
    folder   = PXPaths.STATS + "DATABASE-UPDATES/%s/" %fileType
    fileName = folder + "%s_%s" %( client, machine )
    
    if os.path.isfile( fileName ):
        
        fileHandle  = open( fileName, "r" )
        lastUpdate  = pickle.load( fileHandle )           
        fileHandle.close()     
        
            
    return lastUpdate      


        
def formatMinMaxMean( minimum, maximum, mean, type ):
    """
        Formats min, max and median so that it can be used 
        properly as a label on the produced graphic.
        
    """    
    
    values = [ minimum, maximum, mean]
    
    if type == "bytecount" :
        
        for i in range( len(values) ):
            
            if values[i] != None :
                
                if values[i] < 1000:#less than a k
                    values[i] = "%s Bytes" %int( values[i] )
                    
                elif values[i] < 1000000:#less than a meg 
                    values[i] = "%.2f KiloBytes"  %( values[i]/1000.0 )
                
                elif values[i] < 1000000000:#less than a gig      
                    values[i] = "%.2f MegaBytes"  %( values[i]/1000000.0 )
                
                else:#larger than a gig
                    values[i] = "%.2f GigaBytes"  %( values[i]/1000000000.0 )                 
    
    else:
    
        if minimum != None :
            if type == "latency":
                minimum = "%.2f" %minimum                
            else:
                minimum = "%s" %int(minimum)
                   
        if maximum != None :
            if type == "latency":    
                maximum = "%.2f" %maximum
            else:
                maximum = "%s" %int(maximum)
                
        if mean != None :
            mean = "%.2f" %mean 
        values = [ minimum, maximum, mean]
            
    return values[0], values[1], values[2]            
    
    
            
def getInterval( startTime, timeOfLastUpdate, dataType  ):    
    """
        Returns the interval that was used for data consolidation 
        distance between starTTime being used and the time of the 
        last update of the database. Usefull when using totals
        and and not means.
    
        Will always return 1 if dataType = "latency" because latencies
        cannot be used as totals, only as means.
        
    """    

    if dataType == "latency" :
        interval = 1.0 #No need to multiply average by interval. It's the mean we want in the case of latency.
    elif ( timeOfLastUpdate - startTime ) < (7200 * 60):#less than a week 
        interval = 1.0
    elif ( timeOfLastUpdate - startTime ) < (20160 * 60):#less than two week
        interval = 60.0
    elif (timeOfLastUpdate - startTime) < (1460*240*60):
        interval = 240.0 
    else:
        interval = 1440.0    
        
    return interval


    
def getCopyDestination( type, client, infos ):
    """
       This method returns the absolute path to the copy 
       to create based on the time of creation of the 
       graphic and the span of the graphic.
    
    """
    
    graphicType = "weekly"
    endTimeInSeconds = MyDateLib.getSecondsSinceEpoch( infos.endTime )
    
    
    if infos.timespan >= 365*24:
        graphicType = "yearly"
    elif infos.timespan >= 28*24:
        graphicType = "monthly"    

    if graphicType == "weekly":
        fileName =  time.strftime( "%W", time.gmtime( endTimeInSeconds ) )
    elif graphicType == "monthly":
        fileName =  time.strftime( "%b", time.gmtime( endTimeInSeconds ) )
    elif graphicType == "yearly":
        fileName =  time.strftime( "%Y", time.gmtime( endTimeInSeconds ) )
    
    
    destination = PXPaths.GRAPHS + "webGraphics/%s/%s/%s/%.50s.png" %( graphicType, type , client, fileName )
    
    return destination    
    
         
    
def createCopy( client, type, imageName, infos ):
    """
        Create a copy in the appropriate 
        folder to the file named imageName.
        
    """ 
   
    src         = imageName
    destination = getCopyDestination( type, client, infos )

    if not os.path.isdir( os.path.dirname( destination ) ):
        os.makedirs( os.path.dirname( destination ), mode=0777 )                                                      
    
    if os.path.isfile( destination ):
        os.remove( destination )  
          
    shutil.copy( src, destination ) 
     
    
    
def plotRRDGraph( databaseName, type, fileType, client, machine, infos, lastUpdate = None, logger = None ):
    """
        This method is used to produce a rrd graphic.
        
    """
    
    
    imageName  = buildImageName( type, client, machine, infos, logger )     
    start      = int ( MyDateLib.getSecondsSinceEpoch ( infos.startTime ) ) 
    end        = int ( MyDateLib.getSecondsSinceEpoch ( infos.endTime ) )  
   
    
    if lastUpdate == None :
        lastUpdate = getDatabaseTimeOfUpdate( client, machine, fileType )
    
    
    interval = getInterval( start, lastUpdate, type  )
        
    minimum, maximum, mean = getGraphicsMinMaxMean( databaseName, start, end, interval )
    minimum, maximum, mean = formatMinMaxMean( minimum, maximum, mean, type )            
            
    if type == "latency" or type == "filesOverMaxLatency":
        innerColor = "cd5c5c"
        outerColor = "8b0000"
    elif type == "bytecount" or type == "filecount" :
        innerColor = "019EFF"
        outerColor = "4D9AA9"  
    else:
        innerColor = "54DE4F"
        outerColor = "1C4A1A"     
                   
    title = buildTitle( type, client, infos.endTime, infos.timespan, minimum, maximum, mean )

#     try:
    rrdtool.graph( imageName,'--imgformat', 'PNG','--width', '800','--height', '200','--start', "%i" %(start) ,'--end', "%s" %(end), '--vertical-label', '%s' %type,'--title', '%s'%title,'COMMENT: Minimum: %s     Maximum: %s     Mean: %s\c' %( minimum, maximum, mean), '--lower-limit','0','DEF:%s=%s:%s:AVERAGE'%( type, databaseName, type), 'CDEF:realValue=%s,%i,*' %( type, interval), 'AREA:realValue#%s:%s' %( innerColor, type ),'LINE1:realValue#%s:%s'%( outerColor, type ) )

    if infos.copy == True:
        createCopy( client, type, imageName, infos )
    
    print "Plotted : %s" %imageName
    if logger != None:
        logger.info(  "Plotted : %s" %imageName )
       
    
#     except :
#         if logger != None:
#             logger.error( "Error in generateRRDGraphics.plotRRDGraph. Unable to generate %s" %imageName )
#         pass     

        
        
def createNewDatabase( fileType, type, machine, start, infos, logger ):       
    """
        Creates a brand new database bases on fileType,type and machine.
        
        If a database with the same name allready exists, it will be removed.
        
        Databases are created with rras that are identical to those found in the 
        transferPickleToRRD.py file. If databases are to change there they must be
        changed here also.  
    
    """
    
    combinedDatabaseName = PXPaths.STATS + "databases/combined/%s_%s_%s" %( fileType, type, machine )
     
        
    if os.path.isfile( combinedDatabaseName ):
        status, output = commands.getstatusoutput("rm %s " %combinedDatabaseName )
        
    elif not os.path.isdir( PXPaths.STATS + "databases/combined/" ):
        os.makedirs( PXPaths.STATS + "databases/combined/" )       
    
    if infos.timespan <(5*24):#daily :
        start = start - 60
        rrdtool.create( combinedDatabaseName, '--start','%s' %( start ), '--step', '60', 'DS:%s:GAUGE:60:U:U' %type,'RRA:AVERAGE:0:1:7200','RRA:MIN:0:1:7200', 'RRA:MAX:0:1:7200' )
             
    
    elif infos.timespan >(5*24) and infos.timespan <(14*24):# weekly :  
        start = start - (60*60)
        rrdtool.create( combinedDatabaseName, '--start','%s' %( start ), '--step', '3600', 'DS:%s:GAUGE:3600:U:U' %type,'RRA:AVERAGE:0:1:336','RRA:MIN:0:1:336', 'RRA:MAX:0:1:336' )               
                   
    
    elif infos.timespan <(365*24):#monthly
        start = start - (240*60)
        rrdtool.create( combinedDatabaseName, '--start','%s' %( start ), '--step', '14400', 'DS:%s:GAUGE:14400:U:U' %type, 'RRA:AVERAGE:0:1:1460','RRA:MIN:0:1:1460','RRA:MAX:0:1:1460' )  
        
    
    else:#yearly
        start = start - (1440*60)
        rrdtool.create( combinedDatabaseName, '--start','%s' %( start ), '--step', '86400', 'DS:%s:GAUGE:86400:U:U' %type, 'RRA:AVERAGE:0:1:3650','RRA:MIN:0:1:3650','RRA:MAX:0:1:3650' ) 
        
    
    return combinedDatabaseName
    
    
    
def getPairsFromAllDatabases( type, machine, start, end, infos, logger=None ):
    """
        This method gathers all the needed between start and end from all the
        databases wich are of the specifed type and from the specified machine.
        
        It then makes only one entry per timestamp, and returns the 
        ( timestamp, combinedValue ) pairs.
        
    """
    
    i = 0
    pairs = []
    typeData = {}
    nbEntries = 0    
    lastUpdate =0     
    
    
    for client in infos.clientNames:#Gather all pairs for that type
        
        databaseName = transferPickleToRRD.buildRRDFileName( type, client, machine )
        status, output = commands.getstatusoutput("rrdtool fetch %s  'AVERAGE' -s %s  -e %s" %( databaseName, start, end) )
        output = output.split( "\n" )[2:]
        typeData[client] = output
    
 
    while lastUpdate ==0 and i < len( infos.clientNames ) : # in case some databases dont exist
        lastUpdate = getDatabaseTimeOfUpdate( infos.clientNames[i], machine, infos.fileType )        
        interval  =  getInterval( start, lastUpdate, "other" )           
        nbEntries = int(( end-start ) / (interval * 60)) + 1 
        i = i + 1
        
        
    for i in range( nbEntries ) :#make total of all clients for every timestamp
        
        total = 0.0
        
        for client in infos.clientNames:
            
            try : 
                data = typeData[client][i].split( ":" )[1].replace(" ", "")
                
                if data != None and data != 'None' and data!= 'nan':
                    total = total + float( data )                   
                
                elif logger != None: 
                    logger.warning( "Could not find data for %s for present timestamp." %(client) )
                         
            except:
                
                if logger != None :                    
                    logger.warning( "Could not find data for %s for present timestamp." %(client) )
                             
        
        if type == "latency":#latency is always an average
            total = total / ( len( output ) )
                     
        
        pairs.append( [typeData[client][i].split( " " )[0].replace( ":", "" ), total] )        

    
    return pairs
    
    
    
def createMergedDatabases( infos, logger = None ):
    """
        Gathers data from all needed databases.
        
        Creates new databases to hold merged data.
        
        Feeds new databases with merged data. 
        
        Returns the list of created databases names.
         
    """            

    dataPairs  = {}
    typeData   = {}
    start      = MyDateLib.getSecondsSinceEpoch ( infos.starTime )  
    end        = MyDateLib.getSecondsSinceEpoch ( infos.endTime )     
    databaseNames = {}
    

    for machine in infos.machines:
        
        for type in infos.types :         
            typeData[type] = {}
            pairs = getPairsFromAllDatabases( type, machine, start, end, infos, logger )                        
            
            combinedDatabaseName = createNewDatabase( infos.fileType, type, machine, start, infos, logger )
                                                     
            databaseNames[type] = combinedDatabaseName                            
                
            for pair in pairs:
                rrdtool.update( combinedDatabaseName, '%s:%s' %( int(pair[0]), pair[1] ) )
                 
                
    return databaseNames
                    
            
            
def generateRRDGraphics( infos, logger = None ):
    """
        This method generates all the graphics. 
                
    """    
        
    if infos.totals: #Graphics based on total values from a group of clients.
        #todo : Make 2 title options
        
        databaseNames = createMergedDatabases( infos, logger )
                
        for machine in infos.machines:
            for type in infos.types:
                plotRRDGraph( databaseNames[type], type, infos.fileType, infos.fileType, machine, infos, lastUpdate =  MyDateLib.getSecondsSinceEpoch( infos.endTime ), logger =logger )
                
    else:
        for machine in infos.machines:
            
            for client in infos.clientNames:
                
                for type in infos.types : 
                    databaseName = transferPickleToRRD.buildRRDFileName( type, client, machine ) 
                    plotRRDGraph( databaseName, type, infos.fileType, client, machine, infos,lastUpdate =  MyDateLib.getSecondsSinceEpoch(infos.endTime), logger = logger )
                


def main():
    """
        Gathers options, then makes call to generateRRDGraphics   
    
    """        
        
    if not os.path.isdir( PXPaths.LOG  ):
        os.makedirs( PXPaths.LOG , mode=0777 )
    
    logger = Logger( PXPaths.LOG  + 'stats_'+'rrd_graphs' + '.log.notb', 'INFO', 'TX' + 'rrd_transfer', bytes = True  ) 
    
    logger = logger.getLogger()
       
    parser = createParser() 
   
    infos = getOptionsFromParser( parser )

    generateRRDGraphics( infos, logger = logger )
    
    
    
if __name__ == "__main__":
    main()    
    