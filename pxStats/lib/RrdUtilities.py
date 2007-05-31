#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : rrdUtilities.py
#
# Author: Nicholas Lemay
#
# Date  : 2007-05-08
#
# Description: This file containsmethods that are usefull to all programs that deal with 
#              round robin databases. They have been gathered here as to limit repetition
#              and hopefully make program maintenance easier.
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
    PxManager requires pxlib 
"""
from   PXManager    import *        
from   pxStats.lib.StatsPaths   import StatsPaths
          

LOCAL_MACHINE = os.uname()[1]  

class RrdUtilities:          
    
    def buildRRDFileName( dataType = 'errors', clients = ['client1','client1'] , machines = ['machine1','machine2'], groupName = "", fileType = "", usage = "regular"  ):
        """
        
            @param dataType: byteocunt, errors, filecount, filesOverMaxLatency and latency.
            
            @param clients: list of clients/sources names. If only one is wanted, include it in a list.
            
            @param machines: list of machines associated with client/sources names. If only one is wanted, include it in a list.
            
            @param fileType : Useless for regular and group databases. Obligatory for totalForMachine databases. 
            
            @param groupName: optional. Use only if the list of client/sources has a KNOWN group name.
            
            @param usage: regular, group or totalForMachine.
        
            @return: Returns the name of the round robin database bases on the parameters.
        
        """
        
        
        fileName = ""
        
        combinedMachineName = ""   
        for machine in machines:
            combinedMachineName = combinedMachineName + machine
          
        combinedClientsName = ""  
        for client in clients:
            combinedClientsName = combinedClientsName + client
               
        if usage == "regular":
            fileName = StatsPaths.STATSCURRENTDB + "%s/%s_%s" %( dataType, combinedClientsName, combinedMachineName )  
        elif usage == "group":
             fileName = StatsPaths.STATSCURRENTDB + "%s/%s_%s" %( dataType, groupName, combinedMachineName )    
        elif usage == "totalForMachine":
             fileName = StatsPaths.STATSCURRENTDB + "%s/%s_%s" %( dataType, fileType, combinedMachineName )            
        
        return  fileName 
    
    
    buildRRDFileName = staticmethod( buildRRDFileName )
    
    
    
    def setDatabaseTimeOfUpdate(  databaseName, fileType, timeOfUpdate ):
        """
            This method set the time of the last update made on the database.
            
            Usefull for testing. Round Robin Databae cannot be updates with 
            dates prior to the date of the last update.
            
        """      
         
        folder   = StatsPaths.STATSCURRENTDBUPDATES + "%s/" %fileType
        fileName = folder +  os.path.basename(databaseName)   
        if not os.path.isdir( folder ):
            os.makedirs( folder )
        fileHandle  = open( fileName, "w" )
        pickle.dump( timeOfUpdate, fileHandle )
        fileHandle.close()
    
    setDatabaseTimeOfUpdate = staticmethod( setDatabaseTimeOfUpdate )
    
    
    
    def getDatabaseTimeOfUpdate( databaseName, fileType ):
        """
            If present in DATABASE-UPDATES file, returns the time of the last 
            update associated with the databse name.      
            
            Otherwise returns 0 
            
        """ 
        
        lastUpdate = 0
        folder   = StatsPaths.STATSCURRENTDBUPDATES + "%s/" %(fileType )    
        fileName = folder + os.path.basename( databaseName )
        #print fileName
        if os.path.isfile( fileName ):
            
            fileHandle  = open( fileName, "r" )
            lastUpdate  = pickle.load( fileHandle )           
            fileHandle.close()     
            
                
        return lastUpdate 
    
    getDatabaseTimeOfUpdate = staticmethod( getDatabaseTimeOfUpdate )
    
    