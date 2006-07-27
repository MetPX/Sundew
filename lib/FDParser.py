"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: FDParser.py
#
# Author: Daniel Lemay
#
# Date: 2006-07-12
#
# Description: Use to extract stations from FD bulletins
#
#############################################################################################
"""

import sys, os.path, time
from FileParser import FileParser

class FDParser(FileParser):
    
    def __init__(self, filename, logger=None):
        FileParser.__init__(self, filename) # Stations filename ("/apps/px/etc/stations.conf")
        self.logger = logger     # Logger Object
        self.stations = {}       # Indexed by header
        self.printErrors = True  #
        self.type = 'INT'        # Must be in ['CA', 'US', 'COLL', 'INT']
        self.stationSearched = None  # Station for which we want to find the more recent occurence

    def parse(self):
        try:
            file = self.openFile(self.filename)
            lines = file.readlines()
            file.close()
        except:
            (type, value, tb) = sys.exc_info()
            return 

        selector = { 'INT': self.parseInt,
                   }
                      
        selector[self.type](lines)


    def getFDTitle(self, theFile):
        filename = os.path.basename(theFile)
        parts = filename.split('_')
        prefix = filename[:4]

        try:
            file = open(theFile, 'r')
            lines = file.readlines()
            file.close()
        except:
            (type, value, tb) = sys.exc_info()
            print ("Type: %s, Value: %s" % (type, value))
            sys.exit()

        if prefix in ['FDCN']:
            if parts[1] == 'CWAO':
                bigTitle = ''.join(lines[1:3])
            elif parts[1] == 'KWBC':
                bigTitle = ''.join(lines[1:5])
        elif prefix in ['FDUS', 'FDAK', 'FDUE']:
            bigTitle = ''.join(lines[1:5])

        return bigTitle

    def findStationLine(self, station):
        results = (None, None,) # Station line and Header time
        bigTitle = []
        try:
            file = self.openFile(self.filename)
            lines = file.readlines()
            file.close()
        except:
            (type, value, tb) = sys.exc_info()
            return

        firstLineParts = lines[0].split()
        header = firstLineParts[0] + ' ' + firstLineParts[1]
        time = firstLineParts[2]

        del lines[:3]

        newLines = []
        lines = iter([line.strip() for line in lines])
        for line in lines:
            try:
                if line[-1].upper() == 'W':
                    newLines.append(line + '\n' + lines.next())
                else:
                    newLines.append(line)
            except IndexError:
                pass

        for line in newLines:
            parts = line.split()
            if parts == []: continue  # Happens when the token '==' is in the bulletin
            if station in parts and ('NIL' not in parts):
                #print line
                results = (line, time)
        return results

    def parseInt(self, lines):
        """
        """
        if lines[0][:2] in ['FD']:
            firstLineParts = lines[0].split()
            header = firstLineParts[0] + ' ' + firstLineParts[1]
            time = firstLineParts[2]
            
            del lines[0:3]

            countProblem = 0
            newLines = []
            lines = iter([line.strip() for line in lines])
            for line in lines:
                try:
                    if line[-1].upper() == 'W': 
                        newLines.append(line + '\n' + lines.next())   
                    else:
                        newLines.append(line)   
                except IndexError:
                    pass

            for line in newLines:
                #print repr(line)
                parts = line.split()
                if parts == []: continue  # Happens when the token '==' is in the bulletin
                try: 
                    if len(parts[0]) == 3:
                        # YEA      2210+15 1823+08 1642+02 1934-09
                        self.stations.setdefault(header, []).append(parts[0])
                    elif parts[0] in ['FT', 'DATA', 'UPPER', 'NERN', 'SERN', 'S', 'N', 'NWRN', 'SWRN', 'CANADA']:
                        #FT  3000    6000   9000    12000   18000   24000  30000  34000  39000
                        pass
                    else:
                        print self.filename
                        print("PROBLEM: %s" % line)
                        print parts
                        countProblem += 1
                        #sys.exit()
                except:
                    print newLines
                    print line
                    print parts
                    print self.filename
                    raise

            if countProblem:
                #print "Problem Count: %d" % countProblem
                pass

    def printInfos(self):
        pass

if __name__ == '__main__':
    import os, sys

    from StationFileCreator import StationFileCreator

    root1 = '/apps/px/db/20060522/FD/'
    root2 = '/apps/px/db/20060523/FD/'

    receivers1 = os.listdir(root1)
    receivers2 = os.listdir(root2)

    print receivers1
    print receivers2

    receivers = [root1 + receiver for receiver in receivers1] + [ root2 + receiver for receiver in receivers2] 

    print receivers

    nbFiles = 0
    nbStations = 0

    sp = FDParser('')
    sp.type = 'INT'

    for receiver in receivers:
        dirs = os.listdir(receiver)
        for dir in dirs:
            root = receiver + '/' + dir
            files = os.listdir(root)
            nbFiles += len(files)
            for file in files:
                sp.filename = root + '/' + file
                sp.parse()

    # Remove duplicates stations
    for header in sp.stations.keys():
        noDupStations = sp.removeDuplicate(sp.stations[header])
        noDupStations.sort()
        sp.stations[header] = noDupStations
        nbStations += len(sp.stations[header])
        #print "%s : %s" % (header, sp.stations[header])
    
    print "Number of files: %d" % nbFiles
    print "Number of headers: %d" % len(sp.stations)
    print "Number of stations: %d" % nbStations

    #print sp.stations
    headers = sp.stations.keys()
    headers.sort()
    #print headers

    sfc = StationFileCreator('/apps/px/etc/stations_FDDAN.conf', stations=sp.stations)
