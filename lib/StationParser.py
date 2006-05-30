"""
#############################################################################################
# Name: StationParser.py
#
# Author: Daniel Lemay
#
# Date: 2006-05-21
#
# Description: Use to parse the stations file (collection_stations.conf)
#
#############################################################################################
"""
import sys

class StationParser:
    
    def __init__(self, filename, logger=None):
        self.filename = filename # 
        self.logger = logger     # Logger Object
        self.headers = {}        # Indexed by station
        self.stations = {}       # Indexed by header
        self.printErrors = True  #

    def parse(self):
        try:
            file = open(self.filename, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            #self.logger.error("Type: %s, Value: %s" % (type, value))
            print ("Type: %s, Value: %s" % (type, value))
            sys.exit()

        uniqueHeaders = {}
        duplicateHeaders = {}

        for line in file:
            line = line.strip()
            words = line.split()
            header = words[0]
            stations = words[1:]

            # Find duplicate station for a given header
            uniqueStations = self._removeDuplicate(stations)
            duplicateForHeader = self._identifyDuplicate(stations)
            
            # Populate stations dictionary
            self.stations[header] = uniqueStations

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

        if self.printErrors:
            if len(duplicateHeaders):
                print("Duplicate header line(s): %s" % duplicateHeaders.keys())
            else:
                print("No duplicated header")
        
    def _removeDuplicate(self, list):
        set = {}
        for item in list:
            set[item] = 1
        return set.keys()

    def _identifyDuplicate(self, list):
        duplicate = {}
        list.sort()
        for index in range(len(list)-1):
            if list[index] == list[index+1]:
                duplicate[list[index]]=1
        return duplicate.keys()

    def printMenu(self):
        print
        print("1-Headers indexed by station")
        print("2-Stations indexed by header")
        print("3-Reprint this menu")
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
    sp = StationParser('/apps/px/etc/collection_stations.conf')
    sp.printErrors = True
    sp.parse()
    sp.printInfos()
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
            print sp.stations.get(answer, "%s is not in the table" % answer)


