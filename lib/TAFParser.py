#!/usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: TAFParser.py
#
# Author: Daniel Lemay
#
# Date: 2006-07-10
#
# Description: Use to extract stations from TAF (FT/FC) bulletins
#
#############################################################################################
"""
import sys, time

# default library path

# old way
sys.path.insert(1, '/apps/px/lib/importedLibs')
sys.path.insert(1, '/apps/px/lib')

# debian way
sys.path.insert(1, '/usr/lib/px/importedLibs')
sys.path.insert(1, '/usr/lib/px')

# developpement library path option through PXLIB

try:
    pxlib = os.path.normpath(os.environ['PXLIB'])
    sys.path.insert(1, pxlib + '/importedLibs')
    sys.path.insert(1, pxlib )
except :
         pass

# developpement library path option through PXROOT
try:
    pxroot = os.path.normpath(os.environ['PXROOT'])
    sys.path.insert(1, pxroot + '/lib/importedLibs')
    sys.path.insert(1, pxroot + '/lib')
except :
    pass


import PXPaths
from FileParser import FileParser
from Logger import Logger

PXPaths.normalPaths()

class TAFParser(FileParser):
    
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

    def findStationLine(self, station):
        results = (None, None,) # Station line and Header time
        try:
            file = self.openFile(self.filename)
            lines = file.readlines()
            file.close()
        except:
            (type, value, tb) = sys.exc_info()
            return

        if lines[0][:2] in ['FC', 'FT']:
            firstLineParts = lines[0].split()
            header = firstLineParts[0] + ' ' + firstLineParts[1]
            time = firstLineParts[2]

            while (lines[1] == '\n'):
                del lines[1]

            secondLineParts = lines[1].split()

            if secondLineParts[0] in ['TAF', 'TAFPQ', 'NIL', 'NIL='] and len(secondLineParts) == 1:
                del lines[1]

            newLines = ''.join(lines[1:]).strip().split('=')

            try:
                if newLines[-1] == '': 
                    del newLines[-1]
                    if newLines[-1] == '': del newLines[-1]
            except IndexError:
                (type, value, tb) = sys.exc_info()
                #print("Type: %s, Value: %s" % (type, value))

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
        if lines[0][:2] in ['FC', 'FT']:
            firstLineParts = lines[0].split()
            header = firstLineParts[0] + ' ' + firstLineParts[1]
            time = firstLineParts[2]
            
            while (lines[1] == '\n'):
                del lines[1]

            secondLineParts = lines[1].split()

            if secondLineParts[0] in ['TAF', 'TAFPQ', 'NIL', 'NIL='] and len(secondLineParts) == 1:
                del lines[1]

            newLines = ''.join(lines[1:]).strip().split('=')
            try:
                if newLines[-1] == '': 
                    del newLines[-1]
                    if newLines[-1] == '': del newLines[-1]
            except IndexError:
                (type, value, tb) = sys.exc_info()
                #print("Type: %s, Value: %s" % (type, value))

            #print newLines
                
            countProblem = 0
            for line in newLines:
                #print line
                parts = line.split()
                if parts == []: continue  # Happens when the token '==' is in the bulletin
                try: 
                    if len(parts[0]) == 4:
                        # LTBI 231340Z 231524 VRB02KT CAVOK=
                        self.stations.setdefault(header, []).append(parts[0])
                    elif parts[0] in ['TAF']:
                        if len(parts[1]) == 4:
                            # TAF CYBG 231550Z ... 
                            self.stations.setdefault(header, []).append(parts[1])
                        elif parts[1] in ['AMD', 'COR']:
                            if len(parts[2]) == 4:
                                # TAF AMD CYBG 231550Z ...
                                self.stations.setdefault(header, []).append(parts[2])
                            else:
                                if self.printErrors:
                                    print self.filename
                                    print("PROBLEM: %s" % line)
                                countProblem += 1
                        else:
                            if self.printErrors:
                                print self.filename
                                print("PROBLEM: %s" % line)
                            countProblem += 1
                    elif parts[0] in ['3D', '?', '20', 'CHECK', '//END', 'END....', 'MF']:
                        pass
                                
                    else:
                        if self.printErrors:
                            print self.filename
                            print("PROBLEM: %s" % line)
                            print parts
                        countProblem += 1
                        #sys.exit()
                except:
                    if self.logger:
                        self.logger.debug(newLines)
                        self.logger.debug(line)
                        self.logger.debug(parts)
                        self.logger.error("An error occurs in %s" % self.filename)
                    else:
                        print newLines
                        print line
                        print parts
                        print("An error occurs in %s" % self.filename)
                    break

            if countProblem:
                pass
                #print "Problem Count: %d" % countProblem
                #if self.logger:
                    #self.logger.info("%d problem(s) for %s" % (countProblem, self.filename))

    def printInfos(self):
        pass

if __name__ == '__main__':
    """
    A cron call this to create etc/stations_TAF.conf
    """

    import os, sys
    import PXPaths, dateLib
    from StationFileCreator import StationFileCreator

    #root1 = '/apps/px/db/20060522/FC/'
    #root2 = '/apps/px/db/20060522/FT/'
    #root3 = '/apps/px/db/20060523/FC/'
    #root4 = '/apps/px/db/20060523/FT/'

    PXPaths.normalPaths()

    root1 = PXPaths.DB + '%s/FC/' % dateLib.getYesterdayFormatted() 
    root2 = PXPaths.DB + '%s/FT/' % dateLib.getYesterdayFormatted()
    root3 = PXPaths.DB + '%s/FC/' % dateLib.getTodayFormatted()
    root4 = PXPaths.DB + '%s/FT/' % dateLib.getTodayFormatted()

    try:
        receivers1 = os.listdir(root1)
    except OSError:
        receivers1 = []

    try:
        receivers2 = os.listdir(root2)
    except OSError:
        receivers2 = []

    try:
        receivers3 = os.listdir(root3)
    except OSError:
        receivers3 = []

    try:
        receivers4 = os.listdir(root4)
    except OSError:
        receivers4 = []

    #print receivers1
    #print receivers2
    #print receivers3
    #print receivers4

    receivers = [root1 + receiver for receiver in receivers1] + [ root2 + receiver for receiver in receivers2] + [ root3 + receiver for receiver in receivers3] + [ root4 + receiver for receiver in receivers4]

    #print receivers

    nbFiles = 0
    nbStations = 0

    logger = Logger(PXPaths.LOG + 'TAFParser.log', 'DEBUG', 'TAFP') 
    logger = logger.getLogger()
    logger.info("StartTAF parsing")

    sp = TAFParser('', logger)
    sp.printErrors = False
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
    
    """
    print "Number of files: %d" % nbFiles
    print "Number of headers: %d" % len(sp.stations)
    print "Number of stations: %d" % nbStations

    print sp.stations
    headers = sp.stations.keys()
    headers.sort()
    print headers
    """

    sfc = StationFileCreator(PXPaths.ETC + 'stations_TAF.conf', stations=sp.stations)
    logger.info("Number of files: %d" % nbFiles)
    logger.info("Number of headers: %d" % len(sp.stations))
    logger.info("Number of stations: %d" % nbStations)
    logger.info(PXPaths.ETC + "stations_TAF.conf has been created")
