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
            <h2>Yearly graphics for RX sources from MetPx. <font size = "2">*updated monthly</font></h2>
                        
            <TABLE cellspacing=10 cellpadding=8 id=header bgcolor="#cccccc">
                <tr>   
                
                    <td bgcolor="#006699" width = 280><font color = "white"><div class="left">Sources</div><a target ="popup" href="%s" onClick="wopen('helpPages/source.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699" width = 280 title = "Display the total of bytes received every day of the year for each sources."><font color = "white"><div class="left">Bytecount</div><a target ="popup" href="%s" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a> </font></td>
                    
                    <td bgcolor="#006699" width = 280 title = "Display the total of files received every day of the year for each sources."><font color = "white"><div class="left">Filecount</div><a target ="popup" href="%s" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699" width = 280 title = "Display the total of errors that occured during the receptions for every day of the year for each sources."><font color = "white"><div class="left">Errors</div><a target ="popup"  href="%s" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                </tr>   
            
            </table> 
            
            <DIV STYLE="overflow: auto; width: 1255px; height: 180; 
                    border-left: 0px gray solid; border-bottom: 0px gray solid; 
                    padding:0px; margin: 0px">
            <TABLE cellspacing=10 cellpadding=8>  
    
    """ )
    
    
    
    for rxName in rxNames :
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = 280 > %s </td>
        """ %(rxName) )
    
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = 280 >Years&nbsp;:&nbsp;""" )
        
        for year in years:
            file = "%swebGraphics/yearly/bytecount/%s/%s.png" % (PXPaths.GRAPHS, rxName, year )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file , year ) ) 
        
        fileHandle.write( "</td>" )      
    
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = 280 >Years&nbsp;:&nbsp;""" )
        
        for year in years:
            file = "%swebGraphics/yearly/filecount/%s/%s.png" % (PXPaths.GRAPHS, rxName, year )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file , year ) ) 
        
        fileHandle.write( "</td>" )    
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = 280 >Years&nbsp;:&nbsp;""" )
        
        for year in years:
            file = "%swebGraphics/yearly/errors/%s/%s.png" % (PXPaths.GRAPHS, rxName, year )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file , year ) ) 
        
        fileHandle.write( "</td>" )    
              
    
    fileHandle.write(  """

    </table>
    </div>    
    
    <br>
    <h2>Yearly graphics for TX clients from MetPx. <font size = "2">*updated monthly</h2>
    
        <TABLE cellspacing=10 cellpadding=8 id=header bgcolor="#cccccc"> 
        <tr>

            <td bgcolor="#006699" width = 180><font color = "white"><div class="left">Clients</div><a target ="popup" href="%s" onClick="wopen('helpPages/client.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = 180 title = "Display the average latency of file transfers for every day of the year for each clients."><font color = "white"><div class="left">Latency</div><a target ="popup" href="%s" onClick="wopen('helpPages/latency.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = 180 title = "Display the total number of files for wich the latency was over 15 seconds for every day of the year for each clients."><font color = "white"><div class="left">Files Over Max. Lat.</div><a target ="popup" href="%s" onClick="wopen('helpPages/filesOverMaxLatency.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = 180 title = "Display the total of bytes transfered every day of the year for each clients."><font color = "white"><div class="left">Bytecount</div><a target ="popup" href="%s" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = 180 title = "Display the total of files transferred every day of the year for each clients."><font color = "white"><div class="left">Filecount</div><a target ="popup" href="%s" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
            <td bgcolor="#006699" width = 180 title = "Display the total of errors that occured during file transfers every day of the year for each clients."><font color = "white"><div class="left">Errors</div><a target ="popup" href="%s" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
            
        </tr>  
        </table>
        
        <DIV STYLE="overflow: auto; width: 1255px; height: 180; 
                    border-left: 0px gray solid; border-bottom: 0px gray solid; 
                    padding:0px; margin: 0px">
        <TABLE cellspacing=10 cellpadding=8>       
    
    """)          
        
    for txName in txNames : 
        fileHandle.write(  """<tr> <td bgcolor="#99FF99" width = 180 > %s </td>
        """ %(txName) )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = 180 >Years&nbsp;:&nbsp;""" )
        
        for year in years:
            file = "%swebGraphics/yearly/latency/%s/%s.png" % (PXPaths.GRAPHS, txName, year )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file , str(year)[-2:] ) )
        
        fileHandle.write( "</td>" )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = 180 >Years&nbsp;:&nbsp;""" )
        
        for year in years:
            file = "%swebGraphics/yearly/filesOverMaxLatency/%s/%s.png" % (PXPaths.GRAPHS, txName, year )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file , str(year)[-2:] ) )
        
        fileHandle.write( "</td>" )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = 180 >Years&nbsp;:&nbsp;""" )
        
        for year in years:
            file = "%swebGraphics/yearly/bytecount/%s/%s.png" % (PXPaths.GRAPHS, txName, year )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file , str(year)[-2:] ) )
        
        fileHandle.write( "</td>" )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = 180 >Years&nbsp;:&nbsp;""" )
        
        for year in years:
            file = "%swebGraphics/yearly/filecount/%s/%s.png" % (PXPaths.GRAPHS, txName, year )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file , str(year)[-2:] ) )
        
        fileHandle.write( "</td>" )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF" width = 180 >""" )
        
        for year in years:
            file = "%swebGraphics/yearly/errors/%s/%s.png" % (PXPaths.GRAPHS, txName, year )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, file , str(year)[-2:] ) )
        
        fileHandle.write( "</td>" )

        

    fileHandle.write(  """
        </tr>

    </table>
    </div>
    </body>
    </html>
    
    
    
    """ )     
                
    fileHandle.close()                 



if __name__ == "__main__":
    main()