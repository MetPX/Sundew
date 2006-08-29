#!/usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: pxSearch.py
#
# Author: Dominik Douville-Belanger
#
# Description: Search in the PX logs for bulletins 
#              matching certain criterias.
#
# Date: 2006-05-08
#
# TODO: Comment all functions
#
###########################################################
"""

# Python API imports
import sys
import commands
import time
from optparse import OptionParser

# Local imports
sys.path.insert(1,sys.path[0] + '/../')
import PXPaths; PXPaths.normalPaths()
from SearchObject import SearchObject
from ConfReader import ConfReader

def filterTime(so, lines):
    HOURINSECONDS = 3600
    
    try:
        if so.getSince() != 0:
            upperBound = time.time()
            lowerBound = upperBound - (so.getSince() * HOURINSECONDS)
        else:
            upperBound = time.mktime(time.strptime(so.getTo(), "%Y%m%d%H%M%S"))
            lowerBound = time.mktime(time.strptime(so.getFrom(), "%Y%m%d%H%M%S"))
        
        result = []
        for line in lines:
            stringTime = line.split(":")[-1]
            timeInSec = time.mktime(time.strptime(stringTime, "%Y%m%d%H%M%S"))
            if timeInSec >= lowerBound and timeInSec <= upperBound:
                result.append(line)
    except ValueError:
        sys.exit(1)
    return result

def validateUserInput(options, args):
    pass # No validations for now
    
def updateSearchObject(so, options, args):
    # Setting the search type
    if options.type == True:
        so.setSearchType("rx")
    else:
        so.setSearchType("tx")
    
    # Search in the specified flows
    if len(args) > 0:
        so.setSearchNames(args)
    
    so.setHeaderRegex("ttaaii", options.ttaaii) 
    so.setHeaderRegex("ccccxx", options.ccccxx) 
    so.setHeaderRegex("ddhhmm", options.ddhhmm) 
    so.setHeaderRegex("bbb", options.bbb) 
    so.setHeaderRegex("stn", options.stn) 
    so.setHeaderRegex("seq", options.seq) 
    so.setHeaderRegex("target", options.target) 
    so.setHeaderRegex("prio", options.prio)
   
    so.setSince(options.since)
    
    if options.fromdate == "epoch":
        so.setFrom(time.strftime("%Y%m%d%H%M%S", time.gmtime(0)))
    else:
        so.setFrom(options.fromdate)

    if options.todate == "now":
        so.setTo(time.strftime("%Y%m%d%H%M%S", time.gmtime()))
    else:
        so.setTo(options.todate)
    
    if options.timesort == True:
        so.setTimesort(True)
    
    so.compute() # Compute the necessary informations

def nameSort(lineA, lineB):
    """
    Sorts alphabetically by the TTAAii.
    If boths are equals, it sorts by time.
    """
    nameOrder = cmp(lineA.split(":")[2].split("_")[0], lineB.split(":")[2].split("_")[0])
    if nameOrder == 0: # Both are equal
        return timeSort(lineA, lineB)
    else:
        return nameOrder

def timeSort(lineA, lineB):
    return cmp(lineA.split(":")[-1], lineB.split(":")[-1])

def search(so):
    logFileName = so.getLogPath()
    regex = so.getSearchRegex()
    
    # We get the backends hostname with ConfReader
    cr = ConfReader("%spx.conf" % (PXPaths.ETC))
    machines = cr.getConfigValues("backend")
   
    results = []
    for machine in machines:
        machine = machine.strip()
        cmd = 'ssh %s "egrep -o %s %s"' % (machine, regex, logFileName)
        status, output = commands.getstatusoutput(cmd)
        if output:
            lines = output.splitlines()
            results += ["%s:%s" % (machine, line) for line in lines] # We add the machine name to the start of the line
        else: # This is only added for clarity. When grep doesn't find anything, he returns an error code. But this shouldn't be considered and error by our program.
            pass
            
    if so.getSince() != 0 or (so.getFrom() != "epoch" or so.getTo() != "now"):
        results = filterTime(so, results)
        results.sort(timeSort)
    elif so.getTimesort() == True:
        results.sort(timeSort)
    else:
        results.sort(nameSort)
        
    for result in results:
        print result
    
def createParser(so):
    usagemsg = "%prog [options] <names>\nSearch in the PX logs for bulletins matching certain criterias."
    parser = OptionParser(usage=usagemsg, version="%prog 1.0-rc2")
    
    # These two only offer long option names and using one of them is mandatory
    parser.add_option("--rx", action = "store_true", dest = "type", help = "Perform a search in the RX logs.", default = True)
    parser.add_option("--tx", action = "store_false", dest = "type", help = "Perform a search in the TX logs (default).", default = False)
    
    # Optional. No short option.
    parser.add_option("--timesort", action = "store_true", dest = "timesort", help = "Sort output by timestamps.", default = False)
   
    # Bulletin name's field content specifiers
    parser.add_option("-t", "--ttaaii", dest = "ttaaii", help = "Specify the TTAAii", default = so.getHeaderRegex("ttaaii"))
    parser.add_option("-c", "--ccccxx", dest = "ccccxx", help = "Specify the CCCCxx", default = so.getHeaderRegex("ccccxx"))
    parser.add_option("-d", "--ddhhmm", dest = "ddhhmm", help = "Specify the Day/Hour/Minute", default = so.getHeaderRegex("ddhhmm"))
    parser.add_option("-b", "--bbb", dest = "bbb", help = "Specify the BBB", default = so.getHeaderRegex("bbb"))
    parser.add_option("-s", "--stn", dest = "stn", help = "Specify the station code", default = so.getHeaderRegex("stn"))
    parser.add_option("-g", "--target", dest = "target", help = "Specify the source or the destination", default = so.getHeaderRegex("target"))
    parser.add_option("-q", "--seq", dest = "seq", help = "Specify the sequence number", default = so.getHeaderRegex("seq"))
    parser.add_option("-p", "--prio", dest = "prio", help = "Specify the priority number <1|2|3|4|5>", default = so.getHeaderRegex("prio"))
    
    # Let the user sort matches based on their time field
    parser.add_option("-i", "--since", dest = "since", help = "Only show matches since X hours ago to now (has priority over --from and --to)", default = so.getSince())
    parser.add_option("-f", "--from", dest = "fromdate", help = "Specify a start date <YYYYMMDDhhmmss> (defaults to epoch: fartest date away)", default = so.getFrom())
    parser.add_option("-o", "--to", dest = "todate", help = "Specify a end date <YYYYMMDDhhmmss> (defaults to now)", default = so.getTo())

    return parser
    
def main():
    ##############################
    # 1. Create the search object
    ##############################
    so = SearchObject()
    
    #################################################################
    # 2. Instantiate the parser and parse the command line arguments
    #################################################################
    parser = createParser(so)
    options, args = parser.parse_args()
    
    #########################
    # 3. Validate user input
    #########################
    validateUserInput(options,args)

    ##############################################################################
    # 4. Since input is correct, update the SearchObject with user defined values
    ##############################################################################
    updateSearchObject(so, options, args)
     
    ##############################
    # 5. Begin the search process
    ##############################
    search(so)
    
if __name__ == "__main__":
   main() 
