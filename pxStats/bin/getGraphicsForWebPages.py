#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##########################################################################
##
## Name   : getGraphicsForWebPages.py 
## 
## Description : Gathers all the .png graphics required by the following 
##               web pages: dailyGraphs.html, weeklyGraphs.html, 
##               monthlyGraphs.html, yearlyGraphs.html
##
##                 
## Author : Nicholas Lemay  
##
## Date   : November 22nd 2006, last updated on May 9th 2007
##
#############################################################################
"""
import os, sys, time, shutil, glob, commands
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters




def updateThisYearsGraphs( currentTime, machinePairs, groupParameters ):
    """
        This method generates new yearly graphs
        for all the rx and tx names.       
       
    """   
    
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)    
    
    for machinePair in machinePairs:
        
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( StatsPaths.STATSLIBRARY, machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( StatsPaths.STATSLIBRARY, machineName, currentTime ) )
        print output
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -y --havingRun --fixedCurrent --date "%s"'  %( StatsPaths.STATSLIBRARY, machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -y  --havingRun --fixedCurrent --date "%s"'  %( StatsPaths.STATSLIBRARY, machineName, currentTime ) )
        print output
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f %s --machines '%s'  -c %s --date '%s' --fixedCurrent " %( StatsPaths.STATSLIBRARY, groupFileTypes, groupMachines, group, currentTime ) )        
        
    
    
def setLastYearsGraphs( currentTime, machinePairs, groupParameters ):
    """
        This method generates all the yearly graphs
        of the previous year.        
    """
    
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    
    for machinePairs in machinePairs:
        
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSLIBRARY, machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f rx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSLIBRARY, machineName, currentTime ) )
        print output        
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -y --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machineName, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -y --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machineName, currentTime ) )
        print output    
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f %s --machines '%s'  -c %s --date '%s' --fixedPrevious " %( StatsPaths.STATSLIBRARY, groupFileTypes, groupMachines, group, currentTime ) )
        
      
      
def updateThisMonthsGraphs( currentTime, machinePairs, groupParameters ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
        
    """

    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )

    for machinePair in machinePairs:
    
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output    
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -m --fixedCurrent --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -m --fixedCurrent --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output 
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f %s --machines '%s'  -c %s --date '%s' --fixedCurrent " %( groupFileTypes, groupMachines, group, currentTime ) )
    
    
    
def setLastMonthsGraphs( currentTime, machinePairs, groupParameters ):
    """
        This method generates all the monthly graphs
        for the previous month.
        
    """
    
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    
    for machinePair in machinePairs:
        
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f rx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -m --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -m --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f %s --machines '%s'  -c %s --date '%s' --fixedPrevious " %( StatsPaths.STATSLIBRARY, groupFileTypes, groupMachines, group, currentTime ) )
        
    
    
       
def setLastWeeksGraphs( currentTime, machinePairs, groupParameters ):
    """
        Generates all the graphics of the previous week.
                
    """
    
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    
    for machinePair in machinePairs:
    
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f rx --machines '%s'  --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output    
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -w --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -w --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f %s --machines '%s'  -c %s --date '%s' --fixedPrevious " %( StatsPaths.STATSLIBRARY, groupFileTypes, groupMachines, group, currentTime ) )
    
    
        
def updateThisWeeksGraphs( currentTime, machinePairs, groupParameters ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
            
    """

    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    
    for machinePair in machinePairs:
        #individual graphics 
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent " %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent " %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )    
        print output
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -w --fixedCurrent --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -w --fixedCurrent --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f %s --machines '%s'  -c %s --date '%s' --fixedCurrent " %( StatsPaths.STATSLIBRARY, groupFileTypes, groupMachines, group, currentTime ) )
    
    
    
def setYesterdaysGraphs( currentTime, machinePairs ):
    """
        Takes all of the current individual daily graphs 
        and sets them as yesterdays graph. 
        
        To be used only at midnight where the current columbo graphics 
        are yesterdays graphics.

        Graphics MUST have been updated PRIOR to calling this method!
    
        Combined graphics are generated here.
        
    """
    
    yesterday   = time.strftime( "%a", time.gmtime( currentTime  - (24*60*60) ))
    
    filePattern = StatsPaths.STATSGRAPHS + "webGraphics/columbo/*.png"
    currentGraphs = glob.glob( filePattern )  
    
    filePattern = StatsPaths.STATSGRAPHS + "webGraphics/groups/*.png"
    currentGraphs.extend( glob.glob( filePattern ) ) 
   
    for graph in currentGraphs:
        clientName = os.path.basename(graph).replace( ".png","" )
        dest = StatsPaths.STATSGRAPHS + "webGraphics/daily/%s/%s.png" %( clientName, yesterday )
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname(dest) )
        shutil.copyfile( graph, dest )    
        print "copy %s to %s" %( graph, dest )          
     
    #Totals 
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    for machinePair in machinePairs:   
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -d --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -d --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
  
        
        
        
def setCurrentColumboAndGroupGraphsAsDailyGraphs( currentTime )  :
    """
        This method takes the latest dailygraphics 
        and then copies that file in the appropriate
        folder as to make it accessible via the web
        pages.  
        
        Precondition : Current graphs must have 
        been generated properly prior to calling this 
        method.
          
    """

    filePattern = StatsPaths.STATSGRAPHS + "webGraphics/columbo/*.png"
    currentDay = time.strftime( "%a", time.gmtime( currentTime ) )
    
    currentGraphs = glob.glob( filePattern )
    
    filePattern = StatsPaths.STATSGRAPHS + "webGraphics/groups/*.png"
    currentGraphs.extend( glob.glob( filePattern ) ) 
    #print "filePattern : %s" %filePattern
    
    for graph in currentGraphs:
        clientName = os.path.basename(graph).replace( ".png","" )
        dest =  StatsPaths.STATSGRAPHS + "webGraphics/daily/%s/%s.png" %( clientName,currentDay )
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname( dest ) )
        shutil.copyfile( graph, dest )
        #print "copy %s to %s" %( graph, dest)

        
        
def updateDailyGroupsGraphics( currentTime, groupParameters ):
    """
    
        @param currentTime: currentime in ISO format
        
        @param groupParameters: MachineConfigParameters instance containing the group 
                                parameters found in the config file.
    
    """ 
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        print '%sgenerateGraphics.py -c %s --combineClients --copy -d %s  -m %s -f %s -p %s  ' %( StatsPaths.STATSLIBRARY, groupMembers, currentTime, groupMachines, groupFileTypes, groupProducts )
        status, output = commands.getstatusoutput( '%sgenerateGraphics.py -c %s --groupName %s --combineClients --copy -d "%s"   -m %s -f %s -p %s  -s 24' %( StatsPaths.STATSLIBRARY, groupMembers, group, currentTime, groupMachines, groupFileTypes, "All" ) )
        print output 
        
            
            
def generateColumboGraphics( parameters, machineParameters ):
    """
        Generates all the graphics required by columbo. 
        
        Will generate combined graphics for couples,
        and single for singles.
        
    """
    
    start = 0 
    end   = 0
            
    for machineTag in parameters.sourceMachinesTags:
        
        logins = []
        
        machines = parameters.detailedParameters.sourceMachinesForTag[machineTag]
       
        for machine in machines:
            logins.append( machineParameters.getUserNameForMachine( machine ) )

        print "logins : %s" %logins    
        logins   = str(logins).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        machines = str(machines).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        
        
        if "," in machines :
            print "%sgenerateAllGraphsForServer.py -m '%s' -c  -l '%s'  " %( StatsPaths.STATSLIBRARY, machines.replace( "'","" ),logins.replace( "'","" ))
            status, output = commands.getstatusoutput( "%sgenerateAllGraphsForServer.py -m '%s' -c  -l '%s'  " %( StatsPaths.STATSLIBRARY, machines.replace( "'","" ),logins.replace( "'","" )) )
            print output
        else:
            status, output = commands.getstatusoutput( "%sgenerateAllGraphsForServer.py -i -m '%s' -l '%s'  " %( StatsPaths.STATSLIBRARY, machines.replace( "'","" ),logins.replace( "'","" ) ) )    
            print "%sgenerateAllGraphsForServer.py -i -m '%s' -l '%s'  " %( StatsPaths.STATSLIBRARY, machines.replace( "'","" ),logins.replace( "'","" ) )
            print output


        
def setDailyGraphs( currentTime, machinePairs, machineParameters, configParameters ):
    """
        Sets all the required daily graphs.
    """          
    
    currentTimeSSE = currentTime
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)     
    
    generateColumboGraphics( configParameters, machineParameters )              
    updateDailyGroupsGraphics( currentTime, configParameters.groupParameters )  
    
    setCurrentColumboAndGroupGraphsAsDailyGraphs( currentTimeSSE )
        
    for machinePair in machinePairs:
        
        #Generate all the daily total graphs. 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -d --fixedCurrent --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime) )
        print output
        
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -d --fixedCurrent --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair,currentTime ) )
        print output
    
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -d --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -d --fixedPrevious --date "%s"' %( StatsPaths.STATSLIBRARY, machinePair, currentTime ) )
        print output
        
       
        
def main():
    """
        Set up all the graphics required by 
        the web pages.
        
        ***Note : we suppose here that the web pages
        will require graphics from all the machines
        specified in the configuration file.
                         
    """
    
    configParameters = StatsConfigParameters( )
    configParameters.getAllParameters()       
    
    machineConfig = MachineConfigParameters()
    machineConfig.getParametersFromMachineConfigurationFile()
    machinePairs  = machineConfig.getPairedMachinesAssociatedWithListOfTags(configParameters.sourceMachinesTags)     
                
    currentTime = time.time()
     
    setDailyGraphs( currentTime, machinePairs, machineConfig, configParameters )
        
    if int(time.strftime( "%H", time.gmtime( currentTime ) ) ) == 0:#midnight

        setYesterdaysGraphs( currentTime, machinePairs )#Day has changed,lets keep yesterday's graph.
        
        if  time.strftime( "%a", time.gmtime( currentTime ) ) == 'Mon':#first day of week
            setLastWeeksGraphs( currentTime, machinePairs, configParameters.groupParameters )
            updateThisMonthsGraphs( currentTime, machinePairs, configParameters.groupParameters )
            updateThisWeeksGraphs( currentTime, machinePairs, configParameters.groupParameters )
        
        else:#update daily.
            updateThisWeeksGraphs( currentTime, machinePairs, configParameters.groupParameters )

        if int(time.strftime( "%d", time.gmtime( currentTime ) )) == 1:#first day of month
            setLastMonthsGraphs( currentTime, machinePairs, configParameters.groupParameters )# month is over let's wrap it up.
            updateThisYearsGraphs( currentTime, machinePairs, configParameters.groupParameters )#add past month to years graph.

            if time.strftime( "%a", time.gmtime( currentTime ) ) != 'Mon':#first day of week
                updateThisMonthsGraphs( currentTime, machinePairs, configParameters.groupParameters )

        if int(time.strftime( "%j", time.gmtime( currentTime ) )) == 1:#first day of year
            setLastYearsGraphs( currentTime, machinePairs, configParameters.groupParameters )

    else:
         updateThisWeeksGraphs( currentTime, machinePairs, configParameters.groupParameters )
        
  
    
      
if __name__ == "__main__" :
    main()
