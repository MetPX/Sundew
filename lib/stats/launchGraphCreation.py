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
import PXPaths, MyDateLib
from ConfigParser import ConfigParser
from MyDateLib import *

PXPaths.normalPaths()
LOCAL_MACHINE = os.uname()[1]

        
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
    
                status, output = commands.getstatusoutput( "ssh %s@%s 'rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/ /apps/px/log/%s/' " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i], parameters.logMachinesLogins[i] ,parameters.individualLogMachineNames[i] , parameters.individualLogMachineNames[i] ) )
                       
            else:
                status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/ /apps/px/log/%s/ " %( parameters.logMachinesLogins[i] ,parameters.individualLogMachineNames[i] , parameters.individualLogMachineNames[i] ) )

            print output   
            
        if parameters.picklingMachines[i] != LOCAL_MACHINE :#pickling to be done elsewhere,needs ssh             
                            
            status, output = commands.getstatusoutput( "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py  -m %s -f rx'   " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i],  parameters.individualLogMachineNames[i] ) ) 
            
            print output
            status, output = commands.getstatusoutput( "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py -m %s -f tx'  " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i] ,  parameters.individualLogMachineNames[i] ) )
          
            print output
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/pickleSynchroniser.py -l %s -m %s  " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i] ) )      

            print output
        
        
        else: # pickling is to be done locally. Log files may or may not reside elsewhere.
            
            status, output = commands.getstatusoutput( "python /apps/px/lib/stats/pickleUpdater.py -f rx -m %s " %( parameters.individualLogMachineNames[i] ) )
            print output
            print "python /apps/px/lib/stats/pickleUpdater.py -f rx -m %s " %( parameters.individualLogMachineNames[i])
            
            status, output = commands.getstatusoutput( "python /apps/px/lib/stats/pickleUpdater.py -f tx -m %s "  %(  parameters.individualLogMachineNames[i]) )
            print output
            print "python /apps/px/lib/stats/pickleUpdater.py -f tx -m %s "  %(  parameters.individualLogMachineNames[i])
            
            
            
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
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -m %s -c  -l %s  " %(couple.replace( "'","" ),logins.replace( "'","" )) )
            print output
        else:
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -i -m %s -l %s  " %( couple.replace( "'","" ),logins.replace( "'","" ) ) )    
            print output
        
        start = start + len( couple.split( "," )  )  

        
        
def uploadGraphicFiles( parameters ):
    """
        Takes all created graphics and uploads them
        to the machines specified in the parameters. 
    """
    
   
    for i in range ( len( parameters.uploadMachines ) ):
        status, output = commands.getstatusoutput( "scp /apps/px/stats/graphs/webGraphics/columbo/* %s@%s:/apps/pds/tools/Columbo/ColumboShow/graphs/ " %( parameters.uploadMachinesLogins[i], parameters.uploadMachines[i] ) )
        
        #print "scp /apps/px/stats/graphs/symlinks/* %s@%s:/apps/pds/tools/Columbo/ColumboShow/graphs/ " %( parameters.uploadMachinesLogins[i], parameters.uploadMachines[i] )
        

        
def transferToDatabaseAlreadyRunning():
    """
        Returns whether or not a transfer from pickle 
        to rrd databases is allresdy running.
        
    """
    
    alreadyRuns = False 
    status, output = commands.getstatusoutput( "ps -ax " ) 
    lines = output.splitlines()
    
    for line in lines:        
        if "transferPickleToRRD.py" in line and "R" in line.split()[2]:
            alreadyRuns = True
            break    
        
    return alreadyRuns
    
    
    
def updateDatabases( parameters ):
    """
        Updates all the required databases by transferring the
        data found in the pickle files into rrd databases files.
    """
    if transferToDatabaseAlreadyRunning() == False :    
        for machine in parameters.databaseMachines : 
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/transferPickleToRRD.py -m '%s'" %machine )
            print  "/apps/px/lib/stats/transferPickleToRRD.py -m '%s' " %machine
            print "output:%s" %output
        
        

def getGraphicsForWebPages( ):
    """
        Launchs the getGraphicsForWebPages.py
        program. 
        
    """
    
    status, output = commands.getstatusoutput("/apps/px/lib/stats/getGraphicsForWebPages.py")
    print output                    


def updateWebPages():
    """
        Lauchs all the programs that 
        update the different web pages. 
            
    """ 
       
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/dailyGraphicsWebPage.py" )
    print output
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/weeklyGraphicsWebPage.py" )
    print output
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/monthlyGraphicsWebPage.py" )
    print output
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/yearlyGraphicsWebPage.py" )
    print output
    
    
    
def monitorActivities():
    """
        Monitors all the activities that occured during 
        the course of this program. Report is sent out by mail
        to recipients specified in the config file.
    """    
    currentHour = int( MyDateLib.getIsoFromEpoch( time.time() ).split()[1].split(":")[0] )
    
    if currentHour %4 == 0:
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/statsMonitor.py" )
        print output
        
        
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
    updateDatabases( parameters )
    generateGraphics( parameters )
    getGraphicsForWebPages()
    updateWebPages()
    #uploadGraphicFiles( parameters )
    monitorActivities()        
    print "Finished."
    
    
    
if __name__ == "__main__":
    main()
