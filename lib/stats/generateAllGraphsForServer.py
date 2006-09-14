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
# Description: This program is to be used to create graphics of the same timespan for 
#              one or many machines and for all their respective clients.
#                           
#              Graphics can also be produce by merging the data from different machines.
#
# Usage:   This program can be called from command-line. Use -h for usage.
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

    def __init__( self, date, machines, timespan, logins, combinedName, combine ):
        """
            Data structure to be used to store parameters within parser.
        
        """
                    
        self.logins      = logins       # Logins for all machines. 
        self.timespan    = timespan     # Number of hours we want to gather the data from. 
        self.date        = date         # Time when graphs were queried.
        self.machines    = machines     # Machine from wich the data comes.
        self.combinedName= combinedName # To be used if merges = True.
        self.combine     = combine      # Whether or not the machines passed in parameter need to be combined to create
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
- Default combine value is false.
- Default Date is current system time.
- Default logins is pds.  
- Default machines value is pxatx.
- Default span is 12 hours.

Options:
    - With -c|--combine you specify that graphic produced must also be a combination of numerous machines.  
    - With -d|--date you can specify the time of the request.( Usefull for past days and testing. )
    - With -l|--logins you can specify wich login must be used for each of the enumerated machines.
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
    
    
    
    ( options, args )= parser.parse_args()        
    timespan         = options.timespan
    machines         = options.machines.replace( ' ','' ).split( ',' )
    combinedName     = options.machines.replace( ' ','' ).replace( '[','' ).replace( ']', '' )
    date             = options.date.replace( '"','' ).replace( "'",'')
    logins           = options.logins.replace( '"', '' ).replace( " ","" ).split( ',' )     
    combine          = options.combine
    
    print date 
    
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( date, '%Y-%m-%d %H:%M:%S' )#will raise exception if format is wrong.
        split = date.split()
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
    """
        Create graphics of the same timespan for 
        one or many machines and for all their respective clients.
    """    

    parser = createParser( )  #will be used to parse options 
    
    infos = getOptionsFromParser( parser )    
       
    for i in range ( len( infos.machines ) ) :
        
        #small workaround for temporary test machines    
        if infos.machines[i] == "pds5" :
            machine = "pds3-dev"
        elif infos.machines[i] == "pds6" :
            machine = "pds4-dev"
        else:
            machine = infos.machines[i]
            
            
        #rsync .conf files. to make sure we're up to date.
        if not os.path.isdir( '/apps/px/stats/rx/%s/' %infos.machines[i] ):
            os.makedirs(  '/apps/px/stats/rx/%s/' %infos.machines[i], mode=0777 )
        if not os.path.isdir( '/apps/px/stats/tx/%s' %infos.machines[i]  ):
            os.makedirs( '/apps/px/stats/tx/%s/' %infos.machines[i]  , mode=0777 )
        if not os.path.isdir( '/apps/px/stats/trx/%s/' %infos.machines[i]  ):
            os.makedirs(  '/apps/px/stats/trx/%s/' %infos.machines[i], mode=0777 )
        

            
        status, output = commands.getstatusoutput( "rsync -avzr -e ssh %s@%s:/apps/px/etc/rx/* /apps/px/stats/rx/%s/"  %( infos.logins[i], infos.machines[i], infos.machines[i] ) ) 
        print output # for debugging only
        status, output = commands.getstatusoutput( "rsync -avzr -e ssh %s@%s:/apps/px/etc/tx/* /apps/px/stats/tx/%s/"  %( infos.logins[i], infos.machines[i], infos.machines[i] ) )  
        print output # for debugging only
        status, output = commands.getstatusoutput( "rsync -avzr -e ssh %s@%s:/apps/px/etc/trx/* /apps/px/stats/trx/%s/"  %( infos.logins[i], infos.machines[i], infos.machines[i] ) )         
        print output # for debugging only
                   
        
        #get all clients for wich we need to update the graphics.                
        pxManager = PXManager()#need to reset values afterwards.
        PXPaths.RX_CONF  = '/apps/px/stats/rx/%s/'  %infos.machines[i]
        PXPaths.TX_CONF  = '/apps/px/stats/tx/%s/'  %infos.machines[i]
        PXPaths.TRX_CONF = '/apps/px/stats/trx/%s/' %infos.machines[i]
        pxManager.initNames() # Now you must call this method  
        txNames = pxManager.getTxNames()               
        rxNames = pxManager.getRxNames()      
            
            
        for txName in txNames:
            status, output = commands.getstatusoutput( "python /apps/px/lib/stats/generateGraphics.py -m '%s' -f tx -c '%s' -d '%s' -s %s " %( machine,txName, infos.date, infos.timespan) )
            print output # for debugging only
            
        for rxName in rxNames:
            status, output = commands.getstatusoutput( "python /apps/px/lib/stats/generateGraphics.py -m '%s' -f rx -c '%s' -d '%s' -s %s" %( machine , rxName, infos.date,infos.timespan ) )     
            print output #for debugging only

    print "infos.combine : %s" %infos.combine
    print "len( machines ) : %s" %len( infos.machines )
    
    
    if infos.combine == True and len( infos.machines ) > 1:
    #no need to update list of client since it should be the same for all clients put in a merger.
        
        #workaround to be removed after its installed on real machines
        for i in range ( len( infos.machines ) ) :
        
            #small workaround for temporary test machines    
            if infos.machines[i] == "pds5" :
                infos.machines[i] = "pds3-dev"
            elif infos.machines[i] == "pds6" :
                infos.machines[i] = "pds4-dev"
            else:#case for pxatx?
                infos.machines[i] = infos.machines[i]
        
        infos.combinedName= str(infos.machines).replace( ' ','' ).replace( '[','' ).replace( ']', '' )        
        print "infos.combinedName : %s" %infos.combinedName
        #end of workaround

        
        for txName in txNames:
            status, output = commands.getstatusoutput( "python /apps/px/lib/stats/generateGraphics.py -m %s -f tx -c %s -d '%s' -s %s  " %( infos.combinedName, txName, infos.date,infos.timespan ) )
            print output # for debugging only
            
        for rxName in rxNames:
            status, output = commands.getstatusoutput( "python /apps/px/lib/stats/generateGraphics.py -m %s -f rx -c %s -d '%s' -s %s  " %( infos.combinedName, rxName, infos.date,infos.timespan ) )     
            print output #for debugging on  
    

if __name__ == "__main__":
    main()   
    
    