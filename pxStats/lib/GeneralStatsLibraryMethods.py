#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : generalStatsLibraryMethods.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-12-14, last updated on May 09th 2007
#
# Description: This file contains numerous methods helpfull to many programs within the 
#              stats library. THey have been gathered here as to limit repetition. 
#
##############################################################################################
"""

import os, sys
"""
    Small function that adds pxlib to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    PXManager requires pxlib 
"""
import commands, StatsPaths, PXManager, commands, glob 

import PXPaths

from fnmatch import fnmatch
from PXManager import *

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.MachineConfigParameters import  MachineConfigParameters
from pxStats.lib.RrdUtilities import RrdUtilities
from pxStats.lib.StatsConfigParameters import StatsConfigParameters



class GeneralStatsLibraryMethods:
    
    def filterClientsNamesUsingWilcardFilters( currentTime, timespan, clientNames, machines, fileTypes ):
        """
        
            @param currentTime: currentTime specified in the parameters.
            @param timespan: Time span specified within the parameters.
            @param clientNames:List of client names found in the parameters.
        
        """
        
        newClientNames = []
        
        end   = currentTime
        start = StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch(currentTime)- 60*60*timespan )
        
        if len(clientNames) >=  len( fileTypes ) or len( fileTypes ) ==1:
            
            if len( fileTypes ) == 1 :
                for i in range(1, len( clientNames ) ):
                    fileTypes.append( fileTypes[0])
            
            for clientName,fileType in map( None, clientNames, fileTypes ):
                #print clientName
                
                if  '?' in clientName or '*' in clientName :           
                    
                    pattern =clientName
                   
                    rxHavingRun,txHavingRun = getRxTxNamesHavingRunDuringPeriod(start, end, machines, pattern)
                    
                    if fileType == "rx":
                        namesHavingrun = rxHavingRun
                    else:    
                        namesHavingrun = txHavingRun
                    
                    newClientNames.extend( namesHavingrun )   
                        
                        
                else:
                    newClientNames.append( clientName )   
            
        return newClientNames
    
    
    filterClientsNamesUsingWilcardFilters = staticmethod( filterClientsNamesUsingWilcardFilters )
    
    
    
    def getPathToLogFiles( localMachine, desiredMachine ):
        """
            Local machine : machine on wich we are searching the log files.
            Log source    : From wich machine the logs come from.
        
        """
        
        if localMachine == desiredMachine:
            pathToLogFiles = StatsPaths.PXLOG 
        else:      
            pathToLogFiles = StatsPaths.PXLOG + desiredMachine + "/"        
            
        return pathToLogFiles    
            
    getPathToLogFiles = staticmethod( getPathToLogFiles )
    
     
    def getPathToConfigFiles( localMachine, desiredMachine, confType ):
        """
            Returns the path to the config files.
            
            Local machine : machine on wich we are searching config files.
            desiredMachine : machine for wich we need the the config files.
            confType       : type of config file : rx|tx|trx      
        
        """
            
        pathToConfigFiles = ""
        
        if localMachine == desiredMachine : 
            
            if confType == 'rx': 
                pathToConfigFiles = StatsPaths.PXETCRX
            elif confType == 'tx':
                pathToConfigFiles = StatsPaths.PXETCTX
            elif confType == 'trx':
                pathToConfigFiles = StatsPaths.PXETCTRX
        
        else:
            
            if confType == 'rx': 
                pathToConfigFiles =  StatsPaths.STATSPXRXCONFIGS + desiredMachine
            elif confType == 'tx':
                pathToConfigFiles =  StatsPaths.STATSPXTXCONFIGS + desiredMachine
            elif confType == 'trx':
                pathToConfigFiles =  StatsPaths.STATSPXTRXCONFIGS + desiredMachine             
        
            pathToConfigFiles =   pathToConfigFiles.replace( '"',"").replace( "'",""
                                                                              )   
        return pathToConfigFiles       
        
        
    getPathToConfigFiles = staticmethod( getPathToConfigFiles )    
    
    
    
    def updateConfigurationFiles( machine, login ):
        """
            rsync .conf files from designated machine to local machine
            to make sure we're up to date.
    
        """
    
        if not os.path.isdir( StatsPaths.STATSPXRXCONFIGS + machine ):
            os.makedirs(  StatsPaths.STATSPXRXCONFIGS + machine , mode=0777 )
        if not os.path.isdir( StatsPaths.STATSPXTXCONFIGS + machine  ):
            os.makedirs( StatsPaths.STATSPXTXCONFIGS + machine, mode=0777 )
        if not os.path.isdir( StatsPaths.STATSPXTRXCONFIGS + machine ):
            os.makedirs(  StatsPaths.STATSPXTRXCONFIGS + machine, mode=0777 )
    
    
        status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:%s  %s%s/"  %( login, machine, StatsPaths.PXETCRX, StatsPaths.STATSPXRXCONFIGS, machine ) )
    
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:%s %s%s/"  %( login, machine, StatsPaths.PXETCTX, StatsPaths.STATSPXTXCONFIGS, machine ) )
    
    updateConfigurationFiles = staticmethod( updateConfigurationFiles )    
        
        
        
    def getDataTypesAssociatedWithFileType( fileType ):
        """
            This method is used to get all the data types that 
            are associated withg the file type used as parameter.
            
        """      
            
        dataTypes = []        
        
        if fileType == "tx":
            dataTypes = [ "latency", "bytecount", "errors", "filesOverMaxLatency", "filecount" ]
        elif fileType == "rx":
            dataTypes = [ "bytecount", "errors", "filecount" ]
        
        return dataTypes
    
    getDataTypesAssociatedWithFileType = staticmethod( getDataTypesAssociatedWithFileType )    
    
    
    
    def buildPattern( pattern = "" ):
        '''        
        @param Pattern: pattern from wich to build a matching pattern. Can contain wildcards.               
        
        '''
        
        newPattern = '*'
        
        if pattern == "All":
            newPattern = "*"
        else:
            if pattern[0] != "*" and pattern[0] != '?' :
                newPattern = '*' + pattern
            else:
                newPattern = pattern    
            if pattern[len(pattern) -1] != "*" and pattern[len(pattern) -1] != "?":
                newPattern = newPattern + "*"              
        
        #print "new pattern : %s" %newPattern
                                      
        return newPattern            
    
    
    buildPattern = staticmethod( buildPattern )
    
    
    
    def getRxTxNamesHavingRunDuringPeriod( start, end, machines, pattern = None ):  
        """
            Browses all the rrd database directories to find 
            the time of the last update of each databases.
            
            If database was updated between start and end 
            and the client or source is from the specified 
            machine, the name of the client or source is 
            added to rxNames or txNames.
            
            
        """
        
        rxNames = []
        txNames = []
        txOnlyDatabases = []
        rxTxDatabases = []
        
        
        combinedMachineName = ""
        start = MyDateLib.getSecondsSinceEpoch(start)
        end = MyDateLib.getSecondsSinceEpoch(end)
        
        for machine in machines:
            combinedMachineName = combinedMachineName + machine
        
        rxTxDatabasesLongNames = glob.glob( "%sbytecount/*_%s*" %( StatsPaths.STATSCURRENTDB, combinedMachineName ) )
        txOnlyDatabasesLongNames = glob.glob( "%slatency/*_%s*" %( StatsPaths.STATSCURRENTDB, combinedMachineName )   )
        
        #print combinedMachineName
    
        #Keep only client/source names.
        for rxtxLongName in rxTxDatabasesLongNames:
            if pattern == None:
                rxTxDatabases.append( rxtxLongName )
            else:
                if fnmatch(os.path.basename(rxtxLongName), pattern ):
                    rxTxDatabases.append( rxtxLongName )
             
                
        for txLongName in txOnlyDatabasesLongNames:
            if pattern == None:
                txOnlyDatabases.append( txLongName )    
            else:
                #print "trying to match : %s to %s" %( os.path.basename(txLongName), pattern)
                if fnmatch(os.path.basename(txLongName), pattern):
                 #   print "and it succeeded"
                    txOnlyDatabases.append( txLongName )
       
        #print "@@@@@ %s" %txOnlyDatabases
        #Filter tx names from rxTxNames
        rxOnlyDatabases = filter( lambda x: x not in txOnlyDatabases, rxTxDatabases )    
        
            
            
        for rxDatabase in rxOnlyDatabases:  
            lastUpdate = RrdUtilities.getDatabaseTimeOfUpdate( rxDatabase, "rx" )
            if lastUpdate >= start:
                #fileName format is ../path/rxName_machineName     
                rxDatabase = os.path.basename( rxDatabase )
                rxDatabase = rxDatabase.split("_%s"%combinedMachineName)[0]       
                rxNames.append( rxDatabase  )
            
        for txDatabase in txOnlyDatabases:  
               
            
            #print "lastUpdate: %s" %lastUpdate
            if lastUpdate >= start:
                
                txDatabase = os.path.basename( txDatabase )    
                txDatabase = txDatabase.split("_%s"%combinedMachineName)[0]
                txNames.append( txDatabase )    
       
                
        try:
            rxNames.remove('rx')    
        except:
            pass    
        try:
            txNames.remove('tx')
        except:
            pass
    
        
        rxNames.sort()
        txNames.sort()
        #print "******%s" %rxNames 
        #print "******%s" %txNames        
        return rxNames, txNames               
        
    getRxTxNamesHavingRunDuringPeriod = staticmethod( getRxTxNamesHavingRunDuringPeriod )    
    
    
    
    def getRxTxNames( localMachine, machine ):
        """
            Returns a tuple containing RXnames and TXnames 
            of the currently running sources/clients of a
            desired machine.
             
        """    
                            
        pxManager = PXManager()    
        PXPaths.RX_CONF  = GeneralStatsLibraryMethods.getPathToConfigFiles( localMachine, machine, 'rx' )
        PXPaths.TX_CONF  = GeneralStatsLibraryMethods.getPathToConfigFiles( localMachine, machine, 'tx' )
        PXPaths.TRX_CONF = GeneralStatsLibraryMethods.getPathToConfigFiles( localMachine, machine, 'trx' )
        pxManager.initNames() # Now you must call this method  
        
        if localMachine != machine :
            updateConfigurationFiles( machine, "pds" )
        
        txNames = pxManager.getTxNames()               
        rxNames = pxManager.getRxNames()  
    
        return rxNames, txNames     
        
    
    getRxTxNames = staticmethod(getRxTxNames  )
    
    
    
    def getRxTxNamesForWebPages( start, end ):
        """
    
            @summary: Returns two dictionaries, rx and tx,  whose 
                      keys is the list of rx or tx having run 
                      between start and end.
                      
                      If key has an associated value different from 
                      "", this means that the entry is a group tag name. 
                      
                      The value will be the description of the group. 
                        
            @param start: Start of the span to look into.  
            
            @param end: End of the span to look into.
            
            @return: see summary.
        
        """
    
        
        rxNames = {}
        txNames = {}
    
        
        configParameters = StatsConfigParameters()
        configParameters.getAllParameters()
        machineParameters = MachineConfigParameters()
        machineParameters.getParametersFromMachineConfigurationFile()
        
        
        for sourceMachinesTag in configParameters.sourceMachinesTags:
            machines = machineParameters.getMachinesAssociatedWith( sourceMachinesTag )
    
            newRxNames, newTxNames  = getRxTxNamesHavingRunDuringPeriod( start, end, machines )
             
            for rxName in newRxNames :
                rxNames[rxName] = ""
             
            for txName in newTxNames:
                txNames[txName] = ""
            
        
        for group in configParameters.groupParameters.groups:        
            #print group
            machines  = configParameters.groupParameters.groupsMachines[group]
            machines  = str(machines ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            members   = configParameters.groupParameters.groupsMembers[group]
            members   = str( members ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            fileTypes = configParameters.groupParameters.groupFileTypes[group]
            fileTypes = str(fileTypes ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            products  = configParameters.groupParameters.groupsProducts[group]
            products  = str( products ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            
            description = "-Group Name : %s   -Machine(s) : %s   -Member(s) : %s   -FileType : %s   -Product(s) pattern(s) : %s " %(group, machines, members, fileTypes, products )
            
            if configParameters.groupParameters.groupFileTypes[group] == "tx":
                txNames[group] = description
            elif configParameters.groupParameters.groupFileTypes[group] == "rx":    
                rxNames[group] = description 
                
        return rxNames, txNames
    
        
    getRxTxNamesForWebPages = staticmethod(getRxTxNamesForWebPages  )
    
    
    