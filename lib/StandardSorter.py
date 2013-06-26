"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: StandardSorter.py
#
# Author: Daniel Lemay
#
# Date: 2005-05-05
#
# Description:
#
#############################################################################################

"""
import os,sys
from SortableString import SortableString
import time

class StandardSorter:

    def __init__(self, listx):
        self.list = listx

    def sort(self):
        self.list.sort()
        return self.list

if __name__ == "__main__":

    """

    if sys.version[:1] >= '3' :
       import subprocess
    else :
       import commands
       subprocess = commands

    (status, output) = subprocess.getstatusoutput("date")
    print output
    files = os.listdir("/apps/pds/tools/ColumboNCCS/testfiles1/")
    (status, output) = subprocess.getstatusoutput("date")
    print output
    sortedFiles = MultiKeysStringSorter(files).sort()
    (status, output) = subprocess.getstatusoutput("date")
    print output
    #print sortedFiles
    # regarder si lstat rallonge beaucoup
    """

    l = ['pomme', 'poire', 'abricot', 'tomate', 'banane']

    sorter = StandardSorter(l)
    print(sorter.list)
    sorter.sort()
    print(sorter.list)


