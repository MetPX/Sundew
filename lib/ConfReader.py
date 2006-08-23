#!/usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
"""
###########################################################
# Name: ConfReader.py
#
# Author: Dominik Douville-Belanger
#
# Description: Parse a (type value value ... value)
#              configuration file.
#
# Date: 2006-08-23
#
###########################################################
"""

# An exception class made specifically for the ConfReader
class ConfReaderException(Exception): pass

class ConfReader(object):
    __slots__ = ["configFileName", "configDict"]

    def __init__(self, filename):
        try:
            self.configFileName = filename
        except IOError:
            raise ConfReaderException("Could not open the configuration file.")
            
        self.configDict = {}
        self.parseConfigFile() # This way the user will only have to create an object and everything will have been set up

    def parseConfigFile(self):
        configFile = self.getConfigFileName()
        for line in open(configFile):
            if line.strip() == "": # Ignore blank line
                continue
            else:
                lineParts = line.split()
                if lineParts < 2: # Line doesn't follow syntax: type value
                    raise ConfReaderException("The parser has found an invalid line: %s" % (line))
                else:
                    key = lineParts[0]
                    if key.strip()[0] == '#': # Line is a comment, just skip over it
                        continue
                    else:
                        self.addToConfigDict(key, lineParts[1:]) 

    def getConfigFileName(self):
        return self.configFileName

    def getConfigDict(self):
        return self.configDict

    def addToConfigDict(self, type, values):
        if type in self.configDict.keys():
            self.configDict[type] += values
        else:
            self.configDict[type] = values

    def getConfigValues(self, type):
        configDict = self.getConfigDict()
        try:
            values = configDict[type]
        except KeyError:
            raise ConfReaderException("This type is not associated to any values in the configuration file.")
        return values

    def listConfigTypes(self):
        configDict = self.getConfigDict()
        return configDict.keys()
