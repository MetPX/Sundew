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
        
        It then set a symbolic link to that file 
        in the appropriate folder as to be accessible
        via the web pages.
        
    """
    end = MyDateLib.getIsoFromEpoch(currentTime)
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y -l -f tx --machines 'pds5,pds6' -e '%s'" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y -l -f rx --machines 'pds5,pds6' -e '%s'" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y -l -f tx --machines 'pxatx' -e '%s'" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -y -l -f rx --machines 'pxatx' -e '%s'" %end )
    
    
    
def setLastYearsGraphs( currentTime ):
    """
        This method generates new yearly graphs
        for all the rx and tx names.
        
        It then set a symbolic link with last years 
        name in the appropriate folder and should
        never have to be modified again.
        
    """
    
    lastYear   = time.strftime( "%Y", time.gmtime( currentTime - ( 365*24*60*60 ) ) )
    thisYear   = time.strftime( "%Y", time.gmtime( currentTime ) )
    
    filePattern = PXPaths.GRAPHS + "symlinks/monthly/*/*/%s.png" %( thisYear )    
    
    yearlyGraphs = glob.glob( filePattern )
        
    for graph in yearlyGraphs:
        clientName = os.path.basename( os.path.dirname( graph ) )
        graphType  = os.path.basename(os.path.dirname( os.path.dirname( graph ) ) )        
        dest = PXPaths.GRAPHS + "symlinks/yearly/%s/%s/%s.png" %( graphType, clientName, lastYear )
        
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname(dest) )
        shutil.copyfile( graph, dest )   
        
        #print "copy %s to %s " %(graph, dest)
        
        
        
def updateThisMonthsGraphs( currentTime ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
        
        It then set a symbolic link to that file 
        in the appropriate folder as to be accessible
        via the web pages.
        
    """

    end = MyDateLib.getIsoFromEpoch(currentTime)

    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m -l -f tx --machines 'pds5,pds6' -e '%s'" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m -l -f rx --machines 'pds5,pds6' -e '%s'" %end)
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m -l -f tx --machines 'pxatx' -e '%s'" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -m -l -f rx --machines 'pxatx' -e '%s'" %end )
    
     
    
    
def setLastMonthsGraphs( currentTime ):
    """
        This method generates new monthly graphs
        for all the rx and tx names.
        
        It then set a symbolic link with last months 
        name in the appropriate folder and should
        never have to be modified again.
        
    """
    
    lastMonth   = time.strftime( "%b", time.gmtime( currentTime - ( 30*24*60*60 ) ) )
    thisMonth   = time.strftime( "%b", time.gmtime( currentTime ) )
    
    filePattern = PXPaths.GRAPHS + "symlinks/monthly/*/*/%s.png" %( thisMonth )    
    
    monthlyGraphs = glob.glob( filePattern )
        
    for graph in monthlyGraphs:
        clientName = os.path.basename( os.path.dirname( graph ) )
        graphType  = os.path.basename(os.path.dirname( os.path.dirname( graph ) ) )        
        dest = PXPaths.GRAPHS + "symlinks/monthly/%s/%s/%s.png" %( graphType, clientName, lastMonth )
        
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname(dest) )    
        shutil.copyfile( graph, dest )    
        #print "copy %s   to   %s " %( graph,dest )
    
    
       
def setLastWeeksGraphs( currentTime ):
    """
        This method generates new wekly graphs
        for all the rx and tx names.
        
        It then set a symbolic link with last years 
        name in the appropriate folder and should
        never have to be modified again.
        
    """
    
    lastWeeksNumber   = time.strftime( "%W", time.gmtime( currentTime - ( 7*24*60*60 ) ) )
    thisWeeksNumber   = time.strftime( "%W", time.gmtime( currentTime ))
    
    filePattern = PXPaths.GRAPHS + "symlinks/weekly/*/*/%s.png" %( thisWeeksNumber )    
    
    weeklyGraphs = glob.glob( filePattern )
       
    
    for graph in weeklyGraphs:
        clientName = os.path.basename( os.path.dirname( graph ) )
        graphType  = os.path.basename(os.path.dirname( os.path.dirname( graph ) ) )        
        
        dest = PXPaths.GRAPHS + "symlinks/weekly/%s/%s/%s.png" %( graphType, clientName, lastWeeksNumber )
        if not os.path.isdir( os.path.dirname( dest ) ):
            os.makedirs( os.path.dirname( dest ) )
        
        shutil.copyfile( graph, dest  )    
        #print "copy %s   to   %s " %( graph, dest )
    
    
        
def updateThisWeeksGraphs( currentTime ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
        
        It then set a symbolic link to that file 
        in the appropriate folder as to be accessible
        via the web pages.    
            
    """

    end = MyDateLib.getIsoFromEpoch(currentTime)

    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w -l -f tx --machines 'pds5,pds6' -e '%s'" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w -l -f rx --machines 'pds5,pds6' -e '%s'" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w -l -f tx --machines 'pxatx' -e '%s'" %end )
    
    status, output = commands.getstatusoutput( "/apps/px/lib/stats/generateRRDGraphics.py -w -l -f rx --machines 'pxatx' -e '%s'" %end )
    
    
def setYesterdaysGraphs( currentTime ):
    """
        This method generates new daily graphs 
        (if required)
        for all the rx and tx names.
        
        It then set a symbolic link with yesterdays 
        name in the appropriate folder and should
        never have to be modified again.    
    """
    
    filePattern = PXPaths.GRAPHS + "symlinks/*.png"
    yesterday   = time.strftime( "%a", time.gmtime( currentTime  - (24*60*60) ))
    
    currentGraphs = glob.glob( filePattern )  
    
    
    for graph in currentGraphs:
        clientName = os.path.basename(graph).replace( ".png","" )
        dest =  PXPaths.GRAPHS + "symlinks/daily/%s/%s.png" %( clientName, yesterday )
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname(dest) )
        shutil.copyfile( graph, dest )    
        #print "copy %s to %s" %( graph, dest )

        
        
def setCurrentGraphsAsDailyGraphs( currentTime )  :
    """
        This method takes the latest dailygraphics 
        and then sets a symbolic link to that file 
        in the appropriate folder as to be accessible
        via the web pages.  
        
        Precondition : Current graphs must have 
        been generated properly prior to caling this 
        method.
          
    """

    filePattern = PXPaths.GRAPHS + "symlinks/*.png"
    currentDay = time.strftime( "%a", time.gmtime( currentTime ) )
    
    currentGraphs = glob.glob( filePattern )
    
    #print "filePattern : %s" %filePattern
    
    for graph in currentGraphs:
        clientName = os.path.basename(graph).replace( ".png","" )
        dest =  PXPaths.GRAPHS + "symlinks/daily/%s/%s.png" %( clientName,currentDay )
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname( dest ) )
        shutil.copyfile( graph, dest )
        #print "copy %s to %s" %( graph, dest)
        
    
def main():
    """
    
    """
    currentTime = time.time()
    
    setCurrentGraphsAsDailyGraphs( currentTime )
    
    #print time.strftime( "%H", time.gmtime( currentTime ) ) 
    if int(time.strftime( "%H", time.gmtime( currentTime ) ) ) == 0:#midnight
        
        setYesterdaysGraphs( currentTime )
        
        if  time.strftime( "%a", time.gmtime( currentTime ) ) == 'Mon':#first day of week
            updateThisWeeksGraphs( currentTime )
            setLastWeeksGraphs( currentTime )
        else:
            updateThisWeeksGraphs( currentTime )
            
        if int(time.strftime( "%d", time.gmtime( currentTime ) )) == 1:#first day of month
            updateThisMonthsGraphs( currentTime)
            setLastMonthsGraphs( currentTime )        
        else:
            updateThisMonthsGraphs( currentTime )            
        
        if int(time.strftime( "%j", time.gmtime( currentTime ) )) == 1:#first day of year
            updateThisYearsGraphs( currentTime )
            setLastYearsGraphs( currentTime )
        else:
            updateThisYearsGraphs( currentTime )     
    
    else:
        udateThisWeeksGraphs( currentTime )
            
    
if __name__ == "__main__" :
    main()
