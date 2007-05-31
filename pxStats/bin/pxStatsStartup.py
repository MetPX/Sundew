#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : pxStats.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006, Last updated on May 07th 2007
##
#############################################################################

import os, sys, commands, time
sys.path.insert(1, sys.path[0] + '/../')

from lib.StatsPaths import StatsPaths
from lib.StatsDateLib import StatsDateLib

from lib.MachineConfigParameters import MachineConfigParameters
from lib.StatsConfigParameters import StatsConfigParameters


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
                        status, output = commands.getstatusoutput( "ssh %s@%s 'rsync -avzr --delete-before -e ssh  %s@%s:%s/ %s%s/' "  %( machineParameters.getUserNameForMachine( picklingMachine), picklingMachine,machineParameters.getUserNameForMachine( sourceMachines[i] ) , sourceMachines[i] , StatsPaths.PXLOG, StatsPaths.PXLOG, sourceMachines[i] ) )
                        #print "ssh %s@%s 'rsync -avzr --delete-before -e ssh  %s@%s:%s %s%s/' "%( machineParameters.getUserNameForMachine( picklingMachine), picklingMachine,machineParameters.getUserNameForMachine( sourceMachines[i] ) , sourceMachines[i] , StatsPaths.PXLOG, StatsPaths.PXLOG, sourceMachines[i] ) 
                        #print output
                else:
                    
                    for j in range(3):#do 3 times in case of currently turning log files.
                        status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:%s   %s%s/ " %( machineParameters.getUserNameForMachine( sourceMachines[i] ), sourceMachines[i] , StatsPaths.PXLOG, StatsPaths.PXLOG, sourceMachines[i] ) )
                        #print "rsync -avzr --delete-before -e ssh %s@%s:%s   %s%s/ " %( machineParameters.getUserNameForMachine( sourceMachines[i] ), sourceMachines[i] , StatsPaths.PXLOG, StatsPaths.PXLOG, sourceMachines[i] )
                        #print output   
                                
               
            if picklingMachine != LOCAL_MACHINE :#pickling to be done elsewhere,needs ssh             
                          
                status, output = commands.getstatusoutput( "ssh %s@%s 'python %spickleUpdater.py  -m %s -f rx'   " %( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine, StatsPaths.STATSLIBRARY,  sourceMachines[i] ) ) 
                #print "ssh %s@%s 'python %spickleUpdater.py  -m %s -f rx'   "  %( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine, StatsPaths.STATSLIBRARY, sourceMachines[i] )
                #print output
                
                status, output = commands.getstatusoutput( "ssh %s@%s 'python %spickleUpdater.py -m %s -f tx'  "( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine , StatsPaths.STATSLIBRARY, sourceMachines[i] ) )
                #print "ssh %s@%s 'python %spickleUpdater.py -m %s -f tx'  "%( machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine , StatsPaths.STATSLIBRARY, sourceMachines[i] )
                #print output
                
                status, output = commands.getstatusoutput( "%spickleSynchroniser.py -l %s -m %s  "%( StatsPaths.STATSLIBRARY, machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine ) )      
                #print "%spickleSynchroniser.py -l %s -m %s  " %( StatsPaths.STATSLIBRARY, machineParameters.getUserNameForMachine( picklingMachine ), picklingMachine )
                #print output
            
                
            else: # pickling is to be done locally. Log files may or may not reside elsewhere.
                
                status, output = commands.getstatusoutput( "python %spickleUpdater.py -f rx -m %s "%( StatsPaths.STATSLIBRARY, sourceMachines[i] ) )
                #print output
                #print "python %spickleUpdater.py -f rx -m %s " %( StatsPaths.STATSLIBRARY, sourceMachines[i] )
                
                status, output = commands.getstatusoutput( "python %spickleUpdater.py -f tx -m %s "  %(  StatsPaths.STATSLIBRARY, sourceMachines[i]) )
                #print "python %spickleUpdater.py -f tx -m %s " %( StatsPaths.STATSLIBRARY, sourceMachines[i] )
                #print output
                
                
            

        
def uploadGraphicFiles( parameters, machineParameters ):
    """
        Takes all the created daily graphics dedicated to clumbo and 
        uploads them to the machines specified in the parameters. 
    """
    
   
    for uploadMachine in parameters.graphicsUpLoadMachines :
        status, output = commands.getstatusoutput( "scp %s* %s@%s:%s " %( StatsPaths.STATSCOLGRAPHS, machineParameters.getUserNameForMachine(uploadMachine), uploadMachine, StatsPaths.PDSCOLGRAPHS   ) )
        
        #print "scp %s* %s@%s:%s " %( StatsPaths.STATSCOLGRAPHS, machineParameters.getUserNameForMachine(uploadMachine),uploadMachine, StatsPaths.PDSCOLGRAPHS )
        #print output

        
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
             status, output = commands.getstatusoutput( "%stransferPickleToRRD.py -m '%s'" %(StatsPaths.STATSLIBRARY, machines )  )
             #print  "%stransferPickleToRRD.py -m '%s' " %( StatsPaths.STATSLIBRARY, machines )
             #print "output:%s" %output
        
        if parameters.groupParameters.groups != []:
            
            for group in  parameters.groupParameters.groups :
                                
                groupMembers = str( parameters.groupParameters.groupsMembers[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
                groupMachines = str( parameters.groupParameters.groupsMachines[group] ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )                 
                groupProducts = str( parameters.groupParameters.groupsProducts[group] ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
                groupFileTypes = str(parameters.groupParameters.groupFileTypes[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
               
                status, output = commands.getstatusoutput( "%stransferPickleToRRD.py -c '%s' -m '%s' -g '%s' -f %s -p '%s' " %( StatsPaths.STATSLIBRARY, groupMembers, groupMachines, group, groupFileTypes, groupProducts  ) )
                #print   "%stransferPickleToRRD.py -c '%s' -m '%s' -g '%s' -f %s -p '%s' " %( StatsPaths.STATSLIBRARY, groupMembers, groupMachines, group, groupFileTypes, groupProducts  )
                #print output
 
 
 
def getGraphicsForWebPages( ):
    """
        Launchs the getGraphicsForWebPages.py
        program. 
        
    """
    
    status, output = commands.getstatusoutput( StatsPaths.STATSLIBRARY + "getGraphicsForWebPages.py" )
    #print output                    


    
def updateWebPages():
    """
        Lauchs all the programs that 
        update the different web pages. 
            
    """ 
       
    status, output = commands.getstatusoutput( StatsPaths.STATSLIBRARY + "dailyGraphicsWebPage.py" )  
    status, output = commands.getstatusoutput( StatsPaths.STATSLIBRARY + "weeklyGraphicsWebPage.py" )    
    status, output = commands.getstatusoutput( StatsPaths.STATSLIBRARY + "monthlyGraphicsWebPage.py" )    
    status, output = commands.getstatusoutput( StatsPaths.STATSLIBRARY + "yearlyGraphicsWebPage.py" )    
    status, output = commands.getstatusoutput( StatsPaths.STATSLIBRARY + "totalGraphicsWebPages.py" )    
    status, output = commands.getstatusoutput( StatsPaths.STATSLIBRARY + "generateTopWebPage.py" )
       
    
    
def monitorActivities( timeParameters, currentTime ):
    """
        @summary: Monitors all the activities that occured during 
        the course of this program. Report is sent out by mail
        to recipients specified in the config file.
        
        @param timeParameters: Parameters specifying at wich 
                               frequency the programs need to run.
                               
        @param currenTime: currentTime in seconds since epoch format.
        
    """    
   
    
    if needsToBeRun(timeParameters.monitoringFrequency, currentTime ):        
        status, output = commands.getstatusoutput( StatsPaths.STATSLIBRARY + "statsMonitor.py" )
        #print StatsPaths.STATSLIBRARY + "statsMonitor.py"
        #print output
        
 
def needsToBeRun( frequency, currentTime ):        
    """
    
        @summary : This method is built to mimick the behavior of a crontab entry. 
                    
                   Entries will be judged to be needing to be run if the current time 
                   minus epoch is a multiple of the frequency that was asked in the 
                   parameters. This way we ensure that program are run at every 5 hours
                   for example at not at every hour of the day where the hour number is a
                   5 multiple.
                   
                   Also this prevents us from having to save the time of the last time a 
                   certain program has ran, wich could become troublesome if this program 
                   did not run for a while. 
        
        @param frequency: Frequency at wich a certain program needs to be run.
                          MUST be of the array type and of the the following form: 
                          { value : unitOfTime  } 
       
       @param currentTime: CurrentTime in seconds since epoch format.
       
       @return: Returns wheter a certain program needs to be run or not.
        
    """
    
    needsToBeRun = False     
    
    value = frequency.keys()[0]
     
        
    if frequency[value] == "minutes":
       value = float(value) 
       currentTime = currentTime - ( currentTime % (60) )
       
       if int(currentTime) % int(value*60) == 0:
            needsToBeRun = True    
         
    elif frequency[value] == "hours":      
        value = float(value) 
        currentTime = currentTime - ( currentTime % (60*60) )
        
        if int(currentTime) % int(value*60*60) == 0:
            needsToBeRun = True 
    
    elif frequency[value] == "days":     
        value = float(value)     
        currentTime = currentTime - ( currentTime % (60*60) )
        
        int(currentTime) % int(value*60*60*24)
        if int(currentTime) % int(value*60*60*24) == 0:
            needsToBeRun = True 
    
    elif frequency[value] == "months":
        value = float(value) 
        
        currentMonth = time.strftime( "%m", time.gmtime( currentTime ) )
        if int(currentTime) % int(value) == 0:
            needsToBeRun = True 
    
    return needsToBeRun
    
    
    
def cleanUp( timeParameters, currentTime, daysOfPicklesToKeep ):
    """
    
        @summary: Based on current time and frequencies contained
                  within the time parameters, we will run 
                  the cleaners that need to be run.       
                            
        @param timeParameters: Parameters specifying at wich 
                               frequency the programs need to run.
                               
        @param currenTime: currentTime in seconds since epoch format.
                                  
    """     
    
    if needsToBeRun( timeParameters.pickleCleanerFrequency, currentTime ):
        commands.getstatusoutput( StatsPaths.PXLIB + "pickleCleaner.py")
        #print StatsPaths.PXLIB + "pickleCleaner.py" + " " + str( daysOfPicklesToKeep )
        
    if needsToBeRun( timeParameters.generalCleanerFrequency, currentTime ):
        commands.getstatusoutput( StatsPaths.PXLIB + "clean_dir.plx" + " " + StatsPaths.PXETC + "clean.conf"   )
        #print StatsPaths.PXLIB + "clean_dir.plx" + " " + StatsPaths.PXETC + "clean.conf" 
        
    
    
def backupRRDDatabases( timeParameters, currentTime, nbBackupsToKeep ):
    """
    
        @summary: Based on current time and frequencies contained
                  within the time parameters, we will backup the databases
                  only if necessary.       
                            
        @param timeParameters: Parameters specifying at wich 
                               frequency the programs need to run.
                               
        @param currenTime: currentTime in seconds since epoch format.
                                  
    """  
        
    if needsToBeRun( timeParameters.dbBackupsFrequency, currentTime ):
        commands.getstatusoutput( StatsPaths.PXLIB + "backupRRDDatabases.py" + " " + str(nbBackupsToKeep) )             
        #print StatsPaths.PXLIB + "backupRRDDatabases.py" + " " + str(nbBackupsToKeep)



def main():
    """
        Gets all the parameters from config file.
        Updates pickle files.
        Generates all the required graphics.
        Updates the desired databases. 
        Uploads graphics to the required machines. 
    
    """
    
    currentTime = time.time()
    
    generalParameters = StatsConfigParameters()
    
    generalParameters.getAllParameters()
                                                                
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
    validateParameters( generalParameters, machineParameters, None  )
    
    updatePickles( generalParameters, machineParameters )
    updateDatabases( generalParameters, machineParameters )   
    backupRRDDatabases( generalParameters.timeParameters, currentTime, generalParameters.nbDbBackupsToKeep )
        
    getGraphicsForWebPages()
    updateWebPages()
    uploadGraphicFiles( generalParameters, machineParameters )       
    
    cleanUp( generalParameters.timeParameters, currentTime, generalParameters.daysOfPicklesToKeep )
    
    monitorActivities( generalParameters.timeParameters, currentTime )
    
    print "Finished."
    
    
    
if __name__ == "__main__":
    main()
