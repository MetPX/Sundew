#!/usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

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

import os, os.path, sys, time, copy, pickle
import PXPaths, dateLib
from FileParser import FileParser

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

    #TODAY = '20060523'
    #YESTERDAY = '20060522'

    FD_COUNTRIES = ['can', 'usa', 'ala', 'bfr']
    FD_NUMBERS = [1, 2, 3]

    temp = dict(zip(FD_NUMBERS, ['', '', '']))
    temp = dict(zip(FD_COUNTRIES, [temp.copy() for x in range(4)]))
    FD = {'low': copy.deepcopy(temp), 'high': copy.deepcopy(temp)}

    # Note: The country is not used in the logical of the search.
    # The height (low or high) and number(1,2,3) are used.

    # Canada
    FD['low']['can'][1] = 'FDCN01 CWAO'
    FD['low']['can'][2] = 'FDCN02 CWAO'
    FD['low']['can'][3] = 'FDCN03 CWAO'
    FD['high']['can'][1] = 'FDCN1 KWBC'
    FD['high']['can'][2] = 'FDCN2 KWBC'
    FD['high']['can'][3] = 'FDCN3 KWBC'

    # Usa
    FD['low']['usa'][1] = 'FDUS11 KWBC'
    FD['low']['usa'][2] = 'FDUS13 KWBC'
    FD['low']['usa'][3] = 'FDUS15 KWBC'
    FD['high']['usa'][1] = 'FDUS8 KWBC'
    FD['high']['usa'][2] = 'FDUS9 KWBC'
    FD['high']['usa'][3] = 'FDUS10 KWBC'

    # Alaska
    FD['low']['ala'][1] = 'FDAK1 KWBC'
    FD['low']['ala'][2] = 'FDAK2 KWBC'
    FD['low']['ala'][3] = 'FDAK3 KWBC'
    #FD['high']['ala'][1] = ''
    #FD['high']['ala'][2] = ''
    #FD['high']['ala'][3] = ''

    # BFR and PWM ??
    FD['low']['bfr'][1] = 'FDUS12 KWBC'
    FD['low']['bfr'][2] = 'FDUS14 KWBC'
    FD['low']['bfr'][3] = 'FDUS16 KWBC'
    FD['high']['bfr'][1] = 'FDUE01 KWBC'
    FD['high']['bfr'][2] = 'FDUE03 KWBC'
    FD['high']['bfr'][3] = 'FDUE05 KWBC'

    LOW = []
    LOW1 = []
    LOW2 = []
    LOW3 = []
    HIGH = []
    HIGH1 = []
    HIGH2 = []
    HIGH3 = []

    for height in ['low', 'high']:
        for country in FD_COUNTRIES:
            for number in FD_NUMBERS:
                if height == 'low':
                    LOW.append(FD[height][country][number])
                    eval('LOW' + str(number)).append(FD[height][country][number])
                elif height == 'high':
                    HIGH.append(FD[height][country][number])
                    eval('HIGH' + str(number)).append(FD[height][country][number])

    for country in FD_COUNTRIES:
        exec(country + 'List= []')
        for height in ['low', 'high']:
            for number in FD_NUMBERS:
                if (FD[height][country][number]):
                    eval(country + 'List').append(FD[height][country][number])
                    #eval(country + 'List').sort()

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

        self._parseRequest()      # Will determine the request's type
        #self.printInfos()
        self._search()            # Find what we search

    def _parseRequest(self):
        words = self.request.split()
        words = [word.upper() for word in words]
            
        if len(words) < 2 or len(words) > 6:
            print "\nBad request"
        elif len(words) == 2  and 4 <= len(words[0]) <= 6 and len(words[1]) == 4:
            # ex: SACN31 CWAO
            # ex: FPCN31 CWAO
            #print "\nFully qualified header request\n"
            
            self.requestType = 1 
            self.ttaaii= words[0]
            self.tt = words[0][:2]
            self.center = words[1]
            self.header = words[0] + " " + words[1]
            if self.center[0] == 'C':
                self.country = 'CA'
            elif self.center[0] == 'K':
                self.country = 'US'
            
        elif words[0] in DBSearcher.TYPES:
            # ex: SA YUL
            # ex: SA CYUL PATQ
            #print "\nPartial header request (Type + station(s))\n"
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
        # FIXME: Must select best result from multiple machines
        if self.requestType == 1:
            # Fully qualified header request
            if self.debug: print self.ttaaii, self.center, self.country
            for date in [DBSearcher.TODAY, DBSearcher.YESTERDAY]:
                theFile = self._findFullHeader(True, self.ttaaii, self.center, self.country, date)
                if theFile:
                    print theFile
                    return
        elif self.requestType == 2:
            for station in self.stations:
                for date in [DBSearcher.TODAY, DBSearcher.YESTERDAY]:
                    #print 'DATE: %s' % date
                    if self.type == 'SA':
                        results = self._findSA([station], date)
                        if results[0][1]:
                            #self.printResults(results, self.type)
                            print 80 * '-'
                            for result in results:
                                print self.formatResult(result, self.type)
                            break
                    elif self.type in ['FC', 'FT', 'TAF']:
                        results = self._findTAF([station], date)
                        if results[0][1]:
                            #self.printResults(results, self.type)
                            print 80 * '-'
                            for result in results:
                                print self.formatResult(result, self.type)
                            break

                    elif self.type in ['FD', 'FD1', 'FD2', 'FD3']:
                        results = self._findFD([station], self.type, date)
                        if results[0][1]:
                            #self.printResults(results)
                            print 80 * '-'
                            for result in results:
                                print self.formatResult(result, self.type)
                            break

        #file = open(PXPaths.REQUEST_REPLY + 'results.pickle', 'w')
        #pickle.dump(results, file)
        #file.close()

    def _getFilesToParse(self, root, headers):
        """
        Given a root path (ex: PXPaths.DB + date + '/SA/') and a list of 
        headers (ex: ['SAAK31 KWBC', 'SAAK41 KNKA', 'SAUS20 KNKA', 'SAUS70 KWBC']),
        find the list of files matching these criterias.
        """

        filesToParse = [] 
        
        if headers == ['']:
            pass
        else:
            centers = FileParser.removeDuplicate([header.split()[1] for header in headers])
    
            # Request SA PATQ 
            # => headers = ['SAAK31 KWBC', 'SAAK41 KNKA', 'SAUS20 KNKA', 'SAUS70 KWBC']
            # => ttaaiis = {'KNKA': ['SAAK41', 'SAUS20'], 'KWBC': ['SAAK31', 'SAUS70']}
            ttaaiis = {}    
            for header in headers:
               ttaaiis.setdefault(header.split()[1], []).append(header.split()[0])
    
            try:
                sources = os.listdir(root)
            except:
                (type, value, tb) = sys.exc_info()
                print("Type: %s, Value: %s" % (type, value))
                return filesToParse
    
            #print("Headers: %s" % headers)
            #print("ttaaiis: %s" % ttaaiis)
            #print("centers: %s" % centers)
            #print("sources: %s\n" % sources)
    
            for source in sources:
                for center in centers:    
                    pathToCenter = root + source + '/' + center
                    try:
                        for file in os.listdir(pathToCenter):
                            for ttaaii in ttaaiis[center]:
                                if file[:len(ttaaii)] == ttaaii:
                                    filesToParse.append(pathToCenter + '/' + file)
                                    break
                    except:
                        (type, value, tb) = sys.exc_info()
                        if self.debug: print("Type: %s, Value: %s" % (type, value))
                        continue
    
            #print ("len(filesToParse) = %d\n" % len(filesToParse))

        return filesToParse

    def _findFD(self, stations, fdtype, date=TODAY):
        from StationParser import StationParser
        from FDParser import FDParser

        results = [] # ex: [('CYOW', FD_LINE, FD_HEADER_TIME, FD_FILE, FD_FILE_TIME), ('CYUL', ...)]

        sp = StationParser(PXPaths.ETC + 'stations_FD.conf')
        sp.parse()

        if fdtype in ['FD1', 'FD2', 'FD3']:
            number = fdtype[-1]
        else:
            number = '' 

        for station in stations:
            headers = sp.headers.get(station, [])
            headers.sort()

            lowHeaders = []
            highHeaders = []

            for header in headers:
                if header in eval('DBSearcher.LOW' + number):
                    lowHeaders.append(header)
                elif header in eval('DBSearcher.HIGH' + number):
                    highHeaders.append(header)

            for header in lowHeaders + highHeaders:
                filesToParse = self._getFilesToParse(PXPaths.DB + date + '/FD/', [header])
                #print("In findFD, len(filesToParse) = %d" % len(filesToParse))
                theLine, bestHeaderTime, theFile, bestFileTime = self._findMoreRecentStation(FDParser(''), filesToParse, station)
                if theLine:
                    bigTitle = FDParser('').getFDTitle(theFile)
                    #print("BIG TITLE: \n%s" % bigTitle)
                    #print theFile
                    #print "theLine: %s" % theLine
                    theLine = bigTitle + theLine

                results.append((station, theLine, bestHeaderTime, theFile, bestFileTime))

            if lowHeaders == highHeaders == []:
                results.append((station, None, 0, None, 0))

        return results

    def _findTAF(self, stations, date=TODAY):
        from StationParser import StationParser
        from TAFParser import TAFParser

        results = [] # ex: [('CYOW', TAF_LINE, TAF_HEADER_TIME, TAF_FILE, TAF_FILE_TIME), ('CYUL', ...)]

        sp = StationParser(PXPaths.ETC + 'stations_TAF.conf')
        sp.parse()

        for station in stations:
            headers = sp.headers.get(station, [])
            filesToParse = self._getFilesToParse(PXPaths.DB + date + '/FC/', headers)
            filesToParse.extend(self._getFilesToParse(PXPaths.DB + date + '/FT/', headers))
            #print("In findTAF, len(filesToParse) = %d" % len(filesToParse))
            theLine, bestHeaderTime, theFile, bestFileTime = self._findMoreRecentStation(TAFParser(''), filesToParse, station)

            if theLine:
                theLine += '='

            results.append((station, theLine, bestHeaderTime, theFile, bestFileTime))

        return results

    def _findSA(self, stations, date=TODAY):
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

        for station in stations:
            threeCharHeaders = []

            if len(station) == 3:
                #print ("%s => we will search for %s first, if we obtain no results, we will search for %s" % (station, 'C' + station, station))
                threeCharHeaders = sp.headers.get(station, [])
                station = 'C' + station
                headers = sp.headers.get(station, [])
                
            elif station[0] == 'C':
                #print("%s is a canadian station" % station)
                headers = sp.headers.get(station, []) 

            elif station[0] == 'K':
                #print("%s is an american station" % station)
                headers = sp.headers.get(station, [])

            else:
                #print("%s is an international station" % station)
                headers = sp.headers.get(station, [])

            filesToParse = self._getFilesToParse(PXPaths.DB + date + '/SA/', headers)
            theLine, bestHeaderTime, theFile, bestFileTime = self._findMoreRecentStation(SAParser(''), filesToParse, station)

            if not theLine and threeCharHeaders:
                # If not successful at finding the 4 chars station when the original request was for a 3 chars station
                # we try the 3 chars case
                print 'We are searching for the 3 chars station'
                station = station[1:]
                filesToParse = self._getFilesToParse(PXPaths.DB + date + '/SA/', threeCharHeaders)
                theLine, bestHeaderTime, theFile, bestFileTime = self._findMoreRecentStation(SAParser(''), filesToParse, station)

            if theLine:
                theLine += '='
                parts = os.path.basename(theFile).split('_')
                header = parts[0] + ' ' + parts[1]
                speciLine, speciHeaderTime, speciFile, speciFileTime = self._findSpeci(station, header, bestHeaderTime, date)

                if speciHeaderTime and (speciHeaderTime < bestHeaderTime):
                    surround = 30*'=' 
                    #print 'Speci found has been rejected (%s < %s)' % (speciHeaderTime, bestHeaderTime)
                    speciLine, speciHeaderTime, speciFile, speciFileTime = None, 0, None, 0
                    #print "%s END SPECI INFOS %s\n" % (surround, surround)

            else:
                speciLine, speciHeaderTime, speciFile, speciFileTime = None, 0, None, 0

            results.append((station, theLine, bestHeaderTime, theFile, bestFileTime, speciLine, speciHeaderTime, speciFile, speciFileTime))

        return results

    def formatResult(self, result, type):
        saResult = ''
        speciResult = ''

        if type == 'SA':
            station, theLine, bestHeaderTime, theFile, bestFileTime, speciLine, speciHeaderTime, speciFile, speciFileTime = result
        else:
            station, theLine, bestHeaderTime, theFile, bestFileTime = result
        
        if theFile:
            parts = os.path.basename(theFile).split('_')
            header = parts[0] + ' ' + parts[1]
            saResult = header + ' ' + bestHeaderTime + '\n' + theLine.strip() + '\n'
            #print repr(theLine)
            if type == 'SA' and speciLine:
                speciHeader = header[0] + 'P' + header[2:]
                speciResult = speciHeader + ' ' + speciHeaderTime + '\n' + speciLine.strip() + '\n\n'

        banner = 80 * '-'
        return speciResult + saResult + banner

    def printResults(self, results, type=None):
        print "%s RESULTS %s" % (30*'=', 30*'=')
        for result in results:
            if type == 'SA':
                station, theLine, bestHeaderTime, theFile, bestFileTime, speciLine, speciHeaderTime, speciFile, speciFileTime = result
            else:
                station, theLine, bestHeaderTime, theFile, bestFileTime = result
            
            print "Station: %s" % station
            print "Line:\n%s" % theLine
            print "HeaderTime: %s" % bestHeaderTime
            print "File: %s" % theFile
            print "FileTime: %s" % bestFileTime

            if type == 'SA':
                print "SP_Line: %s" % speciLine
                print "SP_HeaderTime: %s" % speciHeaderTime
                print "SP_File: %s" % speciFile
                print "SP_FileTime: %s" % speciFileTime

            print "\n"

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

        """
        surround = 30*'=' 
        print "%s SPECI INFOS %s" % (surround, surround)
        print "Number of files: %d" % len(filesToParse)
        print "Station: %s" % station
        print "Header: %s" % header
        print "Time: %s" % headerTime
        print "ttaaii: %s" % ttaaii
        print "center: %s" % center
        print "Now: %s\n" % now
        print "%s%s%s" % (surround, len(' SPECI INFOS ') * '=', surround)
        """
        
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
        

    def _findFullHeader(self, unique=True, ttaaii='SACN31', center='CWAO', country='CA', date=TODAY):
        self.theFile = None           # The filename of the more recent header in a full qualified header search
        self.bestFileTime = 0         # More recent file
        self.bestHeaderTime = 0       # More recent header

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

    """
    for country in DBSearcher.FD_COUNTRIES:
        print '%s = %s' % (country, eval('DBSearcher.' + country + 'List'))
        #print DBSearcher.FD['low'][country][1]

    for height in ['LOW', 'HIGH']:
        for i in ['', '1', '2', '3']:
            print("%s%s = %s" % (height, i, eval('DBSearcher.' + height + i)))

    """
