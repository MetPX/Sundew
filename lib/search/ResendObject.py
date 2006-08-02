"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: ResendObject.py
#
# Author: Dominik Douville-Belanger
#
# Description: Class containing the information needed in
#              order to resend bulletins.
#
# Date: 2006-07-10
#
###########################################################
"""

import sys
import time

# Local imports
sys.path.append("../")
sys.path.insert(1, '/apps/px/lib/importedLibs')
import PXPaths; PXPaths.normalPaths()
import PXManager
import Logger
import DirectRoutingParser

class ResendObject(object):
    __slots__ = ["prompt", "destinations", "prio", "machineHeaderDict", "logger", "manager", "drp"]
    
    def __init__(self):
        self.prompt = False
        self.destinations = ""
        self.prio = "3"
        self.machineHeaderDict = {}
        
        # Setting up Logger object and PXManager
        logger = Logger.Logger("/apps/px/log/pxresend.log", "INFO", "DDB")
        self.logger = logger.getLogger()
        self.manager = PXManager.PXManager()
        self.manager.setLogger(self.logger)
        self.manager.initNames()
        self.drp = DirectRoutingParser.DirectRoutingParser(PXPaths.ROUTING_TABLE, self.logger)
        drp.printErrors = False
        drp.parseAlias()
        
    def headerToLocation(self, header):
        headerParts = header.split(":")
        dbPath = PXPaths.DB
        date = headerParts[-1][0:8] # First eight caracters of the timestamp 
        tt = headerParts[0][0:2] # First two letters of the TTAAii
        target = headerParts[1]
        cccc = headerParts[2]

        return "%s%s/%s/%s/%s/%s" % (dbPath, date, tt, target, cccc, header)

    def createAllArtifacts(self):
        commandList = [] # List of command to execute
        for machine in self.machineHeaderDict.keys(): # For every machines with matching bulletins
            try:
                filelogname = "%sfilelogs/filelog.%s" % (PXPaths.SEARCH, machine)
                filelog = open(filelogname, "w") # This file will need to be transfered to the remote machibe
            except IOError:
                print "Could not open filelog for writing!"
                sys.exit(1)

            destinations = " ".join(self.destinations)
            
            bulletins = self.machineHeaderDict[machine]
            for bulletin in bulletins:
                filelog.write("%s\n" % (self.headerToLocation(bulletin)))
            filelog.close()
                    
            commandList += ['ssh %s "%sPXCopy.py -m %s -f %s %s"' % (machine, PXPaths.SEARCH, machine, filelogname, destinations)]
         
        return commandList
   
    def getPrompt(self):
        return self.prompt

    def setPrompt(self, value):
        self.prompt = value

    def getDestinations(self):
        return self.destinations

    def setDestinations(self, value):
        """
        This method receives a list of destination which we'll be checked for alias.
        """
        manager = self.getManager()
        logger = self.getLogger()
        drp = self.getDrp()
        
        destinations = []
        for v in value:
            flowType = manager.getFlowType(v, drp)
            if flowType[0] == "TX" or flowType[0] == "TRX":
                destinations += flowType[1]
            else:
                logger.warning("An RX was used as a destination. Discarded.")
                
        self.destinations = destinations

    def getPrio(self):
        return self.prio

    def setPrio(self, value):
        self.prio = value

    def getMachineHeaderDict(self):
        return self.machineHeaderDict

    def addToMachineHeaderDict(self, machine, header):
        if machine in self.machineHeaderDict.keys():
            self.machineHeaderDict[machine] += [header]
        else:
            self.machineHeaderDict[machine] = [header]

    def getLogger(self):
        return self.logger

    def getManager(self):
        return self.manager

    def getDrp(self):
        return self.drp
