#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
##############################################################################
##
##
## Name   : totalGraphicsWebPages.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 25-01-2007 
##
##
## Description : Generates the web pages that gives access to users
##               to the graphics based on the data totals of all the 
##               rx sources or tx clients combined. Daily, weekly, monthly,
##               and yearly graphics will be made available through these
##               pages.
##
##############################################################################
"""

"""
    Small function that adds pxlib to the environment path.  
"""
import os, time, sys, datetime, string
sys.path.insert(1, sys.path[0] + '/../../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    PXManager requires pxlib 
"""
from PXManager import *
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters

   
LOCAL_MACHINE = os.uname()[1]   


def getDays():
    """
        Returns the last 5 days numbers including the current year.
    
    """
    
    days = []
    
    startTime = (time.time() - (5*24*60*60))
    for i in range(1,6):
        days.append( time.strftime("%a",time.gmtime(startTime + ( i*24*60*60 ) )) )
   
       
    return days
    
    
        
def getWeekNumbers():
    """
        Returns the 5 week numbers including current week number.
    
    """
    
    weekNumbers = []
    
    startTime = (time.time() - (5*7*24*60*60))
    for i in range(1,6):
        weekNumbers.append( time.strftime("%W",time.gmtime(startTime + (i*7*24*60*60))) )
   
    return weekNumbers
    
    
    
def getMonths():
    """
        Returns the 3 months including current month.
    
    """
    currentTime = time.time()
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    currentDate = datetime.date( int(currentTime[0:4]), int(currentTime[5:7]), int(currentTime[8:10]) )     
       
    months = []
    
       
    for i in range(0,5):
        
        if currentDate.month -i < 1 :
            month = currentDate.month -i + 12
            year  = currentDate.year -i 
        else :     
            month = currentDate.month -i 
            year = currentDate.year
            
        if currentDate.day > 28:
            day = currentDate.day -5
        else: 
            day = currentDate.day          
        
        newdate = datetime.date( year,month,day )
        months.append( newdate.strftime("%b") )
        #print year,month,day
    
    months.reverse()
        
    return months
  
    
      
def getYears():
    """
        Returns the last 3 year numbers including the current year.
    
    """
    
    currentTime = time.time()
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    currentDate = datetime.date( int(currentTime[0:4]), int(currentTime[5:7]), int(currentTime[8:10]) )     
    
    years = []    
    
    #prevent errors from bisextile years
    if currentDate.month == 2 and currentDate.day == 29:
        currentDate.day = 28
    for i in range(0,3):
        year = currentDate.year - i
        newDate = datetime.date( year, currentDate.month, currentDate.day )
        years.append( newDate.strftime("%Y") )
        
    years.reverse()
       
    return years   

    
        
def getCombinedMachineName( machines ):
    """
        Gets all the specified machine names
        and combines them so they can be used
        to find pickles.

    """

    combinedMachineName = ""
    splitMachines = machines.split(",")

    for machine in splitMachines:

        combinedMachineName += machine

    return combinedMachineName


            
def generateWebPage( machineNames ):
    """
        Generates a web page based on all the 
        rxnames and tx names that have run during
        the pas x days. 
        
        Only links to available graphics will be 
        displayed.
        
    """  
    
    days   = getDays() 
    weeks  = getWeekNumbers()
    months = getMonths()
    years  = getYears()
    
    rxTypes      = [ "bytecount", "filecount", "errors"]
    txTypes      = [ "latency", "filesOverMaxLatency", "bytecount", "filecount", "errors"]
    timeTypes    = [ "daily","weekly","monthly","yearly"]
    updateFrequency= {"daily":"(upd. hourly)","weekly":"(upd. hourly)","monthly":"(upd. weekly)","yearly":"(upd. monthly)"}  
    
    for machineName in machineNames:
        if not os.path.isdir("StatsPaths.STATSWEBPAGES"):
            os.makedirs( "StatsPaths.STATSWEBPAGES" )
        machineName = getCombinedMachineName( machineName )
        file = "%s%s.html" %( StatsPaths.STATSWEBPAGES,machineName)
        fileHandle = open( file , 'w' )
        
        
        fileHandle.write( """ <html>         
            <head>
                <title> PX Graphics </title>
            </head>
            
            <script>
                counter =0;             
                function wopen(url, name, w, h){
                // This function was taken on www.boutell.com
                    
                    w += 32;
                    h += 96;
                    counter +=1; 
                    var win = window.open(url,
                    counter,
                    'width=' + w + ', height=' + h + ', ' +
                    'location=no, menubar=no, ' +
                    'status=no, toolbar=no, scrollbars=no, resizable=no');
                    win.resizeTo(w, h);
                    win.focus();
                }   
            </script>        
            
            <STYLE>

            </STYLE>
            
            <style type="text/css">
                div.left { float: left; }
                div.right {float: right; }
                <!--
                A{text-decoration:none}
                -->
                <!--
                td {
                    white-space: pre-wrap; /* css-3 */

                }
                // -->
            </style>    
            
            <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC" >
                        
                <h2>RX totals for %s.</h2>
            
    
            <table style="table-layout: fixed; width: 1250px; border-left: 0px gray solid; border-bottom: 0px gray solid; padding:0px; margin: 0px" cellspacing=10 cellpadding=6 >
            
            <tr>    
                <td bgcolor="#006699" ><font color = "white"><div class="left">Type</font></td>   
                
                <td bgcolor="#006699"  title = "Display the total of bytes received by all sources."><font color = "white"><div class="left">ByteCount</div><a target ="popup" href="help" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                
                <td bgcolor="#006699"  title = "Display the total of files received by all sources."><font color = "white"><div class="left">FileCount</div><a target ="popup" href="help" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                
                <td bgcolor="#006699"  title = "Display the total of errors that occured during all the receptions."><font color = "white"><div class="left">Errors</div><a target ="popup"  href="help" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                
            </tr>
               
            """ %( string.upper( machineName ) ) ) 
        
        
        
        for timeType in timeTypes:    
            fileHandle.write( """ 
            <tr> 
                <td bgcolor="#99FF99" > %s %s</td>                  
        
            """ %(( timeType[0].upper() + timeType[1:] ), updateFrequency[timeType] ) )
            if timeType == "daily" :
                timeContainer = days     
            elif timeType == "weekly":
                timeContainer = weeks
            elif timeType == "monthly":
                timeContainer = months
            elif timeType == "yearly":
                timeContainer = years
                         
            for type in rxTypes:
                fileHandle.write( """<td bgcolor="#66CCFF">  """ )
                
                for x in timeContainer:
                    file = "%s/webGraphics/totals/%s/rx/%s/%s/%s.png" %( StatsPaths.STATSGRAPHS, machineName, type, timeType, x ) 
                    if os.path.isfile(file):    
                        fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>""" %( x, file, x ) )
                    
                fileHandle.write( """</td>""" )
            
            fileHandle.write( """</tr>""" )       
                
        fileHandle.write( """</table>""" )      
        
        ####################################txPart
        
        fileHandle.write("""                
           
                <h2>TX totals for %s.</h2>
            
            <table style="table-layout: fixed; width: 1250px; border-left: 0px gray solid; border-bottom: 0px gray solid; padding:0px; margin: 0px" cellspacing=10 cellpadding=6 >
                <tr>
                    
                    <td bgcolor="#006699"   title = >Type</font></td> 
                    
                    <td bgcolor="#006699"  "Display the average latency of file transfers for all clients."><font color = "white"><font color = "white"><div class="left">Latency</div><a target ="popup" href="help" onClick="wopen('helpPages/latency.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699"  title = "Display the number of files for wich the latency was over 15 seconds for all clients."><font color = "white"><div class="left">Files Over Max. Lat.</div><a target ="popup" href="help" onClick="wopen('helpPages/filesOverMaxLatency.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td> 
                    
                    <td bgcolor="#006699"  title = "Display number of bytes transfered to all clients." ><font color = "white"><div class="left">ByteCount</div><a target ="popup" href="help" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699" title = "Display the number of files transferred every day to all clients."><font color = "white"><div class="left">FileCount</div><a target ="popup" href="help" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699"  title = "Display the total of errors that occured during the file transfers to allclients."><font color = "white"><div class="left">Errors</div><a target ="popup" href="help" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                
                </tr>   
               
            """ %( string.upper( machineName ) ) )
        
        
        
        for timeType in timeTypes:    
            fileHandle.write( """ 
            <tr> 
                <td bgcolor="#99FF99" ><div style="width:10pt";>%s%s</div> </td>                  
        
            """ %(( timeType[0].upper() + timeType[1:] ), updateFrequency[timeType] ) ) 
            if timeType == "daily" :
                timeContainer = days     
            elif timeType == "weekly":
                timeContainer = weeks
            elif timeType == "monthly":
                timeContainer = months
            elif timeType == "yearly":
                timeContainer = years
                         
            for type in txTypes:
                fileHandle.write( """<td bgcolor="#66CCFF"> """) 
                
                for x in timeContainer:
                    file = "%swebGraphics/totals/%s/tx/%s/%s/%s.png" %( StatsPaths.STATSGRAPHS, machineName, type, timeType,x ) 
                    if os.path.isfile(file):    
                        fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s </a>""" %( x,file, x ) )
                    else:
                        #print file
                        allo =2  
                fileHandle.write( """</td>""" )
            
            fileHandle.write( """</tr>""" )       
                
        fileHandle.write( """</table>""")             
        
        #End of tx part.             
        
        fileHandle.close()         
                                
                                
    
     
       
def main():
    """
    """
    
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
    machineNames     = machineParameters.getPairedMachinesAssociatedWithListOfTags( configParameters.sourceMachinesTags )

    generateWebPage( machineNames )
     
    
if __name__ == "__main__":
    main()            
            
            
            
            
            
            
    
             