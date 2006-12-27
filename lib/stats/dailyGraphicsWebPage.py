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
        <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC" >
        
        <br>
        <h2>Daily graphics for RX sources from MetPx.</h2>
        <br>
         <table width="100%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
        <tr>    
            <td bgcolor="#006699" width = "25%"><font color = "white">Sources</font></td>
            <td bgcolor="#006699" width = "75%"><font color = "white">List of available daily graphics.</font></td>
        </tr>   
        
    
    """)
    
    
    
    for rxName in rxNames :
        fileHandle.write( """<tr> <td bgcolor="#99FF99" width = "25%%" > %s </td>
        """ %(rxName))
    
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >   Days :   <a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,days[0],days[0], rxName,PXPaths.GRAPHS,rxName,days[1],days[1], rxName,PXPaths.GRAPHS,rxName,days[2],days[2],rxName,PXPaths.GRAPHS,rxName,days[3],days[3], rxName,PXPaths.GRAPHS,rxName,days[4],days[4], rxName,PXPaths.GRAPHS,rxName,days[5],days[5], rxName,PXPaths.GRAPHS,rxName,days[6],days[6] )  ) 
                 
    
    fileHandle.write(  """

    </table>  
       
    <br>
    <h2>Daily graphics for TX Clients from MetPx.</h2>
    <br>
    <table width="100%%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void >    
        <tr>

            <td bgcolor="#006699" width = "25%%"><font color = "white">Clients</font></td>
            <td bgcolor="#006699" width = "75%"><font color = "white">List of available daily graphics.</font></td>
            
        </tr>  
      
    
    """   )       
        
    for txName in txNames : 
        fileHandle.write( """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>
        """ %(txName) )
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >   Days :   <a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a><a target ="%s" href="%swebGraphics/daily/%s/%s.png">%s   </a></td>
        """%( txName,PXPaths.GRAPHS,txName,days[0],days[0], txName,PXPaths.GRAPHS,txName,days[1],days[1], txName,PXPaths.GRAPHS,txName,days[2],days[2],txName,PXPaths.GRAPHS,txName,days[3],days[3], txName,PXPaths.GRAPHS,txName,days[4],days[4], txName,PXPaths.GRAPHS,txName,days[5],days[5], txName,PXPaths.GRAPHS,txName,days[6],days[6] )  )       

        

    fileHandle.write(  """
        </tr>

    </table>

    </body>
    </html>
    
    
    
    """ )       
                
    fileHandle.close()                 
    


if __name__ == "__main__":
    main()