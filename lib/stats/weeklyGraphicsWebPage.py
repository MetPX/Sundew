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


def updateConfigurationFiles( machine, login ):
    """
        rsync .conf files from designated machine to local machine
        to make sure we're up to date.

    """

    if not os.path.isdir( '/apps/px/stats/rx/' ):
        os.makedirs(  '/apps/px/stats/rx/' , mode=0777 )
    if not os.path.isdir( '/apps/px/stats/tx/'  ):
        os.makedirs( '/apps/px/stats/tx/', mode=0777 )
    if not os.path.isdir( '/apps/px/stats/trx/' ):
        os.makedirs(  '/apps/px/stats/trx/', mode=0777 )


    status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/etc/rx/ /apps/px/stats/rx/%s/"  %( login, machine, machine ) )
    #print output # for debugging only

    status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/etc/tx/ /apps/px/stats/tx/%s/"  %( login, machine, machine ) )
    #print output # for debugging only
    
    
    
def getRxTxNames( machine ):
    """
        Returns a tuple containg RXnames and TXnames that we've rsync'ed 
        using updateConfigurationFiles
         
    """    
                        
    pxManager = PXManager()
    
    
    remoteMachines= [ "pds3-dev", "pds4-dev","lvs1-stage", "logan1", "logan2" ]
    if localMachine in remoteMachines :#These values need to be set here.
        updateConfigurationFiles( machine, "pds" )
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
        <h2>Weekly graphics for RX sources from MetPx.</h2>
        <br>
        <table width="100%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void > 
        <tr>    
            
            <td bgcolor="#006699" width = "25%" ><font color = "white">Sources</font></td>
            <td bgcolor="#006699" width = "25%"><font color = "white">Bytecount</font></td>
            <td bgcolor="#006699" width = "25%"><font color = "white">Filecount</font></td>
            <td bgcolor="#006699" width = "25%"><font color = "white">Errors</font></td>
            
        </tr>         
    
    """ )    
    
    
    for rxName in rxNames :
        
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>
        """ %(rxName) )
    
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Weeks &nbsp;:&nbsp; <a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,weekNumbers[0],weekNumbers[0], rxName,PXPaths.GRAPHS,rxName,weekNumbers[1],weekNumbers[1], rxName,PXPaths.GRAPHS,rxName,weekNumbers[2],weekNumbers[2], rxName,PXPaths.GRAPHS,rxName,weekNumbers[3],weekNumbers[3], rxName,PXPaths.GRAPHS,rxName,weekNumbers[4],weekNumbers[4] )  )     
    
    
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Weeks &nbsp;:&nbsp; <a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,weekNumbers[0],weekNumbers[0], rxName,PXPaths.GRAPHS,rxName,weekNumbers[1],weekNumbers[1], rxName,PXPaths.GRAPHS,rxName,weekNumbers[2],weekNumbers[2], rxName,PXPaths.GRAPHS,rxName,weekNumbers[3],weekNumbers[3], rxName,PXPaths.GRAPHS,rxName,weekNumbers[4],weekNumbers[4] )  ) 
        
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "25%%" >Weeks &nbsp;: &nbsp;<a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( rxName,PXPaths.GRAPHS,rxName,weekNumbers[0],weekNumbers[0], rxName,PXPaths.GRAPHS,rxName,weekNumbers[1],weekNumbers[1], rxName,PXPaths.GRAPHS,rxName,weekNumbers[2],weekNumbers[2], rxName,PXPaths.GRAPHS,rxName,weekNumbers[3],weekNumbers[3], rxName,PXPaths.GRAPHS,rxName,weekNumbers[4],weekNumbers[4] ) )                             
    
        
        
    fileHandle.write(  """

    </table>         
    <br>
    <h2>Weekly graphics for TX Clients from MetPx.</h2>
    <br>
    <table width="100%%" border="1" cellspacing="5" cellpadding="5" bgcolor="#cccccc" bordercolor="#CCCCCC" frame = void >    
        <tr>

            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Client</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Latency</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Files Over Maximum Latency</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Bytecount</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Filecount</font></td>
            <td bgcolor="#006699" width = "16.66%%"><font color = "white">Errors</font></td>
            
        </tr>
    
    """ )
        
    for txName in txNames : 
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = "16.66%%" > %s </td>
        """ %(txName) )
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >weeks&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/latency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td> 
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] ) )   
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >weeks&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filesOverMaxLatency/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] ) )   
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >weeks&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/bytecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] ) )   
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >weeks&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/filecount/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] ) )   
        
        fileHandle.write(  """    
            <td bgcolor="#66CCFF" width = "16.66%%" >weeks&nbsp;:&nbsp;<a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a><a target ="popup" href="%s" onClick="wopen('%ssymlinks/weekly/errors/%s/%s.png', 'popup', 875, 240); return false;">%s&nbsp;</a></td>
        """%( txName,PXPaths.GRAPHS,txName,weekNumbers[0],weekNumbers[0], txName,PXPaths.GRAPHS,txName,weekNumbers[1],weekNumbers[1], txName,PXPaths.GRAPHS,txName,weekNumbers[2],weekNumbers[2], txName,PXPaths.GRAPHS,txName,weekNumbers[3],weekNumbers[3], txName,PXPaths.GRAPHS,txName,weekNumbers[4],weekNumbers[4] ) )   
 
        

    fileHandle.write(  """
        </tr>

    </table>

    </body>
    </html>
    
    
    
    """  )      
                
    fileHandle.close()                 
    

if __name__ == "__main__":
    main()