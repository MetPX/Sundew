"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Source.py
#
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#
# Date: 2005-01-10 (Initial version by PS)
#       2005-08-21 (OO version by DL)
#       2005-10-28 (mask in source by MG)
#
# Description:
#
# Revision History: 
#               2005-12-15 Added parsing of collection conf file
#############################################################################################

"""
import sys, os, os.path, time, string, commands, re, signal, fnmatch

sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')

import PXPaths
from Logger import Logger
from Ingestor import Ingestor
from URLParser import URLParser

PXPaths.normalPaths()              # Access to PX paths

class Source(object):

    def __init__(self, name='toto', logger=None) :
        
        # General Attributes
        self.name = name                          # Source's name
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'rx_' + name + '.log', 'INFO', 'RX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger
        self.logger.info("Initialisation of source %s" % self.name)

        # Attributes coming from the configuration file of the source
        #self.extension = 'nws-grib:-CCCC:-TT:-CIRCUIT:Direct'  # Extension to be added to the ingest name
        self.debug = False                        # If we want sections with debug code to be executed
        self.batch = 100                          # Number of files that will be read in each pass
        self.masks = []                           # All the masks (imask and emask)
        self.tmasks = []                          # All the transformation maks (timask, temask)
        self.extension = ':MISSING:MISSING:MISSING:MISSING:'   # Extension to be added to the ingest name
        self.type = None                                       # Must be in ['single-file', 'bulletin-file', 'am', 'wmo']
        self.port = None                                       # Port number if type is in ['am', 'wmo']
        self.mapEnteteDelai = None                             #
        self.addSMHeader = False                               #
        self.use_pds = False                                   #
        self.validation = False                                # Validate the filename (ex: prio an timestamp)
        self.patternMatching = True                            # No pattern matching
        self.clientsPatternMatching = True                     # No clients pattern matching
        self.sorter = None                                     # No sorting on the filnames
        self.collection = None                                 # None for no collection, else the name of the collector
        self.mtime = 0                                         # Integer indicating the number of seconds a file must not have 
                                                               # been touched before being picked
        #-----------------------------------------------------------------------------------------
        # Setting up default collection configuration values
        #-----------------------------------------------------------------------------------------
        self.sentCollectionToken = ''     #Dir name token used to identify collections which have been transmitted.
        self.busyCollectionToken = ''     #Dir name token used to identify that a collection is currently being generated.
        self.headersToCollect = []        #Title for report in the form TT from (TTAAii)
        self.headersValidTime = []        #The amount of time in minutes past the hour for which the report is considered on time.
        self.headersLateCycle = []        #Specified in minutes.  After the valid time period, we will check this often for late arrivals.
        self.headersTimeToLive = []       #The amount of time in hours for which the reports will be kept in the collection db.
        self.futureDatedReportWindow = [] #The amount of time in minutes a report may be in the futere and still acceptable.

        #-----------------------------------------------------------------------------------------
        # Parse the configuration file
        #-----------------------------------------------------------------------------------------
        self.readConfig()

        #-----------------------------------------------------------------------------------------
        # Make sure the collection params are valid
        #-----------------------------------------------------------------------------------------
        self.validateCollectionParams()

        if hasattr(self, 'ingestor'):
            # Will happen only when a reload occurs
            self.ingestor.__init__(self)
        else:
            self.ingestor = Ingestor(self)

        self.ingestor.setClients()

        if self.collection:
            self.ingestor.setCollector(self.collection)

        self.printInfos(self)

    def readConfig(self):

        def isTrue(s):
            if  s == 'True' or s == 'true' or s == 'yes' or s == 'on' or \
                s == 'Yes' or s == 'YES' or s == 'TRUE' or s == 'ON' or \
                s == '1' or  s == 'On' :
                return True
            else:
                return False

        filePath = PXPaths.RX_CONF +  self.name + '.conf'
        try:
            config = open(filePath, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value))
            return 

        # current dir and filename could eventually be used
        # for file renaming and perhaps file move (like a special receiver/dispatcher)

        currentDir = '.'                # just to preserve consistency with client : unused in source for now
        currentFileOption = 'WHATFN'    # just to preserve consistency with client : unused in source for now
        currentTransformation = 'GIFFY' # Default transformation for tmasks

        for line in config.readlines():
            words = line.split()
            if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)):
                try:
                    if words[0] == 'extension':
                        if len(words[1].split(':')) != 5:
                            self.logger.error("Extension (%s) for source %s has wrong number of fields" % (words[1], self.name)) 
                        else:
                            self.extension = ':' + words[1]
                    elif words[0] == 'imask': self.masks.append((words[1], currentDir, currentFileOption))
                    elif words[0] == 'emask': self.masks.append((words[1],))
                    elif words[0] == 'timask': self.tmasks.append((words[1], currentTransformation))
                    elif words[0] == 'temask': self.tmasks.append((words[1],))
                    elif words[0] == 'transformation': currentTransformation = words[1]
                    elif words[0] == 'batch': self.batch = int(words[1])
                    elif words[0] == 'type': self.type = words[1]
                    elif words[0] == 'port': self.port = int(words[1])
                    elif words[0] == 'AddSMHeader' and isTrue(words[1]): self.addSMHeader = True
                    elif words[0] == 'patternMatching': self.patternMatching =  isTrue(words[1])
                    elif words[0] == 'clientsPatternMatching': self.clientsPatternMatching =  isTrue(words[1])
                    elif words[0] == 'validation' and isTrue(words[1]): self.validation = True
                    elif words[0] == 'collection': self.collection = words[1] 
                    elif words[0] == 'debug' and isTrue(words[1]): self.debug = True
                    elif words[0] == 'mtime': self.mtime = int(words[1])
                    elif words[0] == 'sorter': self.sorter = words[1]
                    elif words[0] == 'arrival': self.mapEnteteDelai = {words[1]:(int(words[2]), int(words[3]))}
                    elif words[0] == 'sentCollectionToken': self.sentCollectionToken = string.strip(words[1],'\'')
                    elif words[0] == 'busyCollectionToken': self.busyCollectionToken = string.strip(words[1],'\'')
                    elif words[0] == 'header': self.headersToCollect.append(words[1])
                    elif words[0] == 'headerValidTime': self.headersValidTime.append(words[1])
                    elif words[0] == 'headerLateCycle': self.headersLateCycle.append(words[1])
                    elif words[0] == 'headerTimeToLive': self.headersTimeToLive.append(words[1])
                    elif words[0] == 'futureDatedReportWindow': self.futureDatedReportWindow.append(words[1])

                except:
                    self.logger.error("Problem with this line (%s) in configuration file of source %s" % (words, self.name))

        config.close()

        if len(self.masks) > 0 : self.patternMatching = True

        self.logger.debug("Configuration file of source  %s has been read" % (self.name))

    def getTransformation(self, filename):
        for mask in self.tmasks:
            if fnmatch.fnmatch(filename, mask[0]):
                try:
                    return mask[1]
                except:
                    return None
        return None

    def fileMatchMask(self, filename):
    # IMPORTANT NOTE HERE FALLBACK BEHAVIOR IS TO ACCEPT THE FILE
    # THIS IS THE OPPOSITE OF THE CLIENT WHERE THE FALLBACK IS REJECT

        # check against the masks
        for mask in self.masks:
            if fnmatch.fnmatch(filename, mask[0]):
               try:
                    if mask[2]: return True
               except:
                    return False

        # fallback behavior 
        return True

    def printInfos(self, source):
        print("==========================================================================")
        print("Name: %s " % source.name)
        print("Type: %s" % source.type)
        print("Batch: %s" %  source.batch)
        print("Port: %s" % source.port)
        print("Extension: %s" % source.extension)
        print("Arrival: %s" % source.mapEnteteDelai)
        print("addSMHeader: %s" % source.addSMHeader)
        print("Validation: %s" % source.validation)
        print("patternMatching: %s" % source.patternMatching)
        print("mtime: %s" % source.mtime)
        print("Sorter: %s" % source.sorter)
        
        print("******************************************")
        print("*       Source Masks                     *")
        print("******************************************")

        for mask in self.masks:
            print mask

        print("==========================================================================")

        print("******************************************")
        print("*       Source T-Masks                   *")
        print("******************************************")

        for mask in self.tmasks:
            print mask

        print("==========================================================================")

        print("******************************************")
        print("*       Collection Params                *")
        print("******************************************")        

        print("Sent Collection Identifier: %s" % self.sentCollectionToken)
        print("Busy Collection Identifier: %s" % self.busyCollectionToken)

        
        print ("\nHeader  Valid Time  Late Cycle  Time To Live  Future-Dated Time Window")
        for position, header in enumerate(self.headersToCollect):
            print ("%s %7s %11s %12s %13s" % (header,  self.headersValidTime[position], \
            self.headersLateCycle[position], self.headersTimeToLive[position], \
            self.futureDatedReportWindow[position]))
        
        print("==========================================================================")


    def validateCollectionParams(self):
        """ validateCollectionParams(self)

        The purpose of this method is to make sure that the collection config parameters
        are valid.
        """
        if self.type == 'collector':
            #-----------------------------------------------------------------------------------------
            # Check sent collection identifier
            #-----------------------------------------------------------------------------------------
            if self.sentCollectionToken == '':
                self.logger.error("Error: No value given for the 'sentCollectionToken' parameter in configuration file: %s" % (self.name))
                self.terminateWithError()

            #-----------------------------------------------------------------------------------------
            # Check busy collection identifier
            #-----------------------------------------------------------------------------------------
            if self.busyCollectionToken == '':
                self.logger.error("Error: No value given for the 'busyCollectionToken' parameter in configuration file: %s" % (self.name))
                self.terminateWithError()

            #-----------------------------------------------------------------------------------------
            # Check other collection parameters.  All lists below should have the same size
            #-----------------------------------------------------------------------------------------
            if not (len(self.headersToCollect) == len(self.headersValidTime) \
                    == len(self.headersLateCycle) == len(self.headersTimeToLive) \
                    == len(self.futureDatedReportWindow)):
                    self.logger.error("Error: There should be the same number of parameters given for EACH header in Configuration file: %s" % (self.name))
                    self.terminateWithError()

            #-----------------------------------------------------------------------------------------
            # Make sure that headerValidTime is valid
            #-----------------------------------------------------------------------------------------
            for item in self.headersValidTime:
                if (int(item) < 0) or (int(item) > 60):
                    self.logger.error("Error: The given 'headerValidTime' parameter in Configuration file: %s must be between 0 and 60" % (self.name))
                    self.terminateWithError()
            
            #-----------------------------------------------------------------------------------------
            # Make sure that headerLateCycle is valid
            #-----------------------------------------------------------------------------------------
            for item in self.headersLateCycle:
                if (int(item) < 0):
                    self.logger.error("Error: The given 'headerLateCycle' parameter in Configuration file: %s must be positive" % (self.name))
                    self.terminateWithError()

            #-----------------------------------------------------------------------------------------
            # Make sure that futureDatedReportWindow is valid
            #-----------------------------------------------------------------------------------------
            for item in self.futureDatedReportWindow:
                if (int(item) < 0):
                    self.logger.error("Error: The 'futureDatedReportWindow' parameter is given an invalid value in Configuration file: %s" % (self.name))
                    self.terminateWithError()

            #-----------------------------------------------------------------------------------------
            # The headerTimeToLive determines how long (in minutes) collection bulletins will be
            # kept in the ../collection/.. temp db before being cleaned.  This value must be greater 
            # than 24 hours. This is because the temp db is used to keep track of the state of the 
            # collection application and deleting collections younger or equal to 24 hours could
            # jeopardize the validity of the collection's BBB value
            #-----------------------------------------------------------------------------------------
            for item in self.headersTimeToLive:
                if (int(item) <= 24):
                    self.logger.error("Error: The 'headerTimeToLive' parameter must be set to a value greater than 24 in Configuration file: %s" % (self.name))
                    self.terminateWithError()


    def terminateWithError (self):
        """ terminateWithError(self)

        The purpose of this method is to perform cleanup operations and return from the script 
        with an error
        """
        #-----------------------------------------------------------------------------------------
        # perform cleanup before termination
        #-----------------------------------------------------------------------------------------

        #-----------------------------------------------------------------------------------------
        # Terminate this script
        #-----------------------------------------------------------------------------------------
        sys.exit()

      
if __name__ == '__main__':

    """
    source=  Source('tutu')
    #source.readConfig()
    source.printInfos(source)
    source.ingestor.createDir('/apps/px/turton', source.ingestor.dbDirsCache)
    source.ingestor.setClients()
    print source.ingestor.getIngestName('toto:titi:tata')
    print source.ingestor.getClientQueueName('tutu', source.ingestor.getIngestName('toto:titi:tata'))
    print source.ingestor.getDBName(source.ingestor.getIngestName('toto:titi:tata'))
    print source.ingestor.isMatching(source.ingestor.clients['amis'], source.ingestor.getIngestName('toto:titi:tata'))
    print source.ingestor.getMatchingClientNamesFromMasks(source.ingestor.getIngestName('toto:titi:tata'))
    """
    """
    for filename in os.listdir(PXPaths.RX_CONF):
        if filename[-5:] != '.conf': 
            continue
        else:
            source = Source(filename[:-5])
            source.readConfig()
            source.printInfos(source)
            source.ingestor.setClients()
            print source.ingestor.getIngestName('toto')

    """
    source = Source('wmo')
    if source.getTransformation('ALLOxxxxBonjour'): print source.getTransformation('ALLOxxxxBonjour')
    if source.getTransformation('TUTU'): print source.getTransformation('TUTU')
    if source.getTransformation('*Salut*Bonjour'): print source.getTransformation('*Salut*Bonjour')
    
