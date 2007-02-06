#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
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
import os, time,sys
import generalStatsLibraryMethods

import string 

from PXPaths   import * 
from PXManager import *
from generalStatsLibraryMethods import *
   
LOCAL_MACHINE = os.uname()[1]   


def getDays():
    """
        Returns the last 3 year numbers including the current year.
    
    """
    
    days = []
    
    startTime = (time.time() - (7*24*60*60))
    for i in range(1,8):
        days.append( time.strftime("%a",time.gmtime(startTime + ( i*365*24*60*60 ) )) )
   
       
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
    
    months = []
    
    startTime = (time.time() - (30*3*24*60*60))
    for i in range(1,4):
        months.append( time.strftime("%b",time.gmtime(startTime + (i*30*24*60*60) )) )
   
       
    return months
  
    
      
def getYears():
    """
        Returns the last 3 year numbers including the current year.
    
    """
    
    years = []
    
    startTime = (time.time() - (3*365*24*60*60))
    for i in range(1,4):
        years.append( time.strftime("%Y",time.gmtime(startTime + (i*365*24*60*60) )) )
   
       
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

        
    
def main():
    """
    """
    
    machineNames = [ "pds5,pds6", "pxatx"]
    rxTypes      = [ "bytecount", "filecount", "errors"]
    txTypes      = [ "latency", "filesOverMaxLatency", "bytecount", "filecount", "errors"]
    timeTypes    = [ "daily","weekly","monthly","yearly"]   
    days   = getDays() 
    weeks  = getWeekNumbers()
    months = getMonths()
    years  = getYears()
    
    for machineName in machineNames:
        if not os.path.isdir("/apps/px/stats/webPages/"):
            os.makedirs( "/apps/px/stats/webPages/" )
        machineName = getCombinedMachineName( machineName )
        file = "/apps/px/stats/webPages/%s.html" %machineName
        fileHandle = open( file , 'w' )
        #print "/apps/px/stats/webPages/%s.html" %machineName
        
        fileHandle.write( """ <html>         
            <head>
                <title> PX Graphics </title>
            </head>
            
            <script>             
                function wopen(url, name, w, h){
                // This function was taken on www.boutell.com
                    w += 32;
                    h += 96;
                    var win = window.open(url,
                    name,
                    'width=' + w + ', height=' + h + ', ' +
                    'location=no, menubar=no, ' +
                    'status=no, toolbar=no, scrollbars=no, resizable=no');
                    win.resizeTo(w, h);
                    win.focus();
                }         
            </script>    
            
            <STYLE>
                <!--
                A{text-decoration:none}
                -->
            </STYLE>
            
            <style type="text/css">
                div.left { float: left; }
                div.right {float: right; }
            </style>    
            
            <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC" >
            
            <br>
                <h2>RX totals for %s.</h2>
            <br>
    
            <table width="100%%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
            
            <tr>    
                <td bgcolor="#006699" width = "25%%"><font color = "white"><div class="left">Type</font></td>   
                
                <td bgcolor="#006699" width = "25%%" title = "Display the total of bytes received by all sources."><font color = "white"><div class="left">ByteCount</div><a target ="popup" href="help" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                
                <td bgcolor="#006699" width = "25%%" title = "Display the total of files received by all sources."><font color = "white"><div class="left">FileCount</div><a target ="popup" href="help" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                
                <td bgcolor="#006699" width = "25%%" title = "Display the total of errors that occured during all the receptions."><font color = "white"><div class="left">Errors</div><a target ="popup"  href="help" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                
            </tr>
               
            """ %( string.upper( machineName ) ) ) 
        
        
        
        for timeType in timeTypes:    
            fileHandle.write( """ 
            <tr> 
                <td bgcolor="#99FF99" width = "25%%" > %s receptions </td>                  
        
            """ %( timeType[0].upper() + timeType[1:] ) )
            if timeType == "daily" :
                timeContainer = days     
            elif timeType == "weekly":
                timeContainer = weeks
            elif timeType == "monthly":
                timeContainer = months
            elif timeType == "yearly":
                timeContainer = years
                         
            for type in rxTypes:
                fileHandle.write( """<td bgcolor="#66CCFF" width = "25%%" > %s : """ %(timeType[0].upper() + timeType[1:]) )
                
                for x in timeContainer:
                    file = "%s/webGraphics/totals/%s/rx/%s/%s/%s.png" %( PXPaths.GRAPHS, machineName, type, timeType, x ) 
                    if os.path.isfile(file):    
                        fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>""" %( x, file, x ) )
                    
                fileHandle.write( """</td>""" )
            
            fileHandle.write( """</tr>""" )       
                
        fileHandle.write( """</table>""" )      
        
        ####################################txPart
        
        fileHandle.write("""                
            <br>
                <h2>TX totals for %s.</h2>
            <br>
    
            <table width="100%%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
            
                <tr>
                    
                    <td bgcolor="#006699" width = "16.66%%" title = >Type</font></td> 
                    
                    <td bgcolor="#006699" width = "16.66%%" "Display the average latency of file transfers for all clients."><font color = "white"><font color = "white"><div class="left">Latency</div><a target ="popup" href="help" onClick="wopen('helpPages/latency.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699" width = "16.66%%" title = "Display the number of files for wich the latency was over 15 seconds for all clients."><font color = "white"><div class="left">Files Over Max. Lat.</div><a target ="popup" href="help" onClick="wopen('helpPages/filesOverMaxLatency.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td> 
                    
                    <td bgcolor="#006699" width = "16.66%%" title = "Display number of bytes transfered to all clients." ><font color = "white"><div class="left">ByteCount</div><a target ="popup" href="help" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699" width = "16.66%%" title = "Display the number of files transferred every day to all clients."><font color = "white"><div class="left">FileCount</div><a target ="popup" href="help" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699" width = "16.66%%" title = "Display the total of errors that occured during the file transfers to allclients."><font color = "white"><div class="left">Errors</div><a target ="popup" href="help" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                
                </tr>   
               
            """ %( string.upper( machineName ) ) )
        
        
        
        for timeType in timeTypes:    
            fileHandle.write( """ 
            <tr> 
                <td bgcolor="#99FF99" width = "16.66%%" > %s transmissions </td>                  
        
            """ %( timeType[0].upper() + timeType[1:] ) )
            if timeType == "daily" :
                timeContainer = days     
            elif timeType == "weekly":
                timeContainer = weeks
            elif timeType == "monthly":
                timeContainer = months
            elif timeType == "yearly":
                timeContainer = years
                         
            for type in txTypes:
                fileHandle.write( """<td bgcolor="#66CCFF" width = "16.66%%" > %s : """ %(timeType[0].upper() + timeType[1:]) )
                
                for x in timeContainer:
                    file = "%swebGraphics/totals/%s/tx/%s/%s/%s.png" %( PXPaths.GRAPHS, machineName, type, timeType,x ) 
                    if os.path.isfile(file):    
                        fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>""" %( x,file, x ) )
                    else:
                        print file
                         
                fileHandle.write( """</td>""" )
            
            fileHandle.write( """</tr>""" )       
                
        fileHandle.write( """</table>""")             
        
        #End of tx part.             
        
        fileHandle.close()         
                                
                        
if __name__ == "__main__":
    main()            
            
            
            
            
            
            
    
             