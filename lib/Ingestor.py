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
# Revision :  2006-05-14 (ingestCollection by MG)
#
#############################################################################################

"""
import sys, os, os.path, string, fnmatch, re, time, signal, stat
import PXPaths
from PXManager import PXManager
from Client import Client
from CacheManager        import CacheManager
from DirectRoutingParser import DirectRoutingParser

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
        self.drp    = None
        self.count  = 0
        self.Mcount = 99999

        if source is not None:
            self.ingestDir = PXPaths.RXQ + self.source.name
            if self.source.type == 'filter' :
               self.ingestDir = PXPaths.FXQ + self.source.name
            self.logger = source.logger
        elif logger is not None:
            self.logger = logger
        self.pxManager = PXManager()              # Create a manager
        self.pxManager.setLogger(self.logger)     # Give the logger to the the manager
        self.pxManager.initNames()                # Set rx and tx names
        self.clientNames = self.pxManager.getTxNames()         # Obtains the list of client's names (the ones to wich we can link files)
        self.filterNames = self.pxManager.getFxNames()         # Obtains the list of filter's names (the ones to wich we can link files)
        if source is not None:
           if self.source.name in self.filterNames : self.filterNames.remove(self.source.name)
        self.sourlientNames = self.pxManager.getTRxNames()     # Obtains the list of sourlient's names (the ones to wich we can link files)
        self.allNames = self.clientNames + self.filterNames + self.sourlientNames # Clients + Sourlients names
        self.clients = {}   # All the Client/Filter/Sourlient objects
        self.dbDirsCache = CacheManager(maxEntries=200000, timeout=25*3600)      # Directories created in the DB
        self.clientDirsCache = CacheManager(maxEntries=100000, timeout=2*3600)   # Directories created in TXQ
        self.feedNames = []  # source to feed
        self.feeds = {}
        if source is not None:
           self.logger.info("Ingestor (source %s) can link files to clients: %s" % (source.name, self.allNames))

    def setFeeds(self, feedNames ):
        from Source import Source
        sources = self.pxManager.getRxNames()
        for name in feedNames :
            if not name in sources : continue
            instant = Source(name, self.logger, False)
            if instant.type == 'am' or instant.type == 'wmo' :
               self.logger.warning("Feed (source %s) will be ignored  (type %s)" % (name, instant.type) )
               continue
            self.feedNames.append(name)
            self.feeds[name] = instant
        self.logger.info("Ingestor (source %s) can link files to receiver: %s" % (self.source.name, self.feedNames))

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
        from Source    import Source
        from Sourlient import Sourlient
        for name in self.clientNames:
            self.clients[name] = Client(name, self.logger)
        for name in self.filterNames :
            self.clients[name] = Source(name, self.logger, False, True)
        for name in self.sourlientNames:
            self.clients[name] = Sourlient(name, self.logger, False)
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

    def getClientQueueName(self, clientName, ingestName, priority=None):
        """
        Return the directory into which a file of a given priority should be placed.
        Layout used is: /apps/px/txq/<client>/<priority>/YYYYmmddhh
        """
        parts = ingestName.split(':')
        if not priority:
            priority = parts[4].split('.')[0]

        clientpathName = PXPaths.TXQ + clientName + '/' + str(priority) + '/' + time.strftime("%Y%m%d%H", time.gmtime()) + '/' + ingestName

        if clientName in self.filterNames :
           clientpathName = PXPaths.FXQ + clientName + '/' + ingestName

        return clientpathName

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

    def getRouteKey(self, filename):
        """
        Given an ingest name, return a route key based on the imask given
        """
        # check against the masks
        for mask in self.source.masks:

            # accept/imask
            if len(mask) == 3 :
               parts = re.findall( mask[0], filename )
               if len(parts) == 2 and parts[1] == '' : parts.pop(1)
               if len(parts) != 1 : continue
               key = parts[0]
               if isinstance(parts[0],tuple) : key = '_'.join(parts[0])
               self.logger.debug("RouteKey Key = %s  Mask = %s  Filename = %s" % (key,mask[0],filename) )
               return key

            # reject/emask
            else  :
               parts = re.findall( mask[0], filename )
               if len(parts) == 2 and parts[1] == '' : parts.pop(1)
               if len(parts) == 1 : return None
 
        # fallback behavior 
        return None

    def isMatching(self, client, ingestName):
        """
        Verify if ingestName is matching one mask of a client
        """
        from Source import Source

        if len(client.masks_deprecated) > 0 :
           for mask in client.masks_deprecated:
               if fnmatch.fnmatch(ingestName, mask[0]):
                   try:
                       if mask[2]:
                           return True
                   except:
                       return False

        for mask in client.masks:
            parts = re.findall( mask[0], ingestName )
            if len(parts) == 2 and parts[1] == '' : parts.pop(1)
            if len(parts) == 1 :
               if len(mask) == 3 : return True
               return False

        if isinstance(client,Source) : return True

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

    def getMatchingFeedNamesFromMasks(self, ingestName, potentialFeedNames):
        matchingFeedNames = []
        for name in potentialFeedNames:
            try:
                if self.feeds[name].fileMatchMask(ingestName):
                   matchingFeedNames.append(name)
            except KeyError:
                pass
        return matchingFeedNames

    def ingest(self, receptionName, ingestName, clientNames, priority=None ):
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
            clientQueueName = self.getClientQueueName(name, ingestName, priority)
            self.createDir(os.path.dirname(clientQueueName), self.clientDirsCache)
            #try:
            #    os.link(dbName, clientQueueName)
            #except OSError:
            #    (type, value, tb) = sys.exc_info()
            #    self.logger.error("Unable to link %s %s, Type: %s, Value: %s" % (dbName, clientQueueName, type, value))
            os.link(dbName, clientQueueName)

        feedNames = []
        if len(self.feedNames) > 0 :
           feedNames = self.getMatchingFeedNamesFromMasks(ingestName, self.feedNames )
           self.logger.debug("Matching (from patterns) feed names: %s" % feedNames )

        for name in feedNames:
            if name in clientNames : continue
            sourceQueueName = PXPaths.RXQ + name + '/' + ingestName
            self.createDir(os.path.dirname(sourceQueueName), self.clientDirsCache)
            os.link(dbName, sourceQueueName)

        self.logger.info("Queued for: %s" % string.join(clientNames) + ' ' + string.join(feedNames) )
        return 1
    
    def run(self):
        if self.source.type == 'single-file':
            self.ingestSingleFile()
        elif self.source.type == 'bulletin-file':
            self.ingestBulletinFile()
        elif self.source.type == 'collector':
            self.ingestCollection()

    def ingestSingleFile(self, igniter):
        from DiskReader import DiskReader
        from DirectRoutingParser import DirectRoutingParser

        if self.source.routemask :
           self.drp = DirectRoutingParser(self.source.routingTable, self.allNames, self.logger, self.source.routing_version)
           self.drp.parse()

        reader = DiskReader(self.ingestDir, self.source.batch, self.source.validation, self.source.patternMatching,
                            self.source.mtime, False, self.source.logger, self.source.sorter, self.source)

        while True:
            if igniter.reloadMode == True:
                # We assign the defaults, reread configuration file for the source
                # and reread all configuration file for the clients (all this in __init__)
                self.source.__init__(self.source.name, self.source.logger)

                if self.source.routemask :
                   self.drp = DirectRoutingParser(self.source.routingTable, self.allNames, self.logger)
                   self.drp.parse()

                reader = DiskReader(self.ingestDir, self.source.batch, self.source.validation, self.source.patternMatching,
                                    self.source.mtime, False, self.source.logger, self.source.sorter, self.source)
                self.logger.info("Receiver has been reloaded")
                igniter.reloadMode = False
            reader.read()
            if len(reader.sortedFiles) <= 0:
               time.sleep(1)
               continue

            sortedFiles = reader.sortedFiles[:self.source.batch]
            self.logger.info("%d files will be ingested" % len(sortedFiles))

            for filex in sortedFiles:
                file = filex

                # converting the file if necessary
                if self.source.execfile != None :

                   fxfile = self.source.run_fx_script(file,self.source.logger)

                   # convertion did not work
                   if fxfile == None :
                          self.logger.warning("FX script ignored the file : %s"    % os.path.basename(file) )
                          os.unlink(file)
                          continue

                   # file already in proper format
                   elif fxfile == file :
                          self.logger.warning("FX script kept the file as is : %s" % os.path.basename(file) )

                   # file converted...
                   else :
                          self.logger.info("FX script modified %s to %s " % (os.path.basename(file),fxfile) )
                          os.unlink(file)
                          file = fxfile

                # filename to ingest

                ingestName = self.getIngestName(os.path.basename(file))

                # usual clients

                potentials = self.clientNames + self.filterNames

                # routing clients and priority (accept mask + routing info)

                priority = None
                if self.source.routemask :
                   potentials = []
                   key = self.getRouteKey(ingestName)
                   if key != None :
                      lst = self.drp.getClients(key)
                      if lst != None : potentials = lst
                      priority = self.drp.getHeaderPriority(key)

                # ingesting the file
                matchingClients  = self.getMatchingClientNamesFromMasks(ingestName, potentials )
                self.logger.debug("Matching (from patterns) client names: %s" % matchingClients)
                self.ingest(file, ingestName, matchingClients, priority )
                os.unlink(file)

    def ingestBulletinFile(self, igniter):
        from DiskReader import DiskReader
        import bulletinManager

        bullManager = bulletinManager.bulletinManager(
                    PXPaths.RXQ + self.source.name,
                    self.logger,
                    PXPaths.RXQ + self.source.name,
                    9999,
                    '\n',
                    self.source.extension,
                    PXPaths.ROUTING_TABLE,
                    self.source.mapEnteteDelai,
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
                               9999,
                               '\n',
                               self.source.extension,
                               PXPaths.ROUTING_TABLE,
                               self.source.mapEnteteDelai,
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

    def ingestCollection(self, igniter):
        from DiskReader import DiskReader
        import bulletinManager
        import CollectionManager

        bullManager = bulletinManager.bulletinManager(
                    PXPaths.RXQ + self.source.name,
                    self.logger,
                    PXPaths.RXQ + self.source.name,
                    9999,
                    '\n',
                    self.source.extension,
                    PXPaths.ROUTING_TABLE,
                    self.source.mapEnteteDelai,
                    self.source)

        reader = DiskReader(bullManager.pathSource, self.source.batch, self.source.validation, self.source.patternMatching,
                            self.source.mtime, False, self.source.logger, self.source.sorter)

        collect = CollectionManager.CollectionManager( self, bullManager, reader )

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
                               9999,
                               '\n',
                               self.source.extension,
                               PXPaths.ROUTING_TABLE,
                               self.source.mapEnteteDelai,
                               self.source)
                reader = DiskReader(bullManager.pathSource, self.source.batch, self.source.validation, self.source.patternMatching,
                                    self.source.mtime, False, self.source.logger, self.source.sorter)
                collect = CollectionManager.CollectionManager( self, bullManager, reader )

                self.logger.info("Receiver has been reloaded")
                igniter.reloadMode = False

            collect.process()

            time.sleep(20)

    
if __name__ == '__main__':
    pass
