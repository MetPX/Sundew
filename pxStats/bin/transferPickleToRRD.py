#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
#######################################################################################
##
## Name   : transferPickleToRRD.py 
##  
## Author : Nicholas Lemay  
##
## Date   : September 26th 2006, Last update May 8th 2007
##
## Goal   : This files contains all the methods needed to transfer pickled data 
##          that was saved using pickleUpdater.py into an rrd database. 
##          In turn, the rrd database can be used to plot graphics using rrdTool.
##          
##          
## Note :  Any change in the file naming struture of the databses generated here 
##         will impact generateRRDGraphics.py. Modify the other file accordingly. 
##
#######################################################################################
"""

"""
    Small function that adds pxlib to the environment path.  
"""
import os, time, getopt, pickle, rrdtool
sys.path.insert(1, sys.path[0] + '/../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)

"""
    Imports
    PXManager requires pxlib 
"""
from   Logger    import * 
from   optparse  import OptionParser
from   PXManager import *

from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.PickleMerging import PickleMerging
from pxStats.lib.ClientStatsPickler import ClientStatsPickler
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.RrdUtilities import RrdUtilities

   
LOCAL_MACHINE = os.uname()[1]   

    
#################################################################
#                                                               #
#################PARSER AND OPTIONS SECTION######################
#                                                               #
################################################################# 
class _Infos:

    def __init__( self, endTime, clients, fileTypes, machines, products = "all", group = "" ):
        """
            Data structure to be used to store parameters within parser.
        
        """    
        
        self.endTime   = endTime   # Ending time of the pickle->rrd transfer.         
        self.clients   = clients   # Clients for wich to do the updates.
        self.machines  = machines  # Machines on wich resides these clients.
        self.fileTypes = fileTypes # Filetypes of each clients.        
        self.products  = products  # Products we are interested in.
        self.group     = group     # Whether or not we group data together.
        
        
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
- Default endTime is currentTime.
- Default startTime is a weel ago.
- Default machine is LOCAL_MACHINE.  
- Default client is all active clients.

Options:
    - With -c|--clients you can specify wich clients to transfer.  
    - With -e|--end you can specify the ending time of the transfer.
    - With -f|--fileTypes you can specify the files types of each clients.
    - With -g|--group you can specify that you wan to group the data of the specified clients
      together.
    - With -m|--machines you can specify the list of machines on wich the data client resides.
    - With -p|--products you can specify the list of products you are interested in. 
      Note : this option requires the group options to be enabled.    
                
Ex1: %prog                                     --> All default values will be used. Not recommended.  
Ex2: %prog -m machine1                         --> All default values, for machine machine1. 
Ex3: %prog -m machine1 -d '2006-06-30 05:15:00'--> Machine1, Date of call 2006-06-30 05:15:00.
Ex4: %prog -s 24                               --> Uses current time, default machine and 24 hours span.
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
   
    parser.add_option( "-c", "--clients", action="store", type="string", dest="clients", default="ALL", help = "Clients for wich we need to tranfer the data." ) 
    
    parser.add_option( "-e", "--end", action="store", type="string", dest="end", default=StatsDateLib.getIsoFromEpoch( time.time() ), help="Decide ending time of the update.") 
    
    parser.add_option( "-f", "--fileTypes", action="store", type="string", dest="fileTypes", default="", help="Specify the data type for each of the clients." )
        
    parser.add_option( "-g", "--group", action="store", type="string", dest = "group", default="", help="Transfer the combined data of all the specified clients/sources into a grouped database.")
    
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=LOCAL_MACHINE, help ="Specify on wich machine the clients reside." ) 
  
    parser.add_option( "-p", "--products",action="store", type="string", dest="products", default="ALL", help ="Specify wich product you are interested in.")
    
    
  
def getOptionsFromParser( parser, logger = None  ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the infos variable.   
    
        If errors are encountered in parameters used, it will immediatly terminate 
        the application. 
    
    """    
        
    ( options, args )= parser.parse_args()        
    end       = options.end.replace( '"','' ).replace( "'",'')
    clients   = options.clients.replace( ' ','' ).split( ',' )
    machines  = options.machines.replace( ' ','' ).split( ',' )
    fileTypes = options.fileTypes.replace( ' ','' ).split( ',' )  
    products  = options.products.replace( ' ','' ).split( ',' ) 
    group     = options.group.replace( ' ','' ) 
          
         
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( end, '%Y-%m-%d %H:%M:%S' )#will raise exception if format is wrong.
        split = end.split()
        currentTime = "%s %s" %( split[0], split[1] )

    except:    
        print "Error. The endind date format must be YYYY-MM-DD HH:MM:SS" 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()    
     
    #round ending hour to match pickleUpdater.     
    end   = StatsDateLib.getIsoWithRoundedHours( end )
        
            
    for machine in machines:
        if machine != LOCAL_MACHINE:
            GeneralStatsLibraryMethods.updateConfigurationFiles( machine, "pds" )
    
    if products[0] != "ALL" and group == "" :
        print "Error. Products can only be specified when using special groups." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()        
    
     
                        
    #init fileTypes array here if only one fileType is specified for all clients/sources     
    if len(fileTypes) == 1 and len(clients) !=1:
        for i in range(1,len(clients) ):
            fileTypes.append(fileTypes[0])
        
    if clients[0] == "ALL" and fileTypes[0] != "":
        print "Error. Filetypes cannot be specified when all clients are to be updated." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()        
    
    elif clients[0] != "ALL" and len(clients) != len( fileTypes ) :
        print "Error. Specified filetypes must be either 1 for all the group or of the exact same lenght as the number of clients/sources." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()          
    
    elif clients[0] == 'ALL' :        
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machines[0] )

        clients = []
        clients.extend( txNames )
        clients.extend( rxNames )
        
        fileTypes = []
        for txName in txNames:
            fileTypes.append( "tx" )
        for rxName in rxNames:
            fileTypes.append( "rx" )                 
    
     
    clients = GeneralStatsLibraryMethods.filterClientsNamesUsingWilcardFilters(end, 1000, clients, machines, fileTypes= fileTypes )  
   
    
    infos = _Infos( endTime = end, machines = machines, clients = clients, fileTypes = fileTypes, products = products, group = group )   
    
    return infos     

      
        
def createRoundRobinDatabase( databaseName, startTime, dataType ):
    """
    
    @param databaseName: Name of the database to create.
    
    @param startTime: needs to be in seconds since epoch format.
    
    @param dataType: will be used for data naming within the database. 
    
    @note: startime used within the method will be a minute less than real startTime.
           RRD does not allow to enter data from the same minute as the one
           of the very start of the db. Please DO NOT substract that minute 
           prior to calling this method
    
    """
   
   
    startTime = int( startTime - 60 )    
      
    # 1st  rra : keep last 5 days for daily graphs. Each line contains 1 minute of data. 
    # 2nd  rra : keep last 14 days for weekly graphs. Each line contains 1 hours of data.
    # 3rd  rra : keep last 365 days for Monthly graphs. Each line contains 4 hours of data. 
    # 4th  rra : keep last 10 years of data. Each line contains 24 hours of data.
    rrdtool.create( databaseName, '--start','%s' %( startTime ), '--step', '60', 'DS:%s:GAUGE:60:U:U' %dataType, 'RRA:AVERAGE:0.5:1:7200','RRA:MIN:0.5:1:7200', 'RRA:MAX:0.5:1:7200','RRA:AVERAGE:0.5:60:336','RRA:MIN:0.5:60:336', 'RRA:MAX:0.5:60:336','RRA:AVERAGE:0.5:240:1460','RRA:MIN:0.5:240:1460','RRA:MAX:0.5:240:1460', 'RRA:AVERAGE:0.5:1440:3650','RRA:MIN:0.5:1440:3650','RRA:MAX:0.5:1440:3650' )      
              
      
    

    
def getPairsFromMergedData( statType, mergedData, logger = None  ):
    """
        This method is used to create the data couples used to feed an rrd database.
        
    """
    
    pairs = []        
    nbEntries = len( mergedData.statsCollection.timeSeperators ) - 1     
    
    if nbEntries !=0:        
       
        for i in range( 0, nbEntries ):
            
            try :
                    
                if len( mergedData.statsCollection.fileEntries[i].means ) >=1 :
                    
                    if statType == "filesOverMaxLatency" :
                        pairs.append( [ int(StatsDateLib.getSecondsSinceEpoch( mergedData.statsCollection.timeSeperators[i]))+60, mergedData.statsCollection.fileEntries[i].filesOverMaxLatency ] )                      
                    
                    elif statType == "errors":
                        
                        pairs.append( [int(StatsDateLib.getSecondsSinceEpoch( mergedData.statsCollection.timeSeperators[i])) +60, mergedData.statsCollection.fileEntries[i].totals[statType]] )
                    
                    elif statType == "bytecount":
                    
                        pairs.append( [ int(StatsDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, mergedData.statsCollection.fileEntries[i].totals[statType]] )
                        
                    elif statType == "latency":
                    
                        pairs.append( [ int(StatsDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, mergedData.statsCollection.fileEntries[i].means[statType]] )                          
                    
                    elif statType == "filecount":
                        pairs.append( [ int(StatsDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, len(mergedData.statsCollection.fileEntries[i].values.productTypes)] )
                    
                    else:

                        pairs.append( [ int(StatsDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, 0.0 ])                    
                
                else:      
                                                      
                    pairs.append( [ int(StatsDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, 0.0 ] )
            
            
            except KeyError:
                if logger != None :                    
                    logger.error( "Error in getPairs." )
                    logger.error( "The %s stat type was not found in previously collected data." %statType )    
                pairs.append( [ int(StatsDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, 0.0 ] )
                sys.exit()    
            
               
        return pairs 
        
        
    
def getMergedData( clients, fileType,  machines, startTime, endTime, groupName = "", logger = None ):
    """
        This method returns all data comprised between startTime and endTime as 
        to be able to build pairs.
           
    """
    
    if fileType == "tx":       
        types = [ "errors","bytecount","latency", ]
    else:
        types = [ "errors","bytecount" ]
    
   
    if len( machines ) > 1 or len( clients) > 1:    
       
        statsCollection = pickleMerging.mergePicklesFromDifferentSources( logger = logger , startTime = StatsDateLib.getIsoFromEpoch(startTime), endTime = StatsDateLib.getIsoFromEpoch(endTime), clients = clients, fileType = fileType, machines = machines, groupName = groupName )                           
    
    else:#only one machine, only merge different hours together
       
        statsCollection = pickleMerging.mergePicklesFromDifferentHours( logger = logger , startTime = StatsDateLib.getIsoFromEpoch(startTime), endTime = StatsDateLib.getIsoFromEpoch(endTime), client = clients[0], fileType = fileType, machine = machines[0] )
        
    
    combinedMachineName = ""
    for machine in machines:
        combinedMachineName = combinedMachineName + machine
    
       
    dataCollector =  ClientStatsPickler( client = clients[0], statsTypes = types, directory = "", statsCollection = statsCollection, machine = combinedMachineName, logger = logger )
    
    return dataCollector    
      
        
    
def getPairs( clients, machines, fileType, startTime, endTime, groupName = "", logger = None ):
    """
        
        This method gathers all the data pairs needed to update the different 
        databases associated with a client of a certain fileType.
        
    """
    
    dataPairs = {}
    dataTypes  = GeneralStatsLibraryMethods.getDataTypesAssociatedWithFileType(fileType) 
   
    mergedData = getMergedData( clients, fileType, machines, startTime, endTime, groupName, logger )
        
    for dataType in dataTypes :  
        dataPairs[ dataType ]  = getPairsFromMergedData( dataType, mergedData, logger )
    
   
    return dataPairs
    
    
    
def updateRoundRobinDatabases(  client, machines, fileType, endTime, logger = None ):
    """
        This method updates every database linked to a certain client.
        
        Database types are linked to the filetype associated with the client.
        
    """
            
    combinedMachineName = ""
    for machine in machines:
        combinedMachineName = combinedMachineName + machine
    
    tempRRDFileName = RrdUtilities.buildRRDFileName( dataType = "errors", clients = [client], machines = machines, fileType = fileType)
    startTime   = RrdUtilities.getDatabaseTimeOfUpdate(  tempRRDFileName, fileType ) 
   
    if  startTime == 0 :
        startTime = StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoTodaysMidnight( endTime ) )
    endTime     = StatsDateLib.getSecondsSinceEpoch( endTime )           
    dataPairs   = getPairs( [client], machines, fileType, startTime, endTime, groupName = "", logger = logger )   
        
    for key in dataPairs.keys():
                               
        rrdFileName = RrdUtilities.buildRRDFileName( dataType = key, clients = [client], machines = machines, fileType = fileType )        
        
        if not os.path.isfile( rrdFileName ):             
            createRoundRobinDatabase(  databaseName = rrdFileName , startTime= startTime, dataType = key )
                      
        
        if endTime > startTime :  
            
            for pair in dataPairs[ key ]:
                rrdtool.update( rrdFileName, '%s:%s' %( int(pair[0]), pair[1] ) ) 

            if logger != None :
                logger.info( "Updated  %s db for %s in db named : %s" %( key, client, rrdFileName ) )
        
        else:
            if logger != None :
                logger.warning( "This database was not updated since it's last update was more recent than specified date : %s" %rrdFileName )
        
                
    RrdUtilities.setDatabaseTimeOfUpdate(  rrdFileName, fileType, endTime )  


        
def updateGroupedRoundRobinDatabases( infos, logger = None ):    
    """
        This method is to be used to update the database 
        used to stored the merged data of a group.
         
    """
    
    endTime     = StatsDateLib.getSecondsSinceEpoch( infos.endTime ) 
    
    
    tempRRDFileName = RrdUtilities.buildRRDFileName( "errors", clients = infos.group, machines = infos.machines, fileType = infos.fileTypes[0]  )  
    startTime       = RrdUtilities.getDatabaseTimeOfUpdate(  tempRRDFileName, infos.fileTypes[0] )
    
   
    if startTime == 0 :
        
        startTime = StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoTodaysMidnight( infos.endTime ) )
              
    dataPairs   = getPairs( infos.clients, infos.machines, infos.fileTypes[0], startTime, endTime, infos.group, logger )     
          
     
    for key in dataPairs.keys():
        
        rrdFileName = RrdUtilities.buildRRDFileName( dataType = key, clients = infos.group, groupName = infos.group, machines =  infos.machines,fileType = infos.fileTypes[0], usage = "group" )  
        
        if not os.path.isfile( rrdFileName ):  
            
            createRoundRobinDatabase( rrdFileName, startTime, key)
            
        
        if endTime > startTime :  
            
            for pair in dataPairs[ key ]:       
                         
                rrdtool.update( rrdFileName, '%s:%s' %( int(pair[0]), pair[1] ) ) 

            if logger != None :
                logger.info( "Updated  %s db for %s in db named : %s" %( key, infos.clients, rrdFileName ) )
        
        else:
            if logger != None :
                logger.warning( "This database was not updated since it's last update was more recent than specified date : %s" %rrdFileName )        
    
        
        
    setDatabaseTimeOfUpdate( tempRRDFileName, infos.fileTypes[0], endTime )         
    
    
        
def transferPickleToRRD( infos, logger = None ):
    """
        This method is a higher level method to be used to update as many rrd's as 
        is desired. 
        
        If data is not to be grouped, a new process will be launched 
        for every client to be transferred.
           
        Simultaneous number of launched process has been limited to 5 process' 
        
    """    
    
  
    
    if infos.group == "" :    
        
        for i in range( len( infos.clients ) ):  
            pid = os.fork() #create child process
            
            if pid == 0 :#if child 
                updateRoundRobinDatabases( infos.clients[i], infos.machines, infos.fileTypes[i], infos.endTime, logger =logger )                           
                sys.exit()#terminate child immidiatly
            
            elif (i%5) == 0:
                while True:#wait on all non terminated child process'
                    try:   #will raise exception when no child process remain.        
                        pid, status = os.wait()                    
                    except:    
                        break            
            
            
        while True:#wait on all non terminated child process'
            try:   #will raise exception when no child process remain.  
                pid, status = os.wait( )
            except:    
                break 
    
    else:
        updateGroupedRoundRobinDatabases( infos, logger )

              
                        
def createPaths():
    """
        Create a series of required paths. 
    """            
       
        
    dataTypes = [ "latency", "bytecount", "errors", "filesOverMaxLatency", "filecount" ]
    
        
    for dataType in dataTypes:
        if not os.path.isdir( StatsPaths.STATSCURRENTDB + "%s/" %dataType ):
            os.makedirs(StatsPaths.STATSCURRENTDB + "%s/" %dataType, mode=0777 )          
            
    if not os.path.isdir( StatsPaths.STATSCURRENTDBUPDATES + "tx" ):
        os.makedirs( StatsPaths.STATSCURRENTDBUPDATES + "tx", mode=0777 )
     
    if not os.path.isdir( StatsPaths.STATSCURRENTDBUPDATES + "rx" ):
        os.makedirs( StatsPaths.STATSCURRENTDBUPDATES + "rx" , mode=0777 )      
        
                               
               
def main():
    """
        Gathers options, then makes call to transferPickleToRRD   
    
    """

    
    createPaths()
    
    logger = Logger( StatsPaths.STATSLOGGING + 'stats_' + 'rrd_transfer' + '.log.notb', 'INFO', 'TX' + 'rrd_transfer', bytes = True  ) 
    
    logger = logger.getLogger()
       
    parser = createParser() 
   
    infos = getOptionsFromParser( parser, logger = logger )
   
    transferPickleToRRD( infos, logger = logger )
   

if __name__ == "__main__":
    
    main()
                              
