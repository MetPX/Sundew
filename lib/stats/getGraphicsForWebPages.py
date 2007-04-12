#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##########################################################################
##
## Name   : getGraphicsForWebPages.py 
## 
## Description : Gathers all the .png graphics required by the following 
##               web pages: dailyGraphs.html, weeklyGraphs.html, 
##               monthlyGraphs.html, yearlyGraphs.html
##
## Note        : Graphics are gathered for all the rx/tx sources/clients 
##               present in the pds5,pds6 and pxatx mahcines. This has been 
##               hardcoded here since it is also hardocded within the web 
##               pages.  
##                 
## Author : Nicholas Lemay  
##
## Date   : November 22nd 2006
##
#############################################################################

import os, sys, time, shutil, glob, commands, configFileManager
import PXPaths, MyDateLib

from MyDateLib import *
from configFileManager import *

PXPaths.normalPaths()


def updateThisYearsGraphs( currentTime, machineNames ):
    """
        This method generates new yearly graphs
        for all the rx and tx names.       
       
    """   
    
    currentTime = MyDateLib.getIsoFromEpoch(currentTime)    
    
    for machineName in machineNames:
        
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( machineName, currentTime ) )
        print output
        #total graphics 
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -y --havingRun --fixedCurrent --date "%s"'  %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -y  --havingRun --fixedCurrent --date "%s"'  %( machineName, currentTime ) )
        print output
           
        
    
def setLastYearsGraphs( currentTime, machineNames ):
    """
        This method generates all the yearly graphs
        of the previous year.        
    """
    
    currentTime = MyDateLib.getIsoFromEpoch(currentTime)
    
    for machineName in machineNames:
        
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f rx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( machineName, currentTime ) )
        print output        
        #total graphics 
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -y --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -y --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output    
         
      
def updateThisMonthsGraphs( currentTime, machineNames ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
        
    """

    currentTime = MyDateLib.getIsoFromEpoch( currentTime )

    for machineName in machineNames:
    
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( machineName, currentTime ) )
        print output    
        #total graphics 
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -m --fixedCurrent --date "%s"' %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -m --fixedCurrent --date "%s"' %( machineName, currentTime ) )
        print output 
    
    
def setLastMonthsGraphs( currentTime, machineNames ):
    """
        This method generates all the monthly graphs
        for the previous month.
        
    """
    
    currentTime = MyDateLib.getIsoFromEpoch(currentTime)
    
    for machineName in machineNames:
        
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f rx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( machineName, currentTime ) )
        print output
        #total graphics 
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -m --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -m --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
       
    
    
       
def setLastWeeksGraphs( currentTime, machineNames ):
    """
        Generates all the graphics of the previous week.
                
    """
    
    currentTime = MyDateLib.getIsoFromEpoch( currentTime )
    
    for machineName in machineNames:
    
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f rx --machines '%s'  --havingRun --date '%s' --fixedPrevious" %( machineName, currentTime ) )
        print output    
        #total graphics 
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -w --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -w --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
    
        
def updateThisWeeksGraphs( currentTime, machineNames ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
            
    """

    currentTime = MyDateLib.getIsoFromEpoch(currentTime)
    
    for machineName in machineNames:
        #individual graphics 
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent " %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent " %( machineName, currentTime ) )    
        print output
        #total graphics 
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -w --fixedCurrent --date "%s"' %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -w --fixedCurrent --date "%s"' %( machineName, currentTime ) )
        print output
    
    
    
def setYesterdaysGraphs( currentTime, machineNames ):
    """
        Takes all of the current individual daily graphs 
        and sets them as yesterdays graph. 
        
        To be used only at midnight where the current columbo graphics 
        are yesterdays graphics.

        Graphics MUST have been updated PRIOR to calling this method!
    
        Combined graphics are generated here.
        
    """
    
    filePattern = PXPaths.GRAPHS + "webGraphics/columbo/*.png"
    yesterday   = time.strftime( "%a", time.gmtime( currentTime  - (24*60*60) ))
    
    currentGraphs = glob.glob( filePattern )  
    
    
    for graph in currentGraphs:
        clientName = os.path.basename(graph).replace( ".png","" )
        dest =  PXPaths.GRAPHS + "webGraphics/daily/%s/%s.png" %( clientName, yesterday )
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname(dest) )
        shutil.copyfile( graph, dest )    
        #print "copy %s to %s" %( graph, dest )
    
        
    currentTime = MyDateLib.getIsoFromEpoch(currentTime) 
    
    for machineName in machineNames:   
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -d --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -d --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
  
        
        
        
def setCurrentColumboGraphsAsDailyGraphs( currentTime )  :
    """
        This method takes the latest dailygraphics 
        and then copies that file in the appropriate
        folder as to make it accessible via the web
        pages.  
        
        Precondition : Current graphs must have 
        been generated properly prior to calling this 
        method.
          
    """

    filePattern = PXPaths.GRAPHS + "webGraphics/columbo/*.png"
    currentDay = time.strftime( "%a", time.gmtime( currentTime ) )
    
    currentGraphs = glob.glob( filePattern )
    
    #print "filePattern : %s" %filePattern
    
    for graph in currentGraphs:
        clientName = os.path.basename(graph).replace( ".png","" )
        dest =  PXPaths.GRAPHS + "webGraphics/daily/%s/%s.png" %( clientName,currentDay )
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname( dest ) )
        shutil.copyfile( graph, dest )
        #print "copy %s to %s" %( graph, dest)

        
        
def setDailyGraphs( currentTime, machineNames ):
    """
        Sets all the required daily graphs.
    """          
        
    setCurrentColumboGraphsAsDailyGraphs( currentTime )
    
    currentTime = MyDateLib.getIsoFromEpoch(currentTime)     
              
    for machineName in machineNames:
        
        #Generate all the daily total graphs. 
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -d --fixedCurrent --date "%s"' %( machineName, currentTime) )
        print output
        
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -d --fixedCurrent --date "%s"' %( machineName,currentTime ) )
        print output
    
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -d --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
        
        status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -d --fixedPrevious --date "%s"' %( machineName, currentTime ) )
        print output
        

    
    
def main():
    """
        Set up all the graphics required by 
        the web pages.
        
        ***Note : we suppose here that the web pages
        will require graphics from all the machines
        specified in the configuration file.
                         
    """
    
    configParameters = configFileManager.getParametersFromConfigurationFile( "statsConfig" )
    
    machineNames     = configParameters.coupledLogMachineNames
    
    currentTime = time.time()
     
    setDailyGraphs( currentTime, machineNames )    

    if int(time.strftime( "%H", time.gmtime( currentTime ) ) ) == 0:#midnight
        
        setYesterdaysGraphs( currentTime, machineNames )#Day has changed,lets keep yesterday's graph.
        
        if  time.strftime( "%a", time.gmtime( currentTime, machineNames ) ) == 'Mon':#first day of week
            setLastWeeksGraphs( currentTime, machineNames )
            updateThisMonthsGraphs( currentTime, machineNames )
            updateThisWeeksGraphs( currentTime, machineNames )
        else:#update daily.
            updateThisWeeksGraphs( currentTime, machineNames )
            
        if int(time.strftime( "%d", time.gmtime( currentTime ) )) == 1:#first day of month
            setLastMonthsGraphs( currentTime, machineNames )# month is over let's wrap it up.
            updateThisYearsGraphs( currentTime, machineNames )#add past month to years graph.
            
            if time.strftime( "%a", time.gmtime( currentTime ) ) != 'Mon':#first day of week
                updateThisMonthsGraphs( currentTime, machineNames )         
        
        if int(time.strftime( "%j", time.gmtime( currentTime ) )) == 1:#first day of year
            setLastYearsGraphs( currentTime, machineNames )        
    
    else:        
        updateThisWeeksGraphs( currentTime, machineNames )

    
if __name__ == "__main__" :
    main()
