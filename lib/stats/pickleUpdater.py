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


#important files 
import os, pwd, sys,getopt, commands, fnmatch,pickle
from optparse import OptionParser
from ConfigParser import ConfigParser
from MyDateLib import *
from DirectoryStatsCollector import DirectoryStatsCollector


class _UpdaterInfos: 
    


    def __init__( self, clients, machines, directories, types, startTimes,collectUpToNow, currentDate = '2005-06-27 13:15:00', interval = 1  ):
        
        """
            Data structure used to contain all necessary info for a call to DirectoryStatscollector. 
            
        """ 
        
        systemsCurrentDate  = MyDateLib.getIsoFromEpoch( time.time() )
        self.clients        = clients                                          # Client for wich the job is done.
        self.machines       = machines                                         # Machines on wich we'll search data. 
        self.types          = types                                            # Data types to collect  
        self.directories    = directories                                      # Get the directory containing files  
        self.interval       = interval                                         # Interval..... 
        self.startTimes     = startTimes                                       # Time of last crontab job.... 
        self.currentDate    = currentDate or  systemsCurrentDate               # Time of the cron job.
        self.collectUpToNow = collectUpToNow                                   # Wheter or not we collect up to now or 
        self.endTime        = self.currentDate                                 # Will be currentDate if collectUpTo                                                                             now is true, start of the current                                                                              hour if not 
       



def getfilesIntoDirectory( clientName, machines = "" ):
    """
        This method is used to get all files wich contains the data we need to look up
        to do the pickle job. 
        
        Returns the directory path wich contains all said files.
    
    """
    
    #Later this will have a connection the the real method that will download files into a directory 
    
    return "/apps/px/lib/stats/files/"
    
    
        
def setLastCronJob( clientName, currentDate, collectUpToNow = False    ):
    """
        This method set the clients lastcronjob to the date received in parameter. 
        Creates new key if key doesn't exist.
        Creates new PICKLED-TIMES file if it doesn't allready exist.   
        
    """
    
    times = {}
    lastCronJob = {}
    fileName = str( os.getcwd() ) + "/" + "PICKLED-TIMES"  
    
    if collectUpToNow == False :
        currentDate = MyDateLib.getIsoWithRoundedHours( currentDate ) 
    
    
    if os.path.isfile( fileName ):
        
        fileHandle  = open( fileName, "r" )
        times       = pickle.load( fileHandle )
        fileHandle.close()
        
        times[ clientName ] = currentDate
        
        fileHandle  = open( fileName, "w" )
        pickle.dump( times, fileHandle )
        fileHandle.close()
    
    
    else:#create a new pickle file  
         
        fileHandle  = open( fileName, "w" )
        
        times[ clientName ] = currentDate          
        
        pickle.dump( times, fileHandle )
        
        fileHandle.close()



def getLastCronJob( clientName, currentDate, collectUpToNow = False    ):
    """
        This method gets the dictionnary containing all the last cron job list. From that dictionnary
        it returns the right value. 
        
        Note : pickled-times would need a better path..... 
        
    """ 
    
    times = {}
    lastCronJob = {}
    fileName = str( os.getcwd() ) + "/" + "PICKLED-TIMES"  
    
    if os.path.isfile( fileName ):
        
        
        
            fileHandle  = open( fileName, "r" )
            times       = pickle.load( fileHandle )
            try :
                lastCronJob = times[ clientName ]
            except:
                lastCronJob = MyDateLib.getIsoTodaysMidnight( currentDate )
                
            fileHandle.close()      
            
    
    else:#create a new pickle file  
         
        fileHandle  = open( fileName, "w" )
        lastCronJob = MyDateLib.getIsoTodaysMidnight( currentDate )
        
        if collectUpToNow == True :
            times[ clientName ] = currentDate    
                
        else:#collecting will only have been made up to the top of the hour....
            times[ clientName ] = MyDateLib.getIsoWithRoundedHours( currentDate ) 
            
         
        pickle.dump( times, fileHandle )
        fileHandle.close()
       

    return lastCronJob

    
            
#################################################################
#                                                               #
#############################PARSER##############################
#                                                               #
#################################################################   
def getOptionsFromParser( parser ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the hlE variable.   
    
        If errors are encountered in parameters used, it will terminate the application. 
    
    """ 
    
    directories  = []
    startTimes   = []
    
    ( options, args ) = parser.parse_args()        
     
    clients         = options.clients.replace( ' ','' ).split(',')
    machines        = options.machines.replace( ' ', '' ).split(',')
    types           = options.types.replace( ' ', '').split(',')
    currentDate     = options.currentDate.replace('"','')
    currentDate     = options.currentDate.replace("'",'')
    interval        = options.interval
    collectUpToNow  = options.collectUpToNow
    
    
    try:    
        
        if  interval != 1 :
            if int( interval ) <= 0 :
                raise 
    
    except:
        
        print "Error. The interval value needs to be an integer one above 0." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
        
    
    for client in clients :
        directories.append( getfilesIntoDirectory( client, machines ) )
        startTimes.append( getLastCronJob( clientName = client, currentDate =  currentDate ,collectUpToNow = collectUpToNow ) )
    
    infos = _UpdaterInfos( currentDate = currentDate, clients = clients, startTimes = startTimes, machines = machines, directories = directories ,types = types, collectUpToNow = collectUpToNow )
    
    if collectUpToNow == False:
        infos.endTime = MyDateLib.getIsoWithRoundedHours( infos.currentDate ) 
    
    
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
  from 00:00:00 of the day of the resquest up to the time of the resquest.    
-
-
Defaults :

- Default Client name does not exist.
- Default Date of update is current system time.  
- Default interval is 1 minute. 
- Default machines value is the entire list of existing machines.  
- Default Now value is False.
- Default Types value is latency.

Options:
 
    - With -c|--clients you can specify the clients names on wich you want to collect data. 
    - With -d|--date you can specify the time of the update.( Usefull for past days and testing. )
    - With -i|--interval you can specify interval in minutes at wich data is collected. 
    - With -m|--machines you can specify on wich machine we must try to download log files.
    - With -n|--now you can specify that data must be collected right up to the minute of the call. 
    - With -t|--types you can specify what data types need to be collected
    
      
WARNING: - Client name MUST be specified,no default client exists. 
         - Interval is set by default to 1 minute. If data pickle here is to be used with 
           ClientGraphicProducer, default value will need to be used since current version only 
           supports 1 minute long buckets. 
          
            
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -c satnet                         --> All default values, for client satnet. 
Ex3: %prog -c satnet -d '2006-06-30 05:15:00'--> Client satnet, Date of call 2006-06-30 05:15:00

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
    
    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default="",
                        help="Clients' names")

    parser.add_option("-d", "--date", action="store", type="string", dest="currentDate", default=MyDateLib.getIsoFromEpoch( time.time() ), help="Decide current time. Usefull for testing.")
                                            
    parser.add_option("-i", "--interval", type="int", dest="interval", default=1,
                        help="Interval (in minutes) for which a point will be calculated. Will 'smooth' the graph")
    
    parser.add_option("-m", "--machines", action="store", type="string", dest="machines", default='pds5.cmc.ec.gc.ca, pds6.cmc.ec.gc.ca', help="Machines where the logs are")      
    
    parser.add_option("-n", "--now", action="store_true", dest = "collectUpToNow", default=False, help="Collect data up to current second.")
       
    parser.add_option("-t", "--types", type="string", dest="types", default="latency",
                        help="Types of data to look for.")          
    

    

def main():
    """
        Gathers options, then makes call to DirectoryStatsCollector to collec the stats based 
        on parameters received.  
        
        
        contains a lot of debugging printing ...needs to me removed in future updates.
    """
    
   
    parser = createParser( )  #will be used to parse options 
    infos = getOptionsFromParser( parser )
    
    for i in range( len (infos.clients) ) :
        print "infos.clients :%s" %infos.clients
        print "start time : %s" %infos.startTimes[i]
        print "interval : %s" %infos.interval
        
        ds = DirectoryStatsCollector( infos.directories[i] )
        print "pickle updater startTime: %s" %infos.startTimes
        
        
        #this section would require a lot of testing to make sure it works properly 
        #In case pickling didnt happen for a few days for some reason... 
        print " infos.startTimes[i] : %s infos.endTime : %s" %(infos.startTimes[i],infos.endTime )
        
        if MyDateLib.areDifferentDays( infos.startTimes[i], infos.endTime ) == True :
            print "111-last pickle on a different day "
            
            nbDifferentDays = MyDateLib.getNumberOfDaysBetween( infos.startTimes[i], infos.endTime )
            
            days = range( nbDifferentDays )
            day = days.reverse()
            
            print "... days to manage : %s " %days 
            for j in days: #Covers days where no pickling was done. 
                
                print "2222-goes in the for"    
                
                if j == ( nbDifferentDays - 1 ):#Day where last pickle occured. No need to pickle all day
                    print "3333-goes to day where last pickle occured"
                    endTime = MyDateLib.getIsoLastMinuteOfDay( infos.startTimes[i] )
                    
                    print "pickle wich allready existed : %s" %DirectoryStatsCollector.buildTodaysFileName( clientName = infos.clients[i], tempTime =  infos.startTimes[i] )
                    
                    ds.collectStats( infos.types, startTime = MyDateLib.getIsoTodaysMidnight( infos.startTimes[i] ), endTime = endTime, interval = infos.interval * MyDateLib.MINUTE , pickle = DirectoryStatsCollector.buildTodaysFileName( clientName = infos.clients[i], tempTime =  infos.startTimes[i] )  )
                
                
                else:#in between days....need to collect everything from 00:00:00 23:59:59
                    
                    rewindedTime = MyDateLib.rewindXDays( infos.endTime, j + 1 ) 
                    
                    endTime = MyDateLib.getIsoLastMinuteOfDay( rewindedTime )
                    
                    print "????-goes to day in between"
                    print "startTime day in between : %s" %MyDateLib.getIsoTodaysMidnight( rewindedTime )
                    print "day between pickle : %s " %DirectoryStatsCollector.buildTodaysFileName( clientName = infos.clients[i], tempTime = rewindedTime )
                    print "endTime : %s " %endTime  
                    
                    ds.collectStats( infos.types, startTime = MyDateLib.getIsoTodaysMidnight( rewindedTime ), endTime = endTime, interval = infos.interval * MyDateLib.MINUTE , pickle = DirectoryStatsCollector.buildTodaysFileName( clientName = infos.clients[i], tempTime = rewindedTime ), width = 24 * MyDateLib.HOUR,   )
                
                    
            #Collect todays data.
            pickle = DirectoryStatsCollector.buildTodaysFileName( clientName = infos.clients[i], tempTime = infos.currentDate )
            
            print "pickle used today : %s " %pickle         
            ds.collectStats( infos.types, startTime = MyDateLib.getIsoTodaysMidnight( infos.endTime ), endTime = infos.endTime, interval = infos.interval * MyDateLib.MINUTE , pickle = pickle   )
                    
                    
                    
        else:#last pickleUpdate happened today 
            print "!!!!-goes to same day pickling"
            pickle = DirectoryStatsCollector.buildTodaysFileName( clientName = infos.clients[i], tempTime = infos.currentDate )
            print "pickled used in calling : %s " %pickle 
            ds.collectStats( infos.types, startTime = infos.startTimes[i], endTime = infos.endTime, interval = infos.interval * MyDateLib.MINUTE , pickle = pickle   )
           
        
        setLastCronJob( clientName = infos.clients[i], currentDate = infos.currentDate, collectUpToNow = infos.collectUpToNow )
        

if __name__ == "__main__":
    main()
                              
