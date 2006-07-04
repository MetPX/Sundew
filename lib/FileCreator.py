"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: FileCreator.py
#
# Author: Daniel Lemay
#
# Date: 2006-06-28
#
# Description: Used to create files (parent class)
#
#############################################################################################
"""
import sys
import PXPaths

PXPaths.normalPaths()  # Access to PX Paths

class FileCreatorException(Exception):
    pass

class FileCreator(object):
    
    def __init__(self, filename):
        self.filename = filename # Name of the file we want to create
        self.file = self._openFile(self.filename)

    def _appendToFile(self):
        raise FileCreatorException('Abstract method: not implemented in FileCreator Class')
    
    def _closeFile(self):
        try:
            self.file.close()
        except:
            (type, value, tb) = sys.exc_info()
            print ("Type: %s, Value: %s" % (type, value))
            sys.exit()

    def _openFile(self, filename):
        try:
            file = open(filename, 'w+')
            return file
        except:
            (type, value, tb) = sys.exc_info()
            print ("Type: %s, Value: %s" % (type, value))
            sys.exit()

if __name__ == '__main__':
    import sys

    fc = FileCreator('/apps/px/etc/tutu.conf')
