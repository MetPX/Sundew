"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: pickleUpdater
#
# Author: Nicholas Lemay
#
# Date: 2006-06-15
#
# Description: 
#
#   Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  PickleUpdater -h | --help
#############################################################################################
"""


#important files 
import os, pwd, sys,getopt, commands, fnmatch,pickle
from optparse import OptionParser
from ConfigParser import ConfigParser
from MyDateLib import *
from DirectoryStatsCollector import DirectoryStatsCollector


class _UpdaterInfos: 
    


    def __init__( self, clients, machines, directories, types, startTimes, currentDate = None, interval = 1 , width = 1 ):
        """
            Data structure used to contain all necessary info for a call to DirectoryStatscollector. 
            
        """ 
        
        self.date        = currentDate or MyDateLib.getOriginalDate( time.time() ) # Time of the cron job.
        self.clients     = clients                                          # Client for wich the job is done.
        self.machines    = machines                                         # Machines on wich we'll search data. 
        self.types       = types                                            # Data types to collect  
        self.directories = directories                                      # Get the directory containing the files  
        self.width       = width or 1                                       # Width for wich we'll collect data
        self.interval    = interval or 1                                    # Interval..... 
        self.startTimes  = startTimes                                       #Time of last crontab job.... 

    
    
    
def getfilesIntoDirectory( clientName, machines = "" ):
    """
        This method is used to get all files wich contains the data we need to look up
        to do the pickle job. 
        
        Returns the directory path wich contains all said files.
    
    """
    
    #Later this will have a connection the the real method that will download files into a directory 
    
    return "/apps/px/lib/stats/files/"
        


def getLastCronJob( clientName, currentDate, clients, update = True   ):
    """
        This method gets the dictionnary containing all the last cron job list. From that dictionnary
        it returns the right value. 
        
    """ 
    
      
    if os.path.isfile( "PICKLED-TIMES" ):
        
        fileHandle  = open( "PICKLED-TIMES", "rb" )
        
        times       = pickle.load( fileHandle )
        lastCronjob = times[clientName]
        
        if update == True :
            times[ clientName ] = currentDate     
        
        fileHandle.close()
    
        
    else:#create a new pickle file  
        
        times = {}
        fileHandle  = open( "PICKLED-TIMES", "wb" )
        
        for client in clients :
            times[client]= currentDate     
        
            
        
        lastCronjob = times[clientName]
        pickle.dump( times, fileHandle )
        
        fileHandle.close()
       

    return lastCronjob

    
            
#################################################################
#                                                               #
#############################PARSER##############################
#                                                               #
#################################################################   
def getOptionsFromParser(  parser ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the hlE variable.   
    
        If errors are encountered in parameters used, it will terminate the application. 
    
    """ 
    
    ( options, args ) = parser.parse_args()        
   
    #we take all space out
    directories  = []
    startTimes   = []
    clients      = options.clients.replace( ' ','' ).split(',')
    machines     = options.machines.replace( ' ', '' ).split(',')
    types        = options.types.replace( ' ', '').split(',')
    currentDate  = MyDateLib.getOriginalDate( time.time() )
    width        = options.width
    interval     = options.interval
    
    try:    
        
        print "interval : %s" %interval
        if  interval != 1 :
            if int( interval ) <= 0 :
                raise 
    
    except:
        
        print "Error. The interval value needs to be an integer one above 0." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
        
    
    try:    
        
        print "width : %s" %width
        if  width != 1 :
            if int( width ) <= 0 :
                raise 
    
    except:
        
        print "Error. The width value needs to be an integer one above 0." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit() 
    
    for client in clients :
        directories.append( getfilesIntoDirectory( client, machines ) )
        startTimes.append( getLastCronJob( client,currentDate, clients ) )
    
    
    #everything should be ok                    
    infos = _UpdaterInfos( currentDate = currentDate, clients = clients, startTimes = startTimes, machines = machines, directories = directories ,types = types )
    
    return infos 

    
    
def createParser( ):
    """ 
        Builds and returns the parser 
    
    """
    
    usage = """%prog [options]Write something here about options,proper usage, crontab,etc... """    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    #date, pattern, machines, sources, clients
    

    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default="",
                        help="Clients' names")

    parser.add_option("-i", "--interval", type="int", dest="interval", default=1,
                        help="Interval (in minutes) for which a point will be calculated. Will 'smooth' the graph")
    
    parser.add_option("-m", "--machines", action="store", type="string", dest="machines", default='pds5.cmc.ec.gc.ca, pds6.cmc.ec.gc.ca', help="Machines where the logs are")      
       
    parser.add_option("-t", "--types", type="string", dest="types", default="latency",
                        help="Types of data to look for.")           
    
    parser.add_option("-w", "--width", type="int", dest="width", default=1,
                        help="Width of time (in hours) since last crontab job.")



def main():
    """
        Gathers options, then makes call to DirectoryStatsCollector to collec the stats based 
        on parameters received.  
        
    """
    
   
    parser = createParser( )  #will be used to parse options 
    infos = getOptionsFromParser( parser )
    
   
    for i in range( len (infos.clients) ) :
    
        ds = DirectoryStatsCollector( infos.directories[i] )
        ds.collectStats( infos.types, startTime = infos.startTimes[i], width = infos.width * MyDateLib.HOUR, interval = infos.interval * MyDateLib.MINUTE , pickle = DirectoryStatsCollector.buildTodaysFileName( clientName = infos.clients[i] ) )
    
    

if __name__ == "__main__":
    main()
                              
