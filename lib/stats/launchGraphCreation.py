#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : crontabCommands.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006
##
#############################################################################

import os, sys, commands
import PXPaths
from ConfigParser import ConfigParser


PXPaths.normalPaths()
LOCAL_MACHINE = os.uname()[1]


if LOCAL_MACHINE == "pds3-dev" or LOCAL_MACHINE == "pds4-dev" or LOCAL_MACHINE == "lvs1-stage" or LOCAL_MACHINE == "logan1" or LOCAL_MACHINE == "logan2":
    PATH_TO_LOGFILES = PXPaths.LOG + LOCAL_MACHINE + "/"

else:#pds5 pds5 pxatx etc
    PATH_TO_LOGFILES = PXPaths.LOG


        
class _ConfigParameters:
    """
        This class is usefull to store all the values
        collected from the config file into a single 
        object. 
    
    """
    
    def __init__( self, individualLogMachineNames, logMachinesLogins, coupledLogMachineNames, picklingMachines, picklingMachinesLogins, databaseMachines, uploadMachines, uploadMachinesLogins  ):
        """
            Constructor.        
        """    
        
        self.individualLogMachineNames = individualLogMachineNames
        self.logMachinesLogins         = logMachinesLogins
        self.coupledLogMachineNames    = coupledLogMachineNames
        
        self.picklingMachines          = picklingMachines
        self.picklingMachinesLogins    = picklingMachinesLogins
        
        self.databaseMachines          = databaseMachines
        
        self.uploadMachines            = uploadMachines
        self.uploadMachinesLogins      = uploadMachinesLogins
        
        
        
def getIndividualValues( values ):
    """
        Returns all indvidual values from a line 
        of the 1,2;3;4;5,6 style. 
        
        The above example would return an array 
        containing the following : [1,2,3,4,5,6]
        
    """ 
       
    individualValues = [] 
    values = values.split( ";" )
    
    for value in values :
        individualValues.extend( value.split( "," ) )
        
    return individualValues
    
    
        
def getParametersFromConfigurationFile():
    """
        Gather all the parameters from the /apps/px/.../config file.
        
        Returns all collected values in a  _ConfigParameters instance.
    
    """   

    CONFIG = PXPaths.STATS + "config" 
    config = ConfigParser()
    config.readfp( open( CONFIG ) ) 
    
    logFilesMachines          = config.get( 'graphics', 'logFilesMachines' )
    individualLogMachineNames = getIndividualValues( logFilesMachines )
    coupledLogMachineNames    = logFilesMachines.split( ";" )
    
    logMachinesLogins = config.get( 'graphics', 'logFilesMachinesLogins' )
    logMachinesLogins = getIndividualValues( logMachinesLogins )
        
    picklingMachines = config.get( 'graphics', 'picklingMachines' )
    picklingMachines = getIndividualValues( picklingMachines )
    
    picklingMachinesLogins = config.get( 'graphics', 'picklingMachineLogins' )
    picklingMachinesLogins = getIndividualValues( picklingMachinesLogins )
    
   
    databaseMachines = config.get( 'databases', 'machineNames' ).split( ";" )
    
    uploadMachines       = config.get( 'uploads', 'machineNames' ).split( ";" )
    uploadMachinesLogins = config.get( 'uploads', 'logins' ).split( ";" )
    
    parameters = _ConfigParameters( individualLogMachineNames, logMachinesLogins, coupledLogMachineNames, picklingMachines, picklingMachinesLogins, databaseMachines, uploadMachines, uploadMachinesLogins )
    
    
#     
#     print "individualLogMachineNames : %s" %individualLogMachineNames
#     print "logMachinesLogins : %s" %logMachinesLogins
#     print "coupledLogMachineNames : %s" %coupledLogMachineNames
#     print "picklingMachinesprint : %s"  %picklingMachines
#     print "picklingMachinesLogins  %s" %picklingMachinesLogins
#     print "databaseMachines : %s" % databaseMachines
#     print "uploadMachines : %s"  %uploadMachines
#     print "uploadMachinesLogins : %s" %uploadMachinesLogins
    
    return parameters    

    

def validateParameters( parameters, logger = None  ):
    """
        Validates parameters. 
        
        If a an illegal parameter is encountered application
        will be terminated.     
          
    """   
    
    if len(parameters.individualLogMachineNames ) != len(parameters.picklingMachines ) or  len(parameters.individualLogMachineNames ) !=  len(parameters.picklingMachines )  or len(parameters.picklingMachines ) != len( parameters.picklingMachinesLogins ):
    
        if logger != None:
            logger.error("Error reading config file in launchGraphCreation program. Program was terminated abruptly.") 
        print " Error reading config file in launchGraphCreation program. Program was terminated abruptly."        
        sys.exit()
    
        
    if len( parameters.uploadMachines ) != len( parameters.uploadMachinesLogins ):
            
        if logger != None:
            logger.error("Error reading config file in launchGraphCreation program. Program was terminated abruptly.") 
        print " Error reading config file in launchGraphCreation program. Program was terminated abruptly."        
        sys.exit()
    

            
def updatePickles( parameters ):
    """
        Updates the pickle files for all the specified log machines
        so that they are available for graphic production.
        
        Pickling is to be done on specified pickling machines.
        
        All the pickle files that are produced on remote machines will be 
        downloaded on the local machine.
    
    """      
        
    for i in range( len( parameters.individualLogMachineNames ) ):
        
    
        if parameters.individualLogMachineNames[i] != parameters.picklingMachines[i]: 
            
            if parameters.picklingMachines[i] != LOCAL_MACHINE :#pickling to be done elsewhere
                
                status, output = commands.getstatusoutput( "ssh %s@%s 'rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/ /apps/px/log/%s/' >>/dev/null 2>&1" %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i], parameters.logMachinesLogins[i] ,parameters.individualLogMachineNames[i] , parameters.picklingMachines[i] ) )
                
                #print output
                
                print "ssh %s@%s 'rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/ /apps/px/log/%s/' >>/dev/null 2>&1" %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i], parameters.logMachinesLogins[i] ,parameters.individualLogMachineNames[i] , parameters.picklingMachines[i] )
            
            
            else:
                status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/ /apps/px/log/%s/ >>/dev/null 2>&1" %( parameters.logMachinesLogins[i] ,parameters.individualLogMachineNames[i] , parameters.picklingMachines[i] ) )
                
                print "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/ /apps/px/log/%s/ >>/dev/null 2>&1" %(parameters.logMachinesLogins[i] ,parameters.individualLogMachineNames[i] , parameters.picklingMachines[i] )   
            
        if parameters.picklingMachines[i] != LOCAL_MACHINE :#pickling to be done elsewhere            
                            
            status, output = commands.getstatusoutput( "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py  -f rx'  >>/dev/null 2>&1 " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i] ) )
            print output
            print "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py  -f rx'  >>/dev/null 2>&1 " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i] )
            
            status, output = commands.getstatusoutput( "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py -f tx' >>/dev/null 2>&1 " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i] ) )
            print output
            print "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py -f tx' >>/dev/null 2>&1 " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i] )             
            
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/pickleSynchroniser.py -l %s -m %s >>/dev/null 2>&1 " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i] ) )      
            print output            
            print "/apps/px/lib/stats/pickleSynchroniser.py -l %s -m %s >>/dev/null 2>&1 " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i] )
            
            
        
        
        else: # pickling is to be done locally. Log files may or may not reside elsewhere.
            
            status, output = commands.getstatusoutput( "python /apps/px/lib/stats/pickleUpdater.py -f rx  >>/dev/null 2>&1" )
            print output
            print "python /apps/px/lib/stats/pickleUpdater.py -f rx  >>/dev/null 2>&1"
            
            status, output = commands.getstatusoutput( "python /apps/px/lib/stats/pickleUpdater.py -f tx >>/dev/null 2>&1" )
            print output
            print "python /apps/px/lib/stats/pickleUpdater.py -f tx >>/dev/null 2>&1"
            
            
def generateGraphics( parameters ):
    """
        Generates all the required graphics. 
        
        Will generate combined graphics for couples,
        and single for singles.
        
    """
    
    start = 0 
    end   = 0
            
    for couple in parameters.coupledLogMachineNames:
        
        end    = start + len( couple.split( "," ) ) 
        logins = parameters.logMachinesLogins[ start:end ]

        logins = str(logins).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        
        if "," in couple :
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -m %s -c  -l %s>>/dev/null 2>&1  " %(couple.replace( "'","" ),logins.replace( "'","" )) )
            print output
        else:
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -i -m %s -l %s >>/dev/null 2>&1 " %( couple.replace( "'","" ),logins.replace( "'","" ) ) )    
            print output
        
        start = start + len( couple.split( "," )  )  

        
        
def uploadGraphicFiles( parameters ):
    """
        Takes all created graphics and uploads them
        to the machines specified in the parameters. 
    """
    
   
    for i in range ( len( parameters.uploadMachines ) ):
        status, output = commands.getstatusoutput( "scp /apps/px/stats/graphs/symlinks/* %s@%s:/apps/pds/tools/Columbo/ColumboShow/graphs/ >>/dev/null 2>&1" %( parameters.uploadMachinesLogins[i], parameters.uploadMachines[i] ) )
        
        print "scp /apps/px/stats/graphs/symlinks/* %s@%s:/apps/pds/tools/Columbo/ColumboShow/graphs/ >>/dev/null 2>&1" %( parameters.uploadMachinesLogins[i], parameters.uploadMachines[i] )
        

def updateDatabases( parameters ):
    """
        Updates all the required databases by transferring the
        data found in the pickle files into rrd databases files.
    """
        
    for machine in parameters.databaseMachines : 
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/transferPickleToRRD.py -m %s >>/dev/null 2>&1" %machine )
        print  "/apps/px/lib/stats/transferPickleToRRD.py -m '%s' >>/dev/null 2>&1" %machine


def getGraphicsForWebPages( ):
    """
    """
    x =1
                    
def main():
    """
        Gets all the parameters from config file.
        Updates pickle files.
        Generates all the required graphics.
        Updates the desired databases. 
        Uploads graphics to the required machines. 
    
    """
    
    parameters = getParametersFromConfigurationFile()
    validateParameters( parameters )
    updatePickles( parameters )
    #generateGraphics( parameters )
    #updateDatabases( parameters )
    #getGraphicsForWebPages()
    #uploadGraphicFiles( parameters )
            
    print "Finished."
    
    
    
if __name__ == "__main__":
    main()
