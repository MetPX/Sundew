#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : pickleUpdater
#
# Author: Nicholas Lemay
#
# Date  : 2006-06-15
#
# Description: 
#
#   Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  PickleUpdater -h | --help
#
#
##############################################################################################
"""

"""
    Small function that adds pxlib to the environment path.  
"""
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    PXManager, Logger both require pxlib 
"""
import os,time, pwd, sys, getopt, commands, fnmatch, pickle

from Logger import * 
from optparse import OptionParser
from ConfigParser import ConfigParser

from PXManager import * 
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.ClientStatsPickler import ClientStatsPickler
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
   

LOCAL_MACHINE = os.uname()[1]   
    
    
class _UpdaterInfos:  

    def __init__( self, clients, directories, types, startTimes,collectUpToNow, fileType, currentDate = '2005-06-27 13:15:00', interval = 1, hourlyPickling = True, machine = ""   ):
        
        """
            Data structure used to contain all necessary info for a call to ClientStatsPickler. 
            
        """ 
        
        systemsCurrentDate  = StatsDateLib.getIsoFromEpoch( time.time() )
        self.clients        = clients                            # Client for wich the job is done.
        self.machine        = machine                            # Machine on wich update is made. 
        self.types          = types                              # Data types to collect ex:latency 
        self.fileType       = fileType                           # File type to use ex :tx,rx etc  
        self.directories    = directories                        # Get the directory containing files  
        self.interval       = interval                           # Interval.
        self.startTimes     = startTimes                         # Time of last update.... 
        self.currentDate    = currentDate or  systemsCurrentDate # Time of the update.
        self.collectUpToNow = collectUpToNow                     # Wheter or not we collect up to now or 
        self.hourlyPickling = hourlyPickling                     # whether or not we create hourly pickles.
        self.endTime        = self.currentDate                   # Will be currentDate if collectUpTo                                                                             now is true, start of the current                                                                               hour if not 



def setLastUpdate( machine, client, fileType, currentDate, collectUpToNow = False    ):
    """
        This method set the clients last update to the date received in parameter. 
        Creates new key if key doesn't exist.
        Creates new PICKLED-TIMES file if it doesn't allready exist.   
        
        In final version this will need a better filename and a stable path....
        
    """
    
    times = {}
    lastUpdate = {}
    fileName = StatsPaths.STATSPICKLESTIMEOFUPDATES
    
    if collectUpToNow == False :
        currentDate = StatsDateLib.getIsoWithRoundedHours( currentDate ) 
    
    
    if os.path.isfile( fileName ):
        
        fileHandle  = open( fileName, "r" )
        times       = pickle.load( fileHandle )
        fileHandle.close()
        
        times[ machine + "_" + fileType + "_" + client ] = currentDate
        
        fileHandle  = open( fileName, "w" )
        pickle.dump( times, fileHandle )
        fileHandle.close()
    
    
    else:#create a new pickle file  
         
        fileHandle  = open( fileName, "w" )
        
        times[ fileType + "_" + client ] = currentDate          
        
        pickle.dump( times, fileHandle )
        
        fileHandle.close()



def getLastUpdate( machine, client, fileType, currentDate, collectUpToNow = False ):
    """
        This method gets the dictionnary containing all the last updates list.
        From that dictionnary it returns the right value.         
       
    """ 
    
    times = {}
    lastUpdate = {}
    fileName = StatsPaths.STATSPICKLESTIMEOFUPDATES  
    
    if os.path.isfile( fileName ):
        
        fileHandle  = open( fileName, "r" )
        times       = pickle.load( fileHandle )
        
        try :
            lastUpdate = times[ machine + "_" + fileType + "_" + client ]
        except:
            lastUpdate = StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch(currentDate ) - StatsDateLib.HOUR) )
            pass
            
        fileHandle.close()      
            
    
    else:#create a new pickle file.Set start of the pickle as last update.   
         
        fileHandle  = open( fileName, "w" )
        
    
        lastUpdate = StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch(currentDate ) - StatsDateLib.HOUR) )


        times[ fileType + "_" + client ] = lastUpdate    
         
        pickle.dump( times, fileHandle )
        fileHandle.close()
       

    return lastUpdate

    
            
#################################################################
#                                                               #
#############################PARSER##############################
#                                                               #
#################################################################   
def getOptionsFromParser( parser, logger = None  ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the hlE variable.   
    
        If errors are encountered in parameters used, it will immediatly terminate 
        the application. 
    
    """ 
    
    directories  = []
    startTimes   = []
    
    ( options, args ) = parser.parse_args()        
    
    interval       = options.interval
    collectUpToNow = options.collectUpToNow 
    currentDate    = options.currentDate.replace( '"','' ).replace( "'",'' )
    currentDate    = StatsDateLib.getIsoWithRoundedHours( currentDate ) 
    fileType       = options.fileType.replace( "'",'' )
    machine        = options.machine.replace( " ","" )
    clients        = options.clients.replace(' ','' ).split( ',' )
    types          = options.types.replace( ' ', '' ).split( ',' )
    pathToLogFiles = GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, machine )
    
    #print "*****pathToLogFiles %s" %pathToLogFiles
    
    
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( currentDate, '%Y-%m-%d %H:%M:%S' )
        split = currentDate.split()
        currentDate = "%s %s" %( split[0],split[1] )

    except:    
        print "Error. The date format must be YYYY-MM-DD HH:MM:SS" 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
            
        
    try:    
        if int( interval ) < 1 :
            raise 
    
    except:
        
        print "Error. The interval value needs to be an integer one above 0." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
        
    
    if fileType != "tx" and fileType != "rx":
        print "Error. File type must be either tx or rx."
        print 'Multiple types are not accepted.' 
        print "Use -h for additional help."
        print "Program terminated."
        sys.exit()    
        
    
    if fileType == "tx":       
        validTypes = ["errors","latency","bytecount"]

    else:
        validTypes = ["errors","bytecount"]
     
     
    if types[0] == "All":
        types = validTypes
                     
    try :
        for t in types :
            if t not in validTypes:
                raise 

    except:    
        
        print "Error. With %s fileType, possible data types values are : %s." %(fileType,validTypes )
        print 'For multiple types use this syntax : -t "type1,type2"' 
        print "Use -h for additional help."
        print "Program terminated."
        sys.exit()
    
    
    if clients[0] == "All" :
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machine )
       
        if fileType == "tx": 
            clients = txNames                     
        else:
            clients = rxNames          
        
          
    #print "clients found :%s" %clients   
             
    # Verify that each client needs to be updated. 
    # If not we add a warning to the logger and removwe the client from the list
    # since it's not needed, but other clients might be.
    usefullClients = []
    for client in clients :
        startTime = getLastUpdate( machine = machine, client = client, fileType= fileType, currentDate =  currentDate , collectUpToNow = collectUpToNow )
               
        if currentDate > startTime:
            #print " client : %s currentDate : %s   startTime : %s" %( client, currentDate, startTime )
            directories.append( pathToLogFiles )
            startTimes.append( startTime )
            usefullClients.append( client )
        else:
            #print "This client was not updated since it's last update was more recent than specified date : %s" %client
            if logger != None :
                logger.warning("This client was not updated since it's last update was more recent than specified date : %s" %client)      
       
                
    infos = _UpdaterInfos( currentDate = currentDate, clients = usefullClients, startTimes = startTimes, directories = directories ,types = types, collectUpToNow = collectUpToNow, fileType = fileType, machine = machine )
    
    if collectUpToNow == False:
        infos.endTime = StatsDateLib.getIsoWithRoundedHours( infos.currentDate ) 
    
    
        
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
- Update request for a client with no history means it's data will be collected 
  from xx:00:00 to xx:59:59 of the hour of the request.    

Defaults :

- Default Client name does not exist.
- Default Date of update is current system time.  
- Default interval is 1 minute. 
- Default Now value is False.
- Default Types value is latency.
- Accepted values for types are : errors,latency,bytecount
  -To use mutiple types, use -t|--types "type1,type2"


Options:
 
    - With -c|--clients you can specify the clients names on wich you want to collect data. 
    - With -d|--date you can specify the time of the update.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log files that will be used.  
    - With -i|--interval you can specify interval in minutes at wich data is collected. 
    - With -m|--machines you can specify the machine for wich we are updating the pickles. 
    - With -n|--now you can specify that data must be collected right up to the minute of the call. 
    - With -t|--types you can specify what data types need to be collected
    
      
WARNING: - Client name MUST be specified,no default client exists. 
         - Interval is set by default to 1 minute. If data pickle here is to be used with 
           ClientGraphicProducer, default value will need to be used since current version only 
           supports 1 minute long buckets. 
          
            
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
    
    parser.add_option( "-c", "--clients", action="store", type="string", dest="clients", default="All",
                        help="Clients' names" )

    parser.add_option( "-d", "--date", action="store", type="string", dest="currentDate", default=StatsDateLib.getIsoFromEpoch( time.time() ), help="Decide current time. Usefull for testing." ) 
                                            
    parser.add_option( "-i", "--interval", type="int", dest="interval", default=1,
                        help="Interval (in minutes) for which a point will be calculated. Will 'smooth' the graph" )
    
    parser.add_option( "-f", "--fileType", action="store", type="string", dest="fileType", default='tx', help="Type of log files wanted." )                     
   
    parser.add_option( "-m", "--machine", action="store", type="string", dest="machine", default=LOCAL_MACHINE, help = "Machine for wich we are running the update." ) 
    
    parser.add_option( "-n", "--now", action="store_true", dest = "collectUpToNow", default=False, help="Collect data up to current second." )
       
    parser.add_option( "-t", "--types", type="string", dest="types", default="All", help="Types of data to look for." )          





def updateHourlyPickles( infos, logger = None ):
    """
        This method is to be used when hourly pickling is done. -1 pickle per hour per client. 
        
        This method needs will update the pickles by collecting data from the time of the last 
        pickle up to the current date.(System time or the one specified by the user.)
        
        If for some reason data wasnt collected for one or more hour since last pickle,pickles
        for the missing hours will be created and filled with data. 
        
        If no entries are found for this client in the pickled-times file, we take for granted that
        this is a new client. In that case data will be collected from the top of the hour up to the 
        time of the call.
        
        If new client has been producing data before the day of the first call, user can specify a 
        different time than system time to specify the first day to pickle. He can then call this 
        method with the current system time, and data between first day and current time will be 
        collected so that pickling can continue like the other clients can.
        
        
    """  
    
    cs = ClientStatsPickler( logger = logger )
    
    pathToLogFiles = GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, infos.machine )
    
    for i in range( len (infos.clients) ) :
        
        cs.client = infos.clients[i]
        
        width = StatsDateLib.getSecondsSinceEpoch(infos.endTime) - StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoWithRoundedHours(infos.startTimes[i] ) ) 
        
        
        if width > StatsDateLib.HOUR :#In case pickling didnt happen for a few hours for some reason...   
            
            hours = [infos.startTimes[i]]
            hours.extend( StatsDateLib.getSeparatorsWithStartTime( infos.startTimes[i], interval = StatsDateLib.HOUR, width = width ))
            
            for j in range( len(hours)-1 ): #Covers hours where no pickling was done.                               
                
                startOfTheHour = StatsDateLib.getIsoWithRoundedHours( hours[j] )
                startTime = startOfTheHour        
                                                   
                endTime = StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoWithRoundedHours(hours[j+1] ) ))
                #print " client : %s startTime : %s endTime : %s" %(infos.clients[i], startTime, endTime )
                
                if startTime >= endTime and logger != None :                                
                    logger.warning("Startime used in updateHourlyPickles was greater or equal to end time.")    

                
                cs.pickleName =  ClientStatsPickler.buildThisHoursFileName( client = infos.clients[i], currentTime =  startOfTheHour, machine = infos.machine, fileType = infos.fileType )
                 
                cs.collectStats( types = infos.types, startTime = startTime , endTime = endTime, interval = infos.interval * StatsDateLib.MINUTE,  directory = pathToLogFiles, fileType = infos.fileType )                     
                           
                    
        else:      
           
            startTime = infos.startTimes[i]
            endTime   = infos.endTime             
            startOfTheHour = StatsDateLib.getIsoWithRoundedHours( infos.startTimes[i] )
            #print " client : %s startTime : %s endTime : %s" %(infos.clients[i], startTime, endTime )               
            if startTime >= endTime and logger != None :#to be removed                
                logger.warning( "Startime used in updateHourlyPickles was greater or equal to end time." )    
 
                
            cs.pickleName =   ClientStatsPickler.buildThisHoursFileName( client = infos.clients[i], currentTime = startOfTheHour, machine = infos.machine, fileType = infos.fileType )            
              
            cs.collectStats( infos.types, startTime = startTime, endTime = endTime, interval = infos.interval * StatsDateLib.MINUTE, directory = pathToLogFiles, fileType = infos.fileType   )        
       
                         
        setLastUpdate( machine = infos.machine, client = infos.clients[i], fileType = infos.fileType, currentDate = infos.currentDate, collectUpToNow = infos.collectUpToNow )
              
   
    
def main():
    """
        Gathers options, then makes call to ClientStatsPickler to collect the stats based 
        on parameters received.  
    
    """
    
    if not os.path.isdir( StatsPaths.STATSPICKLES ):
        os.makedirs( StatsPaths.STATSPICKLES, mode=0777 )    
    
    if not os.path.isdir( StatsPaths.STATSLOGGING ):
        os.makedirs( StatsPaths.STATSLOGGING, mode=0777 )
    
    logger = Logger( StatsPaths.STATSLOGGING + 'stats_' + 'pickling' + '.log.notb', 'INFO', 'TX' + 'pickling', bytes = True  ) 
    logger = logger.getLogger()
   
    parser = createParser( )  #will be used to parse options 
    infos = getOptionsFromParser( parser, logger = logger )
    updateHourlyPickles( infos, logger = logger )
     


if __name__ == "__main__":
    main()
                              
