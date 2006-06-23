#!/usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: pxsearch.py
#
# Author: Dominik Douville-Belanger
#
# Description: Search in the PX logs for bulletins 
#              matching certain criterias.
#
# Date: 2006-05-08
#
###########################################################
"""

# Python API imports
import sys
import commands
import time
from optparse import OptionParser

# Local imports
sys.path.append("../")
import PXPaths; PXPaths.normalPaths()
from SearchObject import SearchObject

def filterTime(so, lines):
    HOURINSECONDS = 3600

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

    return result

def validateUserInput(options, args):
    # Validating the search type
    if options.rxtype == True and options.txtype == True:
        print "Cannot search both RX and TX at the same time."
        sys.exit(1)
    elif options.rxtype == False and options.txtype == False:
        print "You must specify a search type (--rx or --tx)."
        sys.exit(1)

    # Validating date arguments
    if options.since != 0 and (options.todate != "" or options.fromdate != ""):
        print "You cannot use --since with another date filtering mechanism."
        sys.exit(1)
    elif (options.todate != "" and options.fromdate == "") or (options.todate == "" and options.fromdate != ""):
        print "You must use --from and --to together."
        sys.exit(1)

def updateSearchObject(so, options, args):
    # Setting the search type
    if options.rxtype == True:
        so.setSearchType("rx")
    else:
        so.setSearchType("tx")
    
    # If there is an argument to the program call, it replaces * with args*
    # By default * means search in everything
    if len(args) > 0:
        so.setSearchName(args[0])
    
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
   
    so.compute() # Compute the necessary informations

def nameSort(lineA, lineB):
    return cmp(lineA.split(":")[1].split("_")[0], lineB.split(":")[1].split("_")[0])

def timeSort(lineA, lineB):
    return cmp(lineA.split(":")[-1], lineB.split(":")[-1])

def search(so):
    logFileName = so.getLogPath()
    regex = so.getSearchRegex()

    print "Searching in: %s" % (logFileName)
    print "Using: %s" % (regex)
  
    # Temporary machine list storage
    machines = open("machines.txt", "r").readlines()
    
    for machine in machines:
        cmd = "ssh %s egrep -o %s %s" % (machine.strip(), regex, logFileName)
        print "Command used: %s" % (cmd)
        status, output = commands.getstatusoutput(cmd)
        lines = output.splitlines()
        
        # Validation was done in validateUserInput()
        if so.getSince() != 0 or so.getFrom() != "" or so.getTo() != "":
            lines = filterTime(so, lines)
            lines.sort(timeSort)
        else:
            lines.sort(nameSort)
            
        for line in lines:
            print line
        print "Number of matches: %s" % (len(lines))
    
def createParser(so):
    usagemsg = "%prog [options] <name>\nSearch in the PX unified log for bulletins matching certain criterias."
    parser = OptionParser(usage=usagemsg, version="%prog 0.2")
    
    # These two only offer long option names and using one of them is mandatory
    parser.add_option("--rx", action="store_true", dest = "rxtype", help = "Perform a search in the RX logs.", default = False)
    parser.add_option("--tx", action="store_true", dest = "txtype", help = "Perform a search in the TX logs.", default = False)
    
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
    parser.add_option("-i", "--since", dest = "since", help = "Only show matches since X hours ago to now", default = so.getSince())
    parser.add_option("-f", "--from", dest = "fromdate", help = "Specify a start date <YYYYMMDDhhmmss> or <epoch>", default = so.getFrom())
    parser.add_option("-o", "--to", dest = "todate", help = "Specify a end date <YYYYMMDDhhmmss> or <now>", default = so.getTo())

    return parser
    
def main():
    ##############################
    # 1. Create the search object
    ##############################
    so = SearchObject()
    
    ################################################################
    # 2. Initantiate the parse and parse the command line arguments
    ################################################################
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
