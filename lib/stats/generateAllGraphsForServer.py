#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.
"""


#############################################################################################
#
# Name  : generateAllGraphsForServer.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-09-12
#
# Description: 
#
# Usage:   This program can be called from command-line.
#
#
##############################################################################################
import os,time, pwd, sys,getopt, commands, fnmatch,pickle
from optparse import OptionParser
import PXPaths 
from PXPaths import * 
from PXManager import *
from  MyDateLib import *
PXPaths.normalPaths()

class _Infos:

    def __init__( self, date, machines, timespan, logins,combinedName, combine ):

            
        self.logins      = logins       # Logins for all machines. 
        self.timespan    = timespan     # Number of hours we want to gather the data from. 
        self.date        = date         # Time when graphs were queried.
        self.machines    = machines     # Machine from wich the data comes.
        self.combinedName= combinedName # To be used if merges = True.
        self.combine     = combine      # Whether or not the machines passes in parameter need to be combined to create
                                        # graphs     

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
- Default Date is current system time.  
- Default span is 12 hours.

Options:
    - With -c|--combine you specify that graphic produced must also be a combination of numerous machines.  
    - With -d|--date you can specify the time of the request.( Usefull for past days and testing. )
    - With -l|--logins you can specifuy wich login must be used for each of the enumerated machines.
    - With -m|--machines you can specify the list of machines to be used.
    - With -s|--span you can specify the time span to be used to create the graphic 
    
      
WARNING: - Client name MUST be specified,no default client exists. 
          
            
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -m pds5                           --> All default values, for machine pds5. 
Ex3: %prog -m pds5 -d '2006-06-30 05:15:00'  --> Machine pds5, Date of call 2006-06-30 05:15:00.
Ex4: %prog -s 24                             --> Uses current time, default machine and 24 hours span.
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
    
    #localMachine = os.uname()[1]
    parser.add_option("-c", "--combine", action="store_true", dest = "combine", default=False, help="Combine data from all specified machines.")
    
    parser.add_option("-d", "--date", action="store", type="string", dest="date", default=MyDateLib.getIsoFromEpoch( time.time() ), help="Decide current time. Usefull for testing.")                     
    parser.add_option( "-l", "--logins", action="store", type="string", dest="logins", default="pds", help = "Logins to be used to connect to machines." ) 
    
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default="pxatx", help = "Machines for wich you want to collect data." ) 
    
    parser.add_option("-s", "--span", action="store",type ="int", dest = "timespan", default=12, help="timespan( in hours) of the graphic.")

    
    
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
    machines         = options.machines.replace( ' ','' ).split( ',' )
    combinedName     = options.machines.replace( ' ','' )
    date             = options.date.replace( '"','' ).replace( "'",'')
    logins           = options.logins.replace( '"', '' ).replace( " ","" ).split( ',' )     
    combine          = options.combine
    
    print date 
    
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
                  
        
    if len( logins ) != len( machines ) :
        print "Error. Number of logins doesn't not match number of machines." 
        print "Use -l 'login1,login2,loginX' for multiple machines."
        print "Program terminated."         
        sys.exit()
        
        
    infos = _Infos( date = date, machines = machines, timespan = timespan, logins = logins, combine = combine, combinedName = combinedName  )
   
    
    return infos     
    
  
    
def main():
    

    parser = createParser( )  #will be used to parse options 
    
    infos = getOptionsFromParser( parser )    
       
    for i in range ( len( infos.machines ) ) :
        
        if not os.path.isdir( '/apps/px/stats/rx/%s/' %infos.machines[i] ):
            os.makedirs(  '/apps/px/stats/rx/%s/' %infos.machines[i], mode=0777 )
        if not os.path.isdir( '/apps/px/stats/tx/%s' %infos.machines[i]  ):
            os.makedirs( '/apps/px/stats/tx/%s/' %infos.machines[i]  , mode=0777 )
        if not os.path.isdir( '/apps/px/stats/trx/%s/' %infos.machines[i]  ):
            os.makedirs(  '/apps/px/stats/trx/%s/' %infos.machines[i], mode=0777 )
        #rsync .conf files. to make sure we're up to date.
        
        status, output = commands.getstatusoutput( "rsync -avzr -e ssh %s@%s:/apps/px/etc/rx/* /apps/px/stats/rx/%s/"  %( infos.logins[i], infos.machines[i], infos.machines[i] ) ) 
        print output
        status, output = commands.getstatusoutput( "rsync -avzr -e ssh %s@%s:/apps/px/etc/tx/* /apps/px/stats/tx/%s/"  %( infos.logins[i], infos.machines[i], infos.machines[i] ) )  
        print output
        status, output = commands.getstatusoutput( "rsync -avzr -e ssh %s@%s:/apps/px/etc/trx/* /apps/px/stats/trx/%s/"  %( infos.logins[i], infos.machines[i], infos.machines[i] ) )         
        print output
        
 
            
                        
        pxManager = PXManager()#need to reset values afterwards.
        PXPaths.RX_CONF  = '/apps/px/stats/tx/%s/'  %infos.machines[i]
        PXPaths.TX_CONF  = '/apps/px/stats/rx/%s/'  %infos.machines[i]
        PXPaths.TRX_CONF = '/apps/px/stats/trx/%s/' %infos.machines[i]
        pxManager.initNames() # Now you must call this method  
        txNames = pxManager.getTxNames()               
        rxNames = pxManager.getRxNames()  
    
            
            
        for txName in txNames:
            status, output = commands.getstatusoutput( "python generateGraphics.py -m '%s' -f tx -c '%s' -d '%s' " %( infos.machines[i],txName, infos.date) )
            print output # for debugging only
            
        for rxName in rxNames:
            status, output = commands.getstatusoutput( "python generateGraphics.py -m '%s' -f rx -c '%s' -d '%s' " %( infos.machines[i] , rxName, infos.date ) )     
            print output #for debugging only

    
    if infos.combine == True and len(machines) > 1:
        #no need to update list of lcient since it should be the same for all clients put in a merger.
        for txName in txNames:
            status, output = commands.getstatusoutput( "python generateGraphics.py -m %s -f tx -c %s -d '2006-09-10 15:00:00' " %( infos.combinedName, txName, infos.date) )
            print output # for debugging only
            
        for rxName in rxNames:
            status, output = commands.getstatusoutput( "python generateGraphics.py -m %s -f rx -c %s -d '2006-09-10 15:00:00' " %( infos.combinedName, rxName,infos.date ) )     
            print output #for debugging on  
    


if __name__ == "__main__":
    main()    