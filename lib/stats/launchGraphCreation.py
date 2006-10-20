#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : launchGraphCreation.py 
##  
## Author : Nicholas Lemay  
##
## Date   : October 20th 2006
##
## Goal   : Launchs the graphic creation mechanism for all specified machines.
##        
##          Machines must be specified in the /apps/px/stats/machine_list_for_graphic_production
##          file. 
##
##          
##   
#############################################################################

import os
import commands, PXPaths

PXPaths.normalPaths()


def getMachines():
    """
        Returns list of machine names found in  /apps/px/stats/machine_list_for_graphic_production
    """
    machines = []
    
    try:
        
        file = PXPaths.STATS + "machine_list_for_graphic_production"
        fileHandle = open( file, "r" )
        firstLine  = fileHandle.readline()
        machines   = firstLine.split( ";" ) 
        machines[ len(machines) -1 ]=  machines[ len(machines) -1 ].replace( "\n", "" )
    
    except: 
        pass
    
    return machines
    
    
def main():
    """
        Launchs the graphic creation mechanism for all specified machines.
    
        Machines must be specified in the /apps/px/stats/machine_list_for_graphic_production
        file. 

    """
    
    machines = getMachines()
    print machines
    
    
    for machine in machines:   
        
        innerMachines = machine.split( "," )
        for innerMachine in innerMachines :
        
            status, output = commands.getstatusoutput( "ssh pds@%s 'python /apps/px/lib/stats/pickleUpdater.py  -f rx'  >>/dev/null 2>&1 " %innerMachine )

            
            status, output = commands.getstatusoutput( "ssh pds@%s 'python /apps/px/lib/stats/pickleUpdater.py  -f tx'  >>/dev/null 2>&1 " %innerMachine )            
            
           
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/pickleSynchroniser.py -l pds -m '%s' >>/dev/null 2>&1 " %innerMachine )   

        if len (innerMachines ) > 1 :#combined graphs coming from numerous machines
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -m '%s' -c  -l 'pds,pds' >>/dev/null 2>&1  " %machine )

            
        else:
            status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -i -m '%s' -l 'pds' >>/dev/null 2>&1 " %machine )

            

    
if __name__ == "__main__":
    main()
