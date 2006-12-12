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
    
    def __init__( self, emails, machines, files, folders, maxUsages, maximumGaps, errorsLogFile, maxSettingsFile, startTime, endTime  ):
        """
            Constructor.   
                 
        """    
        
        self.emails          = emails
        self.machines        = machines 
        self.files           = files 
        self.folders         = folders
        self.maxUsages       = maxUsages
        self.maximumGaps     = maximumGaps
        self.startTime       = startTime 
        self.endTime         = endTime 
        self.errorsLogFile   = errorsLogFile
        self.maxSettingsFile = maxSettingsFile 
    
        
def getParametersFromConfigurationFile():
    """
        Gather all the parameters from the /apps/px/.../config file.
        
        Returns all collected values in a  _ConfigParameters instance.
    
    """   

    CONFIG = PXPaths.STATS + "statsMonitoring/statsMonitoring.conf" 
    config = ConfigParser()
    
    if os.path.isfile( CONFIG ):
    
        config.readfp( open( CONFIG ) ) 
        
        emails        = config.get( 'statsMonitoring', 'emails' ).split( ";" )
        machines      = config.get( 'statsMonitoring', 'machines' ).split( ";" )
        files         = config.get( 'statsMonitoring', 'files' ).split( ";" )
        folders       = config.get( 'statsMonitoring', 'folders' ).split( ";" )
        maxUsages     = config.get( 'statsMonitoring', 'maxUsages' ).split( ";" )
        errorsLogFile = config.get( 'statsMonitoring', 'errorsLogFile' )
        maxSettingsFile=config.get( 'statsMonitoring', 'maxSettingsFile' )
    
    else:
        print "%s configuration file not present. Please restore file prior to running" %CONFIG
        sys.exit()   
        
        
    return emails, machines, files, folders, maxUsages, errorsLogFile, maxSettingsFile  


        
def getMaximumGaps( maxSettingsFile ):
    """
        lire /apps/pds/tools/Columbo/etc/maxSettings.conf
        
    """
    
    maximumGaps = {} 
    allNames = []
    allNames.extend( getAllTxNames( "pds5,pds6" ) )    
    allNames.extend( getAllRxNames( "pds5,pds6" ) )
    
    allNames.extend( getAllRxNames( "pxatx" ) )
    allNames.extend( getAllTxNames( "pxatx" ) )
    
    circuitsRegex, default_circuit, timersRegex, default_timer, pxGraphsRegex, default_pxGraph =    readMaxFile.readQueueMax( maxSettingsFile, "PX" )
     
    for key in timersRegex.keys(): 
        values = timersRegex[key]
        newKey = key.replace( "^", "" ).replace( "$","")
        maximumGaps[newKey] = values
    
    for name in allNames:#add all clients/sources for wich no value was set
        if name not in maximumGaps.keys():
            maximumGaps[name] = default_timer    
        
    return maximumGaps 
    
            
    
def savePreviousMonitoringJob( parameters ) :
    """
        
        Set current crontab as the previous crontab.
    
    """
    
    file  = "/apps/px/stats/statsMonitoring/previousMonitoringJob"
     
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
    
    file  = "/apps/px/stats/statsMonitoring/previousMonitoringJob"
    previousMonitoringJob = ""
    
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        previousMonitoringJob = pickle.load( fileHandle )
        fileHandle.close()
    
    else:
        previousMonitoringJob = MyDateLib.getIsoTodaysMidnight( currentTime )
        
        
    return previousMonitoringJob
        
        
    
def getTimeOfLastFilledEntry( name, startTime ):
    """
        Returns the time of the last
        entry that was filled with data 
        for a client/source name.
        
    """    
    
    file  = "/apps/px/stats/statsMonitoring/lastEntryFilledTimes"
    #timeOfLastFilledEntry = ""
    
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        times = pickle.load( fileHandle )
        fileHandle.close()
        
        if name not in times.keys():
            timeOfLastFilledEntry = startTime
        else:
            timeOfLastFilledEntry = times[name]     
    else:
    
        timeOfLastFilledEntry = startTime 
                
   
    return timeOfLastFilledEntry
    
    
    
def saveTimeOfLastFilledEntry( name, timeOfLastFilledEntry ):
    """
        Returns the time of the last
        entry that was filled with data 
        for a client/source name.
        
    """    
    
    file  = "/apps/px/stats/statsMonitoring/lastEntryFilledTimes"
       
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        times = pickle.load( fileHandle )
        fileHandle.close()
            
    else:
        times= {}

    times[ name ]  =  timeOfLastFilledEntry           
    #print "time to be saved for %s : %s" %( name, timeOfLastFilledEntry)
    fileHandle = open( file, "w" )
    pickle.dump( times, fileHandle )
    fileHandle.close()
    
    
    
def buildReportHeader( parameters ):
    """
        
        Returns the header to eb used 
        within the content of the email.
    
    """
    
    reportHeader = "\n\n"
    reportHeader = reportHeader + "Stats monitor results\n----------------------------------------------------------------------------------------------------------------------------------\n"
    reportHeader = reportHeader + "Time of test : %s\n" %parameters.endTime
    reportHeader = reportHeader + "Time of previous test : %s\n" %parameters.startTime
    reportHeader = reportHeader + "Machine name      : %s\nConfig file  used : %s\n" %( LOCAL_MACHINE, PXPaths.STATS + "statsMonitoring/statsMonitoring.conf" )
    
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
            diskUsage = output.split()[11].replace( "%", "")
            
            if int(diskUsage) > parameters.maxUsages[i]:    
                onediskUsageIsAboveMax = True
                reportLines = reportLines +  "Warning : Disk usage for %s is %s %%.Please investigate cause.\n" %(foldersToVerify[i],diskUsage)   
        else:
            onediskUsageIsAboveMax = True
            reportLines = reportLines +  "Warning : Disk usage for %s was unavailable.Please investigate cause.\n"       %(foldersToVerify[i])
    
    
    if onediskUsageIsAboveMax == True:
        header = "\n\nThe following disk usage warnings have been found : \n"         
    else:
        header = "\n\nNo disk usage warning has been found.\n"
    
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"    
                        
    report = report + header + reportLines 
        
    return report    

        

def saveCurrentCrontab( currentCrontab ) :
    """
        Set current crontab as the previous crontab.
    """
    
    file  = "/apps/px/stats/statsMonitoring/previousCrontab"
     
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
    
    file  = "/apps/px/stats/statsMonitoring/previousCrontab"
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
        report = report + "\nCrontab entries were modified since last monitoring job.\n"
    else:
        report = report + "\nCrontab entries were not modified since last monitoring job.\n"
    report = report + "----------------------------------------------------------------------------------------------------------------------------------"    
    
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
    line      = None
    fileHandle = open( file, 'r') 
    fileHandle.seek( lastReadPosition )
    foundValidLine = False 
    
    while lineFound == False and line != "":
        
        lastReadPosition = fileHandle.tell()
        line = fileHandle.readline()                       
        
        if line != "" :
            timeOfEntry = line.split( "," )[0]            
            if timeOfEntry >= startTime :
                foundValidLine = True 
                lineFound = True 
            if timeOfEntry >= endtime :
                foundValidLine = False 
 
    fileHandle.close()         
    
    return lastReadPosition, foundValidLine, line
    
    
    
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
    
    while i < ( len( hoursBetweenStartAndEnd )-1)  and j < len( logs ):
               
        startTime = hoursBetweenStartAndEnd[i]
        endTime   = hoursBetweenStartAndEnd[i+1]
        
        lastReadPosition, lineFound, line = findFirstInterestingLinesPosition( logs[j], startTime, endTime, lastReadPosition )        
        
        if lineFound == False and line != "": #not eof,line found > endtime
            hoursWithNoEntries.append( hoursBetweenStartAndEnd[i] )        
        
        if line == "": #file is over
            j = j + 1
        else:
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
    logTypes = [ "rrd_transfer" ] # "graphs", "pickling", "rrd_graphs",
    verificationTimeSpan =  (MyDateLib.getSecondsSinceEpoch( parameters.endTime ) - MyDateLib.getSecondsSinceEpoch( parameters.startTime )) / (60*60) 
    
    for logType in logTypes:
        
        dfc =  DirectoryFileCollector( startTime  = parameters.startTime , endTime = parameters.endTime, directory = PXPaths.LOG, lastLineRead = "", fileType = "stats", client = "%s" %logType, logger = logger )    
        
        dfc.collectEntries()
        logs = dfc.entries                
        
        
        if logs == [] and verificationTimeSpan >= 1:#if at least an hour between start and end 
            
            warningsWereFound = True
            newReportLines = newReportLines + "\nWarning : Not a single log entry within %s log files was found between %s and %s. Please investigate. \n "%( logType, parameters.startTime, parameters.endTime )
         
        elif logs != []:   
            hoursWithNoEntries = findHoursWithNoEntries( logs, parameters.startTime, parameters.endTime )
            
            if hoursWithNoEntries != []:
               warningsWereFound = True
               
               newReportLines = newReportLines + "Warning : Not a single log entry within %s log files was found for these hours : %s. Please investigate. \n " %( logType, str(hoursWithNoEntries).replace( "[", "").replace( "]", "") )
                       
             
    if warningsWereFound :
        report = report + "\n\nThe following stats log files warnings were found : \n"
        report = report + "----------------------------------------------------------------------------------------------------------------------------------\n"            
        report = report + newReportLines 
    else:
        report = report + "\n\nNo stats log files warnings were found.\n"
        report = report + "----------------------------------------------------------------------------------------------------------------------------------\n"          
    
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
    server.set_debuglevel(0)

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


    status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/etc/tx/ /apps/px/stats/tx/%s/"  %( login, machine, machine ) )

   


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
    
    
    
def getFoldersAndFilesAssociatedWith( client, fileType, machines, startTime, endtime ):
    """
        This function verifies whether all the
        expected pickles for all the specified machiens
        between a certain interval are present.  
    
    """
    
    folders = {}
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
            fileName = ClientStatsPickler.buildThisHoursFileName( client = client, currentTime = hour, fileType = fileType,machine = machine  )
            
            folder = os.path.dirname( os.path.dirname( fileName ) )
            if folder not in folders.keys():
                folders[folder] = []
                
            folders[folder].append( fileName )
    
            
    if len( splitMachines )  > 1:
        
        combinedMachineName = getCombinedMachineName( machines )
            
        for hour in hours:            
            fileName = ClientStatsPickler.buildThisHoursFileName( client = client, currentTime = hour, fileType = fileType,machine = combinedMachineName  ) 
            
            folder = os.path.dirname( os.path.dirname( fileName ) )
            
            if folder not in folders.keys():
                folders[folder] = []
                
            folders[folder].append( fileName )                      
               
    
    return folders
    

    
def getCombinedMachineName( machines ):
    """
        Gets all the specified machine names 
        and combines them so they can be used
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
    startTime =  MyDateLib.getIsoFromEpoch( MyDateLib.getSecondsSinceEpoch( parameters.endTime ) - ( 7*24*60*60 ) )
    
    for machine in parameters.machines:
        
        txNames = getAllTxNames( machine )
        rxNames = getAllRxNames( machine ) 
        
        for txName in txNames:
            folders = getFoldersAndFilesAssociatedWith( txName, "tx", machine, startTime , parameters.endTime )

            
            for folder in folders.keys():
                if os.path.isdir( folder ):
                    for file in folders[folder]:
                        if not os.path.isfile(file):
                            missingFiles = True
                            clientIsMissingfiles = True
                            clientLines = clientLines + "%s\n" %file
                else:
                    missingFiles = True
                    clientIsMissingfiles = True
                    clientLines = clientLines + folder + "/*\n" 
            
            if clientIsMissingfiles == True : 
                
                newReportLines = newReportLines + "\n%s had the following files and folders missing : \n"%txName
                newReportLines = newReportLines + clientLines
                
            clientLines = ""
            clientIsMissingfiles = False
            
            
        for rxName in rxNames:
            folders = getFoldersAndFilesAssociatedWith( rxName, "rx", machine, parameters.startTime, parameters.endTime )

            
            for folder in folders.keys():
                if os.path.isdir( folder ):
                    for file in folders[folder]:
                        if not os.path.isfile(file):
                            missingFiles = True
                            clientIsMissingfiles = True
                            clientLines = clientLines + "Warning: %s is missing.\n" %file
                else:
                    missingFiles = True
                    clientIsMissingfiles = True
                    clientLines = clientLines + folder + "*\n" 
                    
                                    
            if clientIsMissingfiles == True : 
                newReportLines = newReportLines + "\n%s had the following files and folders missing : \n" %txName
                newReportLines = newReportLines + clientLines
                
            clientLines = ""
            clientIsMissingfiles = False            
            
    
    
    if missingFiles :
        
        report = report + "\n\nMissing files were found on this machine.\n"
        report = report + "----------------------------------------------------------------------------------------------------------------------------------\n"
        report = report + newReportLines
    else:
        report = report + "\n\nThere were no missing pickle files found on this machine.\n"  
        report = report + "----------------------------------------------------------------------------------------------------------------------------------\n"          
    
    return report 


        
def gapInErrorLog( name, start, end, errorLog )  :  
    """
        Returns wheter or not the gap described within the 
        parameters is found in a certain log file.
        
    """
    
    gapFound = False 
    difference = None 
    gapInErrorLog = False 
    lastTimeThisGapWasfound = ""
    
    for line in errorLog:
        try:
        
            splitLine = line.split()
            logEntryTime = MyDateLib.getIsoWithRoundedSeconds( splitLine[1] + " " + splitLine[2][:-4] )
            lastEntryTime = MyDateLib.getIsoWithRoundedSeconds( splitLine[9] + " " + splitLine[10] )
            
            
            if splitLine[3].replace( ":", "" ) == name and lastEntryTime == start :            
                
                if logEntryTime > start:
                    gapFound = True 
                lastTimeThisGapWasfound =  logEntryTime 
                
                if logEntryTime >= end:
                    break
            
            elif splitLine[3].replace( ":", "" ) == name and lastEntryTime > start :#newer entry was found for same name 
                break
            
            elif logEntryTime >= end :#in case file is newer than time of end of verification
                break
                
        except:#no date present for last transmission...
            pass
            

    if gapFound == True and lastTimeThisGapWasfound <= end:

        if abs( ( MyDateLib.getSecondsSinceEpoch(end) -  MyDateLib.getSecondsSinceEpoch(lastTimeThisGapWasfound) ) / 60 ) <= 1 :         
            gapInErrorLog = True 
 
                  
    return gapInErrorLog


def getSortedTextFiles( files ):
    """
        Takes a series of size-based rotating 
        log files and sorts them in chronological 
        order.
        
    """     
       
    files.sort()                
    files.reverse()                      
            
    return files
    
    
def getOutdatedTransmissionsLog( file, startTime ):
    """
        Takes a standard transmisson error log 
        and retunrs only the lines containing 
        infos about outdated transmissions. 
    
    """  
          
    errorLog = []  
    files = glob.glob( file + "*")
    files = getSortedTextFiles( files )
    
    
    for file in files :  
        fileHandle = open( file, "r")
        lines = fileHandle.readlines()
    
        for line in lines :
            splitLine = line.split()
            entryTime = splitLine[1] + " " + splitLine[2][:-4]
            if "outdated" in line and entryTime >= startTime :
                errorLog.append( line )           
    
    return errorLog
    
    
    
def getPickleAnalysis( files, name, startTime, maximumGap, errorLog ):
    """
        This function is used to browse all the pickle files
        in chronological order. 
        
        If any gap longer than maximumGap are found between
        entries they will be added to report. 
        
        Report is returned at the end. 
        
    """
    
    header = ""
    reportLines = ""    
    gapTooWidePresent = False
    timeOfLastFilledEntry =  getTimeOfLastFilledEntry( name, startTime )
    files.sort()
    
    for file in files:
        
        if os.path.isfile(file):
            
            fcs =  cpickleWrapper.load ( file )
            
            for entry in fcs.fileEntries:
                nbEntries = len( entry.values.productTypes )
                nbErrors  = entry.values.dictionary["errors"].count(1)
                
                if (  nbEntries != 0 and nbEntries != nbErrors ) or ( file == files[ len( files ) - 1 ] and entry==fcs.fileEntries[ fcs.nbEntries-1 ] ): 
                    
                    entryTime = MyDateLib.getSecondsSinceEpoch( entry.startTime )
                    
                    lastUpdateInSeconds = MyDateLib.getSecondsSinceEpoch( timeOfLastFilledEntry )  
                    differenceInMinutes = ( entryTime - lastUpdateInSeconds ) / 60                   
                                            
                    if  int(differenceInMinutes) > int(maximumGap) :
                                                
                        if gapInErrorLog( name, timeOfLastFilledEntry, entry.startTime, errorLog ) == False:
                            gapTooWidePresent = True  
                                                
                            reportLines = reportLines + "No data was found between %s and %s.\n" %( timeOfLastFilledEntry, entry.startTime )
                    
                    if (  nbEntries != 0 and nbEntries != nbErrors ):
                        timeOfLastFilledEntry = entry.startTime                                                                 
                    
    if reportLines != "":     
        header = "\n%s.\n" %name
        
    reportLines = header + reportLines
    
    return reportLines, timeOfLastFilledEntry 
    

            
    
def verifyPickleContent( parameters, report ):        
    """
        Browses the content of the pickle files 
        associated with specified clients and sources.       
                
    """
    
    newReportLines = ""
    errorLog = getOutdatedTransmissionsLog( parameters.errorsLogFile,parameters.startTime )          
    
    for machine in parameters.machines:
        
        txNames = getAllTxNames( machine )
        
        if "," in machine:   
            machine = getCombinedMachineName( machine )     
        
        for txName in txNames:
            files = []           
            
            folders = getFoldersAndFilesAssociatedWith( txName,"tx", machine, parameters.startTime, parameters.endTime )
            
            for folder in folders.keys(): 
                files.extend( folders[folder] )            

            brandNewReportLines, timeOfLastFilledEntry =  getPickleAnalysis( files, txName, parameters.startTime, parameters.maximumGaps[txName], errorLog )  
               
            newReportLines = newReportLines + brandNewReportLines
            
            saveTimeOfLastFilledEntry( txName, timeOfLastFilledEntry )
    
    if newReportLines != "":
        header = "\n\nThe following data gaps were not found in error log file :\n" 
    else:
        header = "\n\nAll the data gaps were found within the error log file.\n" 
    
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"       
    
    report = report + header + newReportLines        

    return report               

    
        
def getParameters():
    """
        Get all the required parameters from 
        the pickled files and from the config 
        files. 
         
    """           
    
    currentTime = MyDateLib.getIsoFromEpoch( time.time() )  #"2006-12-07 00:00:00" 
    timeOfLastUpdate = getPreviousMonitoringJob( currentTime )      
    emails, machines, files, folders, maxUsages, errorsLogFile, maxSettingsFile = getParametersFromConfigurationFile()
    maximumGaps = getMaximumGaps( maxSettingsFile )
    parameters = _Parameters( emails, machines, files, folders, maxUsages, maximumGaps,errorsLogFile, maxSettingsFile, timeOfLastUpdate, currentTime )
    
    return parameters 
    
    
    
def getFileChecksum( file ):
    """
        Returns the current file checksum of the 
        file.
         
    """
    
    md5sum = 0 
    status, md5Output = commands.getstatusoutput( "md5sum %s " %file )
    
    if status == 0:
        md5sum,fileName = md5Output.split()
    
    return  md5sum    
    
    
    
def getPresentAndAbsentFilesFromParameters( parameters ):
    """
        This method is to be used to get all the filenames
        associated with the parameters received. 
        
        When a folder is used, all the .py files within this 
        directory will be returned.
        
        Note : search of files within a directory is NOT recursive.
    
    """
    
    presentFiles = []
    absentFiles  = [] 
    
    for file in parameters.files:
        
        if os.path.isdir( file ):
            if file[ len(file) -1 ] != '/':
                filePattern = file + '/*.py'
            else :
                filePattern = file + '*.py'    
                
            presentFiles.extend( glob.glob( filePattern ) )
            
        elif os.path.isfile( file ) :
            files.append( file )
        
        else :
           absentFiles.append( file )
            
               
    return presentFiles, absentFiles
    
    
    
def getSavedFileChecksums():
    """
        Returns the checksums saved 
        from the last monitoring job.
        
    """    
    
    file = "/apps/px/stats/statsMonitoring/previousFileChecksums"
    checksums = {}
        
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        checksums = pickle.load( fileHandle )
        fileHandle.close()
        
        
    return checksums 
    
    
    
def saveCurrentChecksums( currentChecksums ) :
    """
        Takes the current checksums and set them 
        as the previous checksums in a pickle file named 
        /apps/px/stats/statsMonitoring/previousFileChecksums
        
    """   
    
    file  = "/apps/px/stats/statsMonitoring/previousFileChecksums"
     
    if not os.path.isdir( os.path.dirname( file ) ):
        os.makedirs(  os.path.dirname( file ) )
    
    fileHandle  = open( file, "w" )

    pickle.dump( currentChecksums, fileHandle )
     
    fileHandle.close()



def verifyFileVersions( parameters, report  ):
    """
        This method is to be used to add the checksums warning 
        found to the report. 
        
        This will set the current checksums found as the previous 
        checksums.
    
    """   
    
    newReportLines = ""
    currentChecksums = {}
    unequalChecksumsFound = False         
        
    presentFiles, absentFiles = getPresentAndAbsentFilesFromParameters( parameters )
    previousFileChecksums = getSavedFileChecksums()
    
    
    for file in absentFiles:
        unequalChecksumsFound = True
        newReportLines = newReportLines + "%s could not be found." %file
    
    for file in presentFiles:
        
        currentChecksums[file] = getFileChecksum( file ) 
        
        if file not in previousFileChecksums.keys():
            unequalChecksumsFound = True
            newReportLines = newReportLines + "%s has been added.\n" %file
        elif currentChecksums[file] != previousFileChecksums[ file ]:
            unequalChecksumsFound = True
            newReportLines = newReportLines + "Checksum for %s has changed since last monitoring job.\n" %file    
    
     
    if unequalChecksumsFound :        
        header = "\n\n\nThe following warning(s) were found while monitoring file cheksums : \n"   
               
    else:        
        header = "\n\n\nNo warnings were found while monitoring file checksums.\n"        
    
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"           
    
    report = report + header + newReportLines
    
    saveCurrentChecksums( currentChecksums )
    
    return report         
    
    
    
def verifyWebPages( parameters, report ):
    """
        This method verifies whether or not
        the different web pages and images are 
        up to date.  
        
    """
    
    newReportLines = ""
    outdatedPageFound = False 
    files = glob.glob( "/apps/px/stats/webPages/*.html" )  
    currentTime = MyDateLib.getSecondsSinceEpoch( parameters.endTime )
    
    
    for file in files :
        timeOfUpdate = os.path.getmtime( file )
        
        if ( currentTime - timeOfUpdate ) / ( 60*60 ) >1 :
            outdatedPageFound = True 
            newReportLines = newReportLines + "%s was not updated since %s" %( file, timeOfUpdate ) 
    
    if outdatedPageFound :
        header = "\n\nThe following web page warning were found :\n"
    else:        
        header = "\n\nAll web pages were found to be up to date.\n"    
    
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"
    
    report = report + header + newReportLines
                
    return report 
        
    
    
def verifyGraphs( parameters, report ):
    """
        Verifies whether or not all daily 
        graphics seem up to date. 
        
    """    
    
    newReportLines = ""
    outdatedGraphsFound = False 
    folder = ( "/apps/px/stats/graphs/symlinks/daily/" )  
    currentTime = MyDateLib.getSecondsSinceEpoch( parameters.endTime )
    
    allNames = []
    allNames.extend( getAllTxNames( "pds5,pds6" ) )    
    allNames.extend( getAllRxNames( "pds5,pds6" ) )    
    allNames.extend( getAllRxNames( "pxatx" ) )
    allNames.extend( getAllTxNames( "pxatx" ) )
    
    for name in allNames :
        completeFolder = folder + name 
        
        if os.path.isdir( completeFolder ):
            images = glob.glob( completeFolder + "/*" )
            newestImage = images[0]
            
            for image in images:
                if os.path.getmtime( image ) > os.path.getmtime( newestImage ):
                    newestImage = image    
            
            if ( currentTime - os.path.getmtime( newestImage ) ) / ( 60*60 ) >1 :
                outdatedGraphsFound = True 
                newReportLines = newReportLines + "%s's daily image was not updated since %s" %( name, os.path.getmtime( newestImage ) ) 
        else:
            outdatedGraphsFound = True 
            newReportLines = newReportLines + "%s was not found." %( file )   
        
    if outdatedGraphsFound :
        header = "\n\nThe following daily graphics warnings were found :\n"
    else:        
        header = "\n\nAll daily graphics were found to be up to date.\n"    
    
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"
    
    report = report + header + newReportLines
                
    return report
    

def updateRequiredfiles():
    """
        This method is used to download 
        the latest version of all the required
        files.
        
    """    
    
    status, output = commands.getstatusoutput( "scp pds@lvs1-op:/apps/pds/tools/Columbo/ColumboShow/log/PX_Errors.txt* /apps/px/stats/statsMonitoring/ >>/dev/null 2>&1" )
    
    status, output = commands.getstatusoutput( "scp pds@lvs1-op:/apps/pds/tools/Columbo/etc/maxSettings.conf /apps/px/stats/statsMonitoring/maxSettings.conf >>/dev/null 2>&1" ) 
    
   
          
def main():
    """
        Builds the entire report by 
        runnign all the different monitoring functions.
        
        Sends the report by email to the designed recipients.
        
    """ 
    
    updateRequiredfiles()        
    report = ""       
    parameters = getParameters( )     
    
    report = buildReportHeader( parameters )
    report = verifyFreeDiskSpace( parameters, report )    
    report = verifyPicklePresence( parameters, report )    
    report = verifyPickleContent( parameters, report )        
    report = verifyStatsLogs( parameters, report )    
    report = verifyFileVersions( parameters, report  )    
    report = verifyCrontab(  report  )   
    report = verifyWebPages( parameters, report )
    report = verifyGraphs( parameters, report ) 
    
    savePreviousMonitoringJob( parameters  )    
    
    sendReportByEmail( parameters, report  )
    #print report 
        
    
    
if __name__ == "__main__":
    main()        