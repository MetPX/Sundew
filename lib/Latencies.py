#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Latencies
#
# Author: Daniel Lemay
#
# Date: 2005-09-13
#
# Description: Calculate latencies for a product (MPCN for example) sent to
#              a client (wxo-b1 for example)
# 
#############################################################################################
"""
import sys, os, os.path, time, pwd, commands, fnmatch, random

import PXPaths, dateLib
from Logger import Logger
from PXManager import PXManager

class Latencies:

    def __init__(self, nopull=False, keep=False, date=None, xstats=False):

        PXPaths.normalPaths()
        self.manager = PXManager()
        #self.logger = logger.getLogger()

        # Date for which we want to obtain stats
        if date == None:
            self.date = dateLib.getYesterdayFormatted() # ISO Date
        else:
            self.date = date

        self.dateDashed = dateLib.getISODateDashed(self.date)

        self.machines = []         # Machines were the logs can be found
        self.sources = []          # Sources for which we will check arrival time of the products
        self.client = []           # Client for which we will check delivery time of the products (ONLY ONE ENTRY in the list)
        self.messages = []         # FIXME: Special messages coming from weird results

        self.nopull = nopull       # Do not pull the necessary files (we suppose they are already downloaded)
        self.keep =  keep          # Erase all the files present before downloading new files
        self.xstats = xstats       # Boolean that determine if we will use xferlog in making stats

        self.goodRx = []           # Lines matching initial values
        self.goodTx = []           # Lines matching initial values
        self.goodXferlog = []      # Lines matching initial values

        self.receivingInfos = {}   # Dict. addressed by filename and containing a tuple of (formatted date, date in seconds, machine) 
        self.sendingInfos = {}     # Dict. addressed by filename and containing a tuple of (formatted date, date in seconds, machine) 
        self.xferlogInfos = {}     # Dict. addressed by filename and containing a tuple of (formatted date, date in seconds, machine) 

        self.stats = {}            # Final stats
        self.sortedStats = []      # Final sorted stats
        self.max = 0               # Maximum latency time in seconds
        self.min = sys.maxint      # Minimum latency time in seconds
        self.mean = 0              # Mean latency time in seconds
        self.latencyThreshold = 15 # We don't want to go over this threshold (in seconds)
        self.overThreshold = 0     # Number of files with latency over threshold
        self.underThresholdP = 0   # Percentage of files for which the latency is equal or under threshold
        self.meanWaiting = 0       # Mean waiting time before being noticed by the PDS

        self.random = str(random.random())[2:]   # Unique identificator permitting the program to be run in parallel
        self.system = None                       # 'PDS' or 'PX'
        self.rejected = 0                        # Count of rejected files
        self.maxInfos = ['NO FILE', ('00:00:00', 'No machine', 0)]   # Informations about the max.


    def start(self):
        self.extractGoodLines('rx', self.goodRx)
        self.extractInfos('rx', self.goodRx, self.receivingInfos)
        self.extractGoodLines('tx', self.goodTx)
        self.extractInfos('tx', self.goodTx, self.sendingInfos)
        if self.xstats:
            self.makeXferStats()
        else:
            self.makeStats()
        #self.printStats()

    def eraseFiles(self):
        for dir in fnmatch.filter(os.listdir(PXPaths.LAT_TMP), '*' + self.random):
            fullPath = PXPaths.LAT_TMP + dir
            command = 'rm -rf %s' % fullPath
            (status, output) = commands.getstatusoutput(command)

    def obtainFiles(self):
        raise 'Must be implemented in a child class'

    def extractGoodLines(self, prefix, good):
        raise 'Must be implemented in a child class'

    def extractInfos(self, prefix, good, infos):
        raise 'Must be implemented in a child class'

    def makeStats(self):
        total_latency = 0.0

        for file in self.sendingInfos:        
            if file in self.receivingInfos:
                date, seconds, machine = self.receivingInfos[file]
                latency = self.sendingInfos[file][1] - seconds

                if latency > self.latencyThreshold:
                    self.overThreshold += 1

                self.stats[file] =  (date[11:19], machine, latency)
                total_latency += latency
                if latency > self.max:
                    self.max = latency
                    self.maxInfos = [file, self.stats[file]]
                elif latency < self.min:
                    self.min = latency 
            else:
                self.rejected += 1

        if len(self.stats) > 0:
            self.mean =  total_latency / len(self.stats)
            self.underThresholdP =  (len(self.stats) - self.overThreshold) / float(len (self.stats)) * 100
        else:
            self.mean = 0
            self.underThresholdP = 100

        if self.min == sys.maxint:
            self.min = 0

        self.sortedStats = self._getSortedStats(self.stats)

        # Garbage Collection
        self.receivingInfos = {}
        self.sendingInfos = {}
        self.xferlogInfos = {}   
        self.stats = {}

    def makeXferStats(self):
        total_latency = 0.0
        total_waiting = 0.0

        for file in self.sendingInfos:        
            if file in self.receivingInfos and file in self.xferlogInfos:
                xfer_date, seconds, machine = self.xferlogInfos[file]
                waiting = self.receivingInfos[file][1] - seconds
                total_waiting += waiting

                date, seconds, machine = self.receivingInfos[file]
                latency = self.sendingInfos[file][1] - seconds

                if latency > self.latencyThreshold:
                    self.overThreshold += 1

                total_latency += latency

                self.stats[file] =  (xfer_date[11:19], machine, waiting + latency)
                
                bigLat = latency + waiting
                if bigLat > self.max:
                    self.max = bigLat
                    self.maxInfos = [file, self.stats[file]]
                elif bigLat < self.min:
                    self.min = bigLat

                if bigLat > 40000:
                    print file, bigLat, machine
                    print self.xferlogInfos[file]
                    print self.receivingInfos[file]
                    print self.sendingInfos[file]
            else:
                self.rejected += 1

        if len(self.stats) > 0:
            self.mean =  (total_latency + total_waiting) / len(self.stats)
            self.meanWaiting = total_waiting / len(self.stats)
            self.underThresholdP =  (len(self.stats) - self.overThreshold) / float(len (self.stats)) * 100

        else:
            self.mean = 0
            self.meanWaiting = 0
            self.underThresholdP = 100

        if self.min == sys.maxint:
            self.min = 0

        self.sortedStats = self._getSortedStats(self.stats)

        # Garbage Collection
        self.receivingInfos = {}
        self.sendingInfos = {}
        self.xferlogInfos = {}   
        self.stats = {}

    def _getSortedStats(self, statsDict):
        # Will be sorted by date
        items = [(v,k) for k,v in statsDict.items()]
        items.sort()
        return [(k,v) for v,k in items]

    def printStats(self):
        for (filename, (date, machine, latency)) in self.sortedStats:
            print("%s  %6i     %s  (%s)" % (date, latency, filename, machine))

if __name__ == '__main__':

    latencier =  Latencies()
