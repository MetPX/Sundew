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
# Date: 2006-07-24
#
###########################################################
"""

import sys
from optparse import OptionParser

# Local imports
sys.path.append("../")
import PXManager
import PXPaths; PXPaths.normalPaths()

class SafeCopy(object):
    __slots__ = ["file", "destinations", "manager"]

    def __init__(self, file, destinations):
        self.file = file
        self.destinations = destinations
        self.manager = PXManager.PXManager()
        
    def copy(self):
        try:
            manager = self.getManager()
            file = self.getFile()
            destinations = self.getDestinations()
            manager.copyFileList(file, destinations)
        except:
            type, value, tb = sys.exc_info()
            print "An error occured in the PXManager, Type: %s Value: %s" % (type, value)
            sys.exit(1)

    def getFile(self):
        return self.file

    def getDestinations(self):
        return self.destinations

    def getManager(self):
        return self.manager

##################################################################
# This part is useful if you want to use the class as a program. #
##################################################################
def createParser():
    usagemsg = "%prog [options] <destinations>\nCopies multiple files to multiple destinations."
    parser = OptionParser(usage=usagemsg, version="%prog 0.1-alpha")
    parser.add_option("-f", "--file", dest = "file", help = "Specify a file that contains a list of sources.", default = "")

    return parser

def main():
    parser = createParser()
    options, args = parser.parse_args()    
    
    sc = SafeCopy(options.file, args)

    sc.copy()
    
if __name__ == "__main__":
    main()
