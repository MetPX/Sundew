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
sys.path.append("/apps/px/lib/")
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
        sys.exit("Incorrect priority number!\nShould be from 1 to 5 only.")

    if len(args) > 1:
        if len(args.split(":")) < 3:
            sys.exit("Input was not formatted correctly.\nIt should be machine:log:bulletin.\n'log' can be anything, it is a field returned by pxSearch")

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
            lines = output.splitlines()
            count = 0
            problemCount = 0
            for line in lines:
                if line.find("Problem copying") != -1:
                    logger.error(line)
                    problemCount += 1
                else:
                    machine = line.split(":")[0]
                    count += 1
                    logger.info(line)
            print "%s: %s bulletins resent on %s (%s could not be found)." % (machine, count - problemCount, count, problemCount)
    ro.removeFiles()

############################################################################################
# AHHHHHHHHHHHH CHECK COUNT ON MULTIPLE MACHINE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#############################################################################################

def createParser(ro):
    usagemsg = "%prog [options] <machine:log:bulletin>\nResend one or more bulletins."
    parser = OptionParser(usage=usagemsg, version="%prog 1.0-rc1")

    parser.add_option("--ask", action = "store_true", dest = "prompt", help = "Ask for a confirmation for each bulletins.", default=True)
    parser.add_option("--all", action = "store_false", dest = "prompt", help = "Send all bulletins without confirmation (default).", default=False)
    parser.add_option("-p", "--prio", dest = "prio", help = "Specify in which priority you want to put the bulletin in? (default 2).", default = ro.getPrio())
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

if __name__ == "__main__":
    main()
