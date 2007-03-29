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
                div.left { float: left;word-wrap:break-word; }
                div.right {float: right;word-wrap:break-word; }
                    
                div.txScroll {
                    height: 200px;
                    width: 1255px;
                    overflow: auto;
                    word-wrap:break-word;
                    border: 0px ;                    
                    padding: 0px;
                }
                    
                div.txTableEntry{
                    width:177px;            
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
                    width:277px;            
                    height: auto;
                }       
                                
                <!--
                A{text-decoration:none}
                -->
                <!--
                // -->
            
            </style>
            
        </head>    
        
        <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC" >          
        
        <br>
        <h2>Monthly graphics for RX sources from MetPx. <font size = "2">*updated weekly</font></h2>
        
        <table cellspacing=10 cellpadding=8 id=header bgcolor="#cccccc">    
        
        <tr>    
            <td bgcolor="#006699" >
                <div class = "rxTableEntry">
                    <font color = "white">
                        <div class="left">Sources</div>
                        <a target ="popup" href="%s" onClick="wopen('helpPages/source.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a>
                    </font>
                </div>
            </td>
            
            <td bgcolor="#006699" title = "Display the total of bytes received every day of the week for each sources.">
                <div class = "rxTableEntry">
                    <font color = "white">
                        <div class="left">Bytecount</div>
                        <a target ="popup" href="%s" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a> 
                    </font>
                </div>
            </td>
            
            <td bgcolor="#006699" title = "Display the total of files received every day of the week for each sources.">
                <div class = "rxTableEntry">
                    <font color = "white">
                        <div class="left">Filecount</div>
                        <a target ="popup" href="%s" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a>
                    </font>
                </div>        
            </td>
            
            <td bgcolor="#006699" title = "Display the total of errors that occured during the receptions for every day of the week for each sources.">
                <div class = "rxTableEntry">
                    <font color = "white">
                        <div class="left">Errors</div>
                        <a target ="popup"  href="%s" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a>
                    </font>
                </div>
            </td>
            
            
        </tr>   
        
        </table>
        
        <div class="rxScroll"> 
                  
    """ )
    
    
    #print months
    for rxName in rxNames :
        
        fileHandle.write(  """<table cellspacing=10 cellpadding=8><tr> <td bgcolor="#99FF99"><div class = "rxTableEntry"> %s </div></td>""" %(rxName) )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "rxTableEntry">Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/bytecount/%s/%s.png" % (PXPaths.GRAPHS, rxName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file ,month ) ) 
        
        fileHandle.write( "</div></td>" )
            
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "rxTableEntry">Months&nbsp;:&nbsp;""" )        
        
        for month in months:
            file = "%swebGraphics/monthly/filecount/%s/%s.png" % (PXPaths.GRAPHS, rxName, month )
            if os.path.isfile(file):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file ,month ) )   
                        
        fileHandle.write( "</div></td>" )
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "rxTableEntry">Months&nbsp;:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/errors/%s/%s.png" % (PXPaths.GRAPHS, rxName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """ <a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file ,month ) )  
        
        fileHandle.write( "</div></td></tr></table>" )  
              
    
    fileHandle.write(  """

        </table>
    </div>
    
    
    <br>
    <h2>Monthly graphics for TX clients from MetPx. <font size = "2">*updated weekly</font></h2>
    
    
        <table  cellspacing=10 cellpadding=8 id=header bgcolor="#cccccc">
    
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
            
            <td bgcolor="#006699"  title = "Display the taverage latency of file transfers for every day of the week for each clients.">
                <font color = "white">
                    <div class = "txTableEntry">
                        <div class="left">Latency</div>
                        <a target ="popup" href="%s" onClick="wopen('helpPages/latency.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a>                
                    </div>
                </font>            
            </td>
            
            <td bgcolor="#006699"  title = "Display the total number of files for wich the latency was over 15 seconds for every day of the week for each clients.">
                <div class = "txTableEntry">
                    <font color = "white">
                        <div class="left">Files over Max. Lat.</div>
                         <a target ="popup" href="%s" onClick="wopen('helpPages/filesOverMaxLatency.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                         </a>                        
                    </font>
                </div>
            </td>
            
            <td bgcolor="#006699" title = "Display the total of bytes transfered every day of the week for each clients.">
                <div class = "txTableEntry">
                    <font color = "white">
                        <div class="left">Bytecount</div>
                        <a target ="popup" href="%s" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a>
                    </font>
                </div>
            </td>
            
            <td bgcolor="#006699"  title = "Display the total of files transferred every day of the week for each clients.">
                <div class = "txTableEntry">
                    <font color = "white">
                        <div class="left">Filecount</div>
                        <a target ="popup" href="%s" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a>
                    </font>
                </div>
            </td>
            
            <td bgcolor="#006699" title = "Display the total of errors that occured during file transfers every day of the week for each clients.">
                <div class = "txTableEntry">
                    <font color = "white">
                        <div class="left">Errors</div>
                        <a target ="popup" href="%s" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;">
                            <div class="right">?</div>
                        </a>
                    </font>
                </div>
            </td>
            
        </tr>              
        </table>
               
        <div class="txScroll">
          
        
    """   )      
           
    
    for txName in txNames : 
        
        fileHandle.write(  """<table cellspacing=10 cellpadding=8><tr> <td bgcolor="#99FF99" ><div class = "txTableEntry"> %s </div></td>
        """ %(txName) )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" ><div class = "txTableEntry">Months:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/latency/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</div></td>" )
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"  ><div class = "txTableEntry">Months:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/filesOverMaxLatency/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</div></td>" )
        
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"  ><div class = "txTableEntry">Months:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/bytecount/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</div></td>" )
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"  ><div class = "txTableEntry">Months:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/filecount/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</div></td>" )
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "txTableEntry">Months:&nbsp;""" )
        
        for month in months:
            file = "%swebGraphics/monthly/errors/%s/%s.png" % (PXPaths.GRAPHS, txName, month )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file ,month ) )
        
        fileHandle.write( "</div></td></tr></table>" )

        

    fileHandle.write(  """
    
    </div>
    </body>
    </html>
    
    
    
    """  )      
                
    fileHandle.close()                 
     


if __name__ == "__main__":
    main()