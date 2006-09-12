#!/usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: pxResend.py
#
# Author: Dominik Douville-Belanger
#
# Description: Resend a PX file.
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
sys.path.insert(1,sys.path[0] + '/../')
import PXPaths; PXPaths.normalPaths()
from ResendObject import *

def parseRawLine(line):
    lineParts = line.split(":")
    header = ":".join(lineParts[2:])
    machine = lineParts[0]
    return machine, header

def validateUserInput(options, args):
    if len(args) > 1:
        if len(args.split(":")) < 3:
            sys.exit("Input was not formatted correctly.\nIt should be machine:log:header\n'log' can be anything, it is a field returned by pxSearch")

def updateResendObject(ro, options, args):
    ro.setPrompt(options.prompt)
    ro.setDestinations(options.destination.split(","))
    
    if len(args) == 0: # Get bulletin list from stdin
        for searchLine in sys.stdin:
            machine, bulletinHeader = parseRawLine(searchLine.strip())
            ro.addToMachineHeaderDict(machine, bulletinHeader)
        # We must rebind sys.stdin to the tty if we want raw_input() later
        # This is ugly but this is the only solution after reading from a pipe
        try:
            sys.stdin = open("/dev/tty")
        except IOError:
            pass # Without this the web interface will create an error
                 # Anyway, we don't need raw_input() when using the web interface
    else:
        for arg in args:
            machine, bulletinHeader = parseRawLine(arg.strip())
            ro.addToMachineHeaderDict(machine, bulletinHeader)

def resend(ro):
    logger = ro.getLogger()
    commandList = ro.createAllArtifacts()
    for c in commandList:
        status, output = commands.getstatusoutput(c)
        if status:
            sys.exit("An error occured during the resending process!\nCommand used was: %s" % (c))
        else:
            totalCount = 0 # Total number of bulletin processed
            okCount = 0 # Number that were successfully resent
            problemCount = 0 # Number that caused problem
            machine = "" # The hostname on which the action occured

            lines = output.splitlines()
            for line in lines:
                machine = line.split(":")[0]
                if line.find("Problem copying") != -1:
                    logger.error(line)
                    problemCount += 1
                else:
                    okCount += 1
                    logger.info(line)
                totalCount += 1
            print "%s: %s bulletins resent (%s were not found in the database)." % (machine, okCount, problemCount)

def createParser(ro):
    usagemsg = "%prog [options] <machine:log:bulletin>\nResend one or more bulletins."
    parser = OptionParser(usage=usagemsg, version="%prog 1.0-rc1")

    parser.add_option("--ask", action = "store_true", dest = "prompt", help = "Ask for a confirmation for each file", default=True)
    parser.add_option("--all", action = "store_false", dest = "prompt", help = "Send all files without confirmation (default).", default=False)
    parser.add_option("-d", "--destination", dest = "destination", help = "Specify comma-separated list of destinations (ex: ppp1,test,cmc2).", default = ro.getDestinations())
    
    return parser

def main():
    ##############################
    # 1. Create the resend object
    ##############################
    ro = ResendObject()
    logger = ro.getLogger()
    
    #################################################################
    # 2. Instantiate the parser and parse the command line arguments
    #################################################################
    parser = createParser(ro)
    options, args = parser.parse_args()
     
    #########################
    # 3. Validate user input
    #########################
    validateUserInput(options, args)
    
    ##############################################################################
    # 4. Since input is correct, update the ResendObject with user defined values
    ##############################################################################
    updateResendObject(ro, options, args)
    
    #####################
    # 5. Begin resending
    #####################
    resend(ro)
    ro.removeFiles()

if __name__ == "__main__":
    main()
