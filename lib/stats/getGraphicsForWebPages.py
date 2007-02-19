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

import os, sys, time, shutil, glob,commands
import PXPaths, MyDateLib
from MyDateLib import *


PXPaths.normalPaths()


def updateThisYearsGraphs( currentTime ):
    """
        This method generates new yearly graphs
        for all the rx and tx names.       
       
    """
    
    end = MyDateLib.getIsoFromEpoch(currentTime)
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f tx --machines 'pds5,pds6' --date '%s' --fixedCurrent" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f rx --machines 'pds5,pds6' --date '%s' --fixedCurrent" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f tx --machines 'pxatx' --date '%s' --fixedCurrent" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f rx --machines 'pxatx' --date '%s' --fixedCurrent" %end )
    
    #total graphics 
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pds5,pds6" -y --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pds5,pds6" -y --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pxatx" -y --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pxatx" -y --fixedCurrent' )           
        
    
def setLastYearsGraphs( currentTime ):
    """
        This method generates all the yearly graphs
        of the previous year.        
    """
    
    end = MyDateLib.getIsoFromEpoch(currentTime)
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f tx --machines 'pds5,pds6' --date '%s' --fixedPrevious" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f rx --machines 'pds5,pds6' --date '%s' --fixedPrevious" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f tx --machines 'pxatx' --date '%s' --fixedPrevious " %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y --copy -f rx --machines 'pxatx' --date '%s' --fixedPrevious" %end )
        
    #total graphics 
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pds5,pds6" -y --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pds5,pds6" -y --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pxatx" -y --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pxatx" -y --fixedPrevious' )            
      
    
      
def updateThisMonthsGraphs( currentTime ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
        
    """

    end = MyDateLib.getIsoFromEpoch(currentTime)

    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f tx --machines 'pds5,pds6' --date '%s' --fixedCurrent" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f rx --machines 'pds5,pds6' --date'%s' --fixedCurrent" %end)
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f tx --machines 'pxatx' --date'%s' --fixedCurrent" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f rx --machines 'pxatx' --date '%s' --fixedCurrent" %end )
    
    #total graphics 
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pds5,pds6" -m --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pds5,pds6" -m --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pxatx" -m --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pxatx" -m --fixedCurrent' )           
    
    
def setLastMonthsGraphs( currentTime ):
    """
        This method generates all the monthly graphs
        for the previous month.
        
    """
    
    end = MyDateLib.getIsoFromEpoch(currentTime)

    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f tx --machines 'pds5,pds6' --date '%s' --fixedPrevious" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f rx --machines 'pds5,pds6' --date'%s' --fixedPrevious" %end)
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f tx --machines 'pxatx' --date'%s' --fixedPrevious" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m --copy -f rx --machines 'pxatx' --date '%s' --fixedPrevious" %end )

    #total graphics 
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pds5,pds6" -m --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pds5,pds6" -m --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pxatx" -m --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pxatx" -m --fixedPrevious' )        
    
    
       
def setLastWeeksGraphs( currentTime ):
    """
        Generates all the graphics of the previous week.
                
    """
    
    end = MyDateLib.getIsoFromEpoch( currentTime )

    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f tx --machines 'pds5,pds6' --date '%s' --fixedPrevious" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f rx --machines 'pds5,pds6' --date '%s' --fixedPrevious" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f tx --machines 'pxatx' --date '%s' --fixedPrevious" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f rx --machines 'pxatx' --date '%s' --fixedPrevious" %end )
    
    #total graphics 
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pds5,pds6" -w --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pds5,pds6" -w --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pxatx" -w --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pxatx" -w --fixedPrevious' )
    
        
def updateThisWeeksGraphs( currentTime ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
            
    """

    end = MyDateLib.getIsoFromEpoch(currentTime)
    
    #individual graphics 
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f tx --machines 'pds5,pds6' --date '%s' --fixedCurrent " %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f rx --machines 'pds5,pds6' --date '%s' --fixedCurrent " %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f tx --machines 'pxatx' --date '%s' --fixedCurrent " %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w --copy -f rx --machines 'pxatx' --date '%s' --fixedCurrent " %end )
    
    #total graphics 
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pds5,pds6" -w --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pds5,pds6" -w --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pxatx" -w --fixedCurrent' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pxatx" -w --fixedCurrent' )
    
    
    
def setYesterdaysGraphs( currentTime ):
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

    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pds5,pds6" -d --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pds5,pds6" -d --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "rx" --machines "pxatx" -d --fixedPrevious' )
    status, output = commands.getstatusoutput( '/apps/px/lib/stats/generateRRDGraphics.py --copy --totals -f "tx" --machines "pxatx" -d --fixedPrevious' )     
        
        
        
def setCurrentGraphsAsDailyGraphs( currentTime )  :
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
        
    
def main():
    """
        Set up all the graphics required by the web pages.
        
        Since web pages are hard coded the name of the machines
        from wich the graphics are gathered are also hardcoded.   
                
    """
    
    currentTime = time.time()
    
    setCurrentGraphsAsDailyGraphs( currentTime )    

    if int(time.strftime( "%H", time.gmtime( currentTime ) ) ) == 0:#midnight
        
        setYesterdaysGraphs( currentTime )#Day has changed,lets keep yesterday's graph.
        
        if  time.strftime( "%a", time.gmtime( currentTime ) ) == 'Mon':#first day of week
            setLastWeeksGraphs( currentTime )
            updateThisMonthsGraphs( currentTime )
            updateThisWeeksGraphs( currentTime )
        else:#update daily.
            updateThisWeeksGraphs( currentTime )
            
        if int(time.strftime( "%d", time.gmtime( currentTime ) )) == 1:#first day of month
            setLastMonthsGraphs( currentTime )# month is over let's wrap it up.
            updateThisYearsGraphs( currentTime )#add past month to years graph.
            
            if time.strftime( "%a", time.gmtime( currentTime ) ) != 'Mon':#first day of week
                updateThisMonthsGraphs( currentTime )         
        
        if int(time.strftime( "%j", time.gmtime( currentTime ) )) == 1:#first day of year
            setLastYearsGraphs( currentTime )        
    
    else:        
        updateThisWeeksGraphs( currentTime )
            
    
if __name__ == "__main__" :
    main()
