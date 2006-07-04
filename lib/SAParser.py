"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: SAParser.py
#
# Author: Daniel Lemay
#
# Date: 2006-06-09
#
# Description: Use to extract stations from SA bulletins
#
#############################################################################################
"""

import sys, time
from FileParser import FileParser

class SAParser(FileParser):
    
    def __init__(self, filename, logger=None):
        FileParser.__init__(self, filename) # Stations filename ("/apps/px/etc/stations.conf")
        self.logger = logger     # Logger Object
        self.stations = {}       # Indexed by header
        self.metars = {}         # Metar headers
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

        selector = { 'CA': self.parseCA,
                     'US': self.parseUS,
                     'COLL': self.parseColl, 
                     'INT': self.parseInt
                   }
                      
        selector[self.type](lines)

    def findStationLine(self, station):
        results = (None, None,) # Station line and Header time
        try:
            #mtime = 
            file = self.openFile(self.filename)
            lines = file.readlines()
            file.close()
        except:
            (type, value, tb) = sys.exc_info()
            return

        if lines[0][:2] in ['SA', 'SP']:
            firstLineParts = lines[0].split()
            header = firstLineParts[0] + ' ' + firstLineParts[1]
            time = firstLineParts[2]

            while (lines[1] == '\n'):
                del lines[1]

            secondLineParts = lines[1].split()

            # A third line is present?
            try:
                thirdLineParts = lines[2].split()
            except:
                thirdLineParts = [False]

            try:
                if secondLineParts[0] == 'METAR' and len(secondLineParts) == 1 and thirdLineParts[0] == 'METAR':
                    del lines[1]
                elif secondLineParts[0] == 'METAR' and len(secondLineParts) == 1:
                    #print self.filename
                    lines[1] = lines[1].strip()
                    lines[1] += ' '

                elif secondLineParts[0] == 'METAR' and len(secondLineParts) == 2 and len(secondLineParts[1]) == 7:
                    # We erase line like: METAR 221600Z
                    del lines[1]
            except:
                print self.filename
                print secondLineParts
                print thirdLineParts
                raise

            #print lines
            newLines = ''.join(lines[1:]).strip().split('=')
            if newLines[-1] == '':
                del newLines[-1]
                if newLines[-1] == '': del newLines[-1]
            #print newLines

            #print self.filename
            #try:
            count =  0
            for line in newLines:
                parts = line.split()
                if parts == []: continue  # Happens when the token '==' is in the bulletin
                if station in parts and ('NIL' not in parts):
                    #print line
                    results = (line, time)
            if count >= 1: 
                print "The count is %d" % count
            return results

    def parseInt(self, lines):
        if lines[0][:2] == 'SA':
            firstLineParts = lines[0].split()
            header = firstLineParts[0] + ' ' + firstLineParts[1]
            time = firstLineParts[2]
            
            while (lines[1] == '\n'):
                del lines[1]

            secondLineParts = lines[1].split()

            # A third line is present?
            try:
                thirdLineParts = lines[2].split()
            except:
                thirdLineParts = [False]

            try:
                if secondLineParts[0] == 'METAR' and len(secondLineParts) == 1 and thirdLineParts[0] == 'METAR':
                    del lines[1]
                elif secondLineParts[0] == 'METAR' and len(secondLineParts) == 1:
                    #print self.filename
                    lines[1] = lines[1].strip()
                    lines[1] += ' '
    
                elif secondLineParts[0] == 'METAR' and len(secondLineParts) == 2 and len(secondLineParts[1]) == 7:
                    # We erase line like: METAR 221600Z
                    del lines[1]
            except:
                print self.filename
                print secondLineParts
                print thirdLineParts
                raise
            
            #print lines
            newLines = ''.join(lines[1:]).strip().split('=')
            if newLines[-1] == '': 
                del newLines[-1]
                if newLines[-1] == '': del newLines[-1]
            #print newLines
                
            #print self.filename            
            #try:

            countProblem = 0
            for line in newLines:
                #print line
                parts = line.split()
                if parts == []: continue  # Happens when the token '==' is in the bulletin
                try: 
                    if parts[0] in ['METAR', 'SPECI', 'METAR/SPECI']:
                        #print 'TUPLE: ', parts[0], parts[1]
                        if len(parts[1]) == 4:
                            # METAR FCPP ...
                            self.metars[header] = 1
                            self.stations.setdefault(header, []).append(parts[1])
                        elif parts[1] in ['SPECI', 'COR']:
                            # METAR SPECI FCPP ...
                            # METAR COR FCPP ...
                            #print parts
                            self.metars[header] = 1
                            self.stations.setdefault(header, []).append(parts[2])
                        elif parts[1] in ['NIL']:
                            # METAR\nNIL
                            # METAR NIL
                            pass
                        else:
                            # METAR XXXXXX ...
                            #print self.filename
                            #print("PROBLEM: %s" % line)
                            countProblem += 1
                    elif len(parts[0]) == 4:
                        # FCPP ... 
                        self.stations.setdefault(header, []).append(parts[0])
                    elif len(parts[0]) == 3 and parts[0] not in ['NIL', 'COR'] and parts[0].isalpha():
                        # YUL ... 
                        self.stations.setdefault(header, []).append(parts[0])
                    elif parts[0] in ['NIL']:
                        # NIL =
                        pass
                    elif parts[0] in ['COR']:
                        # COR FCPP ...
                        if len(parts[1]) == 4:
                            self.stations.setdefault(header, []).append(parts[2])
                        else:
                            print "COR CASE"
                            print self.filename
                            print("PROBLEM: %s" % line)
                            countProblem += 1
                    else:
                        #print self.filename
                        #print("PROBLEM: %s" % line)
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

    def parseCA(self, lines):
        if lines[0][:2] == 'SA':
            firstLineParts = lines[0].split()
            secondLineParts = lines[1].split()
            
            header = firstLineParts[0] + ' ' + firstLineParts[1]

            if secondLineParts[0] in ['METAR']:
                station = secondLineParts[1]
                self.metars[header] = 1
            else:
                station = secondLineParts[0]

            self.stations.setdefault(header, []).append(station)

    def parseUS(self, file):
        pass

    def parseColl(self, file):
        pass

    def printInfos(self):
        pass

if __name__ == '__main__':
    import os, sys

    """
    root = '/apps/px/db/20060522/SA/ncp1/CWAO'
    root = '/apps/px/db/20060522/SA/ukmet-bkp/AMMC'
    root = '/apps/px/db/20060522/SA/ukmet-bkp/BGSF'
    root = '/apps/px/db/20060522/SA/ukmet-bkp/BICC'
    root = '/apps/px/db/20060522/SA/ukmet-bkp/BKPR'
    proot = '/apps/px/db/20060522/SA/ukmet-bkp'
    #proot = '/apps/px/db/20060522/SA/ncp1'
    #proot = '/apps/px/db/20060522/SA/ukmetin'
    #proot = '/apps/px/db/20060523/SA/ncp2'
    proot = '/apps/px/db/20060523/SA/nws-alph'
    #proot = '/apps/px/db/20060523/SA/ukmet-bkp'
    #proot = '/apps/px/db/20060523/SA/ukmetin'
    #files = os.listdir(root)
    dirs = os.listdir(proot)
    #dirs = ['CWAO']
    #print dirs
    nbFiles = 0
    for dir in dirs:
        root = proot + '/' + dir
        #print root
        files = os.listdir(root)
        nbFiles += len(files)
        #print len(files)
        #files = ['SACN75_CWAO_232200__YXP_97124:ncp2:CWAO:SA:3:Direct:20060523220130']
        
        stationCount = 0
        sp = SAParser('')
        for file in files:
            sp.type = 'INT'
            sp.filename = root + '/' + file
            sp.parse()
        #print "Parsing finished"
        #print len(sp.stations)
    
        # Remove duplicates
        for header in sp.stations.keys():
            sp.stations[header] = sp._removeDuplicate(sp.stations[header])
    
        for header in sp.stations.keys():
            #print "%s : %s" % (header, sp.stations[header])
            stationCount += len(sp.stations[header])
        sp.stations
        headers = sp.stations.keys()
        headers.sort()
        #print headers
        #print stationCount
        metars = sp.metars.keys()
        metars.sort()
        #print metars 
    print "Number of files: %d" % nbFiles

    """
    from StationFileCreator import StationFileCreator


    root1 = '/apps/px/db/20060522/SA/'
    root2 = '/apps/px/db/20060523/SA/'

    receivers1 = os.listdir(root1)
    receivers2 = os.listdir(root2)

    print receivers1
    print receivers2

    receivers = [root1 + receiver for receiver in receivers1] + [ root2 + receiver for receiver in receivers2]

    print receivers

    nbFiles = 0
    nbStations = 0

    sp = SAParser('')
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
        sp.stations[header] = sp._removeDuplicate(sp.stations[header])
        nbStations += len(sp.stations[header])
        #print "%s : %s" % (header, sp.stations[header])
    
    print "Number of files: %d" % nbFiles
    print "Number of headers: %d" % len(sp.stations)
    print "Number of stations: %d" % nbStations

    #print sp.stations

    headers = sp.stations.keys()
    headers.sort()
    #print headers

    metars = sp.metars.keys()
    metars.sort()
    print metars 

    canadianMetars = [metar for metar in metars if metar[:4]=='SACN']
    print canadianMetars

    #sfc = StationFileCreator('/apps/px/etc/stations_SA.conf', stations=sp.stations)
