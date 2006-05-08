"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Ingestor.py
#       
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#
# Date: 2005-01-10 (Initial version by PS)
#       2005-08-21 (OO version by DL)
#
# Description:
#
#############################################################################################

"""
import sys, os, os.path, string, fnmatch, time, signal, stat
import PXPaths
from PXManager import PXManager
from Client import Client
from CacheManager import CacheManager

PXPaths.normalPaths()              # Access to PX paths

class Ingestor(object):
    """
    Normally, an Ingestor will be in a Source. It can also be used for the only reason that this object has
    access to all the configuration options of the clients. For this particular case, source=None.
    """

    def __init__(self, source=None, logger=None):
        
        # General Attributes
        self.source = source
        self.reader = None
        if source is not None:
            self.ingestDir = PXPaths.RXQ + self.source.name
            self.logger = source.logger
        elif logger is not None:
            self.logger = logger
        self.pxManager = PXManager()              # Create a manager
        self.pxManager.setLogger(self.logger)     # Give the logger to the the manager
        self.pxManager.initNames()                # Set rx and tx names
        self.clientNames = self.pxManager.getTxNames() # Obtains the list of client's names (the ones to wich we can link files)
        self.soulientNames = self.pxManager.getTRxNames() # Obtains the list of sourlient's names (the ones to wich we can link files)
        self.clients = {}   # All the Client/Sourlient objects
        self.dbDirsCache = CacheManager(maxEntries=200000, timeout=25*3600)      # Directories created in the DB
        self.clientDirsCache = CacheManager(maxEntries=100000, timeout=2*3600)   # Directories created in TXQ
        self.collector = None  # Access to collector configuration options
        if source is not None:
            self.logger.info("Ingestor (source %s) can link files to clients: %s" % (source.name, self.clientNames + self.soulientNames))

    def setCollector(self, name):
        from Source import Source
        self.collector = Source(name, self.logger)

    def createDir(self, dir, cacheManager):
        if cacheManager.find(dir) == None:
            try:
                os.makedirs(dir, 01775)
            except OSError:
                (type, value, tb) = sys.exc_info()
                self.logger.debug("Problem when creating dir (%s) => Type: %s, Value: %s" % (dir, type, value)) 

    def setClients(self):
        """"
        Set a dictionnary of Clients. Main usage will be to access value of 
        configuration options (mainly masks) of the Client objects.
        """
        for name in self.clientNames:
            self.clients[name] = Client(name, self.logger)
        for name in self.soulientNames:
            self.clients[name] = Soulient(name, self.logger)
            #self.clients[name].readConfig()
            #print self.clients[name].masks

    def getIngestName(self, receptionName):
        """
        Map reception name to ingest name, based on the source configuration.

        This just inserts missing fields, like whattopds. DUMB!
        FIXME: Have a library of functions, configurable per source, to
        perform the mapping, perhaps using rmasks ? & other args.
        """
        receptionNameParts = receptionName.split(':')
        extensionParts = self.source.extension.split(':')

        for i in range(1,6):
            if len(receptionNameParts) == i or receptionNameParts[i] == '':
                receptionNameParts = receptionNameParts + [extensionParts[i]]
        receptionNameParts = receptionNameParts + [time.strftime("%Y%m%d%H%M%S", time.gmtime())]
        return string.join(receptionNameParts,':')

    def getClientQueueName(self, clientName, ingestName):
        """
        Return the directory into which a file of a given priority should be placed.
        Layout used is: /apps/px/txq/<client>/<priority>/YYYYmmddhh
        """
        parts = ingestName.split(':')
        priority = parts[4].split('.')[0]
        return PXPaths.TXQ + clientName + '/' + priority + '/' + time.strftime("%Y%m%d%H", time.gmtime()) + '/' + ingestName

    def getDBName(self, ingestName):
        """
        Given an ingest name, return a relative database name

        Given a file name of the form:
            what : ori_system : ori_site : data_type : format :
            link it to:
                db/<today>/data_type/ori_system/ori_site/ingestName
            (same pattern as PDS)

        NB: see notes/tests.txt for why the date/time is recalculated everytime.
        """
        if ingestName.count(':') >= 4:
            today = time.strftime("%Y%m%d", time.gmtime())
            dirs = ingestName.split(':')
            return PXPaths.DB + today + '/' + dirs[3] + '/' + dirs[1] + '/' + dirs[2] + '/' + ingestName
        else:
            return ''

    def isMatching(self, client, ingestName):
        """
        Verify if ingestName is matching one mask of a client
        """
        for mask in client.masks:
            if fnmatch.fnmatch(ingestName, mask[0]):
                try:
                    if mask[2]:
                        return True
                except:
                    return False
        return False

    def getMatchingClientNamesFromMasks(self, ingestName, potentialClientNames):
        matchingClientNames = []
        for name in potentialClientNames:
            try:
                if self.isMatching(self.clients[name], ingestName):
                    matchingClientNames.append(name)
            except KeyError:
                pass
        return matchingClientNames

    def ingest(self, receptionName, ingestName, clientNames):
        self.logger.debug("Reception Name: %s" % receptionName)
        dbName = self.getDBName(ingestName)

        if dbName == '':
            self.logger.warning('Bad ingest name (%s) => No dbName' % ingestName)
            return 0
        
        self.createDir(os.path.dirname(dbName), self.dbDirsCache)
        #try:
        #    os.link(receptionName, dbName)
        #except OSError:
        #    (type, value, tb) = sys.exc_info()
        #    self.logger.error("Unable to link %s %s, Type: %s, Value: %s" % (receptionName, dbName, type, value))
        os.link(receptionName, dbName)

        nbBytes = os.stat(receptionName)[stat.ST_SIZE]

        if self.source.debug:
            self.logger.info("DBDirsCache: %s" % self.dbDirsCache.cache)
            stats, cached, total = self.dbDirsCache.getStats()
            if total:
                percentage = "%2.2f %% of the last %i requests were cached" % (cached/total * 100,  total)
            else:
                percentage = "No entries in the cache"
            self.logger.info("DB Caching stats: %s => %s" % (str(stats), percentage))


            self.logger.debug("ClientDirsCache: %s" % self.clientDirsCache.cache)
            stats, cached, total = self.clientDirsCache.getStats()
            if total:
                percentage = "%2.2f %% of the last %i requests were cached" % (cached/total * 100,  total)
            else:
                percentage = "No entries in the cache"
            self.logger.debug("Client Caching stats: %s => %s" % (str(stats), percentage))

            self.logger.info("Ingestion Name: %s" % ingestName)
            
        self.logger.info("(%i Bytes) Ingested in DB as %s" % (nbBytes, dbName))

        # Problem bulletins are databased, but not sent to clients
        if ingestName.find("PROBLEM_BULLETIN") is not -1:
            return 1

        for name in clientNames:
            clientQueueName = self.getClientQueueName(name, ingestName)
            self.createDir(os.path.dirname(clientQueueName), self.clientDirsCache)
            #try:
            #    os.link(dbName, clientQueueName)
            #except OSError:
            #    (type, value, tb) = sys.exc_info()
            #    self.logger.error("Unable to link %s %s, Type: %s, Value: %s" % (dbName, clientQueueName, type, value))
            os.link(dbName, clientQueueName)

        self.logger.info("Queued for: %s" % string.join(clientNames))
        return 1
    
    def run(self):
        if self.source.type == 'single-file':
            self.ingestSingleFile()
        elif self.source.type == 'bulletin-file':
            self.ingestBulletinFile()

    def ingestSingleFile(self, igniter):
        from DiskReader import DiskReader

        reader = DiskReader(self.ingestDir, self.source.batch, self.source.validation, self.source.patternMatching,
                            self.source.mtime, False, self.source.logger, self.source.sorter, self.source)

        while True:
            if igniter.reloadMode == True:
                # We assign the defaults, reread configuration file for the source
                # and reread all configuration file for the clients (all this in __init__)
                self.source.__init__(self.source.name, self.source.logger)

                reader = DiskReader(self.ingestDir, self.source.batch, self.source.validation, self.source.patternMatching,
                                    self.source.mtime, False, self.source.logger, self.source.sorter, self.source)
                self.logger.info("Receiver has been reloaded")
                igniter.reloadMode = False
            reader.read()
            if len(reader.sortedFiles) >= 1:
                sortedFiles = reader.sortedFiles[:self.source.batch]
                self.logger.info("%d files will be ingested" % len(sortedFiles))
                for file in sortedFiles:
                    ingestName = self.getIngestName(os.path.basename(file)) 
                    matchingClients = self.getMatchingClientNamesFromMasks(ingestName, self.clientNames)
                    self.logger.debug("Matching (from patterns) client names: %s" % matchingClients)
                    self.ingest(file, ingestName, matchingClients)
                    os.unlink(file)
            else:
                time.sleep(1)

    def ingestBulletinFile(self, igniter):
        from DiskReader import DiskReader
        import bulletinManager

        bullManager = bulletinManager.bulletinManager(
                    PXPaths.RXQ + self.source.name,
                    self.logger,
                    PXPaths.RXQ + self.source.name,
                    '/apps/pds/RAW/-PRIORITY',
                    9999,
                    '\n',
                    self.source.extension,
                    PXPaths.ETC + 'header2client.conf',
                    self.source.mapEnteteDelai,
                    self.source.use_pds,
                    self.source)

        reader = DiskReader(bullManager.pathSource, self.source.batch, self.source.validation, self.source.patternMatching,
                            self.source.mtime, False, self.source.logger, self.source.sorter)
        while True:
            # If a SIGHUP signal is received ...
            if igniter.reloadMode == True:
                # We assign the defaults, reread configuration file for the source
                # and reread all configuration file for the clients (all this in __init__)
                self.source.__init__(self.source.name, self.source.logger)
                bullManager = bulletinManager.bulletinManager(
                               PXPaths.RXQ + self.source.name,
                               self.logger,
                               PXPaths.RXQ + self.source.name,
                               '/apps/pds/RAW/-PRIORITY',
                               9999,
                               '\n',
                               self.source.extension,
                               PXPaths.ETC + 'header2client.conf',
                               self.source.mapEnteteDelai,
                               self.source.use_pds,
                               self.source)
                reader = DiskReader(bullManager.pathSource, self.source.batch, self.source.validation, self.source.patternMatching,
                                    self.source.mtime, False, self.source.logger, self.source.sorter)

                self.logger.info("Receiver has been reloaded")
                igniter.reloadMode = False

            reader.read()
            data = reader.getFilesContent(reader.batch)

            if len(data) == 0:
                time.sleep(1)
                continue
            else:
                self.logger.info("%d bulletins will be ingested", len(data))

            # Write (and name correctly) the bulletins to disk, erase them after
            for index in range(len(data)):
                #nb_bytes = len(data[index])
                #self.logger.info("Lecture de %s: %d bytes" % (reader.sortedFiles[index], nb_bytes))
                bullManager.writeBulletinToDisk(data[index], True, True)
                try:
                    os.unlink(reader.sortedFiles[index])
                    self.logger.debug("%s has been erased", os.path.basename(reader.sortedFiles[index]))
                except OSError, e:
                    (type, value, tb) = sys.exc_info()
                    self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (reader.sortedFiles[index], type, value))

    
if __name__ == '__main__':
    pass
