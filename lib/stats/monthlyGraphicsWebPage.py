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

import os, time,sys
import generalStatsLibraryMethods
from generalStatsLibraryMethods import *
from PXPaths   import * 
from PXManager import *

LOCAL_MACHINE  = os.uname()[1]    

def getMonths():
    """
        Returns the 3 months including current month.
    
    """
    
    months = []
    
    startTime = (time.time() - (30*3*24*60*60))
    for i in range(1,4):
        months.append( time.strftime("%b",time.gmtime(startTime + (i*30*24*60*60) )) )
   
       
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
        <br>
        <h2>Monthly graphics for RX sources from MetPx.</h2>
        <br>
         <table width="100%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
        <tr>    
            <td bgcolor="#006699" width = "25%" ><font color = "white">Client</font></td>
            <td bgcolor="#006699" width = "25%"><font color = "white">Bytecount</font></td>
            <td bgcolor="#006699" width = "25%"><font color = "white">Filecount</font></td>
            <td bgcolor="#006699" width = "25%"><font color = "white">Errors</font></td>
        </tr>   
        
    
    """ )
    
    
    
    for rxName in rxNames :
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = "25%%" > %s </td>
        """ %(rxName) )
    
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Months&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,months[0],months[0], rxName,PXPaths.GRAPHS,rxName,months[1],months[1], rxName,PXPaths.GRAPHS,rxName,months[2],months[2] )   )    
    
    
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Months&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,months[0],months[0], rxName,PXPaths.GRAPHS,rxName,months[1],months[1], rxName,PXPaths.GRAPHS,rxName,months[2],months[2] )  ) 
        
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Months&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,months[0],months[0], rxName,PXPaths.GRAPHS,rxName,months[1],months[1], rxName,PXPaths.GRAPHS,rxName,months[2],months[2] ) )   
              
    
    fileHandle.write(  """

    </table>
    
    
    
    <br>
    <h2>Monthly graphics for TX Clients from MetPx.</h2>
    <br>
    <table width="100%%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void >    
        <tr>

            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Client</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Latency</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Latencies over 15 secs.</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Bytecount</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Filecount</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Errors</font></td>
            
        </tr>  
      
    
    """   )       
        
    for txName in txNames : 
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>
        """ %(txName) )
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Months: <a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,months[0],months[0], txName,PXPaths.GRAPHS,txName,months[1],months[1], txName,PXPaths.GRAPHS,txName,months[2],months[2] ) )   
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Months: <a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,months[0],months[0], txName,PXPaths.GRAPHS,txName,months[1],months[1], txName,PXPaths.GRAPHS,txName,months[2],months[2] )    )
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Months: <a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,months[0],months[0], txName,PXPaths.GRAPHS,txName,months[1],months[1], txName,PXPaths.GRAPHS,txName,months[2],months[2] ) )   
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Months: <a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,months[0],months[0], txName,PXPaths.GRAPHS,txName,months[1],months[1], txName,PXPaths.GRAPHS,txName,months[2],months[2] )    )
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Months: <a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/monthly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,months[0],months[0], txName,PXPaths.GRAPHS,txName,months[1],months[1], txName,PXPaths.GRAPHS,txName,months[2],months[2] ) ) 

        

    fileHandle.write(  """
        </tr>

    </table>

    </body>
    </html>
    
    
    
    """  )      
                
    fileHandle.close()                 
     


if __name__ == "__main__":
    main()