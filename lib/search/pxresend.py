#!/usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: pxresend.py
#
# Author: Dominik Douville-Belanger
#
# Description: Resend a bulletin file.
#
# Date: 2006-07-07
#
###########################################################
"""

# Python API imports
import sys
import commands
from optparse import OptionParser

# Local imports
sys.path.append("../")
import PXPaths; PXPaths.normalPaths()

def validateUserInput(options, args):
    if (options.header != "" and options.machine == "") or (options.header == "" and options.machine != ""):
        print "You must use --header and --machine together."
        sys.exit(1)

    if int(options.prio) < 1 or int(options.prio) > 5:
        print "Incorrect priority number!"
        print "Available priorities are 1 or 2 or 3 or 4 or 5."
        sys.exit(1)

def createParser():
    usagemsg = "%prog [options] <name>\nResend a bulletin or a list of bulletins."
    parser = OptionParser(usage=usagemsg, version="%prog 0.1-alpha")

    parser.add_option("--ask", action = "store_true", dest = "prompt", help = "Ask for a resending confirmation for each bulletins.", default=False)
    parser.add_option("--all", action = "store_false", dest = "prompt", help = "Send all bulletins without confirmation (default).", default=False)
    parser.add_option("-p", "--prio", dest = "prio", help = "Specify in which priority you want to put the bulletin in? (default 3).", default="3")
    parser.add_option("-h", "--header", dest = "header", help = "Specify a precise bulletin header (can be used instead of the output of pxsearch.py", default = "")
    parser.add_option("-m", "--machine", dest = "machine", help = "Specify the machine on which the bulletin can be found. Use this only with --header." default = "") 
    
    return parser

def prepareArgs(args):
    machineDict = {}
    
    for arg in args:
        header, machine = parseInput(arg)
        if machine not in machineDict.keys():
            machineDict[machine] = 

def parseInput(line):
    header = ":".join(line.split(":")[2:])
    machine = (line.split(":")[0])[1:] # Removes the @

    return header, machine

def main():
    parser = createParser()
    options, args = parser.parse_args()
    validateUserInput(options, args)
    
    if options.header != "":
        
    
if __name__ == "__main__":
    main()
