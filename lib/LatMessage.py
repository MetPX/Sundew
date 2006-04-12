#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: LatMessage.py
#
# Author: Daniel Lemay
#
# Date: 2005-09-01
#
# Description: Format Latencies Messages
# 
#############################################################################################
"""
import PXPaths, dateLib

class LatMessage:

    def __init__(self, latencier, imageName=None):
        PXPaths.normalPaths()
        
        self.text = ''              # Results in plain text
        self.html = ''              # Results in html
        self.latencier = latencier  # Latencier (PDS or PX)
        self.imageName = imageName  # Came from the plotter
        self.date = self.latencier.date # Date in ISO Format

        self.setTextResults()
        self.saveResults(PXPaths.LAT_RESULTS)
        
    def saveResults(self, path):
        file = open('%s%s_latencies.%s' % (path, self.latencier.pattern, self.date), 'w')
        file.write(self.text)
        file.close()

    def printResults(self):
        print self.text

    def setTextResults(self):
        part1 = """
<HTML>
<PRE>
<BODY>
"""
        part1a = """
<img src="cid:%s%s" alt="Latencies Graph">
<br>
""" % (PXPaths.LAT_RESULTS, self.imageName)

        part2 = """
####################################################################################################
#                             %s LATENCIES STATS (%s)                                       
####################################################################################################
# Number of files is: %s 
# Max. latency time is: %i seconds
# Mean latency time is: %4.2f seconds
# Min. latency time is: %i seconds
####################################################################################################
# ARRIVAL     LATENCY    FILENAME
####################################################################################################
""" % (self.latencier.pattern, self.date, len(self.latencier.sortedStats),
       self.latencier.max, self.latencier.mean, self.latencier.min)

        part3 = ''
        for (key, value) in self.latencier.sortedStats:
            date, machine, latency = value
            part3 += ("# %s  %6i       %s  (%s)    \n" %  (date, latency, key, machine))            
        #part3.strip('\n')

        part4 = """
####################################################################################################
"""
        part5 = """
</BODY>
</PRE>
</HTML>
"""

        part1 = part1.lstrip()
        part1a = part1a.lstrip()
        part2 = part2.lstrip()
        part4 = part4.lstrip()
        part5 = part5.lstrip()

        self.text =  part2 + part3 + part4

        if self.imageName:
            self.html =  part1 + part1a + part2 + part3 + part4 + part5
        else:
            self.html =  part1 + part2 + part3 + part4 + part5


if __name__ == '__main__':

    message =  LatMessage()
