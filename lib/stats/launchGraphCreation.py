#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : launchGraphCreation.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006, Last updated on May 07th 2007
##
#############################################################################

import os, sys, commands
import PXPaths, MyDateLib

from MachineConfigParameters import MachineConfigParameters
from StatsConfigParameters import StatsConfigParameters
from MyDateLib import *

PXPaths.normalPaths()
LOCAL_MACHINE = os.uname()[1]
            

def validateParameters( parameters, machineParameters, logger = None  ):
    """
        Validates parameters. 
        
        If a an illegal parameter is encountered application
        will be terminated.     
          
    """   
    
    if len( parameters.picklingMachines ) != len(parameters.sourceMachinesTags ) :
    
        if logger != None:
            logger.error("Error reading config file in launchGraphCreation program. Parameter number mismatch. Program was terminated abruptly.") 
        print "Error reading config file in launchGraphCreation program. Parameter number mismatch. Program was terminated abruptly."       
        sys.exit()
    
        
    for tag in parameters.sourceMachinesTags:
        
        if len( parameters.detailedParameters.sourceMachinesForTag[tag]) != len( parameters.detailedParameters.picklingMachines[tag] ):    
            if logger != None:
                logger.error("Error reading config file in launchGraphCreation program. Parameter number mismatch. Program was terminated abruptly.") 
            print tag
            print "Error reading config file in launchGraphCreation program. Parameter number mismatch number 2. Program was terminated abruptly."    
            sys.exit()
               
        for machine in parameters.detailedParameters.sourceMachinesForTag[tag]:
            if machineParameters.getUserNameForMachine( machine ) == "":            
                        
                if logger != None:
                    logger.error("Error reading config file in launchGraphCreation program. Program was terminated abruptly.") 
                print "Error reading config file in launchGraphCreation program. Program was terminated abruptly."    
                sys.exit()
    

            
def updatePickles( parameters, machineParameters ):
    """
        Updates the pickle files for all the specified log machines
        so that they are available for graphic production.
        
        Pickling is to be done on specified pickling machines.
        
        All the pickle files that are produced on remote machines will be 
        downloaded on the local machine.
    
    """      
        
    for tag in parameters.sourceMachinesTags:
        
        sourceMachines = machineParameters.getMachinesAssociatedWith(tag)            
        
        for i in range( len( sourceMachines  ) ):
            
            picklingMachine  = parameters.detailedParameters.picklingMachines[tag][i]
                        
            # If pickling and source machines differ, download log files frm source to pickling machine.            
            if  sourceMachines[i] != picklingMachine: 
                
                if parameters.detailedParameters.picklingMachines[tag][i] != LOCAL_MACHINE :#pickling to be done elsewhere
                    for j in range(3):#do 3 times in case of currently turning log files.
                        status, output = commands.getstatusoutput( "ssh %s@%s 'rsync -avzr --delete-before -e ssh  %s@%s:/apps/px/log/ /apps/px/log/%s/' "  %( machineParameters.getUserNameForMachine( picklingMachine), picklingMachine,machineParameters.getUserNameForMachine( sourceMachines[i] ) ,sourceMachines[i] , sourceMachines[i]) )
                        print "ssh %s@%s 'rsync -avzr --delete-before -e ssh  %s@%s:/apps/px/log/ /apps/px/log/%s/' " %( machineParameters.getUserNameForMachine( picklingMachine), picklingMachine,machineParameters.getUserNameForMachine( sourceMachines[i] ) ,sourceMachines[i] , sourceMachines[i])    
                else:
                    
                    for j in range(3):#do 3 times in case of currently turning log files.
                        status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/   /apps/px/log/%s/ " %( machineParameters.getUserNameForMachine( sourceMachines[i] ), sourceMachines[i] , sourceMachines[i] ) )
                        print "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/   /apps/px/log/%s/ " %( machineParameters.getUserNameForMachine( sourceMachines[i] ), sourceMachines[i] , sourceMachines[i] )
                print output   
                                
                
            if picklingMachine != LOCAL_MACHINE :#pickling to be done elsewhere,needs ssh             
                print "*************pickling machine %s"    %picklingMachine            
                status, output = commands.getstatusoutput( "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py  -m %s -f rx'   " %( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine,  sourceMachines[i] ) ) 
                
                print "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py  -m %s -f rx'   "  %( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine,  sourceMachines[i] )
                
                print output
                status, output = commands.getstatusoutput( "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py -m %s -f tx'  "( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine ,  sourceMachines[i] ) )
                print "ssh %s@%s 'python /apps/px/lib/stats/pickleUpdater.py -m %s -f tx'  "%( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine ,  sourceMachines[i] )
                print output
                status, output = commands.getstatusoutput( "/apps/px/lib/stats/pickleSynchroniser.py -l %s -m %s  "%( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine ) )      
                print "/apps/px/lib/stats/pickleSynchroniser.py -l %s -m %s  " %( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine )
                print output
            
                
            else: # pickling is to be done locally. Log files may or may not reside elsewhere.
                print "*************pickling machine %s"    %picklingMachine
                status, output = commands.getstatusoutput( "python /apps/px/lib/stats/pickleUpdater.py -f rx -m %s "%( sourceMachines[i] ) )
                print output
                print "python /apps/px/lib/stats/pickleUpdater.py -f rx -m %s " %( sourceMachines[i] )
                
                status, output = commands.getstatusoutput( "python /apps/px/lib/stats/pickleUpdater.py -f tx -m %s "  %(  sourceMachines[i]) )
                print output
                
                print "python /apps/px/lib/stats/pickleUpdater.py -f tx -m %s " %( sourceMachines[i] )
            
            
            
            
def generateColumboGraphics( parameters, machineParameters ):
    """
        Generates all the graphics required by columbo. 
        
        Will generate combined graphics for couples,
        and single for singles.
        
    """
    
    start = 0 
    end   = 0
            
    for machineTag in parameters.sourceMachinesTags:
        
        logins = []
        
        machines = parameters.detailedParameters.sourceMachinesForTag[machineTag]
       
        for machine in machines:
            logins.append( machineParameters.getUserNameForMachine( machine ) )

        print "logins : %s" %logins    
        logins   = str(logins).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        machines = str(machines).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        
        
        if "," in machines :
            print "/apps/px/lib/stats/generateAllGraphsForServer.py -m %s -c  -l %s  " %( machines.replace( "'","" ),logins.replace( "'","" ))
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -m %s -c  -l %s  " %( machines.replace( "'","" ),logins.replace( "'","" )) )
            print output
        else:
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -i -m %s -l %s  " %( machines.replace( "'","" ),logins.replace( "'","" ) ) )    
            print "/apps/px/lib/stats/generateAllGraphsForServer.py -i -m %s -l %s  " %( machines.replace( "'","" ),logins.replace( "'","" ) )
            print output
        
         

        
        
def uploadGraphicFiles( parameters, machineParameters ):
    """
        Takes all the created daily graphics dedicated to clumbo and 
        uploads them to the machines specified in the parameters. 
    """
    
   
    for uploadMachine in parameters.graphicsUpLoadMachines :
        status, output = commands.getstatusoutput( "scp /apps/px/stats/graphs/webGraphics/columbo/* %s@%s:/apps/pds/tools/Columbo/ColumboShow/graphs/ " %( uploadMachine, machineParameters.getUserNameForMachine(uploadMachine) ) )
        
        print "scp /apps/px/stats/graphs/webGraphics/columbo/* %s@%s:/apps/pds/tools/Columbo/ColumboShow/graphs/ " %( machineParameters.getUserNameForMachine(uploadMachine),uploadMachine )
        

        
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
    
    
    
def updateDatabases( parameters, machineParameters ):
    """
        Updates all the required databases by transferring the
        data found in the pickle files into rrd databases files.
    """
           
    #Small safety measure in case another instance of the program is allready running.
    if transferToDatabaseAlreadyRunning() == False :
        
        for tag in parameters.machinesToBackupInDb :
             machines = machineParameters.getMachinesAssociatedWith(tag)             
             machines = str( machines ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
             #status, output = commands.getstatusoutput( "/apps/px/lib/stats/transferPickleToRRD.py -m '%s'" %machines )
             print  "/apps/px/lib/stats/transferPickleToRRD.py -m '%s' " %machines
             #print "output:%s" %output

        print "###%s " %parameters.groupParameters.groups
        print "###%s " %parameters.groupParameters.groupFileTypes
        print "###%s " %parameters.groupParameters.groupsMembers
        print "###%s " %parameters.groupParameters.groupsProducts
        
        if parameters.groupParameters.groups != []:
            for group in  parameters.groupParameters.groups :
                                
                groupMembers = str( parameters.groupParameters.groupsMembers[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
                groupMachines = str( parameters.groupParameters.groupsMachines[group] ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )                 
                groupProducts = str( parameters.groupParameters.groupsProducts[group] ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
                             
                status, output = commands.getstatusoutput( "/apps/px/lib/stats/transferPickleToRRD.py -c '%s' -m '%s' -g '%s', -p '%s' " %( groupMembers, groupMachines, group, groupProducts  ) )
                print  "/apps/px/lib/stats/transferPickleToRRD.py -c '%s' -m '%s' -g '%s', -p '%s' "  %( groupMembers, groupMachines, group, groupProducts  )
 
 
def getGraphicsForWebPages( ):
    """
        Launchs the getGraphicsForWebPages.py
        program. 
        
    """
    
    #status, output = commands.getstatusoutput("/apps/px/lib/stats/getGraphicsForWebPages.py")
    #print output                    


    
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
        print "/apps/px/lib/stats/statsMonitor.py"
        
        
def main():
    """
        Gets all the parameters from config file.
        Updates pickle files.
        Generates all the required graphics.
        Updates the desired databases. 
        Uploads graphics to the required machines. 
    
    """
    
    generalParameters = StatsConfigParameters()
    generalParameters.getAllParameters()
    print "***generalParameters.groupParameters %s " %generalParameters.groupParameters.groups 
                                                            
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
       
    validateParameters( generalParameters, machineParameters, None  )
    updatePickles( generalParameters, machineParameters )
    updateDatabases( generalParameters, machineParameters )
    generateColumboGraphics(generalParameters, machineParameters)
    getGraphicsForWebPages()
    updateWebPages()
    uploadGraphicFiles( generalParameters, machineParameters )
    monitorActivities()
    
    
    print "Finished."
    
    
    
if __name__ == "__main__":
    main()
