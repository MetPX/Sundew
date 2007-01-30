#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##############################################################################
##
##
## Name   : generateGraphics.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 22-11-2006 
##
##
## Description : Generates a web pages that givers access to user 
##               to the monthly graphics of the last 3 months for all rx sources 
##               and tx clients.
##
##
##############################################################################

import os, time,sys, MyDateLib, datetime
import generalStatsLibraryMethods
from MyDateLib import *
from generalStatsLibraryMethods import *
from PXPaths   import * 
from PXManager import *

LOCAL_MACHINE  = os.uname()[1]    

def getMonths():
    """
        Returns the 3 months including current month.
    
    """
    currentTime = time.time()
    currentTime = MyDateLib.getIsoFromEpoch( currentTime )
    currentDate = datetime.date( int(currentTime[0:4]), int(currentTime[5:7]), int(currentTime[8:10]) )     
       
    months = []
    
    startTime = (time.time() - (30*3*24*60*60))
    
    for i in range(0,3):
        
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
        print year,month,day
    
    months.reverse()
        
    return months
    
    
def main():        
    """
        Generates the web page.
    """    

    
    rxNames,txNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, "pds5")
    pxatxrxNames,pxatxtxNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, "pxatx")
    
    rxNames.extend(pxatxrxNames)
    txNames.extend(pxatxtxNames)
    
    rxNames.sort()
    txNames.sort()
    months = getMonths()
    
    
    #Redirect output towards html page to generate. 
    if not os.path.isdir("/apps/px/stats/webPages/"):
        os.makedirs( "/apps/px/stats/webPages/" )        
    fileHandle = open( "/apps/px/stats/webPages/monthlyGraphs.html" , 'w' )

    
    fileHandle.write(  """
    
    <html>
        <head>
            <title> PX Graphics </title>
            
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
            
            
        </head>    
        <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC" >
            <STYLE>
                <!--
                A{text-decoration:none}
                -->
            </STYLE>
            <style type="text/css">
                div.left { float: left; }
                div.right {float: right; }
            </style>
        <br>
        <h2>Monthly graphics for RX sources from MetPx.</h2>
        <br>
         <table width="100%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
        
        <tr>    
            <td bgcolor="#006699" width = "16.66%%"><font color = "white"><div class="left">Sources</div><a target ="popup" href="%s" onClick="wopen('helpPages/source.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = "25%" title = "Display the total of bytes received every day of the week for each sources."><font color = "white"><div class="left">Bytecount</div><a target ="popup" href="%s" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a> </font></td>
            
            <td bgcolor="#006699" width = "25%" title = "Display the total of files received every day of the week for each sources."><font color = "white"><div class="left">Filecount</div><a target ="popup" href="%s" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = "25%" title = "Display the total of errors that occured during the receptions for every day of the week for each sources."><font color = "white"><div class="left">Errors</div><a target ="popup"  href="%s" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
        </tr>   
        
    
    """ )
    
    
    print months
    for rxName in rxNames :
        
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = "25%%" > %s </td>""" %(rxName) )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = "25%%" >Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/bytecount/%s/%s.png" % (PXPaths.GRAPHS, rxName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file ,month ) ) 
        
        fileHandle.write( "</td>" )
            
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = "25%%" >Months&nbsp;:&nbsp;""" )        
        
        for month in months:
            file = "%swebGraphics/monthly/filecount/%s/%s.png" % (PXPaths.GRAPHS, rxName, month )
            if os.path.isfile(file):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file ,month ) )   
                        
        fileHandle.write( "</td>" )
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = "25%%" >Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/errors/%s/%s.png" % (PXPaths.GRAPHS, rxName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """ <a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file ,month ) )  
        
        fileHandle.write( "</td>" )  
              
    
    fileHandle.write(  """

    </table>
    
    
    
    <br>
    <h2>Monthly graphics for TX clients from MetPx.</h2>
    <br>
    <table width="100%%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void >    
        <tr>

            <td bgcolor="#006699" width = "16.66%%"><font color = "white"><div class="left">Clients</div><a target ="popup" href="%s" onClick="wopen('helpPages/client.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = "16.66%%" title = "Display the taverage latency of file transfers for every day of the week for each clients."><font color = "white"><div class="left">Latency</div><a target ="popup" href="%s" onClick="wopen('helpPages/latency.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = "16.66%%" title = "Display the total number of files for wich the latency was over 15 seconds for every day of the week for each clients."><font color = "white"><div class="left">Files Over Max. Lat.</div><a target ="popup" href="%s" onClick="wopen('helpPages/filesOverMaxLatency.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = "16.66%%" title = "Display the total of bytes transfered every day of the week for each clients."><font color = "white"><div class="left">Bytecount</div><a target ="popup" href="%s" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = "16.66%%" title = "Display the total of files transferred every day of the week for each clients."><font color = "white"><div class="left">Filecount</div><a target ="popup" href="%s" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = "16.66%%" title = "Display the total of errors that occured during file transfers every day of the week for each clients."><font color = "white"><div class="left">Errors</div><a target ="popup" href="%s" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
        </tr>  
      
    
    """   )       
        
    
    
    for txName in txNames : 
        
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>
        """ %(txName) )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = "16.66%%%%" >Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/latency/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</td>" )
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = "16.66%%%%" >Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/filesOverMaxLatency/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</td>" )
        
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = "16.66%%%%" >Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/bytecount/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</td>" )
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = "16.66%%%%" >Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/filecount/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</td>" )
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = "16.66%%%%" >Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/errors/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</td>" )

        

    fileHandle.write(  """
        </tr>

    </table>

    </body>
    </html>
    
    
    
    """  )      
                
    fileHandle.close()                 
     


if __name__ == "__main__":
    main()