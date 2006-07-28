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
import os
import commands
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
    
    def deleteFile(self):
        try:
            os.remove(self.getFile())
        except OSError:
            type, value, tb = sys.exc_info()
            print "Problem deleting %s, Type: %s Value: %s" % (file, type, value)
    
    def getFile(self):
        return self.file

    def getDestinations(self):
        return self.destinations

    def getManager(self):
        return self.manager

##################################################################
# This part is useful if you want to use the class as a program. #
##################################################################
def pullFile(host, filename):
    saveTo = PXPaths.SEARCH
    status, output = commands.getstatusoutput("scp %s:%s ./" % (host, filename))
    if status:
        print "Could not pull file log from the server."
        sys.exit(1)
    else:
        return filename.split("/")[-1] # Just the name of the file, without the old path

     
def validateUserInput(options, args):
    if (options.file == "" or options.host == ""):
        print "You must specify a valid file and host!"
        sys.exit(1)
        
    if len(args) < 1:
        print "You must specify at least one destination!"
        sys.exit(1)

def createParser():
    usagemsg = "%prog [options] <destinations>\nCopies multiple files to multiple destinations."
    parser = OptionParser(usage=usagemsg, version="%prog 0.1-alpha")
    parser.add_option("-f", "--file", dest = "file", help = "Specify a file that contains a list of sources.", default = "")
    parser.add_option("-h", "--host", dest = "host", help = "Specify the host on which the file resides.", default = "")
    
    return parser

def main():
    parser = createParser()
    options, args = parser.parse_args()    
    validateUserInput(options, args)
    filename = pullFile(options.host, options.file)
    destinations = formatDestinations(args)
    
    sc = SafeCopy(filename, destinations) # args is the list of destinations

    sc.copy()
    sc.deleteFile()
if __name__ == "__main__":
    main()
