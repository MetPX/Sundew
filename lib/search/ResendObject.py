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
import os

# Local imports
sys.path.append("../")
sys.path.insert(1, '/apps/px/lib/importedLibs')
import PXPaths; PXPaths.normalPaths()
import PXManager
import Logger
import DirectRoutingParser

class ResendObject(object):
    __slots__ = ["prompt", "destinations", "prio", "machineHeaderDict", "fileList"]
    
    def __init__(self):
        self.prompt = False
        self.destinations = ""
        self.prio = "3"
        self.machineHeaderDict = {}
        self.fileList = []
        
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
                self.addToFileList(filelogname)        
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
    
    def removeFiles(self):
        fileList = self.getFileList()
        for file in fileList:
            try:
                os.remove(file)
            except OSError:
                type, value, tb = sys.exc_info()
                print "Problem deleting %s, Type: %s Value: %s" % (file, type, value)
    
    def getPrompt(self):
        return self.prompt

    def setPrompt(self, value):
        self.prompt = value

    def getDestinations(self):
        return self.destinations

    def setDestinations(self, value):
        self.destinations = value

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

    def getFileList(self):
        return self.fileList

    def addToFileList(self, value):
        self.fileList += [value]
