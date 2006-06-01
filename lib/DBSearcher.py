"""
#############################################################################################
# Name: DBSearcher.py
#
# Author: Daniel Lemay 
#
# Date: 2006-06-01
#
# Description: Use to search bulletins in the sundew database
#
#############################################################################################
"""

import os, os.path, sys, re
import PXPaths, dateLib
from StationParser import StationParser

class DBSearcher:
    """
    If we don't find what is requested in the current day of the DB, we will check in the previous.

    """
    PXPaths.normalPaths()
    
    TYPES = ['SA', 'FC', 'FT', 'TAF', 'FD', 'FD1', 'FD2', 'FD3'] # bulletin's type
    COUNTRIES = ['CA', 'US']
    INTERNATIONAL_SOURCES = ['nws-alpha', 'ukmetin', 'ukmet-bkp']   # sundew international sources
    CANADIAN_SOURCES = ['cmcin', 'ncp1', 'ncp2']                    # sundew canadian sources 
    TODAY = dateLib.getTodayFormatted()
    YESTERDAY = dateLib.getYesterdayFormatted()

    def __init__(self, request):
        
        self.request = request    # Request before being parsed
        self.requestType = None   # 1 for fully qualified header, 2 for type + station(s)

        # Ex. of a fully qualified header request: FPCN11 CWTO
        self.ttaaii = None        # First word of a fully qualified header 
        self.tt = None            # Type extract from ttaaii
        self.center = None        # Second word of a fully qualified header
        self.header = None        # Fully qualified header (ex: "FPCN11 CWTO")
        self.country = None       # Country is obtained from the center

        # Ex. of a type + station(s) request: SA YUL YQB YZV
        self.type = None          # Must be in TYPES
        self.stations = []        # Between 1 and 5 stations 
        self.stationParser = None # Used to map a station to a fully qualified header
        self.debug = False

    def findFromStation(self):
        pass

    def _findFullHeader(self, ttaaii='SACN31', center='CWAO', country='CA', date=TODAY):
        try:
            iterator = os.walk(PXPaths.DB + date)
            path, dirs, files =  iterator.next()
            if self.debug: print path, dirs, files
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value))
            print("The request (%s) has been stopped at the date (%s) level" % (self.request, date))
            sys.exit()

        # We select only the "tt" directory
        for dir in dirs[:]:
            if dir != ttaaii[:2]:
                dirs.remove(dir)

        # We select the "sources" if possible (CAN or US)
        # This is considered an optimization. We should be 
        # able to turn this off
        try:
            pathBeforeSource, dirs, files = iterator.next()
            if self.debug: print path, dirs, files
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value))
            print("The request (%s) has been stopped at the source(s) level" % (self.request))
            sys.exit()

        if country=='CA':
            for dir in dirs[:]:
                if dir in DBSearcher.INTERNATIONAL_SOURCES:
                    dirs.remove(dir)
            dirs.sort()
        elif country=='US':
            for dir in dirs[:]:
                if dir in DBSearcher.CANADIAN_SOURCES:
                    dirs.remove(dir)
            dirs.sort()
 
        theFile = None  # The file we search
        youngest = 0    # Youngest to date (in secs since Epoch)

        for source in dirs:
            iterator = os.walk(pathBeforeSource + "/" + source)
            # We select only the "center" directory
            try:
                path, dirs, files = iterator.next()
                if self.debug: print path, dirs, files
            except:
                (type, value, tb) = sys.exc_info()
                if self.debug:
                    print("Type: %s, Value: %s" % (type, value))
                    print("The request (%s) has been stopped at the center (%s) level for the source %s" % (self.request, center, source))
                continue

            for dir in dirs[:]:
                if dir != center:
                    dirs.remove(dir)

            #print "Dirs: %s" % dirs

            # We select the "good bulletins"
            try:
                path, dirs, files = iterator.next()
                if self.debug > 10: print path, dirs, files
            except:
                (type, value, tb) = sys.exc_info()
                if self.debug:
                    print("Type: %s, Value: %s" % (type, value))
                    print("The request (%s) has been stopped at the ttaaii (%s) level for the source %s and the center %s" % (self.request, ttaaii, source, center))
                continue

            length = len(ttaaii)
            goodFiles = [path + '/' + file for file in files if file[:length] == ttaaii]

            """
            if len(goodFiles):
                for file in goodFiles:
                    print file
                print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
            else:
                print"No good files for source %s and center %s" % (source, center)
            """

            # We select the more recent bulletin (theFile)
            for file in goodFiles:
                mtime = os.path.getmtime(file)
                if mtime > youngest:
                    youngest = mtime
                    theFile = file

        return theFile

    def search(self):
        if self.requestType == 1:
            # Fully qualified header request
            if self.debug: print self.ttaaii, self.center, self.country
            print self._findFullHeader(self.ttaaii, self.center, self.country, '20060522')

        elif self.type == 'SA':
            # Partial header request (Type + station(s))
            for station in self.stations:
                if len(station) == 3:
                    print("We will try to finder the header for stations %s or %s" % ('C' + station.upper() , station.upper()))
                elif station[0].upper() == 'C':
                    print("%s is a canadian station" % station)
                elif station[0].upper() == 'K':
                    print("%s is an american station" % station)
                else:
                    print("%s is an unknown station (means we will have to parse bulletins in the DB)" % station)
                   
    def printInfos(self):
        print("Request: %s" % self.request)
        print("Request Type: %s" % self.requestType)
        print("Header: %s" % self.header)
        print("tt: %s" % self.tt)
        print("Centre: %s" % self.center)
        print("Type: %s" % self.type)
        print("Stations: %s" % self.stations)
        print("Country: %s" % self.country)

    def _validateStation(self, station):
        return 3 <= len(station) <= 4
        
    def parseRequest(self):
        words = self.request.split()
        if len(words) < 2 or len(words) > 6:
            print "Bad request"
        elif len(words) == 2  and 4 <= len(words[0]) <= 6 and len(words[1]) == 4:
            print "Fully qualified header request"
            self.requestType = 1 
            self.ttaaii= words[0]
            self.tt = words[0][:2]
            self.center = words[1]
            self.header = words[0] + " " + words[1]
            if self.center[0].upper() == 'C':
                self.country = 'CA'
            elif self.center[0].upper() == 'K':
                self.country = 'US'
            
        elif words[0] in DBSearcher.TYPES:
            print "Partial header request (Type + station(s))"
            self.requestType = 2 
            self.type = words[0]
            for station in words[1:]:
                if self._validateStation(station):
                    self.stations.append(station)
                else:
                    print("%s is not a valid station name" % station)
        else:
            print "Bad request even if the word's number is good"

if __name__ == '__main__':
    import sys
    sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')
    #from Logger import *

    #logger = Logger('/apps/px/log/DBSearcher.log', 'DEBUG', 'DBS')
    #logger = logger.getLogger()

    request = ' '.join(sys.argv[1:])

    dbs = DBSearcher(request)
    dbs.parseRequest()
    #dbs.printInfos()
    dbs.search()
