#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
##############################################################################
##
##
## Name   : generateTopWebPage.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 12-04-2007 
##
##
## Description : Generates the top frame to be displayed on the pxstats web 
##               site.
##
##############################################################################
import os, time, sys, datetime, string
import generalStatsLibraryMethods, MyDateLib, configFileManager


import string 

from PXPaths   import * 
from PXManager import *
from MyDateLib import *
from generalStatsLibraryMethods import *
from configFileManager import * 

   
LOCAL_MACHINE = os.uname()[1]   




def generateWebPage( machineNames ):
    """
        Generates the top.html web page
        to be displayed as the top frame
        of the pxstats web site.
    """

    file = "/apps/px/stats/webPages/top.html" 
    fileHandle = open( file , 'w' )
    
    fileHandle.write( """ 
    <html>
    
    <style type="text/css">
        div.left { float: left; }
        div.right {float: right; }
    </style>
    
    <body text="white" link="white" vlink="white" bgcolor="#006699" >
        
        <div class="left">
            Individual graphics&nbsp;&nbsp;:&nbsp;&nbsp;&nbsp;
            <a href="dailyGraphs.html" target="bottom">Daily</a> 
            &nbsp;&nbsp;&nbsp;            
            <a href="weeklyGraphs.html" target="bottom">Weekly</a>
            &nbsp;&nbsp;&nbsp;
            <a href="monthlyGraphs.html" target="bottom">Monthly</a>
            &nbsp;&nbsp;&nbsp;
            <a href="yearlyGraphs.html" target="bottom">Yearly</a>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  
            
       
       
    """)
    
    
    if machineNames != [] :
        fileHandle.write( """
        Combined graphics&nbsp;&nbsp;:&nbsp;&nbsp;&nbsp;
        """ )    
        
        for machineName in machineNames:
            fileHandle.write( """
            <a href="%s.html" target="bottom">%s</a> 
            &nbsp;&nbsp;&nbsp;              
            """ %( machineName.replace( ',','' ), string.upper(machineName) ) ) 
    
        
    fileHandle.write( """ 
        </div> 
        
        <div class="right">
            <a href="glossary.html" target="bottom" >Glossary</a>
        </div>
    
    </body>    

</html>
    
    
    
    
    """)
    
    
    fileHandle.close() 



def main():
    """
    """
    
    configParameters = configFileManager.getParametersFromConfigurationFile( "statsConfig" )
    
    machineNames     = configParameters.coupledLogMachineNames

    generateWebPage( machineNames )
     
    
if __name__ == "__main__":
    main()    