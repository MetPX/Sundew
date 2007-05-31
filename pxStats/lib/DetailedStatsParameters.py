#!/usr/bin/env python2


'''
#############################################################################################
#
#
# Name: Plotter.py
#
# @author: Nicholas Lemay
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : Simple class used to manage parameters from the stats configuration file. 
# 
#############################################################################################
'''


class DetailedStatsParameters:
    
    
    def  __init__(self, sourceMachinesForTag = None , individualSourceMachines =None, sourceMachinesLogins = None, picklingMachines = None, picklingMachinesLogins =None, databaseMachines =None, uploadMachines=None, uploadMachinesLogins=None ):
        '''
        
        @param sourceMachinesForTag:
        @param individualSourceMachines:
        @param sourceMachinesLogins:
        @param picklingMachines:
        @param picklingMachinesLogins:
        @param databaseMachines:
        @param uploadMachines:
        @param uploadMachinesLogins:
        '''
        
        self.sourceMachinesForTag = sourceMachinesForTag or {}
        self.individualSourceMachines = individualSourceMachines or []
        self.sourceMachinesLogins = sourceMachinesLogins or {}
        self.picklingMachines = picklingMachines or {}
        self.picklingMachinesLogins = picklingMachinesLogins or {}
        self.databaseMachines = databaseMachines or []
        self.uploadMachines = uploadMachines or []
        self.uploadMachinesLogins = uploadMachinesLogins or {}
       
        
    def restoreDefaults(self):
        """
            @summary: restore default values for all values. 
                      Either an empty array or an empty dictionary. 
        """
        
        self.sourceMachinesForTag = {}
        self.individualSourceMachines = []
        self.sourceMachinesLogins = {}
        self.picklingMachines = {}
        self.picklingMachinesLogins = {}
        self.databaseMachines = []
        self.uploadMachines = []
        self.uploadMachinesLogins = {}