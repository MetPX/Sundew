#!/usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Plotter.py
#
# Author: Daniel Lemay
#
# Date: 2005-09-01
#
# Description: Make a graph from data points
# 
# MG Not python3 compatible
# 
#############################################################################################
"""

import sys 
import PXPaths, dateLib
from Logger import Logger
from PXManager import PXManager
from PXLatencies import PXLatencies
from Numeric import *
import Gnuplot, Gnuplot.funcutils

class Plotter:

    def __init__(self, type='impulses', interval=1, imageName=None):

        PXPaths.normalPaths()
        self.manager = PXManager()
        #self.logger = logger
        #self.manager.setLogger(self.logger)

        self.latenciers = []                       # Infos about a particular "latencier"

        self.type = type                           # Type of graph must be in: ['linespoint', 'lines', 'boxes', 'impulses']
        self.interval = interval * dateLib.MINUTE  # Number of seconds between each point on the x-axis
        self.imageName = imageName                 # Name of the image file
        self.color = None

        self.width = dateLib.DAY                   # Width of the x-axis in seconds

        # With witdh=DAY and interval=MINUTE => len([60, 120, 180, ..., 86400]) = 1440
        self.separators = dateLib.getSeparators(self.width, self.interval)

        # '"0" 0, "1" 60, "2" 120, "3" 180, "4" 240, ... , "22" 1320, "23" 1380, "24" 1440'
        self.xtics = self.getXTics(len(self.separators), self.interval)

        self.graph = Gnuplot.Gnuplot()

    def getXTics(self, nbPoints, interval):
        nbTics = 24 # This is the number we want (each hour). We don't count the tic at 0
        mult = int(nbPoints/nbTics) # Rounding ???
        xtics = ''

        for i in range(0, nbTics + 1):
            spread = mult * i
            xtics += '"%i" %i, ' % (i, spread)
        
        return xtics[:-2]

    def addLatencier(self, latencier):
        self.latenciers.append(latencier)

    def getPairs(self, data):
         return self._getPairsFromBuckets(self._fillBuckets(dateLib.getEmptyBuckets(self.separators), data))

    def _getPairsFromBuckets(self, buckets):
        # Get coordinates of points (x,y)
        pairs = []
        for (index, values) in buckets.items():
            if values[2]:
                mean_lat = values[3]/values[2]
            else:
                mean_lat = 0.0
            pairs.append([index, mean_lat])
        return pairs

    def _fillBuckets(self, buckets, data):
        # Dict. for which each entry (a bucket) contains a min., a max., the number of latencies for
        # wich the value is between min. and max. and the mean of all latencies contained in this bucket
        from bisect import bisect
        for (file, stats) in data:
            seconds = dateLib.getSeconds(stats[0])
            index = bisect(self.separators, seconds)
            buckets[index][2] += 1        # Make a count
            buckets[index][3] += stats[2] # Add latencies
        return buckets

    def plot(self):

        self.graph('set size 1.5, %2.1f' % (0.5 * len(self.latenciers)))
        self.graph('set origin 0, 0') 

        i = 0
        nbLatenciers = len (self.latenciers)
        for latencier in self.latenciers:
            machines = []
            for machine in latencier.machines:
                machines.append(machine.split('.')[0])


            systemString = 'System: %s' % latencier.system
            machinesString = 'Machines: %s' % str(machines)
            clientString = 'Client: %s' % latencier.client
            if latencier.sources[0] == '__ALL__':
                sourcesString = 'Sources: **ALL**'
            else:
                sourcesString = 'Sources: %s' % str(latencier.sources)
            rejectedString = '# Files rejected: %i' % latencier.rejected
            overThresholdString = '# Files with lat. over %i seconds: %i' % (latencier.latencyThreshold, latencier.overThreshold)
            underThresholdPString = '%% of files with lat. under %i seconds: %4.2f' % (latencier.latencyThreshold, latencier.underThresholdP)
            (filename, (time, host, lat)) = latencier.maxInfos
            maxInfos1 = 'Maximum occurs at: %s' % (time)
            maxInfos2 = '%s (%s)' % (filename.split(':')[0], host)
            xferlogString = 'Xferlog used: %s' % ['No', 'Yes'][latencier.xstats]


            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (systemString, 0.40 + ((nbLatenciers -1) - i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (machinesString, 0.38 + ((nbLatenciers -1) - i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (clientString, 0.36 + ((nbLatenciers -1) -i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (sourcesString, 0.34  + ((nbLatenciers -1) -i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (xferlogString, 0.32  + ((nbLatenciers -1) -i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (maxInfos1, 0.30 + ((nbLatenciers -1) - i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (maxInfos2, 0.28 + ((nbLatenciers -1) - i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (underThresholdPString, 0.26 + ((nbLatenciers -1) - i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (overThresholdString, 0.24 + ((nbLatenciers -1) - i) * 0.5))
            self.graph('set label "%s" at screen 1.00, screen %3.2f' % (rejectedString, 0.22 + ((nbLatenciers -1) - i) * 0.5))
            i += 1

        self.graph('set linestyle 1 lt 4 lw 5')
        self.graph('set linestyle 2 lt 3 lw 3')

        #self.graph('set key left top Left title "%s" box 1' % machinesString)
        #self.graph('set key left samplen 3 top Left title "%s" box 1' % sourcesString)
        #self.graph('set key left bottom')
        #self.graph('set key box linestyle 1')

        self.graph('set lmargin 8')
        
        self.graph.xlabel('time (hours)')
        self.graph.ylabel('latency (seconds)')

        self.graph('set grid')
        #self.graph('set grid linestyle 1')
        #self.graph('set xtics ("low" 0, "medium" 30, "high" 100)')
        self.graph('set xtics (%s)' % self.xtics)

        if self.type == 'lines':
            self.graph('set data style lines')  
        elif self.type == 'impulses':
            self.graph('set data style impulses')  
        elif self.type == 'boxes':
            self.graph('set data style boxes')  
        elif self.type == 'linespoints':
            self.graph('set data style linespoints')  

        self.graph('set terminal png small color')

        #self.graph.plot([[0, 1.1], [1, 5.8], [2, 3.3], [3, 100]])

        self.imageName = "%s_latencies.%s_%s.png" % (self.latenciers[0].pattern, self.latenciers[0].date, self.latenciers[0].random)

        self.graph('set output "%s%s"' % (PXPaths.LAT_RESULTS, self.imageName))

        self.graph('set multiplot')
        
        const = len(self.latenciers) -1
        for i in range(len(self.latenciers)):
            if i == 0:
                color = 1
            elif i == 1:
                color = 3 
            else:
                color = i + 2

            self.graph('set size 1, 0.5')
            self.graph('set origin 0, %3.2f' % ((const - i) * 0.5))
            try:
                if self.latenciers[i].xstats:
                    self.graph("set key title 'MAX: %i,  MEAN: %4.2f (mean wait: %4.2f),  MIN: %i  (#files: %i)' box lt 2" % (
                                               self.latenciers[i].max, self.latenciers[i].mean,
                                               self.latenciers[i].meanWaiting, self.latenciers[i].min, len(self.latenciers[i].sortedStats)))
                else:
                    self.graph("set key title 'MAX: %i,  MEAN: %4.2f,  MIN: %i  (#files: %i)' box lt 2" % (
                                               self.latenciers[i].max, self.latenciers[i].mean,
                                               self.latenciers[i].min, len(self.latenciers[i].sortedStats)))
            except AttributeError:
                self.graph("set key title 'MAX: %i,  MEAN: %4.2f,  MIN: %i  (#files: %i)' box lt 2" % (
                                           self.latenciers[i].max, self.latenciers[i].mean,
                                           self.latenciers[i].min, len(self.latenciers[i].sortedStats)))
            
            if self.latenciers[i].pattern == '__ALL__':
                pattern = 'ALL'
            else:
                pattern = self.latenciers[i].pattern

            self.graph.title('%s Latencies for %s (%s)' % (pattern, str(self.latenciers[i].client), dateLib.getISODateDashed(latencier.date)))
            self.graph.plot(Gnuplot.Data(self.getPairs(self.latenciers[i].sortedStats), with="%s %s 2" % (self.type, color)))
    
            #plotItem = Gnuplot.PlotItems.PlotItem(Gnuplot.Data(self.getPairs(self.latenciers[0].sortedStats), title="MPCN")
            #self.graph.plot(self.getPairs(self.latenciers[0].sortedStats), title="MPCN")
            #self.graph.plot(Gnuplot.Data(self.getPairs(self.latenciers[0].sortedStats), title="MPCN", with="lines 3 2"))
            #self.graph.plot('x')
    
        # FIXME: I start the saving of the file with this (garbage collector). Better command must exist.
        self.graph = None

if __name__ == '__main__':
    latencier1 = PXLatencies()
    #latencier2 = PXLatencies(pattern='SACN')
    plotter = Plotter()
    plotter.addLatencier(latencier1)
    #plotter.addLatencier(latencier2)
    plotter.plot()
