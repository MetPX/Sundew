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

    def __init__(self):
        self.prompt = False
        self.to = []
        self.prio = 3
        self.machineHeaderDict = {}
        
    def getPrompt(self):
        return self.prompt

    def setPrompt(self, value):
        self.prompt = value

    def getTo(self):
        return self.to

    def setTo(self, value):
        self.to = value

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
