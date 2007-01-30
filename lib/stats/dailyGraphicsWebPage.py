#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##############################################################################
##
##
## Name   : dailyGraphicsWebPage.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 22-11-2006 
##
##
## Description : Generates a web pages that gives access to user 
##               to the daily graphics of the last 7 days for all rx sources 
##               and tx clients.
##
##
##############################################################################

import os, time,sys
import generalStatsLibraryMethods

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
    
    
def main():        
    

    
    rxNames,txNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, "pds5" )
    pxatxrxNames,pxatxtxNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, "pxatx" )
    
    rxNames.extend(pxatxrxNames)
    txNames.extend(pxatxtxNames)
    
    rxNames.sort()
    txNames.sort()
    days = getDays()
    
    
    #Redirect output towards html page to generate.    
    if not os.path.isdir("/apps/px/stats/webPages/"):
        os.makedirs( "/apps/px/stats/webPages/" )
    fileHandle = open( "/apps/px/stats/webPages/dailyGraphs.html" , 'w' )

     
    fileHandle.write( """
    <html>
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
        <h2>Daily graphics for RX sources from MetPx.</h2>
        <br>
        <table width="100%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
        <tr>    
            <td bgcolor="#006699" width = "25%%"><font color = "white"><div class="left">Sources</div><a target ="popup" href="%s" onClick="wopen('helpPages/source.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = "75%"><font color = "white">List of available daily graphics.</font></td>
        </tr>   
        
    
    """)
    
    
    
    for rxName in rxNames :
        fileHandle.write( """<tr> <td bgcolor="#99FF99" width = "25%%" > %s </td> """ %(rxName))
        fileHandle.write( """<td bgcolor="#66CCFF" width = "25%%" >   Days :   """ )
        
        for day in days:
            file = "%swebGraphics/daily/%s/%s.png" %( PXPaths.GRAPHS, rxName, day )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="%s" href="%s">%s   </a>"""%( rxName, file, day ) )
                 
    
    fileHandle.write( """</td> 

    </table>  
       
    <br>
    <h2>Daily graphics for TX clients from MetPx.</h2>
    <br>
    <table width="100%%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void >    
        <tr>

             <td bgcolor="#006699" width = "25%%"><font color = "white"><div class="left">Clients</div><a target ="popup" href="%s" onClick="wopen('helpPages/client.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            <td bgcolor="#006699" width = "75%%"><font color = "white">List of available daily graphics.</font></td>
            
        </tr>  
      
    
    """   )       
        
    for txName in txNames : 
        fileHandle.write( """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>""" %(txName) )
        fileHandle.write( """<td bgcolor="#66CCFF" width = "25%%" >   Days :   """ )
        for day in days:
            file = "%swebGraphics/daily/%s/%s.png" %( PXPaths.GRAPHS, txName, day )
            if os.path.isfile( file ):
                fileHandle.write(  """ <a target ="%s" href="%s">%s   </a>""" %( txName, file, day ) )      

        fileHandle.write( "</td>" )

    fileHandle.write(  """
        </tr>

    </table>

    </body>
    </html>
    
    
    
    """ )       
                
    fileHandle.close()                 
    


if __name__ == "__main__":
    main()