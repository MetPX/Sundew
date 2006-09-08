"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: SearchObject.py
#
# Author: Dominik Douville-Belanger
#
# Description: Class containing the information needed in
#              order to perform a search.
#
# Date: 2006-05-15
#
###########################################################
"""

import sys
import time

# Local imports
sys.path.insert(1,sys.path[0] + '/../')
import PXPaths; PXPaths.normalPaths()

class SearchObject(object):
    __slots__ = ["headerRegexes", "searchRegex", "searchType", "names", "logPath", "since", "fromdate", "todate", "timesort", "ftp", "alphanumericRegex", "digitRegex", "zeroOrMoreRegex", "oneOrMoreRegex"]

    def __init__(self):
        self.headerRegexes = {}
        self.searchRegex = ""
        self.searchType = ""
        self.names = ['*']
        self.logPath = ""
        self.since = 0
        self.fromdate = "epoch"
        self.todate = "now"
        self.timesort = False
        self.ftp = False
        
        # These are the default wildcard regexes used throughout the whole program.
        self.alphanumericRegex = "[.[:alnum:]-]"
        self.digitRegex = "[[:digit:]]"
        self.zeroOrMoreRegex = "*"
        self.oneOrMoreRegex = "+"
        
        self.fillHeaderRegexes()

    def fillHeaderRegexes(self):
        alphanumeric = self.getAlphanumericRegex()
        digit = self.getDigitRegex()
        zeroOrMore = self.getZeroOrMoreRegex()
        oneOrMore = self.getOneOrMoreRegex()
        
        self.headerRegexes["ttaaii"] = alphanumeric + oneOrMore
        self.headerRegexes["ccccxx"] = alphanumeric + oneOrMore
        self.headerRegexes["ddhhmm"] = digit + "{6}" # Repeats exactly six times
        self.headerRegexes["bbb"] = alphanumeric + zeroOrMore
        self.headerRegexes["stn"] = alphanumeric + zeroOrMore
        self.headerRegexes["target"] = alphanumeric + oneOrMore
        self.headerRegexes["seq"] = digit + oneOrMore
        self.headerRegexes["prio"] = digit + oneOrMore
        self.headerRegexes["ftpname"] = alphanumeric + oneOrMore
    
    def compute(self):
        """
        Refresh the object based on its updated attributes.
        """
        
        alphanumeric = self.getAlphanumericRegex()
        digit = self.getDigitRegex()
        zeroOrMore = self.getZeroOrMoreRegex()
        oneOrMore = self.getOneOrMoreRegex()
        
        names = self.getSearchNames()
        ftp = self.getFTP()
        if ftp:
            for name in names:
                self.logPath += "%s%s_%s.log* " % (PXPaths.LOG, self.getSearchType(), name)
                self.searchRegex = "%s:%s:%s:%s:%s:%s:%s" % (self.getHeaderRegex("ftpname"), self.getHeaderRegex("target"), alphanumeric + oneOrMore, alphanumeric + oneOrMore, self.getHeaderRegex("prio"), alphanumeric + oneOrMore, digit + "{14}")
        else:
            for name in names:
                self.logPath += "%s%s_%s.log* " % (PXPaths.LOG, self.getSearchType(), name)
            self.searchRegex = "%s_%s_%s_%s_%s_%s:%s:%s:%s:%s:%s:%s" % (self.getHeaderRegex("ttaaii"), self.getHeaderRegex("ccccxx"), self.getHeaderRegex("ddhhmm"), self.getHeaderRegex("bbb"), self.getHeaderRegex("stn"), self.getHeaderRegex("seq"), self.getHeaderRegex("target"), self.getHeaderRegex("ccccxx"), alphanumeric + oneOrMore, self.getHeaderRegex("prio"), alphanumeric + oneOrMore, digit + "{14}")
    
    def getSearchRegex(self):
        return self.searchRegex

    def getLogPath(self):
        return self.logPath

    def getHeaderRegex(self, key):
        return self.headerRegexes[key]
    
    def setHeaderRegex(self, key, value):
        """
        Change the value of the regular expression dictionnary parts.
        It also performs some modification on the value.
        """
        
        alphanumeric = self.getAlphanumericRegex()
        digit = self.getDigitRegex()
        zeroOrMore = self.getZeroOrMoreRegex()
        oneOrMore = self.getOneOrMoreRegex()
       
        if value != self.headerRegexes[key]: # Checks if the new value is different than the old.
            if key != "target" and key != "ftpname": # We don't want to capitalize certain fields.
                value = value.upper()
            
            # If user enters a *, replace it with a regex wildcard
            if "*" in value:
                if type(value) is int:
                    value = value.replace("*", digit + oneOrMore) # Then we can use a digit widlcard
                else:
                    value = value.replace("*", alphanumeric + zeroOrMore)
                
        self.headerRegexes[key] = value

    def getSearchType(self):
        return self.searchType

    def setSearchType(self, value):
        self.searchType = value

    def getSearchNames(self):
        return self.names

    def setSearchNames(self, value):
        self.names = value

    def getSince(self):
        return self.since

    def setSince(self, value):
        self.since = int(value)

    def getFrom(self):
        return self.fromdate

    def setFrom(self, value):
        self.fromdate = value

    def getTo(self):
        return self.todate

    def setTo(self, value):
        self.todate = value

    def getTimesort(self):
        return self.timesort

    def setTimesort(self, value):
        self.timesort = value

    def getFTP(self):
        return self.ftp

    def setFTP(self, value):
        self.ftp = value

    def getAlphanumericRegex(self):
        return self.alphanumericRegex

    def getDigitRegex(self):
        return self.digitRegex

    def getZeroOrMoreRegex(self):
        return self.zeroOrMoreRegex

    def getOneOrMoreRegex(self):
        return self.oneOrMoreRegex
