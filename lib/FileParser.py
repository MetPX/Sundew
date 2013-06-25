"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: FileParser.py
#
# Author: Daniel Lemay
#
# Date: 2006-05-31
#
# Description: Used to parse files (parent class)
#
# MG python3 compatible
#
#############################################################################################
"""
import sys




class FileParserException(Exception):
    pass

class FileParser(object):
    
    def __init__(self, filename):
        self.filename = filename # Name of the file we want to parse
        self.printErrors = True  # Determine if we want to print errors or not

    def removeDuplicate(listx):
        setx = {}
        for item in listx:
            setx[item] = 1
        lst = list(setx.keys())
        return lst
    removeDuplicate = staticmethod(removeDuplicate)

    def identifyDuplicate(listx):
        duplicate = {}
        listx.sort()
        for index in range(len(listx)-1):
            if listx[index] == listx[index+1]:
                duplicate[listx[index]]=1
        lst= list(duplicate.keys())
        return lst
    identifyDuplicate = staticmethod(identifyDuplicate)

    def openFile(self, filename):
        try:
            if sys.version[:1] >= '3' :
               import codecs
               file = codecs.open(filename, 'r', "utf-8")
            else :
               file = open(filename, 'r')
            return file
        except:
            (type, value, tb) = sys.exc_info()
            print ("Type: %s, Value: %s" % (type, value))
            sys.exit()
        
    def parse(self):
        raise FileParserException('Abstract method: not implemented in FileParser Class')

    def clearInfos(self):
        raise FileParserException('Abstract method: not implemented in FileParser Class')

    def printInfos(self):
        raise FileParserException('Abstract method: not implemented in FileParser Class')

    def logInfos(self):
        raise FileParserException('Abstract method: not implemented in FileParser Class')

if __name__ == '__main__':
    import sys

    parser = FileParser('/apps/px/etc/stations.conf')
    print("Filename: %s" % parser.filename)
    #parser.clearInfos()
    parser.printInfos()
