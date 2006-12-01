#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : statsMonitoring.py 
##  
## Author : Nicholas Lemay  
##
## Description : This file is to be used to monitor the different activities
##               that are done with the the stats library. 
##
##               The report build throughout the different monitoring methods
##               will be mailed to the chosen recipients.
##
##  
## Date   : November 29th 2006
##
#############################################################################

import os, sys, commands, pickle
import PXPaths, cpickleWrapper
import smtplib
import DirectoryFileCollector
import mailLib
import readMaxFile
from ClientStatsPickler import ClientStatsPickler 
from PXManager import *

from DirectoryFileCollector import *
from ConfigParser import ConfigParser
from MyDateLib import *
from mailLib import *

PXPaths.normalPaths()

LOCAL_MACHINE = os.uname()[1]



if LOCAL_MACHINE == "pds3-dev" or LOCAL_MACHINE == "pds4-dev" or LOCAL_MACHINE == "lvs1-stage" or LOCAL_MACHINE == "logan1" or LOCAL_MACHINE == "logan2":
    PATH_TO_LOGFILES = PXPaths.LOG + LOCAL_MACHINE + "/"

else:#pds5 pds5 pxatx etc
    PATH_TO_LOGFILES = PXPaths.LOG


        
class _Parameters:
    """
        This class is usefull to store all the values
        collected from the config file into a single 
        object. 
    
    """
    
    def __init__( self, emails, machines, files, folders, maxUsages, startTime, endTime  ):
        """
            Constructor.        
        """    
        
        self.emails    = emails
        self.machines  = machines 
        self.files     = files 
        self.folders   = folders
        self.maxUsages = maxUsages
        self.startTime = startTime 
        self.endTime   = endTime 
          
    
def getParametersFromConfigurationFile():
    """
        Gather all the parameters from the /apps/px/.../config file.
        
        Returns all collected values in a  _ConfigParameters instance.
    
    """   

    CONFIG = PXPaths.STATS + "statsMonitoring/statsMonitoring.conf" 
    config = ConfigParser()
    
    if os.path.isfile( CONFIG ):
        config.readfp( open( CONFIG ) ) 
        
        emails   = config.get( 'statsMonitoring', 'emails' ).split( ";" )
        machines = config.get( 'statsMonitoring', 'machines' ).split( ";" )
        files    = config.get( 'statsMonitoring', 'files' ).split( ";" )
        folders   = config.get( 'statsMonitoring', 'folders' ).split( ";" )
        maxUsages= config.get( 'statsMonitoring', 'maxUsages' ).split( ";" )
    
    else:
        print "%s configuration file not present. Please restore file prior to running" %CONFIG
        sys.exit()   
        
        
    return emails, machines, files, folders, maxUsages   


        
def getMaximumGapsFromConfig():
    """
        lire /apps/pds/tools/Columbo/etc/maxSettings.conf
        
    """
    
    maximumGaps = {} 
    allNames = []
    allNames.extend( getAllTxNames( "pds5,pds6" ) )
    
    allNames.extend( getAllrxNames( "pds5,pds6" ) )
    
    allNames.extend( getAllrxNames( "pxatx" ) )
    allNames.extend( getAllTxNames( "pxatx" ) )
    
    circuitsRegex, default_circuit, timersRegex, default_timer, pxGraphsRegex, default_pxGraph =    readMaxFile.readQueueMax( "/apps/px/lib/stats/", "PX" )
     
    for key in timersRegex.keys(): 
        values = timersRegex[key]
        newKey = key.replace( "^", "" )
        maximumGaps[newKey] = value
    
    for name in allNames:#add all clients/sources for wich no value was set
        if name not in maximumGaps.keys():
            maximumGaps[name] = default_timer    
        
    return maximumGaps 
    
            
    
def savePreviousMonitoringJob( parameters ) :
    """
        
        Set current crontab as the previous crontab.
    
    """
    
    file  = "/apps/px/stats/statMonitoring/previousMonitoringjob"
     
    if not os.path.isdir( os.path.dirname( file ) ):
        os.makedirs(  os.path.dirname( file ) )
    
    fileHandle  = open( file, "w" )

    pickle.dump( parameters.endTime, fileHandle )
     
    fileHandle.close()
    
    
    
def getPreviousMonitoringJob( currentTime ):
    """
        Gets the previous crontab from the pickle file.
        
        Returns "" if file does not exist.
        
    """     
    
    file  = "/apps/px/stats/statMonitoring/previousMonitoringJob"
    previousMonitoringJob = ""
    
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        previousMonitoringJob = pickle.load( fileHandle )
        fileHandle.close()
    
    else:
        previousMonitoringJob = MyDateLib.getIsoTodaysMidnight( currentTime )
        
        
    return previousMonitoringJob
    
    
        
    
def buildReportHeader( parameters ):
    """
        
        Returns the header to eb used 
        within the content of the email.
    
    """
    
    reportHeader = "\n----------------------------------------------------\n"
    reportHeader = reportHeader + "Stats monitor results\n\nTime of test      : %s\n"% parameters.endTime
    reportHeader = reportHeader + "Machine name      : %s\nConfig file  used : %s" %( LOCAL_MACHINE, PXPaths.STATS + "statsMonitoring/statsMonitoring.conf" )
    
    return reportHeader

    
    
def getEmailSubject( currentTime):
    """
        Returns the subject of the
        email to be sent.
    
    """    
    
    
    subject = "[Stats Library Monitoring] %s %s" %( LOCAL_MACHINE, currentTime )
    
    return subject    
    
    
    
def verifyFreeDiskSpace( parameters, report ):
    """
        This method verifies all the free disk 
        space for all the folders where the stats library. 
        
        A disk usage wich is too hight might be a symptom
        of the cleaning systems not working or not being 
        installed properly. 
        
        Adds a warning to the report when the usage is over x%.             
        
    """
    
    reportLines = ""
    onediskUsageIsAboveMax = False    
    foldersToVerify = parameters.folders
    
    for i in range( len( foldersToVerify ) ):
        
        status, output = commands.getstatusoutput( "df %s" %foldersToVerify[i] )
        
        if status == 0 :
            #print "output : %s" %output
            #output = output.splitlines()[1]        
            diskUsage = output.split()[11].replace( "%", "")
            
            if int(diskUsage) > parameters.maxUsages[i]:    
                onediskUsageIsAboveMax = True
                reportLines = reportLines +  "Warning : Disk usage for %s is %s %%.Please investigate cause.\n" %(foldersToVerify[i],diskUsage)   
        else:
            onediskUsageIsAboveMax = True
            reportLines = reportLines +  "Warning : Disk usage for %s was unavailable.Please investigate cause.\n"       %(foldersToVerify[i])
    
    report = report + "\n\n-----------------------------------------------------------------\n"
    if onediskUsageIsAboveMax == True:
        header = "The following disk usage warnings have been found : \n\n"         
    else:
        header = "No disk usage warning has been found.\n"
        
    report = report + header + reportLines 
        
    return report    

        

def saveCurrentCrontab( currentCrontab ) :
    """
        Set current crontab as the previous crontab.
    """
    
    file  = "/apps/px/stats/statMonitoring/previousCrontab"
     
    if not os.path.isdir( os.path.dirname( file ) ):
        os.makedirs(  os.path.dirname( file ) )
    
    fileHandle  = open( file, "w" )

    pickle.dump( currentCrontab, fileHandle )
     
    fileHandle.close()
    
    
    
def getPreviousCrontab():
    """
        Gets the previous crontab from the pickle file.
        
        Returns "" if file does not exist.
        
    """     
    
    file  = "/apps/px/stats/statMonitoring/previousCrontab"
    previousCrontab = ""
    
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        previousCrontab = pickle.load( fileHandle )
        fileHandle.close()
        
    return previousCrontab

    
    
def verifyCrontab( report ):
    """
        Verifies if crontab has been modified since last update. 
        
    """
    
    previousCrontab = getPreviousCrontab()
    status, currentCrontab = commands.getstatusoutput( "crontab -l" )
    
    if currentCrontab != previousCrontab :
        report = report + "\nCrontab entries were modified since last report.\n"
    else:
        report = report + "\n\n"
    
    saveCurrentCrontab( currentCrontab )       
    
    return report
    

def findFirstInterestingLinesPosition( file, startTime, endtime, lastReadPosition = 0 ):
    """
        This method browses a file from the specified lastReadPosition.
        
        From there it tries to find the position of the first interesting line 
        based on specified startTime and endtime. 
        
        Returns last readposition so it can be seeked to read the line found.
        
        Returns the first interesting line line wich will equal "" if end of file was met.
        
        Returns linefound and a line different than "" when a line >= then endtime
        was found without finid a line between startTime and endTime.  
        
        
    """       
    
    lineFound = False
    line = None
    fileHandle = open( file, 'r') 
    fileHandle.seek( lastReadPosition )
    
    
    while lineFound == False and line != "":
        
        lastReadPosition = fileHandle.tell()
        line = fileHandle.readline()            
            
        if line != "" :
            timeOfEntry = line.split( "," )[0]
            #print "timeOfEntry : %s startTime %s" %(timeOfEntry, startTime)
            if timeOfEntry >= startTime :
                lineFound = True 
            if timeOfEntry >= endtime :
                line      = "" 
    
    fileHandle.close()         
    
    return lastReadPosition, lineFound, line
    
    
    
def findHoursBetween( startTime, endTime ):
    """
        Returns all hours between start time and end time.
        
        A startTime of 2006-11-11 01:00:00 and an endTime of
         
    """
    
    hours = []
    start = MyDateLib.getSecondsSinceEpoch( MyDateLib.getIsoWithRoundedHours( startTime ) )
    end   = MyDateLib.getSecondsSinceEpoch( MyDateLib.getIsoWithRoundedHours( endTime ) )
    
    for time in range( int(start), int(end), 3600 ):
        hours.append( MyDateLib.getIsoWithRoundedHours( MyDateLib.getIsoFromEpoch( time )  ))
   
    hours.append( MyDateLib.getIsoWithRoundedHours( endTime ) )
    
    
    return hours
    
    
    
def getSortedLogs( logs ):
    """
        Takes a series of size-based rotating 
        log files and sorts them in chronological 
        order.
        
    """     
       
    logs.sort()                
    logs.reverse()
    
    if len( logs) > 1 and logs[0].endswith("log"):#.log file is always newest.
            
        firstItem     = logs[ 0 ]
        remainingList = logs[ 1: ]
        logs          = remainingList
        logs.append( firstItem )                            
            
    return logs
    
    
         
def findHoursWithNoEntries( logs, startTime, endTime ):
    """
        Returns all the hours for wich no entries were 
        found within specified 
        
    """
    
    i = 0
    j = 0
    hoursWithNoEntries = [] 
    lastReadPosition =0 
    logs = getSortedLogs( logs )     
    hoursBetweenStartAndEnd = findHoursBetween( startTime, endTime )     
    
    while i < ( len( hoursBetweenStartAndEnd ) - 1 ) and j < len( logs ):
        
        lastReadPosition, lineFound, line = findFirstInterestingLinesPosition( logs[j], startTime, endTime, lastReadPosition )        
        
        if lineFound == True and line == "": #not eof,line found > endtime
            hours.append( hoursBetweenStartAndEnd[i] )        
        elif line == "": #file is over
            j = j +1
        
        i = i + 1
    
        
    if i < ( len( hoursBetweenStartAndEnd ) - 1 ):#if j terminated prior to i.
    
        for k in range( i, len( hoursBetweenStartAndEnd ) - 1 ):
            hoursWithNoEntries.append( hoursBetweenStartAndEnd[ k ])
            
    
    return hoursWithNoEntries
    


def verifyStatsLogs( parameters, report ,logger = None ):    
    """
    
        Verifies if any entries exists within all
        4 types of stats log files between the time 
        of the last monitoring job and current time.
        
        Adds to the report the log types for 
        wich there was no entry during specified
        amount of time. 
        
        Returns the report with the added lines
        
    """    
    
    warningsWereFound = False
    newReportLines = ""
    logTypes = [ "graphs", "pickling", "rrd_graphs","rrd_transfer" ]
    
    for logType in logTypes:
        
        dfc =  DirectoryFileCollector( startTime  = parameters.startTime , endTime = parameters.endTime, directory = PXPaths.LOG, lastLineRead = "", fileType = "stats", client = "%s" %logType, logger = logger )    
        dfc.collectEntries()
        logs = dfc.entries         
        #print "logs:%s" %logs
        
        if logs == []:
            warningWereFound = True
            newReportLines = newReportLines + "\nWarning : Not a single log entry within %s log files was found between %s and %s. Please investigate. \n "%( logType, parameters.startTime, parameters.endTime )
         
        else:   
        
            hoursWithNoEntries = findHoursWithNoEntries( logs, parameters.startTime, parameters.endTime )
            
            if hoursWithNoEntries != []:
               warningWereFound = True
               
               newReportLines = newReportLines + "Warning : Not a single log entry within %s log files was found for these hours : %s. Please investigate. \n " %( logType, str(hoursWithNoEntries).replace( "[", "").replace( "]", "") )
            
            
    report = report + "\n\n-----------------------------------------------------------------\n"            
    if warningWereFound :
        report = report + "\nThe following stats log files warnings were found : \n"            
        report = report + newReportLines 
    else:
        report = report + "\nNo stats log files warnings were found.\n"
                
    
    return report

 
def sendReportByEmail( parameters, report  ) :
    """
        Takes the report and sends it to the specified 
        recipients using cmc's server.
        
    """

    html = " <html> %s </html>" %(report).replace( "\n", "<br>" )
    text = report
    
    subject = getEmailSubject( parameters.endTime )
    message = mailLib.createhtmlmail(html, text, subject)
    server = smtplib.SMTP("smtp.cmc.ec.gc.ca")
    server.set_debuglevel(1)

    receivers = parameters.emails
    server.sendmail('nicholas.lemay@ec.gc.ca', receivers, message)
    server.quit()

    
def updateConfigurationFiles( machine, login ):
    """
        rsync .conf files from designated machine to local machine
        to make sure we're up to date.

    """

    if not os.path.isdir( '/apps/px/stats/rx/' ):
        os.makedirs(  '/apps/px/stats/rx/' , mode=0777 )
    if not os.path.isdir( '/apps/px/stats/tx/'  ):
        os.makedirs( '/apps/px/stats/tx/', mode=0777 )
    if not os.path.isdir( '/apps/px/stats/trx/' ):
        os.makedirs(  '/apps/px/stats/trx/', mode=0777 )


    status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/etc/rx/ /apps/px/stats/rx/%s/"  %( login, machine, machine) )
    #print output # for debugging only

    status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/etc/tx/ /apps/px/stats/tx/%s/"  %( login, machine, machine ) )
    #print output # for debugging only
   


def getAllTxNames( machines ):
    """
        Gets all the active tx names
        for all the specified machines.
        
    """  
    
    pxManager = PXManager()
    
    if "," in machines:
        machine = machines.split(',')[0]
    else:
        machine = machines    

    remoteMachines= [ "pds3-dev", "pds4-dev","lvs1-stage", "logan1", "logan2" ]
    if localMachine in remoteMachines :#These values need to be set here.
        updateConfigurationFiles( machine, "pds" )
        PXPaths.RX_CONF  = '/apps/px/stats/rx/%s/'  %machine
        PXPaths.TX_CONF  = '/apps/px/stats/tx/%s/'  %machine
        PXPaths.TRX_CONF = '/apps/px/stats/trx/%s/' %machine
    pxManager.initNames() # Now you must call this method

    txNames = pxManager.getTxNames()
    
    return txNames
    
    
    
def getAllRxNames( machines ):
    """
        Gets all the active tx names
        for all the specified machines.
        
    """  
    
    pxManager = PXManager()
    
    if "," in machines:
        machine = machines.split(',')[0]
    else:
        machine = machines    

    remoteMachines= [ "pds3-dev", "pds4-dev","lvs1-stage", "logan1", "logan2" ]
    if localMachine in remoteMachines :#These values need to be set here.
        updateConfigurationFiles( machine, "pds" )
        PXPaths.RX_CONF  = '/apps/px/stats/rx/%s/'  %machine
        PXPaths.TX_CONF  = '/apps/px/stats/tx/%s/'  %machine
        PXPaths.TRX_CONF = '/apps/px/stats/trx/%s/' %machine
    pxManager.initNames() # Now you must call this method

    rxNames = pxManager.getRxNames()
    
    return rxNames
    
    
    
def getFilesAssociatedWith( client, fileType, machines, startTime, endtime ):
    """
        This function verifies whether all the
        expected pickles for all the specified machiens
        between a certain interval are present.  
    
    """
    
    files = []
    hours = findHoursBetween( startTime, endtime )
    
    splitMachines = machines.split(",")
    
    for machine in splitMachines:
    
        if machine == "pxatx":
            machine = LOCAL_MACHINE
        elif machine == "pds5":
            machine = "pds3-dev"
        elif machine == "pds6":
            machine = "pds4-dev"
            
        for hour in hours:
            files.append( ClientStatsPickler.buildThisHoursFileName( client = client, currentTime = hour, fileType = fileType,machine = machine  ) )
    
            
    if len( splitMachines )  > 1:
        
        combinedMachineName = getCombinedMachineName( machines )
            
        for hour in hours:            
            files.append( ClientStatsPickler.buildThisHoursFileName( client = client, currentTime = hour, fileType = fileType,machine = combinedMachineName  ) )
     
                   
    return files
    

def getCombinedMachineName( machines ):
    """
        Gets all the specified machine names 
        and combines the mso they can be used
        to find pickles.
        
    """        
    
    combinedMachineName = ""
    splitMachines = machines.split(",")
    
    for machine in splitMachines:
        if machine == "pxatx":
            machine = LOCAL_MACHINE
        elif machine == "pds5":
            machine = "pds3-dev"
        elif machine == "pds6":
            machine = "pds4-dev"
        
        combinedMachineName += machine
    
    return combinedMachineName                    
            
            
    
def verifyPicklePresence( parameters, report ):
    """
        This fucntion verifies wheteher all the
        expected pickles for all the specified machiens
        between a certain interval are present.   
                  
    """
    
    missingFiles   = False  
    clientLines    = ""
    newReportLines = "" 
    clientIsMissingfiles = False
           
    
    for machine in parameters.machines:
        
        txNames = getAllTxNames( machine )
        rxNames = getAllRxNames( machine ) 
        
        for txName in txNames:
            files = getFilesAssociatedWith( txName, "tx", machine, parameters.startTime, parameters.endTime )
            #print files
            for file in files:
                if not os.path.isfile(file):
                    missingFiles = True
                    clientIsMissingfiles = True
                    clientLines = clientLines + "Warning: %s is missing.\n" %file
            
            if clientIsMissingfiles == True : 
                newReportLines = newReportLines + "\n%s had the following file(s) missing : \n"%txName
                newReportLines = newReportLines + clientLines
                
            clientLines = ""
            clientIsMissingfiles = False
            
            
        for rxName in rxNames:
            files = getFilesAssociatedWith( rxName, "rx", machine, parameters.startTime, parameters.endTime )
            #print files
            for file in files:
                if not os.path.isfile(file):
                    missingFiles = True
                    clientIsMissingfiles = True
                    clientLines = clientLines + "Warning: %s is missing.\n" %file
            
            if clientIsMissingfiles == True : 
                newReportLines = newReportLines + "\n%s had the following file(s) missing : \n"%txName
                newReportLines = newReportLines + clientLines
                
            clientLines = ""
            clientIsMissingfiles = False            
            
    
    report = report + "\n\n-----------------------------------------------------------------\n"
    if missingFiles :
        
        report = report + "\nMissing files were found on this machine.\n"
        report = report + newReportLines
    else:
        report = report + "\nThere were no missing pickle files found on this machine.\n"            
    
    return report 

    
    
def getPickleAnalysis( files, name , timeOfLastUpdate, maximumGap = 10 ):
    """
        This function is used to browse all the pickle files
        in chronological order. 
        
        If any gap longer than maximumGap are found between
        entries they will be added to report. 
        
        Report is returned at the end. 
        
    """
    
    report = ""
    files.sort()
    gapTooWidePresent = False 
    
    for file in files:
        if os.path.isfile(file):
            fcs =  cpickleWrapper.load ( file )
            for entry in fcs.fileEntries:
                if entry.nbFiles != 0 or ( file == files[ len( files ) - 1 ]  ): 
                    entryTime = MyDateLib.getSecondsSinceEpoch( entry.startTime )   
                    lastUpdateInSeconds = MyDateLib.getSecondsSinceEpoch( timeOfLastUpdate )  
                    
                    if ( ( entryTime - lastUpdateInSeconds ) / 60 ) > maximumGap:
                        gapTooWidePresent = True                         
                        report = report + "No data was found between %s and %s.\n" %(timeOfLastUpdate,entry.startTime)    
                        timeOfLastUpdate = entry.startTime                   
                  
                                                    
    if gapTooWidePresent:
        header = "\n%s.\n" %name
        report = header + report
    
    return report 
    
        
    
def verifyPickleContent( parameters, report ):        
    """
        Browses the content of the pickle files 
        associated with specified clients and sources.       
                
    """
    
    # get infos from /pds/tools/Columbo/ColumboShow/lib$ vi readMaxFile.py
    # wich get its infos from  pds/tools/Columbo/etc$ vi maxSettings.conf
            
    for machine in parameters.machines:
        
        txNames = getAllTxNames( machine )
        rxNames = getAllRxNames( machine ) 
        
        if "," in machine:   
            machine = getCombinedMachineName( machine )     
        
        for txName in txNames:
            files = getFilesAssociatedWith( txName, "tx", machine, parameters.startTime, parameters.endTime )
            newReportLines = getPickleAnalysis( files, txName, timeOfLastUpdate = "2006-11-29 00:59:59" )
        
        report = report + newReportLines 
         
        for rxName in rxNames:            
            files = getFilesAssociatedWith( rxName, "rx", machine, parameters.startTime, parameters.endTime )
            newReportLines = getPickleAnalysis( files, rxName, timeOfLastUpdate = "2006-11-29 00:59:59" )
        
        report = report + newReportLines        

    return report               

        
def getParameters():
    """
        Get all the required parameters from 
        the pickled files and from the config 
        files. 
         
    """           
    
    currentTime = MyDateLib.getIsoFromEpoch( time.time() )   
    timeOfLastUpdate = getPreviousMonitoringJob( currentTime ) 
    
    emails, machines, files, folders, maxUsages = getParametersFromConfigurationFile()
    parameters = _Parameters( emails, machines, files, folders, maxUsages,timeOfLastUpdate, currentTime )
    
    return parameters 
    
    
    
    
def main():
    """
        Builds the entire report by 
        runnign all the different monitoring functions.
        
        Sends the report by email to the designed recipients.
        
    """         
    report = ""       
    parameters = getParameters( )     
    
    report = buildReportHeader( parameters )
    report = verifyFreeDiskSpace( parameters, report )    
    report = verifyPicklePresence( parameters, report )    
    report = verifyPickleContent( parameters, report )    
    report = verifyStatsLogs( parameters, report )    
#     #report = verifyFileVersions( parameters, report  )    
    report = verifyCrontab(  report  )    
    savePreviousMonitoringJob( parameters  )    
    sendReportByEmail( parameters, report  )
    
    print parameters
    
    
    
if __name__ == "__main__":
    main()        