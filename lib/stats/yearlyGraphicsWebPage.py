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
## Description : Generates a web pages that gives access to user 
##               to the yearly graphics of the last 3 years for all rx sources 
##               and tx clients.
##
##
##############################################################################



import os, time, sys
import generalStatsLibraryMethods
from generalStatsLibraryMethods import *
from PXPaths   import * 
from PXManager import *

LOCAL_MACHINE = os.uname()[1]
    
    
def getYears():
    """
        Returns the last 3 year numbers including the current year.
    
    """
    
    years = []
    
    startTime = (time.time() - (3*365*24*60*60))
    for i in range(1,4):
        years.append( time.strftime("%Y",time.gmtime(startTime + (i*365*24*60*60) )) )
   
       
    return years
    
    
def main():        
    

    
    rxNames, txNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, "pds5" )
    pxatxrxNames, pxatxtxNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, "pxatx" )
    
    rxNames.extend(pxatxrxNames)
    txNames.extend(pxatxtxNames)
    
    rxNames.sort()
    txNames.sort()
    years = getYears()
    
    
    #Redirect output towards html page to generate.    
    if not os.path.isdir("/apps/px/stats/webPages/"):
        os.makedirs( "/apps/px/stats/webPages/" )     
    fileHandle = open( "/apps/px/stats/webPages/yearlyGraphs.html" , 'w' )

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
            <h2>Yearly graphics for RX sources from MetPx.</h2>
            <br>
            
            <table width="100%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
            <tr>    
                <td bgcolor="#006699" width = "25%"><font color = "white">Client</font></td>
                <td bgcolor="#006699" width = "25%"><font color = "white">Bytecount</font></td>
                <td bgcolor="#006699" width = "25%"><font color = "white">Filecount</font></td>
                <td bgcolor="#006699" width = "25%"><font color = "white">Errors</font></td>
            </tr>   
        
    
    """ )
    
    
    
    for rxName in rxNames :
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = "25%%" > %s </td>
        """ %(rxName) )
    
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Years&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,years[0],years[0], rxName,PXPaths.GRAPHS,rxName,years[1],years[1], rxName,PXPaths.GRAPHS,rxName,years[2],years[2] )  )     
    
    
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Years&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,years[0],years[0], rxName,PXPaths.GRAPHS,rxName,years[1],years[1], rxName,PXPaths.GRAPHS,rxName,years[2],years[2] )   )
        
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Years&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,years[0],years[0], rxName,PXPaths.GRAPHS,rxName,years[1],years[1], rxName,PXPaths.GRAPHS,rxName,years[2],years[2] )    )
              
    
    fileHandle.write(  """

    </table>
    
    
    
    <br>
    <h2>Yearly graphics for TX Clients from MetPx.</h2>
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
      
    
    """)          
        
    for txName in txNames : 
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>
        """ %(txName) )
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Years:<a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,years[0],years[0], txName,PXPaths.GRAPHS,txName,years[1],years[1], txName,PXPaths.GRAPHS,txName,years[2],years[2] ) )   
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Years:<a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,years[0],years[0], txName,PXPaths.GRAPHS,txName,years[1],years[1], txName,PXPaths.GRAPHS,txName,years[2],years[2] ) )
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Years:<a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,years[0],years[0], txName,PXPaths.GRAPHS,txName,years[1],years[1], txName,PXPaths.GRAPHS,txName,years[2],years[2] )    )
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Years:<a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,years[0],years[0], txName,PXPaths.GRAPHS,txName,years[1],years[1], txName,PXPaths.GRAPHS,txName,years[2],years[2] )  )  
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Years:<a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%swebGraphics/yearly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s</a></td>
        """%( txName,PXPaths.GRAPHS,txName,years[0],years[0], txName,PXPaths.GRAPHS,txName,years[1],years[1], txName,PXPaths.GRAPHS,txName,years[2],years[2] ) )       

        

    fileHandle.write(  """
        </tr>

    </table>

    </body>
    </html>
    
    
    
    """ )     
                
    fileHandle.close()                 



if __name__ == "__main__":
    main()