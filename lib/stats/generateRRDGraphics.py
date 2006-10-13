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


import os, time, getopt, rrdtool  
import ClientStatsPickler, MyDateLib, pickleMerging, PXManager, PXPaths, transferPickleToRRD

from   ClientStatsPickler import *
from   optparse  import OptionParser
from   PXPaths   import *
from   PXManager import *
from   MyDateLib import *
from   Logger    import *     
from   Logger    import *       


PXPaths.normalPaths()   



class _GraphicsInfos:

    def __init__( self, directory, fileType, types, clientNames = None ,  timespan = 12, endDate = None, machines = ["pdsGG"]  ):

            
        self.directory    = directory         # Directory where log files are located. 
        self.fileType     = fileType          # Type of log files to be used.    
        self.types        = types             # Type of graphics to produce. 
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        self.timespan     = timespan          # Number of hours we want to gather the data from. 
        self.endDate      = endDate       # Time when stats were queried.
        self.machines     = machines          # Machine from wich we want the data to be calculated.
        
        
        
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
    
    endDate   = []
    
    ( options, args )= parser.parse_args()        
    timespan         = options.timespan
    machines         = options.machines.replace( ' ','').split(',')
    clientNames      = options.clients.replace( ' ','' ).split(',')
    types            = options.types.replace( ' ', '').split(',')
    endDate          = options.endDate.replace('"','').replace("'",'')
    fileType         = options.fileType.replace("'",'')
    individual       = options.individual
    daily            = options.daily
    weekly           = options.weekly
    yearly           = options.yearly    
    
    
    counter = 0  
    specialParameters = [daily, weekly, yearly]
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
    
    elif counter == 0 and timespan == None :
        timespan = 12
    
    if daily == True :
        timeSpan = 24
    elif weekly == True:
        timeSpan = 24 * 7
    elif yearly == True:
        timeSpan = 24 * 365        
         
            
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( endDate, '%Y-%m-%d %H:%M:%S' )
        split = endDate.split()
        endDate = "%s %s" %( split[0], split[1] )

    except:    
        print "Error. The date format must be YYYY-MM-DD HH:MM:SS" 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
    
    
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
        updateConfigurationFiles( machines[0], "pds" )
        #get rx tx names accordingly.         
        if fileType == "tx":    
            clientNames = getNames( "tx",machines[0] )  
        else:
            clientNames = getNames( "rx",machines[0] )      
            
    
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

        print "Error. With %s fileType, possible data types values are : %s." %( fileType,validTypes )
        print 'For multiple types use this syntax : -t "type1,type2"' 
        print "Use -h for additional help."
        print "Program terminated."
        sys.exit()
    
    #workaround because of mirroring
    for i in range( len(machines) ):
        if machines[i] == "pds5":
            machines[i] = "pds3-dev"
        elif machines[i] == "pds6":
            machines[i] = "pds4-dev"
            
            
    if individual != True :        
        combinedMachineName = ""
        for machine in machines:
            combinedMachineName = combinedMachineName + machine
                    
        machines = [ combinedMachineName ]              
    

            
    directory = PXPaths.LOG + localMachine + "/"
    
    endDate = MyDateLib.getIsoWithRoundedHours( endDate )
    
    infos = _GraphicsInfos( endDate = endDate, clientNames = clientNames,  directory = directory , types = types, timespan = timespan, machines = machines, fileType = fileType )   
            
    return infos 
       
    
                
def getNames( fileType, machine ):
    """
        Returns a tuple containg RXnames or TXnames that we've rsync'ed 
        using updateConfigurationFiles
         
    """    
                        
    pxManager = PXManager()
    
    #These values need to be set here.
    PXPaths.RX_CONF  = '/apps/px/stats/rx/%s/'  %machine
    PXPaths.TX_CONF  = '/apps/px/stats/tx/%s/'  %machine
    PXPaths.TRX_CONF = '/apps/px/stats/trx/%s/' %machine
    pxManager.initNames() # Now you must call this method  
    
    if fileType == "tx":
        names = pxManager.getTxNames()               
    else:
        rxNames = pxManager.getRxNames()  

    return names 
        
    
    
def updateConfigurationFiles( machine, login ):
    """
        rsync .conf files from designated machine to local machine
        to make sure we're up to date.
    
    """  
    
    if not os.path.isdir( '/apps/px/stats/rx/%s/' %machine):
        os.makedirs(  '/apps/px/stats/rx/%s/' %machine, mode=0777 )
    if not os.path.isdir( '/apps/px/stats/tx/%s' %machine ):
        os.makedirs( '/apps/px/stats/tx/%s/' %machine , mode=0777 )
    if not os.path.isdir( '/apps/px/stats/trx/%s/' %machine ):
        os.makedirs(  '/apps/px/stats/trx/%s/' %machine, mode=0777 )       

        
    status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/etc/rx/ /apps/px/stats/rx/%s/"  %( login, machine, machine) ) 

    
    status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/etc/tx/ /apps/px/stats/tx/%s/"  %( login, machine, machine) )  



def createParser( ):
    """ 
        Builds and returns the parser 
    
    """
    
    usage = """

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************
Notes :
- Now option not yet implemented.    

Defaults :

- Default Client is the entire tx/rx list that corresponds to the list of machine passed in parameter.
- Default Date is current system time.  
- Default Types value is latency.
- Default span is 12 hours.
- Accepted values for types are : errors,latency,bytecount
  -To use mutiple types, use -t|--types "type1,type2"
- Whether a date is specified or the default current time is used, 

Options:
 
    - With -c|--clients you can specify the clients names on wich you want to collect data. 
    - With -d|--date you can specify the time of the request.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log fiels that will be used.  
    - With -m|--machines you can specify from wich machine the data is to be used.
    - With -s|--span you can specify the time span to be used to create the graphic 
    - With -t|--types you can specify what data types need to be collected
    
      
WARNING: - Client name MUST be specified,no default client exists. 
          
            
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -d "2006-10-10 15:13:00" -s 12 
     -m "pds1" -f tx                         --> Generate all avaibable graphic types for every tx 
                                                 client found on the machine named pds1. Graphics will
                                                 be 12 hours wide and will end at 15:00:00.  
Ex3: %prog -d "2006-10-10 15:13:00" -s 12 
     -m "pds1" -f tx -t "latency,errors"     --> Generate latency and errors graphics for tx client named 
     -c "pds"                                    pds with data found on the machine named pds1. Graphics will
                                                 be 12 hours wide and will end at 15:00:00. 
                                                                                                
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
    
    localMachine = os.uname()[1]
    
    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default="ALL",
                        help="Clients' names")
    
    parser.add_option("-d", "--daily", action="store_true", dest = "daily", default=False, help="Create daily graph(s).")
    
    parser.add_option("-e", "--endDate", action="store", type="string", dest="endDate", default=MyDateLib.getIsoFromEpoch( time.time() ), help="Decide end time of graphics. Usefull for testing.")
    
    parser.add_option("-f", "--fileType", action="store", type="string", dest="fileType", default='tx', help="Type of log files wanted.")                     
    
    parser.add_option("-i", "--individual", action="store_true", dest = "individual", default=False, help="Dont combine data from specified machines. Create graphs for every machine independently")
        
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=localMachine, help = "Machines for wich you want to collect data." )   
    
    parser.add_option("-s", "--span", action="store",type ="int", dest = "timespan", default=None, help="timespan( in hours) of the graphic.")
       
    parser.add_option("-t", "--types", type="string", dest="types", default="All",help="Types of data to look for.")   
    
    parser.add_option("-w", "--weekly", action="store_true", dest = "weekly", default=False, help="Create weekly graph(s).")
    
    parser.add_option("-y", "--yearly", action="store_true", dest = "yearly", default=False, help="Create yearly graph(s).")
    
        
def buildTitle( type, client, endDate, timespan, minimum, maximum, mean  ):
    """
        Returns the title of the graphic base on infos. 
    """
    
    return  "%s for %s queried at %s for a span of %s hours." %( type, client,  endDate , timespan )    

    
 
def getOverallMin( databaseName, startTime, endTime, logger = None ):
    """
        This methods returns the minimum of the entire set of data found between 
        startTime and endTime within the specified database name.
    
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
                    print minimum
            i = i + 1 
       
         
    except :
        if logger != None:
            logger.error( "Error in generateRRDGraphics.getOverallMin. Unable to read %s" %databaseName )
        pass    
        
    return minimum
    
    
    
def getOverallMax( databaseName, startTime, endTime, logger = None ):
    """
        This methods returns the max of the entire set of data found between 
        startTime and endTime within the specified database name.
    """  
    
    maximum = None
    
    try:
    
        output = rrdtool.fetch( databaseName, 'MAX', '-s', "%s" %startTime, '-e', '%s' %endTime )      
        
        maxTuples = output[2]
        
        for maxTuple in maxTuples :
            if maxTuple[0] != 'None' and maxTuple[0] != None :
                if maxTuple[0] > maximum : 
                    maximum = maxTuple[0]
                    #print maxTuple
        #print "maximum : %s " %maximum
    
    except :
        if logger != None:
            logger.error( "Error in generateRRDGraphics.getOverallMin. Unable to read %s" %databaseName )
        pass    
    
    return maximum 
 
    
       
def getOverallMean( databaseName, startTime, endTime, logger = None  ):
    """
        This methods returns the mean of the entire set of data found between 
        startTime and endTime within the specified database name.
        
    """
    
    sum = 0 
    avg = 0
    
    try :
        
        output = rrdtool.fetch( databaseName, 'AVERAGE', '-s', "%s" %startTime, '-e', '%s' %endTime )
        meanTuples = output[2]
        
        for meanTuple in meanTuples :            
            if meanTuple[0] != 'None' and meanTuple[0] != None :
                sum = sum + meanTuple[0]
    
        avg = sum / len( meanTuples )  
        #print "avg : %s " %avg
    
    except :
        if logger != None:
            logger.error( "Error in generateRRDGraphics.getOverallMin. Unable to read %s" %databaseName )
        pass    
            
    return avg 
    


def buildImageName(  type, client, machine, infos, logger = None ):
    """
        Builds and returns the image name to be created by rrdtool.
        
    """

    
    date = infos.endDate.replace( "-","" ).replace( " ", "_")
    
    fileName = PXPaths.GRAPHS + "%s/rrdgraphs/%s_%s_%s_%s_%shours_on_%s.png" %( client,infos.fileType, client, date, type, infos.timespan, machine )
    
    
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



def plotRRDGraph( databaseName, type, client, machine, infos, logger = None ):
    """
        This method is used to produce a rrd graphic.
        
    """

    imageName = buildImageName( type, client, machine, infos, logger )     
    end       = int ( MyDateLib.getSecondsSinceEpoch ( infos.endDate ) )  
    start     = end - ( infos.timespan * 60 * 60) 
    
    mean    = getOverallMean( databaseName, start, end )
    maximum = getOverallMax( databaseName, start, end )   
    minimum = getOverallMin( databaseName, start, end  ) 
    
    
    if type == "latency" or type == "filesOverMaxLatency":
        innerColor = "cd5c5c"
        outerColor = "8b0000"
    elif  type == "bytecount" or type == "filecount" :
        innerColor = "019EFF"
        outerColor = "4D9AA9"  
    else:
        innerColor = "54DE4F"
        outerColor = "1C4A1A"
    
    title = buildTitle( type, client, infos.endDate, infos.timespan, minimum, maximum, mean )
    
#     try:
    rrdtool.graph( imageName,'--imgformat', 'PNG','--width', '600','--height', '200','--start', "%i" %(start) ,'--end', "%s" %(end), '--vertical-label', '%s' %type,'--title', '%s'%title,'COMMENT: Minimum %s Maximum  %s Mean %.2f\c' %( minimum, maximum, mean), '--lower-limit','0','DEF:latency=%s:latency:AVERAGE'%databaseName, 'AREA:latency#%s:%s' %( innerColor, type ),'LINE1:latency#%s:%s'%( outerColor, type ) )
    
    print "Plotted : %s" %imageName
    if logger != None:
        logger.info(  "Plotted : %s" %imageName )
       
#     
#     except :
#         if logger != None:
#             logger.error( "Error in generateRRDGraphics.plotRRDGraph. Unable to generate %s" %imageName )
#         pass     
    
    

        
    
def generateRRDGraphics( infos, logger = None ):
    """
        This method generate all the graphics. 
        
    """    
    
    for machine in infos.machines:
        
        for client in infos.clientNames:
            
            for type in infos.types : 
                databaseName = transferPickleToRRD.buildRRDFileName( type, client, machine )    
                plotRRDGraph( databaseName, type, client, machine, infos, logger )
                


def main():
    """
        Gathers options, then makes call to generateRRDGraphics   
    
    """    
    
    localMachine = os.uname()[1] # /apps/px/log/ logs are stored elsewhere at the moment.
    
    if not os.path.isdir( PXPaths.LOG + localMachine + '/' ):
        os.makedirs( PXPaths.LOG + localMachine + '/', mode=0777 )
    
    logger = Logger( PXPaths.LOG + localMachine + "/" + 'stats_' + 'rrd_graphs' + '.log.notb', 'INFO', 'TX' + 'rrd_transfer', bytes = True  ) 
    
    logger = logger.getLogger()
       
    parser = createParser() 
   
    infos = getOptionsFromParser( parser )

    generateRRDGraphics( infos, logger = logger )
    
    
if __name__ == "__main__":
    main()    
    