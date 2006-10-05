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
#from   transferPickleToRRD import *


PXPaths.normalPaths()   



class _GraphicsInfos:

    def __init__( self, directory, fileType, types, clientNames = None ,  timespan = 12, currentTime = None, machines = ["pdsGG"]  ):

            
        self.directory    = directory         # Directory where log files are located. 
        self.fileType     = fileType          # Type of log files to be used.    
        self.types        = types             # Type of graphics to produce. 
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        self.timespan     = timespan          # Number of hours we want to gather the data from. 
        self.currentTime  = currentTime       # Time when stats were queried.
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
    
    currentTime   = []
    
    ( options, args )= parser.parse_args()        
    timespan         = options.timespan
    machines         = options.machines.replace( ' ','').split(',')
    clientNames      = options.clients.replace( ' ','' ).split(',')
    types            = options.types.replace( ' ', '').split(',')
    currentTime      = options.currentTime.replace('"','').replace("'",'')
    fileType         = options.fileType.replace("'",'')
       
     
    
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( currentTime, '%Y-%m-%d %H:%M:%S' )
        split = currentTime.split()
        currentTime = "%s %s" %( split[0], split[1] )

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
        #get rx tx names accordingly.         
        if fileType == "tx":    
            x = 1 
        else:
            x = 2    
            
    
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
    
                
                
    directory = PXPaths.LOG + localMachine + "/"
    
    currentTime = MyDateLib.getIsoWithRoundedHours( currentTime )
    
    infos = _GraphicsInfos( currentTime = currentTime, clientNames = clientNames,  directory = directory , types = types, timespan = timespan, machines = machines, fileType = fileType )   
            
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
Notes :
- Now option not yet implemented.    

Defaults :

- Default Client is the entire tx/rx list that corresponds to the list of machine passed in parameter.
- Default Date is current system time.  
- Default Types value is latency.
- Default span is 12 hours.
- Accepted values for types are : errors,latency,bytecount
  -To use mutiple types, use -t|--types "type1,type2"


Options:
 
    - With -c|--clients you can specify the clients names on wich you want to collect data. 
    - With -d|--date you can specify the time of the request.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log fiels that will be used.  
    - With -m|--machines you can specify from wich machine the data is to be used.
    - With -s|--span you can specify the time span to be used to create the graphic 
    - With -t|--types you can specify what data types need to be collected
    
      
WARNING: - Client name MUST be specified,no default client exists. 
          
            
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -c satnet                         --> All default values, for client satnet. 
Ex3: %prog -c satnet -d '2006-06-30 05:15:00'--> Client satnet, Date of call 2006-06-30 05:15:00.
Ex4: %prog -c satnet -t "errors,latency"     --> Uses current time, client satnet and collect those 2 types.
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
    
    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default="satnet",
                        help="Clients' names")

    parser.add_option("-d", "--date", action="store", type="string", dest="currentTime", default=MyDateLib.getIsoFromEpoch( time.time() ), help="Decide current time. Usefull for testing.")
    
    parser.add_option("-f", "--fileType", action="store", type="string", dest="fileType", default='tx', help="Type of log files wanted.")                     
   
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=localMachine, help = "Machines for wich you want to collect data." )   
    
    parser.add_option("-s", "--span", action="store",type ="int", dest = "timespan", default=12, help="timespan( in hours) of the graphic.")
       
    parser.add_option("-t", "--types", type="string", dest="types", default="All",help="Types of data to look for.")   

    
        
def buildTitle( type, client, currentTime, timespan, minimum, maximum, mean  ):
    """
        Returns the title of the graphic base on infos. 
    """
    
    return  "%s for %s queried at %s for a span of %s hours." %( type, client,  currentTime , timespan )    

    

 
def getOverallMin( databaseName, startTime, endTime, logger = None ):
    """
        This methods returns the minimum of the entire set of data found between 
        startTime and endTime within the specified database name.
    
    """
    
    minimum = None 
    output = rrdtool.fetch( databaseName, 'MIN', '-s', "%s" %startTime, '-e', '%s' %endTime )
    #print output
    minTuples = output[2]
     
    i = 0 
    while i < len( minTuples ):
        if minTuples[i][0] != 'None' and minTuples[i][0] != None  :        
            if minTuple[0] < minimum or minimum == None : 
                minimum = minTuple[0]
        i = i + 1 
    #print "minimum : %s " %minimum
    return minimum
    
    
    
def getOverallMax( databaseName, startTime, endTime, logger = None ):
    """
        This methods returns the max of the entire set of data found between 
        startTime and endTime within the specified database name.
    """  

    output = rrdtool.fetch( databaseName, 'MAX', '-s', "%s" %startTime, '-e', '%s' %endTime )
    
    maximum = None 
    maxTuples = output[2]
    for maxTuple in maxTuples :
        if maxTuple[0] != 'None' and maxTuple[0] != None :
            if maxTuple[0] > maximum : 
                maximum = maxTuple[0]
    
    #print "maximum : %s " %maximum

    return maximum 
 
       
def getOverallMean( databaseName, startTime, endTime, logger = None  ):
    """
        This methods returns the mean of the entire set of data found between 
        startTime and endTime within the specified database name.
        
    """
    
    output = rrdtool.fetch( databaseName, 'AVERAGE', '-s', "%s" %startTime, '-e', '%s' %endTime )
    
    #print output
    
    sum = 0
    meanTuples = output[2]
    i =0
    for meanTuple in meanTuples :
        
        if meanTuple[0] != 'None' and meanTuple[0] != None :
            sum = sum + meanTuple[0]

    avg = sum / len( meanTuples )  
    #print "avg : %s " %avg
    
    return avg 

    


def buildImageName(  type, client, machine, infos, logger = None ):
    """
        Builds and returns the image name to be created by rrdtool.
        
    """

    
    date = infos.currentTime.replace( "-","" ).replace( " ", "_")
    
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
    #print "databaseName : %s" %databaseName
    #print "made it up to plotGraph"
    imageName = buildImageName( type, client, machine, infos, logger )     
    end       = int ( MyDateLib.getSecondsSinceEpoch ( infos.currentTime ) )  
    start     = end - ( infos.timespan * 60 * 60) 
    
    mean    = getOverallMean( databaseName, start, end )
    maximum = getOverallMax( databaseName, start, end )   
    minimum = 0#getOverallMin( databaseName, start, end  ) 
    
    
    title = buildTitle( type, client, infos.currentTime, infos.timespan, minimum, maximum, mean )
    
    rrdtool.graph( imageName,'--imgformat', 'PNG','--width', '600','--height', '200','--start', "%i" %(start) ,'--end', "%s" %(end), '--vertical-label', '%s' %type,'--title', '%s'%title,'COMMENT: Minimum %s Maximum  %s Mean %.2f\c' %( minimum, maximum, mean), '--lower-limit','0','DEF:latency=%s:latency:AVERAGE'%databaseName, 'AREA:latency#cd5c5c:%s' %type,'LINE1:latency#8b0000:%s'%type)
    
    print "plotted : %s" %imageName
    
    
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
    
    logger = Logger( PXPaths.LOG + localMachine + "/" + 'stats_' + 'rrd_graphs' + '.log.notb', 'INFO', 'TX' + 'rrd_transfer' ) 
    
    logger = logger.getLogger()
       
    parser = createParser() 
   
    infos = getOptionsFromParser( parser )
#     #print "infos : %s" %infos.clients
    generateRRDGraphics( infos, logger = logger )
    
    
if __name__ == "__main__":
    main()    
    