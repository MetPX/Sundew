#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.


#############################################################################################
#
#
# Name  : pickleSynchroniser
#
# Author: Nicholas Lemay
#
# Date  : 2006-08-07
#
# Description : This program is to be used to synchronise the data found on the graphic 
#               producing machine with the machines producing the data. 
#
# Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  PickleUpdater -h | --help
#
#
##############################################################################################
"""

import os, sys
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
    Logger requires pxlib 
"""

import commands

from   pxStats.lib.StatsPaths import StatsPaths
from   optparse import OptionParser 
from   Logger import *

LOCAL_MACHINE = os.uname()[1]


def getOptionsFromParser( parser ):
    """
        
        This method parses the argv received when the program was called
        and returns the parameters.    
 
    """ 

    
    ( options, args ) = parser.parse_args()       
    verbose           = options.verbose   
    machines          = options.machines.replace( " ","" ).split( ',' )
    clients           = options.clients.replace( ' ','' ).split( ',')
    logins            = options.logins.replace( ' ', '' ).split( ',' )
    output            = options.output.replace( ' ','' )

    if (len(logins) != len(machines) ) and len(logins)!=1:
        raise Exception("Error. Number of logins doest not match number of machines.")    
    elif (len(machines) >1 ) and len(logins)==1: 
        for i in range( 1,len(machines) ):
            logins.append( logins[0] )
            
    return machines, clients, logins, verbose, output 

    
    
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

- Default list of machine names is every machine available.
- Default list of client is every client found of a given machine at the time of the call.  
- Default logins value is pds.
- Default verbose value is false. 
- Default output log file is none.

Options:
 
    - With -c|--clients you can specify the clients names for wich you want to synch the data. 
    - With -l|--logins you can specify the name(s) you want to use to connect to ssh machines.
    - With -m|--machines you can specify the machines to be used as source for the synch.
    - With -o|--output you can specify an output log file name to be used to store errors that occured with rsync. 
    - with -v|--verbose you can specify that you want to see the ryncs error printed on screen.
         
            
Ex1: %prog                                    --> All default values will be used. 
Ex2: %prog -m 'machine1'"                     --> All clients, on machine1 only.
Ex3: %prog -c 'client1, client2' -m 'machine1 --> Machine1, for clients 1 and 2 only.

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
   
    parser.add_option( "-l", "--logins", action="store", type="string", dest="logins", default="pds", help = "SSH login name(s) to be used to connect to machines." ) 
    
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=LOCAL_MACHINE, help = "Machine on wich the update is run." ) 
    
    parser.add_option( "-o", "--output", action="store", type="string", dest="output", default="", help = "File to be used as log file." ) 
    
    parser.add_option( "-v", "--verbose", action="store_true", dest = "verbose", default=False, help="Whether or not to print out the errors reported by rsync." )
    


    
    
def buildCommands( logins, machines, clients ):
    """
       @summary: Build all the commands that will be needed to synch the files that need to be synchronized.
       
       @param logins: Logins to be used to build the command.
       
       @param machines: Machines with whom you want to be synchronised.
       
       @param clients: Specific clients/sources for wich you want to be synchronised.
       
       @return: The list of commands that need to be run to be synchronised.
          
    """ 
    
    commands = []

    if clients[0] == "All" :
        for login,machine in map( None, logins, machines) :
            for i in range(3):#do 3 times in case of currently turning log files. 
                commands.append( "rsync -avzr  -e ssh %s@%s:%s %s"  %( login, machine, StatsPaths.STATSPICKLES, StatsPaths.STATSPICKLES )  )
          
    else:
        
        for client in clients :
            path = StatsPaths.STATSPICKLES + client + "/"
            for login, machine in  map( None, logins, machines ):
                for i in range(3):#do 3 times in case of currently turning log files.
                    commands.append( "rsync  -avzr -e ssh %s@%s:%s %s"  %( login, machine, path, path )  )

    
    return commands 
    
    
    
def synchronise( commandList, verbose, logger = None ):
    """
        Runs every commands passed in parameter.
        
        Todo : split output from rsync so we get only the usefull part
    
    """
    
    if not os.path.isdir( StatsPaths.STATSPICKLES ):
        os.makedirs( StatsPaths.STATSPICKLES, mode=0777 )

    for command in commandList :     

        status, rsyncOutput = commands.getstatusoutput( command  )
        
        if status != 0 :
        
            if logger != None :
                logger.warning( rsyncOutput ) 
            elif verbose == True :
                print "There was an error while calling rsync using the following line : %s. " %command
                print "Output was : %s" %rsyncOutput 


                
def buildLogger( output ):
    """
        Build and returns the logger object to be used. 
        
        If output is false logger will equal None
        
    """
    
    logger = None 
    
    if output != "":     
        if not os.path.isdir( StatsPaths.STATSLOGGING  ):
            os.makedirs( StatsPaths.STATSLOGGING  , mode=0777 )  
        logger = Logger( StatsPaths.STATSLOGGING  + 'stats_' + output + '.log.notb', 'INFO', 'TX' + output, bytes = True  ) 
        logger = logger.getLogger()    
    
    return logger 
    
    
    
def main():
    """
        Gathers options, then makes call to synchronise to synchronise the pickle files from the
        different clients and machines received in parameter.  
    
    """       
    parser   = createParser( )  #will be used to parse options 
    machines, clients, logins, verbose, output = getOptionsFromParser( parser )
    logger   = buildLogger( output )    
    commands = buildCommands( logins, machines, clients )    
        
    synchronise( commands, verbose, logger )
    
    if logger != None :
        logger.info( "This machine has been synchronised with the %s machines for %s clients. " %( machines,clients ) )



if __name__ == "__main__":
    main()
