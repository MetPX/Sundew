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

import os, os.path, sys, time
import PXPaths, dateLib

class DBSearcher:
    """
    If we don't find what is requested in the current day of the DB, we will check in the previous.

    """
    PXPaths.normalPaths()
    
    TYPES = ['SA', 'FC', 'FT', 'TAF', 'FD', 'FD1', 'FD2', 'FD3']    # bulletin's type for which a specialized search exists
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
        self.country = None       # Country is obtained from the center (Only used for CA and US)

        # Ex. of a type + station(s) request: SA YUL YQB YZV
        self.type = None          # Must be in TYPES
        self.stations = []        # Between 1 and 5 stations 
        self.stationParser = None # Used to map a station to a fully qualified header
        self.debug = False

        self._initResults()       # See the method

        self._parseRequest()      # Will determine the request's type
        #self..printInfos()
        self._search()            # Find what we search

    def _initResults(self):
        self.theFile = None           # The filename of the more recent header in a full qualified header search
        self.theLine = None           # The more recent line for a given station in a type+station search

        self.bestFileTime = 0         # More recent file
        self.bestHeaderTime = 0       # More recent header

    def _parseRequest(self):
        words = self.request.split()
        if len(words) < 2 or len(words) > 6:
            print "\nBad request"
        elif len(words) == 2  and 4 <= len(words[0]) <= 6 and len(words[1]) == 4:
            # ex: SACN31 CWAO
            # ex: FPCN31 CWAO
            print "\nFully qualified header request\n"
            
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
            # ex: SA YUL
            # ex: SA CYUL PATQ
            print "\nPartial header request (Type + station(s))\n"
            self.requestType = 2 
            self.type = words[0]
            for station in words[1:]:
                if self._validateStation(station):
                    self.stations.append(station)
                else:
                    print("%s is not a valid station name" % station)
        else:
            print "\nBad request even if the word's number is good"

    def _search(self):
        if self.requestType == 1:
            # Fully qualified header request
            if self.debug: print self.ttaaii, self.center, self.country
            print self._findFullHeader(True, self.ttaaii, self.center, self.country, '20060522')

        elif self.type == 'SA':
            results = self._findSA('20060522')
            self.printSAResults(results)

        # Under construction
        elif self.type in ['FC', 'FT', 'TAF']:
            results = self._findTAF('20060522')
            self.printTAFResults(results)

        # Under construction
        elif self.type in ['FD', 'FD1', 'FD2', 'FD3']:
            results = self._findFD('20060522')
            self.printFDResults(results)

    def _findSA(self, date=TODAY):
        # Partial header request (Type + station(s))
        # ex: SA CYOW CYUL
        # Note: Once we find the better match, we take the header we found (ex: SACN31 CWAO) and we replace the 
        # A by a P (ex: SPCN31 CWAO) and try to find a speci for the station. The speci must be between the full 
        # hour of the SA and the request time.
        from StationParser import StationParser
        from SAParser import SAParser

        results = [] # ex: [('CYOW', SA_LINE, SA_HEADER_TIME, SA_FILE, SA_FILE_TIME, SP_LINE, SP_HEADER_TIME, SP_FILE, SP_FILE_TIME), ('CYUL', ...)]

        sp = StationParser(PXPaths.ETC + 'stations_SA.conf')
        sp.parse()

        for station in self.stations:
            filesToParse = []

            if len(station) == 3:
                #print("We will try to find the header for stations %s or %s" % ('C' + station.upper() , station.upper()))
                #headers = sp.headers.get('C' + station.upper(), [])  + sp.headers.get(station, [])

                print ("%s => we will search for %s" % (station.upper(), 'C' + station.upper()))
                station = 'C' + station.upper()
                headers = sp.headers.get(station, []) 
                
            elif station[0].upper() == 'C':
                print("%s is a canadian station" % station)
                headers = sp.headers.get(station, []) 

            elif station[0].upper() == 'K':
                print("%s is an american station" % station)
                headers = sp.headers.get(station, [])

            else:
                print("%s is an international station" % station)
                headers = sp.headers.get(station, [])

            # Request SA PATQ 
            # => headers = ['SAAK31 KWBC', 'SAAK41 KNKA', 'SAUS20 KNKA', 'SAUS70 KWBC']
            # => ttaaiis = {'KNKA': ['SAAK41', 'SAUS20'], 'KWBC': ['SAAK31', 'SAUS70']}
            ttaaiis = {}    
            for header in headers:
               ttaaiis.setdefault(header.split()[1], []).append(header.split()[0])

            centers = sp._removeDuplicate([header.split()[1] for header in headers])

            root = PXPaths.DB + date + '/SA/'

            try:
                sources = os.listdir(root)
            except:
                (type, value, tb) = sys.exc_info()
                print("Type: %s, Value: %s" % (type, value))
                sys.exit()

            print("Headers: %s" % headers)
            print("ttaaiis: %s" % ttaaiis)
            print("centers: %s" % centers)
            print("sources: %s\n" % sources)

            for source in sources:
                for center in centers:    
                    pathToCenter = root + source + '/' + center
                    try:
                        for file in os.listdir(pathToCenter):
                            for ttaaii in ttaaiis[center]:
                                if file[:len(ttaaii)] == ttaaii:
                                    filesToParse.append(pathToCenter + '/' + file)
                                    break

                        #files = [pathToCenter + '/' + file for file in  os.listdir(pathToCenter) if file[:6] in ttaaiis]
                        #print "Number of files for %s: %i" % (center, len(files))
                    except:
                        (type, value, tb) = sys.exc_info()
                        if self.debug: print("Type: %s, Value: %s" % (type, value))
                        continue

            print ("len(filesToParse) = %d\n" % len(filesToParse))
            
            theLine, bestHeaderTime, theFile, bestFileTime = self._findMoreRecentStation(SAParser(''), filesToParse, station)
            
            if theLine:
                theLine += '='
                parts = os.path.basename(theFile).split('_')
                header = parts[0] + ' ' + parts[1]
                speciLine, speciHeaderTime, speciFile, speciFileTime = self._findSpeci(station, header, bestHeaderTime, date)

                if speciHeaderTime and (speciHeaderTime < bestHeaderTime):
                    surround = 30*'=' 
                    print 'Speci found has been rejected (%s < %s)' % (speciHeaderTime, bestHeaderTime)
                    speciLine, speciHeaderTime, speciFile, speciFileTime = None, 0, None, 0
                    print "%s END SPECI INFOS %s\n" % (surround, surround)


            else:
                speciLine, speciHeaderTime, speciFile, speciFileTime = None, 0, None, 0

            results.append((station, theLine, bestHeaderTime, theFile, bestFileTime, speciLine, speciHeaderTime, speciFile, speciFileTime))

        return results

    def printSAResults(self, results):
        print "%s RESULTS %s" % (30*'=', 30*'=')
        for result in results:
            station, theLine, bestHeaderTime, theFile, bestFileTime, speciLine, speciHeaderTime, speciFile, speciFileTime = result
            print "Station: %s" % station
            print "SA_Line: %s" % theLine
            print "SA_HeaderTime: %s" % bestHeaderTime
            print "SA_File: %s" % theFile
            print "SA_FileTime: %s" % bestFileTime
            print "SP_Line: %s" % speciLine
            print "SP_HeaderTime: %s" % speciHeaderTime
            print "SP_File: %s" % speciFile
            print "SP_FileTime: %s" % speciFileTime
            print "\n"

    def printTAFResults(self, results):
        pass

    def printFDResults(self, results):
        pass

    def _findSpeci(self, station, header, headerTime, DBDate):
        from SAParser import SAParser

        now = time.mktime(time.gmtime())
        ttaaii, center = header.split()
        ttaaii = ttaaii[0] + 'P' + ttaaii[2:]

        filesToParse = self._findFullHeader(False, ttaaii, center, 'INT',  DBDate)

        theLine, bestHeaderTime, theFile, bestFileTime = self._findMoreRecentStation(SAParser(''), filesToParse, station)

        if theLine:
            theLine += '='

        #for file in files:
        #    print file

        surround = 30*'=' 
        print "%s SPECI INFOS %s" % (surround, surround)
        print "Number of files: %d" % len(filesToParse)
        print "Station: %s" % station
        print "Header: %s" % header
        print "Time: %s" % headerTime
        print "ttaaii: %s" % ttaaii
        print "center: %s" % center
        print "Now: %s\n" % now
        
        return (theLine, bestHeaderTime, theFile, bestFileTime)

    def _findMoreRecentStation(self, parser, files, station, startDate=None):
        bestHeaderTime = 0
        bestFileTime = 0
        theLine = None
        theFile = None

        for file in files:
            parser.filename = file
            stationLine, headerTime = parser.findStationLine(station)
            if headerTime > bestHeaderTime:
                bestHeaderTime = headerTime
                bestFileTime = os.path.getmtime(file)
                theLine = stationLine
                theFile = file
            elif headerTime == bestHeaderTime:
                if os.path.getmtime(file) > bestFileTime:
                    bestFileTime = os.path.getmtime(file)
                    theLine = stationLine
                    theFile = file

        return (theLine, bestHeaderTime, theFile, bestFileTime)
        
    def _findTAF(self):
        pass

    def _findFD(self):
        pass

    def _findFullHeader(self, unique=True, ttaaii='SACN31', center='CWAO', country='CA', date=TODAY):
        self._initResults()
        allGoodFiles = []
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
            if self.debug: print pathBeforeSource, dirs, files
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

            #self._findMoreRecentFile(goodFiles)
            if unique:
                self._findMoreRecentHeader(goodFiles)
            else:
                allGoodFiles.extend(goodFiles)
        
        if unique:
            return self.theFile
        else:
            return allGoodFiles

    def _findMoreRecentFile(self, files):
        """
        The search is based on the time when the file was written on disk
        """
        for file in files:
            mtime = os.path.getmtime(file)
            if mtime > self.bestFileTime:
                self.bestFileTime = mtime
                self.theFile = file

    def _findMoreRecentHeader(self, files):
        """
        The search is based on the time when the header was written in the bulletin 
        and in case of equality, the time when the file was written on disk
        """
        for file in files:
            try:
                handle = open(file, 'r')
            except:
                (type, value, tb) = sys.exc_info()
                print("Type: %s, Value: %s" % (type, value))
                print("Cannot open %s" % file)
                continue

            parts = handle.readline().split()
            if len(parts) < 3:
                print("Not enough parts (%s)  in the header" % parts)
                continue

            elif len(parts[2]) == 7:
                if parts[2][:6].isdigit() and parts[2][-1].upper() == 'Z':
                    pass
                else:
                   print("(CASE 1)Third part is not a valid time (%s)" % parts)
                   continue

            elif len(parts[2]) == 6:
                if parts[2][:6].isdigit():
                    pass
                else:
                   print("(CASE 2)Third part is not a valid time (%s)" % parts)
                   continue
            else:
                print("(CASE 3)Third part is not a valid time (%s)" % parts)
                continue

            ddhhmm = parts[2][:6]

            if ddhhmm > self.bestHeaderTime:
                self.theFile = file
                self.bestFileTime = os.path.getmtime(file)
                self.bestHeaderTime = ddhhmm

            elif ddhhmm == self.bestHeaderTime:
                mtime = os.path.getmtime(file)
                if mtime > self.bestFileTime: 
                    self.theFile = file
                    self.bestFileTime = mtime
                    self.bestHeaderTime = ddhhmm

            handle.close()

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
        

if __name__ == '__main__':
    import sys
    sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')
    #from Logger import *

    #logger = Logger('/apps/px/log/DBSearcher.log', 'DEBUG', 'DBS')
    #logger = logger.getLogger()

    request = ' '.join(sys.argv[1:])
    dbs = DBSearcher(request)
