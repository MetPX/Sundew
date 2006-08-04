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
from ResendObject import *

def parseRawLine(line):
    lineParts = line.split(":")
    header = ":".join(lineParts[2:])
    machine = lineParts[0]
    return machine, header

def validateUserInput(options, args):
    # Priority number must be between 1 and 5
    if int(options.prio) < 1 or int(options.prio) > 5:
        print "Incorrect priority number!"
        print "Available priorities are 1 or 2 or 3 or 4 or 5."
        sys.exit(1)

    if len(args) > 1:
        if len(args.split(":")) < 2:
            print "Input was not formatted correctly."
            print "It should be machine:bulletin."
            sys.exit(1)

def updateResendObject(ro, options, args):
    ro.setPrompt(options.prompt)
    ro.setPrio(options.prio)
    ro.setDestinations(options.destination.split(","))
    
    if len(args) == 0: # Get bulletin list from stdin
        for searchLine in sys.stdin:
            machine, bulletinHeader = parseRawLine(searchLine.strip())
            ro.addToMachineHeaderDict(machine, bulletinHeader)
        
        # We must rebind sys.stdin to the tty.
        # This is ugly but this is the only solution after reading from a pipe
        sys.stdin = open("/dev/tty")
    else:
        for arg in args:
            argParts = arg.split(":")
            machine = argParts[0]
            bulletinHeader = ":".join(argsParts[1:]) # A bulletin file header contains multiple ':'
            ro.addToMachineHeaderDict(machine, bulletinHeader)

def resend(ro):
    logger = ro.getLogger()
    commandList = ro.createAllArtifacts()
    for c in commandList:
        status, output = commands.getstatusoutput(c)
        if status:
            print "An error occured during the resending process!"
            print "Command used was: %s" % (c)
            sys.exit(1)
        else:
            lines = output.splitlines()
            problemCount = 0
            for line in lines:
                if line.find("Problem copying") != -1:
                    logger.error(line)
                    problemCount += 1
                else:
                    logger.info(line)
            print "%s bulletins resent on %s (%s could not be found)." % (ro.getHeaderCount() - problemCount, ro.getHeaderCount(), problemCount)
    ro.removeFiles()

def createParser(ro):
    usagemsg = "%prog [options] <machine:bulletin>\nResend one or more bulletins."
    parser = OptionParser(usage=usagemsg, version="%prog 0.9-beta")

    parser.add_option("--ask", action = "store_true", dest = "prompt", help = "Ask for a resending confirmation for each bulletins.", default=True)
    parser.add_option("--all", action = "store_false", dest = "prompt", help = "Send all bulletins without confirmation (default).", default=False)
    parser.add_option("-p", "--prio", dest = "prio", help = "Specify in which priority you want to put the bulletin in? (default 3).", default = ro.getPrio())
    parser.add_option("-d", "--destination", dest = "destination", help = "Specify comma-separated list of destinations (ex: ppp1,test,cmc2).", default = ro.getDestinations())
    
    return parser

def main():
    ##############################
    # 1. Create the resend object
    ##############################
    ro = ResendObject()
    
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

if __name__ == "__main__":
    main()
