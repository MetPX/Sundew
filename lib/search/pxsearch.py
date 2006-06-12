#!/usr/bin/env python
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

import sys
import commands
from optparse import OptionParser

from SearchObject import SearchObject

def updateSearchObject(so, options, args):
    # Verifying the search type
    if options.rxtype == True and options.txtype == True:
        print "Cannot search both RX and TX at the same time."
        sys.exit(1)
    elif options.rxtype == False and options.txtype == False:
        print "You must specify a search type (--rx or --tx)."
        sys.exit(1)
    elif options.rxtype == True:
        so.setSearchType("rx")
    else:
        so.setSearchType("tx")

    if len(args) > 0:
        so.setSearchName(args[0]) # First argument should be the name of the "thing" to search
    
    so.setHeaderRegex("ttaaii", options.ttaaii) 
    so.setHeaderRegex("ccccxx", options.ccccxx) 
    so.setHeaderRegex("ddhhmm", options.ddhhmm) 
    so.setHeaderRegex("bbb", options.bbb) 
    so.setHeaderRegex("stn", options.stn) 
    so.setHeaderRegex("seq", options.seq) 
    so.setHeaderRegex("target", options.target) 
    so.setHeaderRegex("prio", options.prio)
    
    so.compute() # Compute the necessary informations
    
def search(logFileName, regex):
    print "Searching in: %s" % (logFileName)
    print "Using: %s\n" % (regex)
    
    status, output = commands.getstatusoutput("egrep %s %s" % (regex, logFileName))
    lines = output.splitlines()
    for line in lines:
        print line
    print "Number of matches: %s" % (len(lines))
    
def createParser(so):
    usagemsg = "%prog [options] <name>\nSearch in the PX unified log for bulletins matching certain criterias."
    parser = OptionParser(usage=usagemsg, version="%prog 0.2")
    
    # These two only offer long option names
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

    return parser
    
def main():
    so = SearchObject()
    parser = createParser(so)
    options, args = parser.parse_args()
   
    updateSearchObject(so, options, args)
    #search(so.getLogPath(), so.getSearchRegex())
    search("./logs/rx_ncp2.log", so.getSearchRegex())
    
if __name__ == "__main__":
   main() 
