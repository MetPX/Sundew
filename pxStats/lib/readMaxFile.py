"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: readMaxFile.py
#
# Author: Daniel Lemay
#
# Date: 2004-11-29
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: From a configuration file, obtain the maximum value for which you want Columbo Show
#              to "wave a flag" indicating something is wrong
#############################################################################################
import re
#from ColumboPath import *

DEBUG = 0

def setValueMax(namesList, regexesDict, default):
   namesMax = {}
   for name in namesList:
      if len(regexesDict.keys()) > 0:
         for regex in regexesDict.keys():
            match = re.search(regex, name) 
            if match:
               namesMax[name] = regexesDict[regex]
               break
            else:
               namesMax[name] = default 
      else:
         namesMax[name] = default 
   return namesMax

def readQueueMax(filename, system):
    clientsRegex = {}
    directoriesRegex = {}
    circuitsRegex = {}
    timersRegex = {}
    pdsGraphsRegex = {}
    pxGraphsRegex = {}

    file = open(filename, 'r')
    lines = file.readlines()

    # Parsing
    inClients = 0
    inInputDirs = 0
    inPXCircuits = 0
    inPXTimers = 0
    inPDSGraphs = 0
    inPXGraphs = 0
    regex_CLIENTS = re.compile(r'^PDS_CLIENTS\s*')  
    regex_INPUT_DIRECTORIES = re.compile(r'^PDS_INPUT_DIRECTORIES\s*')
    regex_PDS_GRAPHS = re.compile(r'^PDS_GRAPHS\s*')
    regex_PX_GRAPHS = re.compile(r'^PX_GRAPHS\s*')
    regex_PX_CIRCUITS = re.compile(r'^PX_CIRCUITS\s*')
    regex_PX_TIMERS = re.compile(r'^PX_TIMERS\s*')
    regex_DEFAULT = re.compile(r'^DEFAULT\s+(\d+).*')
    regex_NameValue = re.compile(r'^(.*?)\s+(\d+).*')

    for line in lines:
        match_CLIENTS = regex_CLIENTS.match(line)
        match_INPUT_DIRECTORIES = regex_INPUT_DIRECTORIES.match(line)
        match_PDS_GRAPHS = regex_PDS_GRAPHS.match(line)
        match_PX_GRAPHS = regex_PX_GRAPHS.match(line)
        match_PX_CIRCUITS = regex_PX_CIRCUITS.match(line)
        match_PX_TIMERS = regex_PX_TIMERS.match(line)
        match_DEFAULT = regex_DEFAULT.match(line)
        match_NameValue = regex_NameValue.match(line)

        if line[0] == "#": 
            continue

        elif match_CLIENTS:
            if DEBUG: print "Les Clients"
            inClients = 1
            (inInputDirs, inPXCircuits, inPXTimers, inPDSGraphs, inPXGraphs) = (0, 0, 0, 0, 0)
        elif match_INPUT_DIRECTORIES:
            if DEBUG: print "Les Directories"
            inInputDirs = 1
            (inClients, inPXCircuits, inPXTimers, inPDSGraphs, inPXGraphs) = (0, 0, 0, 0, 0)
        elif match_PDS_GRAPHS:
            if DEBUG: print "Les Graphs PDS"
            inPDSGraphs = 1
            (inClients, inInputDirs, inPXCircuits, inPXTimers, inPXGraphs) = (0, 0, 0, 0, 0)
        elif match_PX_GRAPHS:
            if DEBUG: print "Les Graphs PX"
            inPXGraphs = 1
            (inClients, inInputDirs, inPXCircuits, inPXTimers, inPDSGraphs) = (0, 0, 0, 0, 0)
        elif match_PX_CIRCUITS:
            if DEBUG: print "Les Circuits"
            inPXCircuits = 1
            (inClients, inInputDirs, inPXTimers, inPDSGraphs, inPXGraphs) = (0, 0, 0, 0, 0)
        elif match_PX_TIMERS:
            if DEBUG: print "Les Timers"
            inPXTimers = 1
            (inClients, inInputDirs, inPXCircuits, inPDSGraphs, inPXGraphs) = (0, 0, 0, 0, 0)

        elif inClients:
            if (match_DEFAULT):
                default_client = match_DEFAULT.group(1)
            elif (match_NameValue):
                (name, number) = match_NameValue.groups()
                clientsRegex[glob_to_regex(name)] = number    
                if DEBUG:
                    print "client ",
                    print match_NameValue.groups()
        elif inInputDirs:
            if (match_DEFAULT):
                default_inputDir = match_DEFAULT.group(1)
            elif (match_NameValue):
                (name, number) = match_NameValue.groups()
                directoriesRegex[glob_to_regex(name)] = number    
                if DEBUG:
                    print "inputDir ",
                    print match_NameValue.groups()
        elif inPDSGraphs:
            if (match_DEFAULT):
                default_pdsGraph = match_DEFAULT.group(1)
            elif (match_NameValue):
                (name, number) = match_NameValue.groups()
                pdsGraphsRegex[glob_to_regex(name)] = number    
                if DEBUG:
                    print "PDS graph ",
                    print match_NameValue.groups()
        elif inPXGraphs:
            if (match_DEFAULT):
                default_pxGraph = match_DEFAULT.group(1)
            elif (match_NameValue):
                (name, number) = match_NameValue.groups()
                pxGraphsRegex[glob_to_regex(name)] = number    
                if DEBUG:
                    print "PX graph ",
                    print match_NameValue.groups()
        elif inPXCircuits:
            if (match_DEFAULT):
                default_circuit = match_DEFAULT.group(1)
            elif (match_NameValue):
                (name, number) = match_NameValue.groups()
                circuitsRegex[glob_to_regex(name)] = number
                if DEBUG:
                    print "circuit",
                    print match_NameValue.groups()
        elif inPXTimers:
            if (match_DEFAULT):
                default_timer = match_DEFAULT.group(1)
            elif (match_NameValue):
                (name, number) = match_NameValue.groups()
                timersRegex[glob_to_regex(name)] = number
                if DEBUG:
                    print "timer",
                    print match_NameValue.groups()
    
    if system == 'PDS':
        return clientsRegex, default_client, directoriesRegex, default_inputDir, pdsGraphsRegex, default_pdsGraph
    elif system == 'PX':
        return circuitsRegex, default_circuit, timersRegex, default_timer, pxGraphsRegex, default_pxGraph

def glob_to_regex (glob):
# Transform a glob into a regex
# The glob has to be not too complicated
   #print "Original glob = " + glob + " regex = ", 
   glob = list(glob)
   regex_dict = {
     '*' : '.*',
     '?' : '.',
     '[' : '[',
     ']' : ']',
   }
   for index in range(len(glob)):
      if glob[index] in regex_dict:
         glob[index] = regex_dict[glob[index]] 
   return str ('^' + ''.join(glob) + '$')

#############################################################################################
# Testing
#############################################################################################
"""
theClients = ['toto', 'www', 'wxo-ww', 'tata-wxo', 'wxo-b2', 'testDaniel', 'testDan', 'testdan', 'allo-www-sal']
theDirs = ['/apps/pds/RAW/urp', '/apps/pds/RAW/urpd', '/apps/pds/RAW/chart']
clientsRegex, inputDirsRegex, defaultClient, defaultInputDir = readQueueMax("path/Columbo/etc.sample/queueMax", "PDS")
clientsRegex, inputDirsRegex, defaultClient, defaultInputDir = readQueueMax("path/Columbo/etc.sample/queueMax", "PX")
clientsMax =  setValueMax(theClients, clientsRegex, defaultClient)
dirsMax = setValueMax(theDirs, inputDirsRegex, defaultInputDir) 
print defaultClient
print defaultInputDir
print clientsRegex
print inputDirsRegex
print clientsMax
print dirsMax
"""


