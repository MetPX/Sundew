#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : StatsMonitoringConfigParameters.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 09th 2007
##
##
## Description : 
##
##
#############################################################################

import os, sys, commands
import StatsPaths, MyDateLib
from ConfigParser import ConfigParser
from MachineConfigParameters import MachineConfigParameters
from MyDateLib import *
from FileStatsCollector import FileStatsCollector
# 

LOCAL_MACHINE = os.uname()[1]


         
         
class StatsMonitoringConfigParameters:
    '''
    
    @summary: This class is used to store all the parameters that are required 
              to run the stats monitoring properly.  
    
    '''
    
    def __init__(self, emails = None, machines = None , files = None, folders = None, maxUsages = None, errorsLogFile = None, maxSettingsFile = None):
        '''
        
        @param emails: Emails to whom the stats monitoring resultats will be sent
        @param machines: machines to monitor
        @param files: program files to monitor for version changes
        @param folders: folders to verify for disk usage
        @param maxUsages: max disk usage for each specified folders 
        @param errorsLogFile: path to px error log files.
        @param maxSettingsFile: path to max setting config fileassociated with the px error file.
        
        '''
        
        self.emails = emails
        self.machines = machines
        self.files = files
        self.folders = folders
        self.maxUsages = maxUsages
        self.errorsLogFile = errorsLogFile
        self.maxSettingsFile = maxSettingsFile
                 
                 
   
    def updateMachineNamesBasedOnExistingMachineTags(self):
        """
            @summary : browses the list of existing machine
                       tags to see if the specified name was 
                       a tag or not. 
        """
        
        machineParameters = MachineConfigParameters()
        machineParameters.getParametersFromMachineConfigurationFile()
        
        for i in range( len( self.machines ) ):
            if self.machines[i] in machineParameters.getMachineTags():                
                self.machines[i] = str( machineParameters.getMachinesAssociatedWith(self.machines[i])).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            
        
    
    
    def getParametersFromMonitoringConfigurationFile( self ):
        """
            Gather all the parameters from the StatsPaths.STATSROOT/config file.
            
            Returns all collected values in this order emails, machines,
            files, folders, maxUsages, errorsLogFile, maxSettingsFile.
        
        """   
    
        CONFIG = StatsPaths.STATSMONITORING +"statsMonitoring.conf" 
        config = ConfigParser()
        
        if os.path.isfile( CONFIG ):
        
            config.readfp( open( CONFIG ) ) 
            
            self.emails        = config.get( 'statsMonitoring', 'emails' ).split( ";" )
            self.machines      = config.get( 'statsMonitoring', 'machines' ).split( ";" )
            self.files         = config.get( 'statsMonitoring', 'files' ).split( ";" )
            self.folders       = config.get( 'statsMonitoring', 'folders' ).split( ";" )
            self.maxUsages     = config.get( 'statsMonitoring', 'maxUsages' ).split( ";" )
            self.errorsLogFile = config.get( 'statsMonitoring', 'errorsLogFile' )
            self.maxSettingsFile=config.get( 'statsMonitoring', 'maxSettingsFile' )
        
            self.updateMachineNamesBasedOnExistingMachineTags()
            
        else:
            print "%s configuration file not present. Please restore file prior to running" %CONFIG
            sys.exit()   
        
        parameters = _StatsMonitoringConfigParameters(emails, machines, files, folders, maxUsages, errorsLogFile, maxSettingsFile)    
            
        return parameters
        
        parameters =getParametersFromStatsConfigurationFile()
    
