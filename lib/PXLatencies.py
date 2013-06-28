#!/usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PXLatencies
#
# Author: Daniel Lemay
#
# Date: 2005-09-01
#
# Description: Calculate latencies for a product (MPCN for example) sent to 
#              a PX client (wxo-b1 for example)
# 
#############################################################################################
"""
import sys, os, os.path, commands, fnmatch

import PXPaths, dateLib
from Latencies import Latencies

class PXLatencies(Latencies):

    def __init__(self, nopull=False, keep=False, date=None, pattern='MPCN', machines=['pds5', 'pds6'], sources=['ncp1', 'ncp2'], client='wxo-b1', xstats=False):
        
        Latencies.__init__(self, nopull, keep, date, xstats) # Parent Constructor

        self.pattern = pattern     # Products that we want to match
        self.machines = machines   # Machines were the logs can be found
        self.sources = sources     # Sources for which we will check arrival time of the products
        self.client = client       # Client for which we will check delivery time of the products (A string)
        self.system = 'PX'
        
        if not self.nopull:
            self.obtainFiles()
        
        self.start()

        if not self.keep:
            self.eraseFiles()

    def obtainFiles(self):

        # Used for xferlog
        (dummy, month, day) = dateLib.getISODateParts(self.date)
        if day[0] == '0':
            day = ' ' +  day[1]
        monthAbbrev = dateLib.getMonthAbbrev(month)

        for machine in self.machines:
            self.manager.createDir(PXPaths.LAT_TMP +  machine + '_' + self.random)
            
            if self.sources[0] == '__ALL__':
                command = "ssh %s grep -h -e \"'%s.*INFO.*Ingested'\" %s/rx*" % (machine, self.dateDashed, PXPaths.LOG)
                #print command
                (status, output) = commands.getstatusoutput(command)
                allSources = open(PXPaths.LAT_TMP + machine + '_' + self.random + '/rx_all.log', 'w')
                allSources.write(output)
                allSources.close()
            else:
                for source in self.sources:
                    command = "ssh %s grep -h -e \"'%s.*INFO.*Ingested'\" %s/rx_%s*" % (machine, self.dateDashed, PXPaths.LOG, source)
                    (status, output) = commands.getstatusoutput(command)
                    sourceFile = open(PXPaths.LAT_TMP + machine + '_' + self.random + '/rx_' + source, 'w')
                    sourceFile.write(output)
                    sourceFile.close()

                    #command = 'scp -q %s:%s %s' % (machine, PXPaths.LOG + 'rx_' + source + '*', PXPaths.LAT_TMP + machine + '_' + self.random)
                    #(status, output) = commands.getstatusoutput(command)

            # xferlog data
            if self.xstats:
                command = "ssh %s grep -h -e \"'%s %s'\" /var/log/wu-ftpd/xferlog" % (machine, monthAbbrev, day)
                (status, output) = commands.getstatusoutput(command)
                xferlog = open(PXPaths.LAT_TMP + machine + '_' + self.random + '/xferlog_paplat', 'w')
                xferlog.write(output)
                xferlog.close()

            command = 'scp -q %s:%s %s' % (machine, PXPaths.LOG + 'tx_' + self.client + '.*', PXPaths.LAT_TMP + machine + '_' + self.random)
            (status, output) = commands.getstatusoutput(command)

    def extractGoodLines(self, prefix, good):
        for machine in self.machines:
            hostOnly = machine.split('.')[0]
            lines = []
            xferlogLines = []
            dirPath = PXPaths.LAT_TMP + machine + '_' + self.random
            try:
                files = os.listdir(dirPath)
            except OSError:
                print "%s doesn't exist!\nDon't use -n|--nopull option if you don't have some data." % dirPath
                sys.exit(1)

            if prefix == 'rx' and self.xstats:
                for file in [x for x in files if x == 'xferlog_paplat']:
                        xferlogLines.extend(open(dirPath + '/' + file).readlines())
                
            for file in [x for x in files if x[0:2] == prefix]:
                lines.extend(open(dirPath + '/' + file).readlines())

            if self.pattern == '__ALL__' and prefix == 'rx':
                # Good matching is done in obtaining the lines via grep
                good.extend(map(lambda x: (x, hostOnly), lines))
                if self.xstats:
                    self.goodXferlog.extend(map(lambda x: (x, hostOnly), xferlogLines))
            elif self.pattern == '__ALL__' and prefix == 'tx':
                #print("Lines length: %s" % str(len(lines)))
                good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '%s*[INFO]*delivered*' % (self.dateDashed))))

            elif prefix == 'rx': # With a pattern to match
                good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '%s*INFO*%s*' % (self.dateDashed, self.pattern))))
                if self.xstats:
                    self.goodXferlog.extend(map(lambda x: (x, hostOnly), fnmatch.filter(xferlogLines, '*%s*' % (self.pattern))))
            elif prefix == 'tx': # With a pattern to match
                good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '%s*INFO*%s*' % (self.dateDashed, self.pattern))))
                
            #print len(good)

    def extractInfos(self, prefix, good, infos):
        if prefix == 'rx':
            #print("GOOD RX: %i" % len(good))
            for (line, machine) in good:
                date = line[:19]
                filename = os.path.basename(line.split()[-1])
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                infos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            self.goodRx = []

        # xferlog stuff
            for (line, machine) in self.goodXferlog:
                parts = line.split()
                hhmmss = parts[3]
                date = '%s %s' % (self.dateDashed, hhmmss)
                filename = os.path.split(parts[8])[1]
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                self.xferlogInfos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            self.goodXferlog = []

        if prefix == 'tx':
            #print("GOOD TX: %i" % len(good))
            for (line, machine) in good:
                date = line[:19]
                filename = os.path.basename(line.split()[6])
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                infos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            self.goodTx = []

if __name__ == '__main__':

    latencier =  PXLatencies()
