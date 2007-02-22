#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : configFileManager.py 
##  
## Author : Nicholas Lemay  
##
## Date   : February 19th 2007
##
##
## Description : 
##
##
#############################################################################

import os, sys, commands
import PXPaths, MyDateLib
from ConfigParser import ConfigParser
from MyDateLib import *
# 
PXPaths.normalPaths()
LOCAL_MACHINE = os.uname()[1]


class _StatsConfigParameters:
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
    
    
        
def getParametersFromStatsConfigurationFile():
    """
        Gather all the parameters from the /apps/px/.../config file.
        
        Returns all collected values in a  _StatsConfigParameters instance.
    
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
    
    parameters = _StatsConfigParameters( individualLogMachineNames, logMachinesLogins, coupledLogMachineNames, picklingMachines, picklingMachinesLogins, databaseMachines, uploadMachines, uploadMachinesLogins )

    
    return parameters
    
    
    
def getParametersFromMonitoringConfigurationFile():
    """
        Gather all the parameters from the /apps/px/.../config file.
        
        Returns all collected values in this order emails, machines,
        files, folders, maxUsages, errorsLogFile, maxSettingsFile.
    
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
    
    
         
def getParametersFromConfigurationFile( fileType = "statsConfig" ):
    """
        Gets the required parameters based on the specified
        configuration file type. 
    """
    
    parameters = None
    
    if fileType == "statsConfig":
        parameters = getParametersFromStatsConfigurationFile()
    
    elif fileType == "monitoringConfig":
        parameters = getParametersFromMonitoringConfigurationFile()
    
    return parameters