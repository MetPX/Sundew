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
# Description : Simple class used to manage parameters from the machineConfigurationFile. 
# 
#############################################################################################
'''
import os, sys 
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsPaths import StatsPaths


class MachineConfigParameters:
    '''
        @summary: Contains all the different parameters 
                  found in the configForMachines file
                  of the stats library.         
    '''  
    

    def __init__( self, machinesForMachineTags = None, machines= None, userNames = None ):
        '''
        
        @summary: Constructor. 
        
        @note: You can use the small utility methods given by this class
               isntead of setting up the data structures yourself.
        
        @param machineForMachineTags: Dictionary of machineTags/machine associations found
                            in the configuration file.
                                                           
        @param machines:  List of machines found within the config file.
        
        @param userNames: Dictionary associating proper user name to machines
                          found in machines array.
        
        @raise exception: Will raise an exception if list of machine names in 
                          dictionary do not match those in array.                    
        
        '''
                
        
        if machines != None:
            
            self.machinesForMachineTags = machinesForMachineTags
            self.machines = machines  
            self.userNames = usersNames
                        
            for userName in userNames.keys():
                if userName not in self.machines:
                    raise Exception( "_MachineConfigParameters init error. Machines in self.machine do not match those in userNames." )
        
        else:
            self.machinesForMachineTags = {}   
            self.machines = []
            self.userNames = {}  
    
        
    def getMachinesAssociatedWith(self, machineTag ):    
        '''
        
        @param machineTag: machine tag for wich you want to know the machines.
        
        @return: The machine(s) associated with the tag in list format. 
        
        '''
        
        return self.machinesForMachineTags[machineTag]
    
    
    def getMachinesAssociatedWithListOfTags(self,tags):
        """
        
        @param tags: List of machine tags for wich you want to know the machines.
        
        @return: The machine(s) associated with the tag in list format. 
        
        """
        
        machines = []
        for tag in tags :
            machines.extend( self.machinesForMachineTags[tag] )
         
        return machines    
    
    
    def getListOfPairsAssociatedWithListOfTags(self,tags):
        """
        
        @param tags: List of machine tags for wich you want to know the machines.
        
        @return: The machine(s) associated with the tag in list format. 
        
        """
        
        machines = []
        for tag in tags :
                                         
            machines.append( self.machinesForMachineTags[tag] )
         
        return machines 
    
    
    def getPairedMachinesAssociatedWithListOfTags(self,tags):
        """
        
        @param tags: List of machine tags for wich you want to know the machines.
        
        @return: The machine(s) associated with the tag in list format. 
        
        """
        
        machines = []
        for tag in tags :
            pair = ""
            for machine in self.machinesForMachineTags[tag]:
                pair = pair + machine
                
            machines.append( pair )
         
        return machines   
    
    
    
    def getMachineTags(self):
        '''
        
        @return:  Returns the list of machine tags. 
        
        '''
        
        return self.machinesForMachineTags.keys()
    
        
    
    def addMachineToMachineTag( self, machine, machineTag ):
        '''
        
        @param machine: Machine you want to add to a certain machineTag.
        @param machineTag: Machine tag with whom to make the association.
        
        '''
        
        
        if  machine not in self.machines :            
            self.addMachineToMachineList(machine)
        if machineTag not in self.machinesForMachineTags.keys():
            self.addMachineTagToTagList(machineTag)
                
        self.machinesForMachineTags[machineTag].append( machine )
    
    
    
    def setUserNameForMachine( self, machine, userName ):
        '''
        
        @param machine: Machine for wich to set the userName
        @param userName: User name to set for the machine.
        
        '''           
        
        self.userNames[machine] =  userName       
    
    
    def getUserNameForMachine(self, machine):
        '''
        
        @param machine: Machine for wich you want to know 
                        the userName.
                        
        @return: The user name of the specified machine.
        
        '''
        
        userName = ""
        
        if machine in self.userNames.keys(): 
            userName = self.userNames[machine]
        
        return userName
        
        
        
    def addMachineToMachineList(self, machine):
        '''
        
        @param machine: Machine to add to the list.
        
        '''
        
        if not machine in self.machines:
            self.machines.append( machine )
            
            
    
    def addMachineTagToTagList( self, machineTag ):            
        """
        
        @param machineTag:
        """
        
        if machineTag not in self.machinesForMachineTags.keys():
            self.machinesForMachineTags[machineTag] = []
    
        
    def getParametersFromMachineConfigurationFile(self):     
        '''
        
        @summary: Gathers all the information found within 
                  the configForMachines configuration file.
                  
        @return: Returns an _MachineConfigParameters instance 
                 containing all the found parameters.            
        
        '''
                  
        CONFIG = StatsPaths.STATSETC + "configForMachines"     
        
        if os.path.isfile( CONFIG ):
            
            fileHandle =  open( CONFIG )    
            lines = fileHandle.readlines() 
            
            for line in lines:
                if line != '' and  line[0] != '#' and line[0] != '\n' :
                    
                    splitLine = line.split()                    
                    machineTag = splitLine[0]
                    machines = splitLine[1].split(",")
                    userNames = splitLine[2].split(",")
                   
                    if ( len(machines) ==  len(userNames) ):
                        for i in range( len( machines ) ):                    
                            self.addMachineTagToTagList( machineTag)    
                            self.addMachineToMachineList( machines[i] )
                            self.addMachineToMachineTag(machines[i], machineTag)
                            self.setUserNameForMachine(machines[i], userNames[i])
            
            fileHandle.seek(0)
            fileHandle.close()          
            
            
            
            
            
            
            
            
            
            
            