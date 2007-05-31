#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

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
"""
"""
    Small function that adds pxlib to the environment path.  
"""
import os, time, sys, datetime, string
sys.path.insert(1, sys.path[0] + '/../../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    PXManager requires pxlib 
"""
from PXManager import *
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
   
LOCAL_MACHINE = os.uname()[1]   



def generateWebPage( machineNames ):
    """
        Generates the top.html web page
        to be displayed as the top frame
        of the pxstats web site.
    """

    file = "%stop.html" %StatsPaths.STATSWEBPAGES 
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
    
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
    machineNames     = machineParameters.getPairedMachinesAssociatedWithListOfTags( configParameters.sourceMachinesTags )

    generateWebPage( machineNames )
    
     
    
if __name__ == "__main__":
    main()    