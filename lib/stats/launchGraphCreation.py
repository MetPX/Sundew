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
import configFileManager
from ConfigParser import ConfigParser
from MyDateLib import *

PXPaths.normalPaths()
LOCAL_MACHINE = os.uname()[1]
            

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
                for j in range(3):#do 3 times in case of currently turning log files.
                    status, output = commands.getstatusoutput( "ssh %s@%s 'rsync -avzr --delete-before -e ssh  %s@%s:/apps/px/log/ /apps/px/log/%s/' " %( parameters.picklingMachinesLogins[i], parameters.picklingMachines[i], parameters.logMachinesLogins[i] ,parameters.individualLogMachineNames[i] , parameters.individualLogMachineNames[i] ) )
                       
            else:
                for j in range(3):#do 3 times in case of currently turning log files.
                    status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/   /apps/px/log/%s/ " %( parameters.logMachinesLogins[i] ,parameters.individualLogMachineNames[i] , parameters.individualLogMachineNames[i] ) )

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
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/totalGraphicsWebPages.py" )
    print output 
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateTopWebPage.py" )
    print output
    
    
def monitorActivities():
    """
        Monitors all the activities that occured during 
        the course of this program. Report is sent out by mail
        to recipients specified in the config file.
    """    
    currentHour = int( MyDateLib.getIsoFromEpoch( time.time() ).split()[1].split(":")[0] )
    
    if currentHour %12 == 0:
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/statsMonitor.py" )
        
        
        
def main():
    """
        Gets all the parameters from config file.
        Updates pickle files.
        Generates all the required graphics.
        Updates the desired databases. 
        Uploads graphics to the required machines. 
    
    """
    
    parameters = configFileManager.getParametersFromConfigurationFile( fileType = "statsConfig" )
    validateParameters( parameters )
    updatePickles( parameters )
    updateDatabases( parameters )
    generateGraphics( parameters )
    getGraphicsForWebPages()
    updateWebPages()
    uploadGraphicFiles( parameters )
    monitorActivities()        
    #print "Finished."
    
    
    
if __name__ == "__main__":
    main()
