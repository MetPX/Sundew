#!/usr/bin/env python2


'''
#############################################################################################
#
#
# Name: GroupConfigParameters
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


class GroupConfigParameters:
    
    
    def  __init__(self, groups = [], groupsMachines = {}, groupFileTypes = {}, groupsMembers  = {}, groupsProducts = {}  ):
        """
        
        @param groups:   Groups names
        @param groupsMachines: groupName -> [machines] associations
        @param groupsMembers: groupName -> [members] associations
        @param groupsProducts: groupName -> [products] associations
        """
        self.groups = groups
        self.groupsMachines = groupsMachines
        self.groupFileTypes = groupFileTypes
        self.groupsMembers  = groupsMembers
        self.groupsProducts = groupsProducts
        
        
        
    def restoreDefaults(self):
        """
            @summary: empties out the arrays and the dictionaries 
        """
        self.groups = []
        self.groupFileTypes = {}
        self.groupsMachines = {}
        self.groupsMembers = {}
        self.groupsProducts = {}
    
    
    
    def getAssociatedParametersInStringFormat(self, group ):
        """        
        
            @param group: Group for wich you want to know 
                          the different infos.
        
            @return: groupsMachines, groupsFileTypes, groupsMembers
                     and groupsProducts values associated with 
                     the specified group. All values will be formated in a string
                     format. 
    
        """
           
        groupMembers   = str(self.groupsMembers[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        groupMachines  = str(self.groupsMachines[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )                 
        groupProducts  = str(self.groupsProducts[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        groupFileTypes = str(self.groupFileTypes[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )

        return groupMembers, groupMachines, groupProducts, groupFileTypes
