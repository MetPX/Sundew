#!/usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: PXCopy.py
#
# Author: Dominik Douville-Belanger
#
# Description: 
#
# Date: 2006-08-02
#
# TODO: Let the user select the priority
#       So add an option to optparse for that.
#       Won't be necessary if all we need is 0
#
###########################################################
"""

import sys
import os
import commands
import shutil
import socket
from optparse import OptionParser

# Local imports
sys.path.insert(1,sys.path[0] + '/../')
sys.path.append(sys.path[1] + "/importedLibs")
import PXManager
import DirectRoutingParser
import CacheManager
import PXPaths; PXPaths.normalPaths()
import Logger

class PXCopy(object):
    __slots__ = ["file", "destinations", "logger", "manager", "drp", "flowDirsCache", "machine"]

    def __init__(self, file, destinations):
        self.file = file
        self.destinations = destinations

        self.logger = Logger.Logger("/apps/px/log/PXCopy.log", "INFO", "DDB").getLogger()
        self.manager = PXManager.PXManager()
        self.manager.setLogger(self.logger)
        self.manager.initNames()
        self.drp = DirectRoutingParser.DirectRoutingParser(PXPaths.ROUTING_TABLE, [], self.logger)
        self.drp.printErrors = False
        self.drp.parseAlias()
        self.flowDirsCache = CacheManager.CacheManager(maxEntries = 10000, timeout = 2*3600)
        self.machine = socket.gethostname()
        
    def copy(self):
        machine = self.getMachine()
        try:
            fileLog = self.getFile()
            destinations = self.getDestinations()
            if len(destinations) < 1:
                raise "Invalid destination list."

            try:
                flog = open(fileLog, 'r')
            except IOError:
                (type, value, tb) = sys.exc_info()
                sys.exit("Problem opening %s, Type: %s Value: %s" % (fileLog, type, value))

            filesToCopy = flog.readlines()
            flog.close()

            for file in filesToCopy:
                file = file.strip()
                for destination in destinations:
                    destination = self.createCompleteDestination(destination, file.split("/")[-1])
                    try:
                        shutil.copy(file, destination)
                        print "%s: Resent %s to %s" % (machine, file, destination)
                    except IOError:
                        (type, value, tb) = sys.exc_info()
                        print "%s: Problem copying %s to %s, Type: %s" % (machine, file, destination, type)
        except:
            type, value, tb = sys.exc_info()
            sys.exit("An error occured in the PXCopy, Type: %s Value: %s" % (type, value))
    
    def createCompleteDestination(self, flow, filename):
        """
        Converts a flow name to a path on the hard drive.
        """
        manager = self.getManager()
        drp = self.getDrp()
        flowDirsCache = self.getFlowDirsCache()
        prio = 2 # Enventually or user selected
        
        if prio == -1:
            flowQueueName = manager.getFlowQueueName(flow, drp, filename)
        else:
            flowQueueName = manager.getFlowQueueName(flow, drp, filename, prio)

        if flowQueueName:
            manager.createCachedDir(os.path.dirname(flowQueueName), flowDirsCache)
        else:
            raise "Invalid destination."

        return flowQueueName
    
    def checkDestinationsForAlias(self):
        """
        Updates the destinations attributes by replacing alias with the corresponding
        flow names.
        """
        manager = self.getManager()
        destinations = self.getDestinations()
        drp = self.getDrp()
    
        expandedDest = []
        for destination in destinations:
            flowType = manager.getFlowType(destination, drp)
            expandedDest += flowType[1]
        self.setDestinations(expandedDest)
    
    def deleteFile(self):
        try:
            os.remove(self.getFile())
        except OSError:
            type, value, tb = sys.exc_info()
            print "Problem deleting %s, Type: %s Value: %s" % (file, type, value)
    
    def getFile(self):
        return self.file

    def getDestinations(self):
        return self.destinations
    
    def setDestinations(self, value):
        self.destinations = value
    
    def getManager(self):
        return self.manager

    def getLogger(self):
        return self.logger

    def getDrp(self):
        return self.drp

    def getFlowDirsCache(self):
        return self.flowDirsCache

    def getMachine(self):
        return self.machine

####################################################
# THESE ARE USED WHEN CALLED FROM THE COMMAND LINE #
####################################################
def pullFile(host, filename):
    """
    Pulls the file list from another server (usually the frontend).
    """
    
    cmdLine = "scp %s:%s ./" % (host, filename)
    status, output = commands.getstatusoutput(cmdLine)
    if status:
        sys.exit("Could not pull file log from the server.\nCommand was: %s\nCommand output: %s" % (cmdLine, output))
    else:
        return filename.split("/")[-1] # Just the name of the file, without the old path

def validateUserInput(options, args):
    if (options.file == "" or options.machine == ""):
        sys.exit("You must specify a valid file and host!")
    if len(args) < 1:
        sys.exit("You must specify at least one destination!")

def createParser():
    usagemsg = "%prog [options] <destinations>\nCopies multiple bulletins files to multiple flows."
    parser = OptionParser(usage=usagemsg, version="%prog 0.99-rc1")
    parser.add_option("-f", "--file", dest = "file", help = "Specify a file that contains a list of sources.", default = "")
    parser.add_option("-m", "--machine", dest = "machine", help = "Specify the machine on which the file resides.", default = "")
    
    return parser

def main():
    parser = createParser()
    options, args = parser.parse_args()    
    validateUserInput(options, args)
    filename = pullFile(options.machine, options.file)
    
    pxcp = PXCopy(filename, args) # args is the list of destinations
    pxcp.checkDestinationsForAlias()
    pxcp.copy()
    pxcp.deleteFile()

if __name__ == "__main__":
    main()
