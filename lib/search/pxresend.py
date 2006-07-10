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

def validateUserInput(options, args):
    # Those two options must be used together
    if (options.header != "" and options.machine == "") or (options.header == "" and options.machine != ""):
        print "You must use --header and --machine together."
        sys.exit(1)
    
    # Priority number must be between 1 and 5
    if int(options.prio) < 1 or int(options.prio) > 5:
        print "Incorrect priority number!"
        print "Available priorities are 1 or 2 or 3 or 4 or 5."
        sys.exit(1)

def updateResendObject(ro, options, args):
    pass

def createParser(ro):
    usagemsg = "%prog [options] <name>\nResend a bulletin or a list of bulletins."
    parser = OptionParser(usage=usagemsg, version="%prog 0.1-alpha")

    parser.add_option("--ask", action = "store_true", dest = "prompt", help = "Ask for a resending confirmation for each bulletins.")
    parser.add_option("--all", action = "store_false", dest = "prompt", help = "Send all bulletins without confirmation (default).")
    parser.add_option("-t", "--to", dest = "to", help = "Specify the client to which you want to resend.", default = ro.getTo())
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
    pass

if __name__ == "__main__":
    main()
