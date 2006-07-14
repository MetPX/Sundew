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
from ResendObject import *

def parseRawLine(line):
    lineParts = line.split(":")
    header = ":".join(lineParts[2:])
    machine = lineParts[0]
    return header, machine

def validateUserInput(options, args):
    # Priority number must be between 1 and 5
    if int(options.prio) < 1 or int(options.prio) > 5:
        print "Incorrect priority number!"
        print "Available priorities are 1 or 2 or 3 or 4 or 5."
        sys.exit(1)

def updateResendObject(ro, options, args):
    ro.setPrompt = options.prompt
    ro.setPrio = options.prio
    ro.setTo(args) # All trailing arguments are destinations
    
    if len(sys.stdin.readlines()) > 0:
        for searchLine in sys.stdin:
            machine, bulletinHeader = parseRawLine(searchLine)
            ro.addToMachineHeaderDict(machine, bulletinHeader)

def resend(ro):
    pass

def createParser(ro):
    usagemsg = "%prog [options] <destinations>\nResend a bulletin or a list of bulletins."
    parser = OptionParser(usage=usagemsg, version="%prog 0.2-alpha")

    parser.add_option("--ask", action = "store_true", dest = "prompt", help = "Ask for a resending confirmation for each bulletins.")
    parser.add_option("--all", action = "store_false", dest = "prompt", help = "Send all bulletins without confirmation (default).")
    parser.add_option("-p", "--prio", dest = "prio", help = "Specify in which priority you want to put the bulletin in? (default 3).", default = ro.getPrio())
    parser.add_option("-b", "--bulletin", dest = "bulletin", help = "Specify a precise bulletin header to be resent (i.e.: machine:full_header)")
    
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
