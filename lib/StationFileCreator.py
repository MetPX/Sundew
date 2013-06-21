"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: StationFileCreator.py
#
# Author: Daniel Lemay
#
# Date: 2006-06-28
#
# Description: Used to create stations file
#
# MG python3 compatible
#
#############################################################################################
"""
import sys
from FileCreator import FileCreator
import PXPaths

PXPaths.normalPaths()  # Access to PX Paths

class StationFileCreator(FileCreator):
    
    def __init__(self, filename=PXPaths.ETC + 'titi.conf', logger=None, stations=None, stationsColl=None):
        FileCreator.__init__(self, filename)
        self.logger = logger
        self.stations = stations
        self.stationsColl = stationsColl
        self._appendToFile()
        self._closeFile()

    def _appendToFile(self):
        headers = list(self.stations.keys())
        headers.sort()

        for header in headers:
            #print "%s: %s" % (header, self.stations[header])
            stations = ''
            for station in self.stations[header]:
                if stations:
                    stations += ' ' + station
                else:
                    stations = station

            coll = ''

            if self.stationsColl:
                if header in self.stationsColl:
                    coll = 'COLL'

            line = "%s:%s:%s:\n" % (header, coll, stations)
            self.file.write(line)

if __name__ == '__main__':
    from StationParser import StationParser
    sp = StationParser('/apps/px/etc/stations.conf')
    sp.parse()

    sfc = StationFileCreator(stations=sp.stations, stationsColl=sp.stationsColl)
    #sfc.appendToFile()
    #sfc.closeFile()
