#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.
"""
#############################################################################################
#
# Name  : retreiveDataFromMachine.py
#
# Author: Nicholas Lemay
#
# Date  : 2007-02-19, last update on May 9th 2007
#
# Description: 
#
# Usage:   This program can be called from command-line.
#          
#          Call examples :                   
#              python pickleViewer.py px machineName 
#              
#                
#
#
##############################################################################################


import commands, os, sys, ConfigParser 
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsConfigParameters import StatsConfigParameters   
from pxStats.lib.MachineConfigParameters import MachineConfigParameters

LOCAL_MACHINE = os.uname()[1]


def transferLogFiles():
    """
        Log files will not be tansferred if local machine
        is not designed to be a pickling machine. 
        If log files are to be transferred, they will be straight
        from the source."
    """
    
    parameters = StatsConfigParameters()    
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
    parameters.getAllParameters()
    individualSourceMachines   = machineParameters.getMachinesAssociatedWithListOfTags( parameters.sourceMachinesTags )
    individualPicklingMachines = machineParameters.getMachinesAssociatedWithListOfTags( parameters.picklingMachines )
        
    for sourceMachine,picklingMachine in map( None, individualSourceMachines, individualPicklingMachines ) :      
               
        if picklingMachine == LOCAL_MACHINE :#pickling to be done here  
            userName = machineParameters.getUserNameForMachine(sourceMachine)
            print  "rsync -avzr --delete-before -e ssh %s@%s:/%s %s%s/ " %( userName , sourceMachine, StatsPaths.PXLOG, StatsPaths.PXLOG, sourceMachine  )
            status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:%s %s%s/ " %( userName , sourceMachine, StatsPaths.PXLOG, StatsPaths.PXLOG, sourceMachine  ) )
            print output
    
    
        
def transfer( login, machine ):
    """
        Transfers all the required files
        from specified machine into local 
        machine.
    
        Every task is done 5 times.
        
        This is done in hope that everything 
        downloaded will be as coherent as possible.
        
        Example: If a large amount of file is to 
        be transferred, some files that were downloaded
        at the beginning of the transfer,wich can take up to a few hours,
        might 
        
    """    
    
    paths = [ StatsPaths.STATSMONITORING , StatsPaths.STATSGRAPHS , StatsPaths.STATSPICKLES, StatsPaths.STATSCURRENTDB, StatsPaths.STATSDBBACKUPS , StatsPaths.STATSCURRENTDBUPDATES, StatsPaths.STATSDBUPDATESBACKUPS ]
    
    for path in paths:
        if not os.path.isdir( path ) :            
                print path
                os.makedirs( path )
            
    paths.append( StatsPaths.STATSMONITORING + 'maxSettings.conf' )
    paths.append( StatsPaths.STATSMONITORING + 'previousCrontab' )      
    paths.append( StatsPaths.STATSMONITORING + 'previousFileChecksums')
    
            
    for i in range(5):
                
        transferLogFiles()
        
        for path in paths :
            status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:%s %s"  %( login, machine, path, path ) )
            print output        
         
    
def main():
    """
        Parses parameters then calls 
        the tranferMethod.
    """
    
    login   = ""
    machine = ""
    
    if len( sys.argv ) == 3   :
        
        login   = sys.argv[1]
        machine = sys.argv[2]     
        transfer( login, machine )
    else:
        print "#######################################################################################################"
        print "#"
        print "#    Help for retreiveDataFromMachine.py"
        print "#"
        print "#    This program is to be used to transfer all the important stats files"
        print "#    from a remote machine into the local machine."
        print "#" 
        print "#    If large transfers are to be done, program may take many hours to complete."
        print "#    Output from every operation will be printed so that the user can see exactly what is going on"
        print "#    so that errors can be detected : example invalid login or ssh other ssh errors"
        print "#" 
        print "#    This will also serve as to take out the guesswork as to why the program is taking so long to complete it's execution."
        print "#"
        print "#    Log files will not be tansferred if local machine is not designed to be a pickling machine. "
        print "#    If log files are to be transferred, they will be straight from the source."
        print "#"
        print "#    ******Make sur /appx/px/stats/config is filled properly prio to running this script !!!*****"
        print "#"
        print "#    Program must receive exactly two arguments."
        print "#"
        print "#    Usage  : python retreiveDataFromMachine.py login machineName "   
        print "#"      
        print "#######################################################################################################"
        print ""
        print ""
        print ""
        sys.exit()
    
      
    
if __name__ == "__main__":
    main()    