"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Sourlient.py
#
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#
# Date: 2005-01-10 (Initial version by PS)
#       2005-08-21 (OO version by DL)
#
# Description: Used to parse configuration file of transceivers (source and client)
#
#############################################################################################

"""
import sys, os, re, time, fnmatch
sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')

import PXPaths
from Logger import Logger
from Ingestor import Ingestor
from URLParser import URLParser

PXPaths.normalPaths()              # Access to PX paths

class Sourlient(object):

    def __init__(self, name='toto', logger=None, ingestion=True) :

        # General Attributes
        self.name = name                          # Sourlient's name
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'trx_' + name + '.log', 'INFO', 'TRX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger
        self.logger.info("Initialisation of sourlient %s" % self.name)

        self.ingestion = ingestion                # Determine if the Sourlient will have an Ingestor
        self.debug = False                        # If we want sections with debug code to be executed
        self.subscriber = True                    # False if it is a provider

        self.type = 'aftn'                        # Must be in ['aftn']
        self.host = 'localhost'                   # Remote host name (or ip) where to send files
        self.portR = 56550                        # Receiving port
        self.portS = 5160                         # Sending port

        self.stationID = 'SUB'                    # Three letter ID of this process
        self.otherStationID = 'MHS'               # Three letter ID of the other party
        self.address = 'CYHQUSER'                 # AFTN address of this process 
        self.otherAddress = 'CYHQMHSN'            # AFTN address of the other party
        self.digits = 4                           # Number of digits used in the CSN

        self.batch = 100                          # Number of files that will be read in each pass
        self.timeout = 10                         # Time we wait between each tentative to connect
        self.maxLength = 0                        # Max. length of a message... limit use for segmentation, 0 means unused

        self.validation = False                   # Validation of the filename (prio + date)
        self.patternMatching = False              # Verification of the emask and imask of the client before sending a file
        self.nodups = True                        # Check if the file has already been sent (md5sum present in the cache)
        self.mtime = 0                            # Integer indicating the number of seconds a file must not have
                                                  # been touched before being picked

        self.sorter = 'MultiKeysStringSorter'     # Class (or object) used to sort
        self.masks = []                           # All the masks (imask and emask)
        self.collection = None                    # Sourlient do not participate in the collection effort

        # Socket Attributes
        self.port = None 

        self.readConfig()
        
        if self.ingestion:
            if hasattr(self, 'ingestor'):
                # Will happen only when a reload occurs
                self.ingestor.__init__(self)
            else:
                self.ingestor = Ingestor(self)
                self.printInfos(self)
            self.ingestor.setClients()


    def readConfig(self):
        
        def isTrue(s):
            if  s == 'True' or s == 'true' or s == 'yes' or s == 'on' or \
                s == 'Yes' or s == 'YES' or s == 'TRUE' or s == 'ON' or \
                s == '1' or  s == 'On' :
                return True
            else:
                return False

        currentDir = '.'                # Current directory
        currentFileOption = 'WHATFN'    # Under what filename the file will be sent (WHATFN, NONE, etc., See PDS)

        filePath = PXPaths.TRX_CONF +  self.name + '.conf'

        try:
            config = open(filePath, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value))
            return 

        for line in config.readlines():
            words = line.split()
            if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)):
                try:
                    if words[0] == 'imask': self.masks.append((words[1], currentDir, currentFileOption))  
                    elif words[0] == 'emask': self.masks.append((words[1],))
                    elif words[0] == 'subscriber': self.subscriber =  isTrue(words[1])
                    elif words[0] == 'validation': self.validation =  isTrue(words[1])
                    elif words[0] == 'noduplicates': self.nodups =  isTrue(words[1])
                    elif words[0] == 'patternMatching': self.patternMatching =  isTrue(words[1])
                    elif words[0] == 'mtime': self.mtime = int(words[1])
                    elif words[0] == 'sorter': self.sorter = words[1]
                    elif words[0] == 'type': self.type = words[1]
                    elif words[0] == 'maxLength': self.maxLength = int(words[1])
                    elif words[0] == 'host': self.host = words[1]
                    elif words[0] == 'portR': self.portR = int(words[1])
                    elif words[0] == 'portS': self.portS = int(words[1])

                    elif words[0] == 'stationID': self.stationID = words[1]
                    elif words[0] == 'otherStationID': self.otherStationID = words[1]
                    elif words[0] == 'address': self.address = words[1]
                    elif words[0] == 'otherAddress': self.otherAddress = words[1]
                    elif words[0] == 'digits': self.digits = int(words[1])
                    
                    elif words[0] == 'batch': self.batch = int(words[1])
                    elif words[0] == 'debug' and isTrue(words[1]): self.debug = True
                    elif words[0] == 'timeout': self.timeout = int(words[1])
                    elif words[0] == 'timeout_send': self.timeout_send = int(words[1])
                except:
                    self.logger.error("Problem with this line (%s) in configuration file of client %s" % (words, self.name))

        if not self.validation:
            self.sorter = 'None'    # Must be a string because eval will be subsequently applied to this

        config.close()
    

    def _getMatchingMask(self, filename): 
        for mask in self.masks:
            if fnmatch.fnmatch(filename, mask[0]):
                try:
                    if mask[2]:
                        return mask
                except:
                    return None
        return None

    def printInfos(self, client):
        print("==========================================================================")
        print("Name: %s " % client.name)
        print("Type: %s" % client.type)
        print("Subscriber: %s" % client.subscriber)
        print("Host: %s" % client.host)
        print("PortR: %s" % client.portR)
        print("PortS: %s" % client.portS)
        print("Station ID: %s" % client.stationID)
        print("Other Station ID: %s" % client.otherStationID)
        print("Address: %s" % client.address)
        print("Other Address: %s" % client.otherAddress)
        print("Digits: %i" % client.digits)
        print("Batch: %s" %  client.batch)
        print("Max length: %i" % client.maxLength)
        print("Mtime: %i" % client.mtime)
        print("Timeout: %s" % client.timeout)
        print("Sorter: %s" % client.sorter)
        print("Validation: %s" % client.validation)
        print("Pattern Matching: %s" % client.patternMatching)

        print("******************************************")
        print("*       Sourlient Masks                  *")
        print("******************************************")

        for mask in self.masks:
            print mask
        print("==========================================================================")

if __name__ == '__main__':

    #sourlient =  Sourlient('aftn')
    #sourlient.printInfos(sourlient)

    for filename in os.listdir(PXPaths.TRX_CONF):
        if filename[-5:] != '.conf': 
            continue
        else:
            sourlient = Sourlient(filename[0:-5])
            #sourlient.readConfig()
            sourlient.printInfos(sourlient)
