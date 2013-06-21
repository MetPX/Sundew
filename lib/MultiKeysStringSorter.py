"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: MultiKeyStringSorter.py
#
# Author: Daniel Lemay
#
# Date: 2005-02-01
#
# Description:
#
# MG python3 compatible
#
#############################################################################################

"""
import os,sys
from SortableString import SortableString
import time

class MultiKeysStringSorter:

    def __init__(self, list):
        self.list = list

    def sort(self):
        ssList = [SortableString(string) for string in self.list]
        #temp = [ (ss.priority, ss.timestamp, i, ss.data) for i, ss in enumerate(ssList) ]
        #temp = [ (ss.priority, ss.timestamp, ss.data) for ss in ssList ]
        temp = [ (ss.concatenatedKeys, ss.data) for ss in ssList ]
        temp.sort()
        #return [ data for priority, timestamp, i, data in temp ]
        #return [ data for priority, timestamp, data in temp ]
        return [ data for concatenatedKeys, data in temp ]

if __name__ == "__main__":


    if sys.version[:1] >= '3' :
       import subprocess
    else :
        import commands
        subprocess = commands

    (status, output) = subprocess.getstatusoutput("date")
    print(output)
    #files = os.listdir("/apps/pds/tools/ColumboNCCS/testfiles1/")
    files = os.listdir("/users/dor/aspy/dan/metpx/sundew/test/")
    #for f in files:
    #    print f
    (status, output) = subprocess.getstatusoutput("date")
    print(output)
    sortedFiles = MultiKeysStringSorter(files).sort()
    (status, output) = subprocess.getstatusoutput("date")
    print(output)
    #print sortedFiles
    for f in sortedFiles:
        print(f)
    # regarder si lstat rallonge beaucoup
