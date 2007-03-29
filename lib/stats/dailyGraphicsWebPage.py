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
            <!--
            A{text-decoration:none}
            -->
        </STYLE>
        <style type="text/css">
            div.left { float: left; }
            div.right {float: right; }
        
            div.txScroll {
                height: 200px;
                width: 1255px;
                overflow: auto;
                word-wrap:break-word;
                border: 0px ;                    
                padding: 0px;
            }
                
            div.txTableEntry{
                width:580px;            
                height: auto;
            }
            
            div.rxScroll {
                height: 200px;
                width: 1255px;
                overflow: auto;
                word-wrap:break-word;
                border: 0px ;                    
                padding: 0px;
            }
                
            div.rxTableEntry{
                width:580px;            
                height: auto;
            }        
        
        
        
        </style>    
        
        <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC" >
        
        <br>
        <h2>Daily graphics for RX sources from MetPx. <font size = "2">*updated hourly</font></h2>
        
        
        <TABLE cellspacing=10 cellpadding=8 id=header bgcolor="#cccccc"> 
            <tr>    
                <td bgcolor="#006699">
                    <div class = "rxTableEntry">
                        <font color = "white">
                            <div class="left">Sources</div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/source.html', 'popup', 875, 100); return false;">
                                <div class="right">?</div>
                            </a>
                        </font>
                    </div>
                </td>
                
                <td bgcolor="#006699">
                    <div class = "rxTableEntry">
                        <font color = "white">List of available daily graphics.</font>
                    </div>
                </td>
            </tr>   
        </table>
        
        
        <div class="rxScroll"> 
    
    """)
    
    
    
    for rxName in rxNames :
        fileHandle.write( """<table cellspacing=10 cellpadding=8> <tr> <td bgcolor="#99FF99"><div class = "rxTableEntry"> %s </div></td> """ %(rxName))
        fileHandle.write( """<td bgcolor="#66CCFF"><div class = "rxTableEntry">   Days :   """ )
        
        for day in days:
            file = "%swebGraphics/daily/%s/%s.png" %( PXPaths.GRAPHS, rxName, day )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="%s" href="%s">%s   </a>"""%( rxName, file, day ) )
                 
        fileHandle.write( """</div></td></tr></table>""" )
    
    fileHandle.write( """
      
    </div>
       
    <br>
    <h2>Daily graphics for TX clients from MetPx. <font size = "2">*updated hourly</font></h2>
    
    <TABLE cellspacing=10 cellpadding=8 id=header bgcolor="#cccccc">   
        <tr>

             <td bgcolor="#006699">
                <div class = "txTableEntry">
                    <font color = "white">
                        <div class="left">Clients</div>
                        <a target ="popup" href="%s" onClick="wopen('helpPages/client.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a>
                    </font>
                </div>
            </td>
            
            <td bgcolor="#006699">
                <div class = "txTableEntry">
                    <font color = "white">List of available daily graphics.</font>
                </div>    
            </td>
            
        </tr>  
     </table>   
     
     
    <div class="txScroll"> 
    
       
    """   )       
        
    for txName in txNames : 
        fileHandle.write( """<table cellspacing=10 cellpadding=8><tr><td bgcolor="#99FF99"><div class = "txTableEntry"> %s </div></td>""" %(txName) )
        
        fileHandle.write( """<td bgcolor="#66CCFF"><div class = "txTableEntry">   Days :   """ )
        
        for day in days:
            file = "%swebGraphics/daily/%s/%s.png" %( PXPaths.GRAPHS, txName, day )
            if os.path.isfile( file ):
                fileHandle.write(  """ <a target ="%s" href="%s">%s   </a>""" %( txName, file, day ) )      

        fileHandle.write( "</div></td></tr></table>" )

    fileHandle.write(  """
      
    </div>
    
    </body>

</html>
    
    
    
    """ )       
                
    fileHandle.close()                 
    


if __name__ == "__main__":
    main()