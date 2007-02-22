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
import generalStatsLibraryMethods
from   generalStatsLibraryMethods import *
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

    def __init__( self, fileType, types, totals, graphicType, clientNames = None ,  timespan = 12, startTime = None, endTime = None, machines = ["pdsGG"], copy = False  ):            
        
        self.fileType     = fileType          # Type of log files to be used.    
        self.types        = types             # Type of graphics to produce. 
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        self.timespan     = timespan          # Number of hours we want to gather the data from.
        self.startTime    = startTime         # Time where graphic(s) starts 
        self.endTime      = endTime           # Time where graphic(s) ends.
        self.machines     = machines          # Machine from wich we want the data to be calculated.
        self.totals       = totals            # Make totals of all the specified clients 
        self.copy         = copy              # Whether or not to create copies of the images. 
        self.graphicType  = graphicType       # daily, weekly, monthly yearly or other        
        
       
    
#################################################################
#                                                               #
#############################PARSER##############################
#                                                               #
#################################################################      
def getOptionsFromParser( parser ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the infos variable.   
    
        If errors are encountered in parameters used, it will immediatly terminate 
        the application. 
    
    """ 
    
    date   = []
    graphicType = "other"
    
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
        
     
    #TODO fix timeSpan method???   
    if daily :
        timespan = 24  
        graphicType = "daily"      
    elif weekly:
        timespan = 24 * 7  
        graphicType = "weekly"  
    elif monthly:
        timespan = 24 * 30 
        graphicType = "monthly"       
    elif yearly:
        timespan = 24 * 365
        graphicType = "yearly"   
    
    #TODO :fixStartEnd method???    
    if fixedPrevious :
        if daily :
            start, end = MyDateLib.getStartEndFromPreviousDay( date )             
        elif weekly:
            start, end = MyDateLib.getStartEndFromPreviousWeek( date )
        elif monthly:
            start, end = MyDateLib.getStartEndFromPreviousMonth( date )
        elif yearly:
            start, end = MyDateLib.getStartEndFromPreviousYear( date )
            
    elif fixedCurrent:
        if daily :
            start, end = MyDateLib.getStartEndFromCurrentDay( date )   
        elif weekly:
            start, end = MyDateLib.getStartEndFromCurrentWeek( date )
        elif monthly:
            start, end = MyDateLib.getStartEndFromCurrentMonth( date )    
        elif yearly:
            start, end = MyDateLib.getStartEndFromCurrentYear( date ) 
    
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
    
    infos = _GraphicsInfos( startTime = start, endTime = end, graphicType = graphicType, clientNames = clientNames, types = types, timespan = timespan, machines = machines, fileType = fileType, totals = totals, copy = copy  )   
            
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
    - With --copy you can specify that you want to create a copy of the image file that will 
      be stored in the webGraphics folder in either the weekly, motnhly or yearly section.
    - With -d|--daily you can specify you want daily graphics.
    - With --date you can specify the time of the request.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log fiels that will be used.  
    - With --fixedPrevious you can specify that you want a graphic based on the previous( week, month year)
      based on the fixed dates of the calendar.
    - With --fixedPrevious you can specify that you want a graphic based on the current( week, month year)
      based on the fixed dates of the calendar.
    - With --individual you can specify that you want to genrate graphics for each machine 
      and not the combined data of two machines when numerous machiens are specified.
    - With -m|--monthly you can specify you want monthly graphics.
    - With   |--machines you can specify from wich machine the data is to be used.
    - With -s|--span you can specify the time span to be used to create the graphic 
    - With -t|--types you can specify what data types need to be collected
    - With --totals you can specify that you want a single grpahics for every datatype that
      uses the cmbined data of all the client or sources of a machien or collection of machines instead 
      of creating a graphic per client/source. 
    - With -w|--weekly you can specify you want monthly graphics. 
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
    
    
        
def buildTitle( type, client, endTime, timespan, minimum, maximum, mean, graphicType = "daily"  ):
    """
        Returns the title of the graphic based on infos. 
    
    """    
    
    span        = timespan
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

    
    
def getGraphicsNote( interval, type ):
    """
        Returns the note to be displayed at the bottom of the graphic.
    """
    
    graphicsNote = ""
    
    if type != "latency":
    
        if interval < 60.0 :    
            graphicsNote = "Graphics generated using %s minute(s) averages." %( int(interval) )
        
        else:    
            graphicsNote = "Graphics generated using %s hour(s) averages." %( int(interval/60) )

    
    return graphicsNote    
        
    
             
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


        
def getGraphicsMinMaxMeanTotal( databaseName, startTime, endTime, interval, logger = None, type = "average"  ):
    """
        This methods returns the min max and mean of the entire set of data that is drawn 
        on the graphic.
                
    """
    
    min = None
    max = None
    sum = 0 
    avg = 0
    total = 0.0
    nbEntries = 0      
    
    try :
        
        output = rrdtool.fetch( databaseName, 'AVERAGE', '-s', "%s" %startTime, '-e', '%s' %endTime )
        meanTuples = output[2]
        nbEntries = len( meanTuples )
        
        if type == "totals":
            
            for meanTuple in meanTuples :            
                
                if meanTuple[0] != 'None' and meanTuple[0] != None :
                    
                    realValue = ( float(meanTuple[0]) * float(interval) ) 
                    
                    if  realValue > max:
                        max = realValue
                    if realValue < min or min == None :
                        min = realValue 
                    
                    sum = sum + realValue 
                    
                else:# don't count non-filled entries in mean.
                    nbEntries = nbEntries - 1
                     
            if nbEntries != 0:            
                avg = sum / nbEntries 
            
            
            total = sum
             
        else:
            
            for meanTuple in meanTuples :            
                if meanTuple[0] != 'None' and meanTuple[0] != None :
                    value = float( meanTuple[0] ) 
                    if  value > max:
                        max = value
                    if value < min or min == None :
                        min = value 
                    
                    sum = sum + value               
                                                        
                    
                else:# don't count non-filled entries in mean.
                    nbEntries = nbEntries - 1    
            
            if nbEntries != 0:            
                avg = sum / nbEntries  
            
            total = float( sum ) * float( interval )
            print "total %s interval %s nbentries %s" %(total,interval,nbEntries)           
    
    except :
        if logger != None:
            logger.error( "Error in generateRRDGraphics.getOverallMin. Unable to read %s" %databaseName )
        pass    
            
    
    return min, max, avg, total
    
    
    
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


        
def formatMinMaxMeanTotal( minimum, maximum, mean, total, type, averageOrTotal = "average" ):
    """
        Formats min, max and median so that it can be used 
        properly as a label on the produced graphic.
        
    """    
    
    values = [ minimum, maximum, mean, total ]
    nbEntries = len(values)
    
    if type == "bytecount" :
        
        for i in range( nbEntries ):
            
            if values[i] != None :
                
                if values[i] < 1000:#less than a k
                    if i != nbEntries-1:
                        values[i] = "%s B/Min" %int( values[i] )
                    else:
                        values[i] = "%s Bytes" %int( values[i] )
                
                elif values[i] < 1000000:#less than a meg 
                    if i != nbEntries-1:
                        values[i] = "%.2f KB/Min"  %( values[i]/1000.0 )
                    else:
                        values[i] = "%.2f kiloBytes" %( values[i]/1000.0 )
                
                elif values[i] < 1000000000:#less than a gig      
                    if i != nbEntries-1:
                        values[i] = "%.2f MB/Min"  %( values[i]/1000000.0 )
                    else:
                        values[i] = "%.2f MegaBytes" %( values[i]/1000000.0 )
                
                else:#larger than a gig
                    if i != nbEntries-1:
                        values[i] = "%.2f GB/Min"  %( values[i]/1000000000.0 )                 
                    else:
                        values[i] = "%.2f GigaBytes" %( values[i]/1000000000.0 )
        
    else:
    
        if type == "filecount":
            tag = "Files"
        elif type == "filesOverMaxLatency":
            tag = "F" 
        elif type == "errors":
            tag = "Errors"
        elif type == "latency":
            tag = "Avg"
            
        
        if minimum != None :
            if type == "latency" or averageOrTotal == "average":
                if minimum > 1:
                    minimum = "%.2f %s/Min" %( minimum, tag )
                else: 
                    minimum = "%.4f %s/Min" %( minimum, tag )                
            
            else:
                minimum = "%s" %int( minimum )
                   
        if maximum != None :
            if type == "latency" or averageOrTotal == "average":    
                if maximum > 1:
                    maximum = "%.2f %s/Min" %( maximum, tag ) 
                else:    
                    maximum = "%.4f %s/Min" %( maximum, tag ) 
            else:
                maximum = "%s" %int(maximum)
                
        if mean != None :
            if mean > 1:
                mean = "%.2f %s/Min" %( mean, tag )             
            else:    
                mean = "%.4f %s/Min" %( mean, tag ) 
        
        if type == "filesOverMaxLatency":    
            tag = "Files"
            
        total = "%s %s" %( int(total), tag )           
                    
        values = [ minimum, maximum, mean, total]
            
    return values[0], values[1], values[2], values[3]            
    


def getGraphicsLegend( maximum ):
    """
        Returns the legend according to the 
        unit that is anticipated to be displayed within the graphics.
        Legend is based on the maximum observed.
    """
    
    legend = ""
   
     
    if "KB" in str(maximum):
        legend = "k on the y axis stands for kilo, meaning x thousands."
    elif "MB" in str(maximum):
        legend = "M on the y axis stands for Mega, meaning x millions."
    elif "GB" in str(maximum):
        legend = "G on the y axis stats for giga, meaning x billions."
    else:
        
        try:
            maximum = float( str(maximum).split(" ")[0] )          
            
            if maximum > 1000000000:
                legend = "G on the y axis stats for giga, meaning x billions."
            elif maximum > 1000000:
                legend = "M on the y axis stands for Mega, meaning x millions."
            elif maximum > 1000:    
                legend = "k on the y axis stands for kilo, meaning x thousands."
        except:            
            pass
        
    return legend
            
            
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
    elif ( timeOfLastUpdate - startTime ) < (7200 * 60):#less than 5 days
        interval = 1.0         
    elif ( timeOfLastUpdate - startTime ) < (20160 * 60):#less than two week
        interval = 60.0
    elif (timeOfLastUpdate - startTime) < (1460*240*60):
        interval = 240.0 
    else:
        interval = 1440.0    
        
    print "startTime %s, timeOfLastUpdate %s, interval %s" %(startTime, timeOfLastUpdate, interval)
    
    return interval


        
def getIntervalForTotalGraphics( graphicsType ):    
    """
        Returns the interval that was used for data consolidation. 
        
        When total graphics are used, a temporary db is used.        
        wich makes the interval calculation different from other graphics.
        
    """ 
    
    if graphicsType == "daily"   :
        interval = 1.0             
    elif graphicsType == "weekly"  :
        interval = 60.0     
    elif graphicsType == "monthly":
        interval = 240.0                
    elif graphicsType == "yearly":
        interval = 1440.0
        
    return interval    

    
def getCopyDestination( type, client, machine, infos ):
    """
       This method returns the absolute path to the copy 
       to create based on the time of creation of the 
       graphic and the span of the graphic.
       
       Precondition : graphic type must be either weekly, monthly or yearly. 
    
    """
    
    oneDay = 24*60*60
    endTimeInSeconds = MyDateLib.getSecondsSinceEpoch( infos.endTime )
    
    if infos.totals != True:
        
        if infos.graphicType == "weekly":
            fileName =  time.strftime( "%W", time.gmtime( endTimeInSeconds - oneDay ) )
        elif infos.graphicType == "monthly":
            fileName =  time.strftime( "%b", time.gmtime( endTimeInSeconds - oneDay ) )
        elif infos.graphicType == "yearly":
            fileName =  time.strftime( "%Y", time.gmtime( endTimeInSeconds - oneDay ) )
        else:
            fileName = client
        
        destination = PXPaths.GRAPHS + "webGraphics/%s/%s/%s/%.50s.png" %( infos.graphicType, type , client, fileName )
    
    else :
        if infos.graphicType == "weekly":
            fileName =  time.strftime( "%W", time.gmtime( endTimeInSeconds - oneDay ) )
        elif infos.graphicType == "monthly":
            fileName =  time.strftime( "%b", time.gmtime( endTimeInSeconds - oneDay ) )
        elif infos.graphicType == "yearly":
            fileName =  time.strftime( "%Y", time.gmtime( endTimeInSeconds - oneDay ) )
        elif infos.graphicType == "daily":
            fileName =  time.strftime( "%a", time.gmtime( endTimeInSeconds - oneDay ) )
        else:
            fileName = client
        
        destination = "%s/webGraphics/totals/%s/%s/%s/%s/%s.png" %( PXPaths.GRAPHS, machine,infos.fileType, type, infos.graphicType, fileName)
    
    
    return destination    
    
         
    
def createCopy( client, type, machine, imageName, infos ):
    """
        Create a copy in the appropriate 
        folder to the file named imageName.
        
    """ 
   
    src         = imageName
    destination = getCopyDestination( type, client, machine, infos )

    if not os.path.isdir( os.path.dirname( destination ) ):
        os.makedirs( os.path.dirname( destination ), mode=0777 )                                                      
    
    if os.path.isfile( destination ):
        os.remove( destination )  
       
    shutil.copy( src, destination ) 
     
    
    
def formatedTypesForLables( type ):
    """
        Takes the type of a graphic to be drawn
        ( latency, filesOverMaxLatency...) and formats
        it so that it can be used in the graphics labels.
        ( y-axis label and title)       
        
        Will not format an unknown type.
        
    """
    
    formatedTitle  = type 
    formatedYLabel = type
    
    if type == "latency":
        formatedTitle = "Averaged latency per minute"   
        formatedYLabel = "Latency(seconds)"    
    elif type== "filesOverMaxLatency":
        formatedTitle  = "Latencies over 15 seconds"   
        formatedYLabel = "Files/Minute"
    elif type== "bytecount":
        formatedTitle = "Bytes/Minute"     
        formatedYLabel = "Bytes/Minute"    
    elif type== "filecount":
        formatedTitle = "Files/Minute"     
        formatedYLabel = "Files/Minute"   
    elif type== "errors":
        formatedTitle = "Errors/Minute" 
        formatedYLabel = "Errors/Minute"        
            
    return formatedTitle, formatedYLabel
    
    
    
        
def plotRRDGraph( databaseName, type, fileType, client, machine, infos, lastUpdate = None, logger = None ):
    """
        This method is used to produce a rrd graphic.
        
    """
    
    imageName    = buildImageName( type, client, machine, infos, logger )        
    start        = int ( MyDateLib.getSecondsSinceEpoch ( infos.startTime ) ) 
    end          = int ( MyDateLib.getSecondsSinceEpoch ( infos.endTime ) )  
    formatedTitleType, formatedYLabelType = formatedTypesForLables( type )
    
    
    if lastUpdate == None :
        if infos.totals != True:
            lastUpdate = getDatabaseTimeOfUpdate( client, machine, fileType )
            interval = getInterval( start, lastUpdate, type  )
        else:
            lastUpdate = getDatabaseTimeOfUpdate( client = fileType, machine = machine, fileType = "totals" )
            interval   = getIntervalForTotalGraphics(infos.graphicType)
    
          
    minimum, maximum, mean, total = getGraphicsMinMaxMeanTotal( databaseName, start, end, interval )
    minimum, maximum, mean, total = formatMinMaxMeanTotal( minimum, maximum, mean,total, type )            
    graphicsLegeng         = getGraphicsLegend( maximum )      
    graphicsNote           = getGraphicsNote( interval, type  )        
    
    if graphicsNote == "" and graphicsLegeng == "":
        comment = ""
    else:
        comment = "Note(s):"
        
            
    if type == "latency" :
        innerColor = "cd5c5c"
        outerColor = "8b0000"
        total = ""
    elif type == "filesOverMaxLatency":
        innerColor = "cd5c5c"
        outerColor = "8b0000"
        total = "Total: %s" %total                
    elif type == "bytecount" or type == "filecount" :
        innerColor = "019EFF"
        outerColor = "4D9AA9"  
        total = "Total: %s" %total
    else:
        innerColor = "54DE4F"
        outerColor = "1C4A1A"     
        total = "Total: %s" %total   
        
    title = buildTitle( formatedTitleType, client, infos.endTime, infos.timespan, minimum, maximum, mean )   
                
    #note : in CDEF:realValue the i value can be changed from 1 to value of the interval variable
    #       in order to get the total displayed instead of the mean.
    if infos.graphicType != "monthly":
        rrdtool.graph( imageName,'--imgformat', 'PNG','--width', '800','--height', '200','--start', "%i" %(start) ,'--end', "%s" %(end), '--vertical-label', '%s' %formatedYLabelType,'--title', '%s'%title, '--lower-limit','0','DEF:%s=%s:%s:AVERAGE'%( type, databaseName, type), 'CDEF:realValue=%s,%i,*' %( type, 1), 'AREA:realValue#%s:%s' %( innerColor, type ),'LINE1:realValue#%s:%s'%( outerColor, type ), 'COMMENT: Min: %s   Max: %s   Mean: %s   %s\c' %( minimum, maximum, mean,total ), 'COMMENT:%s %s %s\c' %( comment, graphicsNote, graphicsLegeng )  )

    else:#With monthly graphics, we force the use the day of month number as the x label.       
        rrdtool.graph( imageName,'--imgformat', 'PNG','--width', '800','--height', '200','--start', "%i" %(start) ,'--end', "%s" %(end), '--vertical-label', '%s' %formatedYLabelType,'--title', '%s'%title, '--lower-limit','0','DEF:%s=%s:%s:AVERAGE'%( type, databaseName, type), 'CDEF:realValue=%s,%i,*' %( type, 1), 'AREA:realValue#%s:%s' %( innerColor, type ),'LINE1:realValue#%s:%s'%( outerColor, type ), '--x-grid', 'HOUR:24:DAY:1:DAY:1:0:%d','COMMENT: Min: %s   Max: %s   Mean: %s   %s\c' %( minimum, maximum, mean, total ), 'COMMENT:%s %s %s\c' %(comment,graphicsNote, graphicsLegeng)  )       
    
    
    if infos.copy == True:
        createCopy( client, type, machine, imageName, infos )
    
    print "Plotted : %s" %imageName
    if logger != None:
        logger.info(  "Plotted : %s" %imageName )
        
        
        
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
    
    
def getInfosFromDatabases( names, machine, fileType, startTime, endTime ):
    """
        This method browsess a list of database names and returns
        the infos of the first valid databases found.
        
        names, machine and type are used to generate the db names.
        startTime is the time for wich we want to know the interval 
        between itself and the time of the last update of the db.
        
        Return nbEntries, lastUpdate and interval that is used 
        between a certain start time and the time of the last 
        update of that db. 
         
    """
    
    i = 0 
    lastUpdate =0
    nbEntries = 0    
        
    while lastUpdate == 0 and i < len( names) : # in case some databases dont exist
        lastUpdate = getDatabaseTimeOfUpdate( names[i], machine, fileType )        
        interval  =  getInterval( startTime, lastUpdate, "other" )           
        nbEntries = int(( endTime-startTime ) / (interval * 60)) + 1 
        i = i + 1

    return nbEntries, lastUpdate, interval

    
    
def getPairsFromAllDatabases( type, machine, start, end, infos, logger=None ):
    """
        This method gathers all the needed between start and end from all the
        databases wich are of the specifed type and from the specified machine.
        
        It then makes only one entry per timestamp, and returns the 
        ( timestamp, combinedValue ) pairs.
        
    """
    
    pairs = []
    typeData = {}     
       
    
    
    for client in infos.clientNames:#Gather all pairs for that type
        
        databaseName = transferPickleToRRD.buildRRDFileName( type, client, machine )

        status, output = commands.getstatusoutput("rrdtool fetch %s  'AVERAGE' -s %s  -e %s" %( databaseName, start, end) )
        #print "rrdtool fetch %s  'AVERAGE' -s %s  -e %s" %( databaseName, start, end)
        #print output
        output = output.split( "\n" )[2:]
        typeData[client] = output
    
    
    nbEntries, lastUpdate, interval = getInfosFromDatabases(infos.clientNames, machine, infos.fileType, start, end)   
        
    for i in range( nbEntries ) :#make total of all clients for every timestamp
        
        total = None
        
        for client in infos.clientNames:
            #print client
            try : 
                data = typeData[client][i].split( ":" )[1].replace(" ", "")
                
                if data != None and data != 'None' and data!= 'nan':                  
                    
                    try:
                        total = total + ( float( data ) )                                       
                    except:#total == None :
                        total = 0.0
                        total = total + ( float( data ) )                       
                        
                        
                elif logger != None: 
                    logger.warning( "Could not find data for %s for present timestamp." %(client) )
                         
            except:
                
                if logger != None :                    
                    logger.warning( "Could not find data for %s for present timestamp." %(client) )
                             
        
        if type == "latency" and total != None:#latency is always an average
            total = total / ( len( output ) )
                     
        #print "type : %s" %type 
        #print "typeData: %s" %typeData
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
    start      = int( MyDateLib.getSecondsSinceEpoch ( infos.startTime )  )
    end        = int( MyDateLib.getSecondsSinceEpoch ( infos.endTime )    ) 
    databaseNames = {}
    

    for machine in infos.machines:
        
        for type in infos.types :         
            typeData[type] = {}
            pairs = getPairsFromAllDatabases( type, machine, start, end, infos, logger )                        
            
            combinedDatabaseName = createNewDatabase( infos.fileType, type, machine, start, infos, logger )
                                                     
            databaseNames[type] = combinedDatabaseName                            
                
            for pair in pairs:
                if pair[1] != None :
                    rrdtool.update( combinedDatabaseName, '%s:%s' %( int(pair[0]), pair[1] ) )
            
            nbEntries, lastUpdate, interval = getInfosFromDatabases(infos.clientNames, machine, infos.fileType, start, end)
            
            transferPickleToRRD.setDatabaseTimeOfUpdate( client = infos.fileType, machine = machine, fileType = "totals", timeOfUpdate = lastUpdate)                       
                
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
                plotRRDGraph( databaseNames[type], type, infos.fileType,infos.fileType, machine, infos,logger =logger )
                
    else:
        for machine in infos.machines:
            
            for client in infos.clientNames:
                
                for type in infos.types : 
                    databaseName = transferPickleToRRD.buildRRDFileName( type, client, machine ) 
                    plotRRDGraph( databaseName, type, infos.fileType, client, machine, infos,logger = logger )
                


def main():
    """
        Gathers options, then makes call to generateRRDGraphics   
    
    """        
        
    if not os.path.isdir( PXPaths.LOG  ):
        os.makedirs( PXPaths.LOG , mode=0777 )
    
    logger = Logger( PXPaths.LOG  + 'stats_'+'rrd_graphs' + '.log.notb', 'INFO', 'TX' + 'rrd_graphs', bytes = True  ) 
    
    logger = logger.getLogger()
       
    parser = createParser() 
   
    infos = getOptionsFromParser( parser )

    generateRRDGraphics( infos, logger = logger )
    
    
    
if __name__ == "__main__":
    main()    
    