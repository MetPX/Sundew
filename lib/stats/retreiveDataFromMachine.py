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


import commands, os, sys, PXPaths 
import ConfigParser, configFileManager

from StatsConfigParameters import StatsConfigParameters   
from MachineConfigParameters import MachineConfigParameters

PXPaths.normalPaths()
LOCAL_MACHINE = os.uname()[1]



def transferLogFiles():
    """
        Log files will not be tansferred if local machine
        is not designed to be a pickling machine. 
        If log files are to be transferred, they will be straight
        from the source. Ex : pxatx, pds5, etc"
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
            status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/log/ /apps/px/log/%s/ " %( userName , sourceMachine, sourceMachine  ) )
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
    
    paths = [ "/apps/px/stats/statsMonitoring/" ,"/apps/px/stats/graphs/ ","/apps/px/stats/pickles/","/apps/px/stats/databases/","/apps/px/stats/databases_backups/","/apps/px/stats/DATABASE-UPDATES/","/apps/px/stats/DATABASE-UPDATES_BACKUPS/" ]
    
    for path in paths:
        if not os.path.isdir( path ) :            
                print path
                os.makedirs( path )
            
           
            
    for i in range(5):
                
        transferLogFiles()
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/statsMonitoring/maxSettings.conf /apps/px/stats/statsMonitoring/maxSettings.conf"  %( login, machine ) )
        print output
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/statsMonitoring/previousCrontab /apps/px/stats/statsMonitoring/previousCrontab"  %( login, machine ))
        print output
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/statsMonitoring/previousFileChecksums /apps/px/stats/statsMonitoring/previousFileChecksums"  %( login, machine ))
        print output
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/graphs/ /apps/px/stats/graphs/"  %( login, machine ) )
        print output
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/pickles/ /apps/px/stats/pickles/"  %( login, machine ) )
        print output
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/databases/ /apps/px/stats/databases/"  %( login, machine ) )
        print output
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/databases_backups/ /apps/px/stats/databases_backups/"  %( login, machine ) )
        print output
                
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/DATABASE-UPDATES/ /apps/px/stats/DATABASE-UPDATES/"  %( login, machine ) )
        print output
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/DATABASE-UPDATES_BACKUPS/ /apps/px/stats/DATABASE-UPDATES_BACKUPS/"  %( login, machine ) )
        print output        
        
        status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/stats/PICKLED-TIMES /apps/px/stats/PICKLED-TIMES "  %( login, machine ) )
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
        print "#    If log files are to be transferred, they will be straight from the source. Ex : pxatx, pds5, etc"
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