#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

"""
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

import os
import commands
import PXPaths
from   optparse import OptionParser 
from   Logger import *

PXPaths.normalPaths()

localMachine = os.uname()[1]

MACHINE_LIST = 'cmisx-spare1'



def getOptionsFromParser( parser ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the hlE variable.    
 
    """ 

    
    ( options, args ) = parser.parse_args()       
    verbose           = options.verbose   
    machines          = options.machines.replace( " ","" ).split( ',' )
    clients           = options.clients.replace( ' ','' ).split( ',')
    login             = options.login.replace( ' ', '' )
    output            = options.output.replace( ' ','' )

    return machines, clients, login, verbose, output 

    
    
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
- Default login value is pds.
- Default verbose value is false. 
- Default output log file is none.

Options:
 
    - With -c|--clients you can specify the clients names for wich you want to synch the data. 
    - With -l|--login you can specify the name you want to use to connect to ssh machines.
    - With -m|--machines you can specify the machines to be used as source for the synch.
    - With -o|--output you can specify an output log file name to be used to store errors that occured with rsync. 
    - with -v|--verbose you can specify that you want to see the ryncs error printed on screen.
         
            
Ex1: %prog                                   --> All default values will be used. 
Ex2: %prog -c satnet                         --> All machines, for client satnet only. 
Ex3: %prog -m 'pds5'"                        --> All clients, on machine pds5 only.
Ex4: %prog -c 'satnet, satnet2' -m 'pds5'    --> Clients satnet, satnet2 on machine named pds5 only.

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
   
    parser.add_option( "-l", "--login", action="store", type="string", dest="login", default="pds", help = "SSH login name to be used to connect to machines." ) 
    
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=MACHINE_LIST, help = "Machine on wich the update is run." ) 
    
    parser.add_option( "-o", "--output", action="store", type="string", dest="output", default="", help = "File to be used as log file." ) 
    
    parser.add_option( "-v", "--verbose", action="store_true", dest = "verbose", default=False, help="Whether or not to print out the errors reported by rsync." )
    


    
    
def buildCommands( machines, clients ):
    """
       Build all the commands that will be needed to synch the files that need to be synchronized.
       
    """ 
    
    commands = []
    
    if clients[0] == "All" :
        for machine in machines :
            commands.append( "rsync -avzr -e ssh pds@%s:%s %s"  %( machine, PXPaths.PICKLES, PXPaths.PICKLES )  )
          
    else:
        
        for client in clients :
            path = PXPaths.PICKLES + client + "/"
            for machine in machines :
                commands.append( "rsync -avzr -e ssh pds@%s:%s %s"  %( machine, path, path )  )

    
    return commands 
    
    
    
def synchronise( commandList, verbose, logger = None ):
    """
        Runs every commands passed in parameter.
        
        Todo : split output from rsync so we get only the usefull part
    
    """
    
    if not os.path.isdir( PXPaths.PICKLES ):
        os.makedirs( PXPaths.PICKLES, mode=0777 )

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
        logger = Logger( PXPaths.LOG + localMachine + '/' + 'stats_' + output + '.log.notb', 'INFO', 'TX' + output ) 
        logger = logger.getLogger()    
    
    return logger 
    
    
    
def main():
    """
        Gathers options, then makes call to synchronise to synchronise the pickle files from the
        different clients and machines received in parameter.  
    
    """
    
    parser   = createParser( )  #will be used to parse options 
    machines, clients, login, verbose, output = getOptionsFromParser( parser )
    logger   = buildLogger( output )    
    commands = buildCommands( machines, clients )
    
    print "Commands that will be executed : %s " %commands 
    synchronise( commands, verbose, logger )
    
    if logger != None :
        logger.info( "This machine has been synchronised with the %s machines for %s clients. " %( machines,clients ) )



if __name__ == "__main__":
    main()