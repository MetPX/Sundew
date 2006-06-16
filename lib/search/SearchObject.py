#!/usr/bin/env python
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

class SearchObject(object):
    __slots__ = ["headerRegexes", "searchRegex", "searchType", "name", "logPath"]

    def __init__(self):
        self.headerRegexes = {}
        self.searchRegex = ""
        self.searchType = ""
        self.name = "*"
        self.logPath = ""
        
        self.fillHeaderRegexes()

    def fillHeaderRegexes(self):
        alphanumeric = "[[:alnum:]-]" # Just an alias instead of typing it everytime
        digits = "[[:digit:]]"
        zeroOrMore = "*"
        oneOrMore = "+"
        
        self.headerRegexes["ttaaii"] = alphanumeric + oneOrMore
        self.headerRegexes["ccccxx"] = alphanumeric + oneOrMore
        self.headerRegexes["ddhhmm"] = digits + "{6}" # Repeats exactly six times
        self.headerRegexes["bbb"] = alphanumeric + zeroOrMore
        self.headerRegexes["stn"] = alphanumeric + zeroOrMore
        self.headerRegexes["target"] = alphanumeric + oneOrMore
        self.headerRegexes["seq"] = digits + "{5}"
        self.headerRegexes["prio"] = digits + "{1}"
    
    def compute(self):
        """
        Refresh the object based on its updated attributes.
        """

        self.logPath = "/apps/px/log/%s_%s.log*" % (self.getSearchType(), self.getSearchName())
        self.searchRegex = "%s_%s_%s_%s_%s_%s:%s:%s:%s:%s:%s:%s" % (self.getHeaderRegex("ttaaii"), self.getHeaderRegex("ccccxx"), self.getHeaderRegex("ddhhmm"), self.getHeaderRegex("bbb"), self.getHeaderRegex("stn"), self.getHeaderRegex("seq"), self.getHeaderRegex("target"), self.getHeaderRegex("ccccxx"), "[[:alnum:]]+", self.getHeaderRegex("prio"), "[[:alnum:]]+", "[[:digit:]]+")
    
    def getSearchRegex(self):
        return self.searchRegex

    def getLogPath(self):
        return self.logPath

    def getHeaderRegex(self, key):
        return self.headerRegexes[key]
    
    def setHeaderRegex(self, key, value):
        self.headerRegexes[key] = value

    def getSearchType(self):
        return self.searchType

    def setSearchType(self, value):
        self.searchType = value

    def getSearchName(self):
        return self.name

    def setSearchName(self, value):
        self.name = value
