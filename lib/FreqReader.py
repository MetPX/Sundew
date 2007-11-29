"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: FreqReader.py
#
# Authors: Daniel Lemay
#
# Date: 2007-11-29
#
# Description: Used to parse frequency files
#
#############################################################################################

"""
import sys, os, os.path, re, time, fnmatch
import PXPaths, generalLib

PXPaths.normalPaths()              # Access to PX paths

class FreqReader(object):
    def __init__(self, name='px.db', cluster='px') :
        self.name = name              # frequency file name
        self.cluster = cluster        # cluster name (px, pds, pxatx)
        self.sources = {}
        self.freqs = {}
        self.sourcesAndFreqs = {}
        self.clients = {}

        self.read()

    def _reformatSourcesAndFreq(self, sourcesAndFreqs):
        """
        input format: ['source1=01:00:00', 'source2=NA', ...]
        output sources: ['source1', 'source2', ...]
        output freqs: ['01:00:00', 'NA', ...]
        output newSourcesAndFreqs: [('source1', '01:00:00'), ('source2', 'NA'), ...]
        """
        sources = []
        freqs   = [] 
        newSourcesAndFreqs = []
        for sourceFreq in sourcesAndFreqs:
            sourceFreq = tuple(sourceFreq.split('='))
            sources.append(sourceFreq[0])
            freqs.append(sourceFreq[1])
            newSourcesAndFreqs.append(sourceFreq)
        return sources, freqs, newSourcesAndFreqs

    def read(self):
        self._read(PXPaths.PX_DATA + self.cluster + "/" + self.name) 

    def _read(self, filename):
        try:    
            file = open(filename, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value))
            print("File (%s) is not present") % filename
            return

        for line in file.readlines():
            words = line.split()
            sourcesAndFreqs = words[1][1:-1].split(',')
            sources, freqs, sourcesAndFreqs = self._reformatSourcesAndFreq(sourcesAndFreqs)
            self.sources[words[0]] = sources
            self.freqs[words[0]] = freqs
            self.sourcesAndFreqs[words[0]] = sourcesAndFreqs
            
            clients = words[2][1:-1].split(',')
            self.clients[words[0]] = clients

if __name__ == '__main__':
    fr = FreqReader()
    #print fr.sources
    #print fr.freqs
    #print fr.sourcesAndFreqs
    #print fr.clients 
