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
# Date  : 2006-12-14
#
# Description: This file contains numerous methods helpfull to many programs within the 
#              stats library. THey have been gathered here as to limit repetition. 
#
##############################################################################################
"""

import os, commands, PXPaths, PXManager, commands, glob 
import MyDateLib, configFileManager
from PXManager import *
from MyDateLib import *
from configFileManager import *


PXPaths.normalPaths()

def getPathToLogFiles( localMachine, desiredMachine ):
    """
        Local machine : machine on wich we are searching the log files.
        Log source    : From wich machine the logs come from.
    
    """
    
    if localMachine == desiredMachine:
        pathToLogFiles = PXPaths.LOG 
    else:      
        pathToLogFiles = PXPaths.LOG + desiredMachine + "/"        
        
    return pathToLogFiles    
        
 
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
            pathToConfigFiles = PXPaths.RX_CONF
        elif confType == 'tx':
            pathToConfigFiles = PXPaths.TX_CONF
        elif confType == 'trx':
            pathToConfigFiles = PXPaths.TRX_CONF
    
    else:
        
        if confType == 'rx': 
            pathToConfigFiles =  '/apps/px/stats/rx/%s/' %desiredMachine
        elif confType == 'tx':
            pathToConfigFiles = '/apps/px/stats/tx/%s/' %desiredMachine
        elif confType == 'trx':
            pathToConfigFiles = '/apps/px/stats/trx/%s/'  %desiredMachine             
    
                
    return pathToConfigFiles       
    
    
    
def updateConfigurationFiles( machine, login ):
    """
        rsync .conf files from designated machine to local machine
        to make sure we're up to date.

    """

    if not os.path.isdir( '/apps/px/stats/rx/%s' %machine ):
        os.makedirs(  '/apps/px/stats/rx/%s' %machine , mode=0777 )
    if not os.path.isdir( '/apps/px/stats/tx/%s' %machine  ):
        os.makedirs( '/apps/px/stats/tx/%s' %machine, mode=0777 )
    if not os.path.isdir( '/apps/px/stats/trx/%s' %machine ):
        os.makedirs(  '/apps/px/stats/trx/%s' %machine, mode=0777 )


    status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/etc/rx/ /apps/px/stats/rx/%s/"  %( login, machine, machine ) )

    status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/etc/tx/ /apps/px/stats/tx/%s/"  %( login, machine, machine ) )

    
    
def getDatabaseTimeOfUpdate( client, machine, fileType ):
    """
        If present in DATABASE-UPDATES file, returns the time of the last 
        update associated with the databse name.      
        
        Otherwise returns 0 
        
    """ 
    
    lastUpdate = 0
    folder   = PXPaths.STATS + "DATABASE-UPDATES/%s/" %(fileType )
    fileName = folder + "%s_%s" %( client, machine )
    
    if os.path.isfile( fileName ):
        
        fileHandle  = open( fileName, "r" )
        lastUpdate  = pickle.load( fileHandle )           
        fileHandle.close()     
        
            
    return lastUpdate 
    
            

def getRxTxNamesHavingRunDuringPeriod( start, end, machines ):  
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
    
    rxTxDatabasesLongNames = glob.glob( "/apps/px/stats/databases/bytecount/*%s*" %combinedMachineName ) 
    txOnlyDatabasesLongNames = glob.glob( "/apps/px/stats/databases/latency/*%s*" %combinedMachineName )   
    
    
    #Keep only client/source names.
    for rxtxLongName in rxTxDatabasesLongNames:
        rxTxDatabases.append( os.path.basename(rxtxLongName) )
            
    for txLongName in txOnlyDatabasesLongNames:
        txOnlyDatabases.append( os.path.basename(txLongName) )    
    
    #Filter tx names from rxTxNames
    rxOnlyDatabases = filter( lambda x: x not in txOnlyDatabases, rxTxDatabases )    
    
        
        
    for rxDatabase in rxOnlyDatabases:  
    
        rxDatabase = rxDatabase.split("_%s"%combinedMachineName)[0]  
        lastUpdate = getDatabaseTimeOfUpdate( rxDatabase, combinedMachineName, "rx" )
        if lastUpdate >= start:
            #fileName format is ../path/rxName_machineName            
            rxNames.append( rxDatabase  )
        
    for txDatabase in txOnlyDatabases:
        txDatabase = txDatabase.split("_%s"%combinedMachineName)[0]
        lastUpdate = getDatabaseTimeOfUpdate( txDatabase, combinedMachineName, "tx" )
       
        if lastUpdate >= start:
            #fileName format is ../rxName_machineName
            txNames.append( txDatabase )    
        
    rxNames.sort()
    txNames.sort()
            
    return rxNames, txNames
           
    
    
def getRxTxNames( localMachine, machine ):
    """
        Returns a tuple containing RXnames and TXnames 
        of the currently running sources/clients of a
        desired machine.
         
    """    
                        
    pxManager = PXManager()    
    PXPaths.RX_CONF  = getPathToConfigFiles( localMachine, machine, 'rx' )
    PXPaths.TX_CONF  = getPathToConfigFiles( localMachine, machine, 'tx' )
    PXPaths.TRX_CONF = getPathToConfigFiles( localMachine, machine, 'trx' )
    pxManager.initNames() # Now you must call this method  
    
    if localMachine != machine :
        updateConfigurationFiles( machine, "pds" )
    
    txNames = pxManager.getTxNames()               
    rxNames = pxManager.getRxNames()  

    return rxNames, txNames     
    

def getSortedRxTxNamesForWebPages( start, end ):
    """
        Returns the list of all the rx and tx names
        that are running between start and and.        
        
    """ 
    
    rxNames = []
    txNames = []
    
    interestingMachines = []
    
    configParameters = configFileManager.getParametersFromConfigurationFile( "statsConfig" )
            
    
    for coupledMachineName in configParameters.coupledLogMachineNames :  
                
        machines = coupledMachineName.split(",")        
        newRxNames, newTxNames  = getRxTxNamesHavingRunDuringPeriod( start, end, machines ) 

        rxNames.extend( newRxNames )
        txNames.extend( newTxNames )

    rxNames.sort()
    txNames.sort()
        
    return rxNames, txNames        
    
    
    
    
    