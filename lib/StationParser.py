"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: StationParser.py
#
# Author: Daniel Lemay
#
# Date: 2006-05-21
#
# Description: Use to parse the stations file (stations.conf)
#
#############################################################################################
"""
import sys, time
from FileParser import FileParser

class StationParser(FileParser):
    
    def __init__(self, filename, logger=None):
        FileParser.__init__(self, filename) # Stations filename ("/apps/px/etc/stations.conf")
        self.logger = logger     # Logger Object
        self.headers = {}        # Indexed by station
        self.stations = {}       # Indexed by header
        self.stationsColl = {}   # Indexed by header (only the ones that have to be collected)
        self.printErrors = False # Print errors
        self.logErrors = True    # Log errors

    def getStationsColl(self):
        return self.stationsColl

    def parse(self):
        file = self.openFile(self.filename)

        uniqueHeaders = {}
        duplicateHeaders = {}

        for line in file:
            line = line.strip()
            words = line.split(':')
            header = words[0]
            coll = words[1]
            stations = words[2].split()

            # Find duplicate station for a given header
            uniqueStations = self._removeDuplicate(stations)
            duplicateForHeader = self._identifyDuplicate(stations)
            
            # Sort the stations
            uniqueStations.sort()

            # Populate stations dictionary
            self.stations[header] = uniqueStations

            # Populate stationsColl dictionary
            if coll:
                self.stationsColl[header] = uniqueStations

            # Find duplicate headers
            if uniqueHeaders.has_key(header):
                duplicateHeaders[header] = 1
            else:
                uniqueHeaders[header] = 1
                # Populate headers dictionary
                for station in uniqueStations:
                    self.headers.setdefault(station, []).append(header)

            if duplicateForHeader and self.printErrors:
                print("%s has duplicate(s): %s" % (header, duplicateForHeader))

            if duplicateForHeader and self.logErrors and self.logger:
                self.logger.warning("%s has duplicate(s): %s" % (header, duplicateForHeader))

        if self.printErrors:
            if len(duplicateHeaders):
                print("Duplicate header line(s): %s" % duplicateHeaders.keys())
            #else:
            #    print("No duplicated header")
        if self.logErrors and self.logger:
            if len(duplicateHeaders):
                self.logger.warning("Duplicate header line(s): %s" % duplicateHeaders.keys())

    def printMenu(self):
        print
        print("1-Headers indexed by station")
        print("2-Stations indexed by header")
        print("3-Reprint this menu")
        print("q-Quit")
        print

    def printInfos(self):
            max = 0
            min = 1000
            for key in self.headers.keys():
                #print key, self.headers[key]
                nbHeaders = len(self.headers[key])
                if nbHeaders >= 3:
                    print "%s: %s" % (key, self.headers[key])
                #if key == 'CYBL':
                #    print "%s: %s" % (key, self.headers[key])
                if nbHeaders > max:
                    max = nbHeaders
                    station = key
                elif nbHeaders < min:
                    min = nbHeaders
            print "=============================================================================="
            print "Number of different stations: %i" % len(self.headers.keys())
            print "Max: %i (%s): %s" % (max, repr(station), self.headers[station]) 
            print "Min: %i" % min
            print "=============================================================================="

if __name__ == '__main__':
    import sys
    #sp = StationParser('/apps/px/etc/collection_stations.conf')
    sp = StationParser('/apps/px/etc/stations.conf')
    sp.printErrors = True
    sp.parse()
    sp.printInfos()
    print sp.getStationsColl()
    sp.printMenu()
    mustChoose = True
    while True:
        if mustChoose:
            mode = raw_input("Your choice: ")
            if mode == '1':
                selector = 'station'
            elif mode == '2':
                selector = 'header'
            elif mode == '3':
                sp.printMenu()
                continue 
            elif mode == 'q' or mode == 'Q': sys.exit()
            mustChoose = False

        print
        answer = raw_input("Enter a %s:  " % selector).upper()
        if answer == 'Q' or answer == '': sys.exit()
        elif answer == '3':
            sp.printMenu()
            mustChoose = True
            continue

        if mode == '1':
            print sp.headers.get(answer, "%s is not in the table" % answer)
        elif mode == '2':
            print sp.stations.get(answer, "%s is not in the table" % answer),
            
