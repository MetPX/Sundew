#!/usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PDSLatencies
#
# Author: Daniel Lemay
#
# Date: 2005-09-13
#
# Description: Calculate latencies for a product (MPCN for example) sent to
#              a PDS client (wxo-b1 for example)
# 
#############################################################################################
"""
import sys, os, os.path, fnmatch

if sys.version[:1] >= '3' :
   import subprocess
else :
   import commands
   subprocess = commands



import PXPaths, dateLib
from Latencies import Latencies

class PDSLatencies(Latencies):

    def __init__(self, nopull=False, keep=False, date=None, pattern='ACC', machines=['pds1', 'pds2', 'pds3', 'pds4'], sources=['pdschkprod'], client='wxo-b1-oper-ww', xstats=False):

        Latencies.__init__(self, nopull, keep, date, xstats) # Parent Constructor

        self.pattern = pattern     # Products that we want to match
        self.machines = machines   # Machines were the logs can be found
        self.sources = sources     # Sources for which we will check arrival time of the products
        self.client = client       # Client for which we will check delivery time of the products (ONLY ONE ENTRY in the list)
        self.system = 'PDS'

        if not self.nopull:
            self.obtainFiles()
        
        self.start()

        if not self.keep:
            self.eraseFiles()

    def obtainFiles(self):
        date = self.date
        
        # Used for xferlog
        (dummy, month, day) = dateLib.getISODateParts(date)
        if day[0] == '0':
            day = ' ' +  day[1]
        monthAbbrev = dateLib.getMonthAbbrev(month)

        LOG = '/apps/pds/log/'
        for machine in self.machines:
            self.manager.createDir(PXPaths.LAT_TMP +  machine + '_' + self.random)
            for source in self.sources:
                command = 'scp -q %s:%s %s' % (machine, LOG + source + '.' + date, PXPaths.LAT_TMP + machine + '_' + self.random)
                (status, output) = subprocess.getstatusoutput(command)

            command = 'scp -q %s:%s %s' % (machine, LOG + self.client + '.' + date, PXPaths.LAT_TMP + machine + '_' + self.random)
            (status, output) = subprocess.getstatusoutput(command)

            # xferlog data
            if self.xstats:
                command = "ssh %s grep -h -e \"'%s %s'\" /var/log/xferlog /var/log/xferlog.?" % (machine, monthAbbrev, day)
                (status, output) = subprocess.getstatusoutput(command)
                xferlog = open(PXPaths.LAT_TMP + machine + '_' + self.random + '/xferlog_paplat', 'w')
                xferlog.write(output)
                xferlog.close()

    def extractGoodLines(self, prefix, good):
        date = self.date
        for machine in self.machines:
            hostOnly = machine.split('.')[0]
            lines = []
            xferlogLines = []
            dirPath = PXPaths.LAT_TMP + machine + '_' + self.random
            try:
                files = os.listdir(dirPath)
            except OSError:
                print("%s doesn't exist!\nDon't use -n|--nopull option if you don't have some data." % dirPath)
                sys.exit(1)
                
            if prefix == 'rx':
                for file in [x for x in files if x == 'pdschkprod.%s' % (date)]:
                    lines.extend(open(dirPath + '/' + file).readlines())

                if self.xstats:
                    for file in [x for x in files if x == 'xferlog_paplat']:
                        xferlogLines.extend(open(dirPath + '/' + file).readlines())

                if self.pattern == '__ALL__':
                    good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '*Written*')))
                    if self.xstats:
                        self.goodXferlog.extend(map(lambda x: (x, hostOnly), xferlogLines))
                else:
                    good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '*Written*%s*' % (self.pattern))))
                    if self.xstats:
                        self.goodXferlog.extend(map(lambda x: (x, hostOnly), fnmatch.filter(xferlogLines, '*%s*' % (self.pattern))))

            if prefix == 'tx':
                for file in [x for x in files if x == '%s.%s' % (self.client, date)]:
                    lines.extend(open(dirPath + '/' + file).readlines())

                if self.pattern == '__ALL__':
                    good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, 'INFO*sent to*')))
                else:
                    good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, 'INFO*%s*sent to*' % (self.pattern))))

    def extractInfos(self, prefix, good, infos):
        if prefix == 'rx':
            #print("GOOD RX: %i" % len(good))
            for (line, machine) in good:
                parts = line.split()
                hhmmss = parts[3][:-1] 
                date = '%s %s' % (self.dateDashed, hhmmss)
                if self.xstats:
                    # Remove ::20050918000030
                    filename_parts = os.path.split(parts[9])[1].split(':')
                    filename = ':'.join(filename_parts[:-2])
                else:
                    filename = os.path.split(parts[9])[1] 
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                infos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            #print len(infos)
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
                parts = line.split()
                hhmmss = parts[3][:-1]
                date = '%s %s' % (self.dateDashed, hhmmss)
                if self.xstats:
                    # Remove ::20050918020123:pds4
                    filename_parts = parts[7].split(':')
                    filename = ':'.join(filename_parts[:-3])
                else:
                    # Only remove machine name
                    filename_parts = parts[7].split(':') 
                    filename = ':'.join(filename_parts[:-1])

                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                infos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            #print len(infos)
            self.goodTx = []

        """    
        print "*************************************** RX ********************************"
        for tuple in  self.goodRx:
            print (tuple[0].strip(), tuple[1])
        print "*************************************** TX ********************************"
        for tuple in  self.goodTx:
            print (tuple[0].strip(), tuple[1])
        """

if __name__ == '__main__':

    latencier =  PDSLatencies()
