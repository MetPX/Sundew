"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: DiskReader.py
#
# Author: Daniel Lemay
#
# Date: 2005-02-01
#
# Description:
#
#############################################################################################

"""
import os, sys, os.path, re, commands, time, fnmatch
import Client, Source, Sourlient
from MultiKeysStringSorter import MultiKeysStringSorter
from CacheManager import CacheManager
from stat import *

class _DirIterator(object):
    """ Author: Sebastien Keim

        Used to obtain a list of all entries (filename + directories) contained in a
        root directory
    """
    def __init__(self, path, deep=False):
        self._root = path
        self._files = None
        self.deep = deep

    def __iter__(self):
        return self

    def next(self):
        join = os.path.join
        if self._files:
            d = self._files.pop()
            r = join(self._root, d)
            if self.deep and os.path.isdir(r):
                self._files += [join(d,n) for n in os.listdir(r)]
        elif self._files is None:
            self._files = [join(self._root,n) for n in os.listdir(self._root)]
        if self._files:
            return self._files[-1]
        else:
            raise StopIteration

class DiskReader:

    def __init__(self, path, batch=20000, validation=False, patternMatching=False, mtime=0, prioTree=False, logger=None, sorterClass=None, flow=None):
        """
        Set the root path and the sorter class used for sorting

        The regex will serve (if we use validation) to validate that the filename has the following form:
        SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339"

        FIXME: The regex should be passed otherwise!  config file?

        """
        # self.regex = re.compile(r'^[^:]*?:[^:]*?:[^:]*?:[^:]*?:(\d)[^:]*?:[^:]*?:(\d{14})$')
        # This regex would be better than the one actually in use because it don't match the following entry:
        # "A:B:C:WXO_DAN:BAD:3:ALLO:20050714183623"
        # Surprisingly this entry match (priority in 6th position, should be in 5th) in spite of the use of *? operator ???
        # Maybe we already accept some file badly named, so it's risky to change the regex now

        self.regex = re.compile(r'^.*?:.*?:.*?:.*?:(\d).*?:.*?:(\d{14})$')  # Regex used to validate filenames
        self.path = path                          # Path from where we ingest filenames
        self.flowName = os.path.basename(path)    # Last part of the path correspond to client/source name 
        self.validation = validation              # Name Validation active (True or False)
        self.patternMatching = patternMatching    # Pattern matching active (True or False)
        self.logger = logger                      # Use to log information
        self.batch = batch                        # Maximum number of files that we are interested to sort
        self.mtime = mtime                        # If we want to check modification time before taking a file                             
        self.sortedFiles = []                     # Sorted filenames
        self.data = []                            # Content of x filenames (x is set in getFilesContent())
        self.prioTree = prioTree                  # Boolean that determine if the "priorities" structure is enforced
        self.sorterClass = sorterClass            # Sorting algorithm that will be used by sort()
        self.flow = flow                          # Flow (Client, Source, Sourlient) object, only used when patternMatching is True
        self.cacheManager = CacheManager(maxEntries=120000, timeout=12*3600) # Used to cache read entries

        #self.read()

    def read(self):
        self.sortedFiles = []
        self.data = []
        if self.prioTree: # If we want to use predefine priority directories tree
            self.files = self._getFilesList()                          # List of filenames under the priorities
        else:
            self.files = self. _getFilesListForOneBranch(self.path, self.batch)  # List of filenames under the path

        self.sort()
        
    def _validateName(self, basename):
        """
        Validate that the filename has the following form:
        "SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339"
        """
        match = self.regex.search(basename)
        if match:
            #print match.group(2), match.group(1)
            return True
        else:
            #print "Don't match: " + basename
            return False

    # Method augmented by MG ... proposed by DL
    def _matchPattern(self, basename):
        """
        Verify if basename is matching one mask of a flow
        """

        if self.flow == None: return (True, 'RX')

        if isinstance(self.flow, Source.Source): 
            return (self.flow.fileMatchMask(basename), 'RX')

        elif isinstance(self.flow, Client.Client) or isinstance(self.flow, Sourlient.Sourlient):
           for mask in self.flow.masks:
               parts = re.findall( mask[0], basename )
               if len(parts) == 2 and parts[1] == '' : parts.pop(1)
               if len(parts) == 1 :
                  if len(mask) == 3 : return (True, 'TX')
                  return (False, 'TX')

        return (False, 'TX')

    def _getFilesList(self):
        """
        We obtain a list of files to sort. The directory structure is the following:
        level 1: priorities (1,2,3,4,5)
        level 2: date (YYYYMMDDHH, 2005042218)
        If we decide to scan a directory of level 2 (because we haven't attained the "batch" value),
        we will scan it entirely, even if this implies that "batch" value will be exceeded

        """
        priorities = ['1', '2', '3', '4', '5']
        files = []
        start = 0

        for priority in priorities:
             path = self.path + '/' + priority
             if os.path.exists(path):
                 dates = os.listdir(path)
                 dates.sort()
                 for date in dates:
                     start = len(files)
                     if start < self.batch:
                         datePath = path + '/' + date
                         if os.path.isdir(datePath):
                             files += self._getFilesListForOneBranch(datePath, self.batch - start)
        return files

    def _getFilesListForOneBranch(self, path, batch):
        """
        Set and return a list of all the filenames (not directories) contained in root directory (path) and
        all the subdirectories under it. A validation is done (if self.validation is True) on the names.
        If a filename is not valid, the file is unlinked and a log entry is added to the log. Batch is the
        maximum number of files that can be returned.

        FIXME: Add try/except for unlink
        """
        dirIterator = _DirIterator(path, True)
        files = []
        for file in dirIterator:
            if not os.path.isdir(file):
                basename = os.path.basename(file)
                # Files we don't want to touch
                if basename[0] == '.' or basename[-4:] == ".tmp" or not os.access(file, os.R_OK):
                    continue

                # If we use stats informations (useful with rcp)
                if self.mtime:
                    if  not time.time() - os.stat(file)[ST_MTIME] > self.mtime:
                        self.logger.debug("File (%s) too recent (mtime = %d)" % (file, self.mtime))
                        continue

                # If we use name validation 
                if self.validation:
                    if not self._validateName(basename):
                        os.unlink(file)
                        if self.logger is not None:
                            self.logger.info("Filename incorrect: " + file + " has been unlinked!")
                        continue

                # If we use pattern matching
                if self.patternMatching:
                    # Does the filename match a pattern ?
                    match, type = self._matchPattern(basename)
                    if not match:
                        os.unlink(file)
                        if self.logger is not None:
                            self.logger.info("No pattern (%s) matching: %s has been unlinked!" % (type, file))
                        continue

                # We don't want to exceed the batch value 
                #if len(files) >= batch:
                #        break

                # All "tests" have been passed
                files.append(file)

        return files
    
    def getFilesContent(self, number=1000000):
        """
        Set and return a list having the content (data) of corresponding filenames in the
        SORTED list (imply sort() must be called before this function). The number of elements is
        determined by "number"
        """
        self.data = []
        shortList = self.sortedFiles[0:number]
        for file in shortList:
            try:
                fileDesc = open(file, 'r')
                self.data.append(fileDesc.read())
            except:
                self.logger.warning("DiskReader.getFilesContent(): " + file + " not on disk anymore")
                # We don't raise the exception because we assume that this error has been created
                # by a legitimate process that has cleared some client/source queue.
        return self.data

    def getFilenamesAndContent(self, number=1000000):
        """
        Set and return a list of tuples composed of the content (data) of corresponding filenames in the
        SORTED list (imply sort() must be called before this function) and the filename. The number of
        elements is determined by "number"
        """
        self.data = []
        shortList = self.sortedFiles[0:number]
        for file in shortList:
            try:
                fileDesc = open(file, 'r')
                self.data.append((fileDesc.read(), file))
            except:
                self.logger.warning("DiskReader.getFilesContent(): " + file + " not on disk anymore")
                # We don't raise the exception because we assume that this error has been created
                # by a legitimate process that has cleared some client/source queue.
        return self.data

    def sort(self):
        """
        Set and return a sorted list of the files
        """
        if self.sorterClass is not None:
            sorter = self.sorterClass(self.files)
            self.sortedFiles = sorter.sort()
        else:
            self.sortedFiles = self.files

        return self.sortedFiles

if __name__ == "__main__":

    """
    (status, output) = commands.getstatusoutput("date")
    print output
    #reader = DiskReader("/home/ib/dads/dan/progProj/pds-nccs/bulletins", validation=True, sorterClass=MultiKeysStringSorter)
    reader = DiskReader("/apps/px/bulletins", 41, validation=True, sorterClass=MultiKeysStringSorter)
    (status, output) = commands.getstatusoutput("date")
    print output
    for file in  reader.files:
       print file
    reader.sort()
    print "************************************ Sorted files *******************************************"
    for file in  reader.sortedFiles:
       print file

    (status, output) = commands.getstatusoutput("date")
    print output
    """
    #iterator = _DirIterator('/apps/px/toto' , True)
    #reader = DiskReader('/apps/px/txq/amis', 20)
    reader = DiskReader('/apps/px/toto', 20, False, 5, False)
    #for file in iterator:
       #print file
    print "List of all files:"
    print reader.files
    reader.sort()
    print reader.files
    for file in reader.files:
       print file
