#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : crontabCommands.py 
##  
## Author : Nicholas Lemay  
##
## Date   : May 19th 2006
##
#############################################################################

import os
import commands
import PXPaths

PXPaths.normalPaths()
localMachine = os.uname()[1]

if localMachine == "pds3-dev" or localMachine == "pds4-dev" or localMachine == "lvs1-stage" :
    PATH_TO_LOGFILES = PXPaths.LOG + localMachine + "/"

elif localMachine == "logan1" or localMachine == "logan2":
    PATH_TO_LOGFILES = PXPaths.LOG + localMachine + "/" + localMachine + "/"

else:#pds5 pds5 pxatx etc
    PATH_TO_LOGFILES = PXPaths.LOG  


def main():
    """
    """
    
    
    print localMachine    
    status, output = commands.getstatusoutput( "rsync -avzr --delete-before  -e ssh pds@pxatx:/apps/px/log/ %s >>/dev/null 2>&1 " %PATH_TO_LOGFILES )
    print output
    status, output = commands.getstatusoutput( "python /apps/px/lib/stats/pickleUpdater.py -f rx  >>/dev/null 2>&1" )
    print output
    status, output = commands.getstatusoutput( "python /apps/px/lib/stats/pickleUpdater.py -f tx >>/dev/null 2>&1" )
    print output
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -i -m 'pxatx' -l 'pds' >>/dev/null 2>&1 " )
    print output
    status, output = commands.getstatusoutput( "ssh pds@pds3-dev 'rsync -avzr --delete-before -e ssh pds@pds5:/apps/px/log/ /apps/px/log/pds3-dev/' >>/dev/null 2>&1" )
    print output
    status, output = commands.getstatusoutput( "ssh pds@pds3-dev 'python /apps/px/lib/stats/pickleUpdater.py  -f rx'  >>/dev/null 2>&1 " )
    print output
    status, output = commands.getstatusoutput( "ssh pds@pds3-dev 'python /apps/px/lib/stats/pickleUpdater.py -f tx' >>/dev/null 2>&1 " )
    print output
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/pickleSynchroniser.py -l pds -m 'pds3-dev' >>/dev/null 2>&1 " )
    print output
    status, output = commands.getstatusoutput( "ssh pds@pds4-dev 'rsync -avzr --delete-before -e ssh pds@pds6:/apps/px/log/ /apps/px/log/pds4-dev/' >>/dev/null 2>&1" )
    print output
    status, output = commands.getstatusoutput( "ssh pds@pds4-dev 'python /apps/px/lib/stats/pickleUpdater.py -f rx' >>/dev/null 2>&1" )
    print output
    status, output = commands.getstatusoutput( "ssh pds@pds4-dev 'python /apps/px/lib/stats/pickleUpdater.py -f tx' >>/dev/null 2>&1" )
    print output
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/pickleSynchroniser.py -l pds -m 'pds4-dev' >>/dev/null 2>&1" )
    print output
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateAllGraphsForServer.py -m 'pds5,pds6' -c  -l 'pds,pds' >>/dev/null 2>&1  " )
    print output
    #status, output = commands.getstatusoutput( "/apps/px/lib/stats/transferPickleToRRD.py >>/dev/null 2>&1" )
    #print output
    status, output = commands.getstatusoutput( "scp /apps/px/stats/graphs/symlinks/* lvs2-op:/apps/pds/tools/Columbo/ColumboShow/graphs/ >>/dev/null 2>&1" )
    print output
    status, output = commands.getstatusoutput( "scp /apps/px/stats/graphs/symlinks/* lvs1-op:/apps/pds/tools/Columbo/ColumboShow/graphs/ >>/dev/null 2>&1" )
    print output
    print "made it to the end!"
    
if __name__ == "__main__":
    main()
