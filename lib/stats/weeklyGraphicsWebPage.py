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
##               to the weekly graphics of the last 5 weeks for all rx sources 
##               and tx clients.
##
##
##############################################################################


import os, time,sys
from PXPaths   import * 
from PXManager import *

localMachine = os.uname()[1]

def getRxTxNames( machine ):
    """
        Returns a tuple containg RXnames and TXnames that we've rsync'ed 
        using updateConfigurationFiles
         
    """    
                        
    pxManager = PXManager()
    
    
    remoteMachines= [ "pds3-dev", "pds4-dev","lvs1-stage", "logan1", "logan2" ]
    if localMachine in remoteMachines :#These values need to be set here.
        PXPaths.RX_CONF  = '/apps/px/stats/rx/%s/'  %machine
        PXPaths.TX_CONF  = '/apps/px/stats/tx/%s/'  %machine
        PXPaths.TRX_CONF = '/apps/px/stats/trx/%s/' %machine
    pxManager.initNames() # Now you must call this method  
    
    txNames = pxManager.getTxNames()               
    rxNames = pxManager.getRxNames()  

    return rxNames, txNames 
    
    
def getWeekNumbers():
    """
        Returns the 5 week numbers including current week number.
    
    """
    
    weekNumbers = []
    
    startTime = (time.time() - (5*7*24*60*60))
    for i in range(1,6):
        weekNumbers.append( time.strftime("%W",time.gmtime(startTime + (i*7*24*60*60))) )
   
    return weekNumbers
    
    
def main():        
    

    
    rxNames,txNames = getRxTxNames("pds5")
    pxatxrxNames,pxatxtxNames = getRxTxNames("pxatx")
    
    rxNames.extend(pxatxrxNames)
    txNames.extend(pxatxtxNames)
    
    rxNames.sort()
    txNames.sort()
    weekNumbers = getWeekNumbers()
    
    
    #Redirect output towards html page to generate.    
    fileHandle = open( "weeklyGraphs.html" , 'w' )
    old_stdout = sys.stdout 
    sys.stdout = fileHandle  
     
    print """
    <html>
        <head>
            <title> PX Graphics </title>
        </head>    
        <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC" >
        
        <br>
        <h2>Weekly graphics for RX sources from MetPx.</h2>
        <br>
        <table width="100%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
        <tr>    
            <td bgcolor="#006699" width = "25%" >Client</td>
            <td bgcolor="#006699" width = "25%">Bytecount</td>
            <td bgcolor="#006699" width = "25%">Filecount</td>
            <td bgcolor="#006699" width = "25%">Errors</td>
        </tr>         
    
    """     
    
    
    for rxName in rxNames :
        
        print """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>
        """ %(rxName)
    
        print """    
            <td bgcolor="#66CCFF" width = "25%%" >Weeks: <a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,weekNumbers[0],weekNumbers[0], rxName,PXPaths.GRAPHS,rxName,weekNumbers[1],weekNumbers[1], rxName,PXPaths.GRAPHS,rxName,weekNumbers[2],weekNumbers[2], rxName,PXPaths.GRAPHS,rxName,weekNumbers[3],weekNumbers[3], rxName,PXPaths.GRAPHS,rxName,weekNumbers[4],weekNumbers[4] )       
    
    
        
        print """    
            <td bgcolor="#66CCFF" width = "25%%" >Weeks: <a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,weekNumbers[0],weekNumbers[0], rxName,PXPaths.GRAPHS,rxName,weekNumbers[1],weekNumbers[1], rxName,PXPaths.GRAPHS,rxName,weekNumbers[2],weekNumbers[2], rxName,PXPaths.GRAPHS,rxName,weekNumbers[3],weekNumbers[3], rxName,PXPaths.GRAPHS,rxName,weekNumbers[4],weekNumbers[4] )   
        
        
        print """    
            <td bgcolor="#66CCFF" width = "25%%" >Weeks: <a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,weekNumbers[0],weekNumbers[0], rxName,PXPaths.GRAPHS,rxName,weekNumbers[1],weekNumbers[1], rxName,PXPaths.GRAPHS,rxName,weekNumbers[2],weekNumbers[2], rxName,PXPaths.GRAPHS,rxName,weekNumbers[3],weekNumbers[3], rxName,PXPaths.GRAPHS,rxName,weekNumbers[4],weekNumbers[4] )                              
    
        
        
    print """

    </table>         
    <br>
    <h2>Weekly graphics for TX Clients from MetPx.</h2>
    <br>
    <table width="100%%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void >    
        <tr>

            <td bgcolor="#006699" width = "16.66%%">Client</td>
            <td bgcolor="#006699" width = "16.66%%">Latency</td>
            <td bgcolor="#006699" width = "16.66%%">Files Over Maximum Latency</td>
            <td bgcolor="#006699" width = "16.66%%">Bytecount</td>
            <td bgcolor="#006699" width = "16.66%%">Filecount</td>
            <td bgcolor="#006699" width = "16.66%%">Errors</td>
            
        </tr>
    
    """
        
    for txName in txNames : 
        print """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>
        """ %(txName)
        
        print """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Weeks: <a target ="%s" href="%ssymlinks/weekly/latency/%s/%s">%s  </a><a target ="%s" href="%ssymlinks/weekly/latency/%s/%s">%s  </a><a target ="%s" href="%ssymlinks/weekly/latency/%s/%s">%s  </a><a target ="%s" href="%ssymlinks/weekly/latency/%s/%s">%s  </a><a target ="%s" href="%ssymlinks/weekly/latency/%s/%s">%s  </a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] )    
        
        print """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Weeks: <a target ="%s" href="%ssymlinks/weekly/filesOverMaxLatency/%s/%s">%s  </a><a target ="%s" href="%ssymlinks/weekly/filesOverMaxLatency/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filesOverMaxLatency/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filesOverMaxLatency/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filesOverMaxLatency/%s/%s">%s </a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] )    
        
        print """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Weeks: <a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/bytecount/%s/%s">%s </a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] )    
        
        print """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Weeks: <a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/filecount/%s/%s">%s </a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] )    
        
        print """    
            <td bgcolor="#66CCFF" width = "16.66%%" >Weeks: <a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a><a target ="%s" href="%ssymlinks/weekly/errors/%s/%s">%s </a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] )    
 
        

    print """
        </tr>

    </table>

    </body>
    </html>
    
    
    
    """        
                
    fileHandle.close()                 
    sys.stdout = old_stdout #resets standard output  


if __name__ == "__main__":
    main()