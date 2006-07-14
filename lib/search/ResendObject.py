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

# Local imports
sys.path.append("../")
import PXPaths; PXPaths.normalPaths()

class ResendObject(object):
    __slots__ = ["prompt", "destinations", "prio", "machineHeaderDict"]
    
    def __init__(self):
        self.prompt = False
        self.destinations = ""
        self.prio = 3
        self.machineHeaderDict = {}
    
    def headerToLocation(self, header):
        headerParts = header.split(":")
        dbPath = PXPaths.DB
        date = headerParts[-1][0:8] # First eight caracters of the timestamp 
        tt = headerParts[0][0:2] # First two letters of the TTAAii
        target = headerParts[1]
        cccc = headerParts[2]

        return "%s%s/%s/%s/%s/%s" % (dbPath, date, tt, target, cccc, header)
    
    def createCommandList(self):
        commandList = []
        for machine in self.machineHeaderDict.keys():
            for destination in self.destinations:
                bulletins = self.machineHeaderDict[machine]
                bstring = ""
                for bulletin in bulletins:
                    #############
                    print "Bulletin is : " + bulletin
                    #############
                    bstring += "%s " % (self.headerToLocation(bulletin))
                commandList += 'ssh %s "cp %s"' % (machine, bstring)
        return commandList
        
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
            self.machineHeaderDict[machine] += header
        else:
            self.machineHeaderDict[machine] = [header] 
