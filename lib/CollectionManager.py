# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: CollectionManager.py
#       
# Authors: Michel Grenier
#
# Date: 2006-05-16
#
# Description: yet another implementation of a collection...
#
#############################################################################################

"""

import bulletin
import os,string,sys,time
import PXPaths
import CollectionBuilder
import CollectionEntry
import CollectionState
import StationParser

from CacheManager import CacheManager

PXPaths.normalPaths()              # Access to PX paths

# CollectionManager

class CollectionManager(object):
    """
    The collectionManager reads RXQ dir, classifies the bulletins:
    If they have to be ingested do it, if they have to be collected than collect and ingest.
    Unrelated files are removed. Files that are not ready to be collected stay in the RXQ dir.
    """

    def __init__(self, ingestor, bullManager, reader ):
        
        # General Attributes

        self.bullManager   = bullManager
        self.ingestor      = ingestor
        self.logger        = ingestor.logger
        self.reader        = reader
        self.source        = ingestor.source

        self.files         = []
        self.data          = []
        self.entry         = None

        self.now           = time.mktime(time.localtime())

        # a cacheManager to make sure we process a file only once

        self.cacheManager  = CacheManager(maxEntries=250000, timeout=int(self.source.history)*3600)

        # reading the collection station config file...

        sp = StationParser.StationParser(PXPaths.STATION_TABLE)
        sp.parse()
        self.mapCollectionStation = sp.getStationsColl()

        # instantiate the collection state class

        self.collectionState    = CollectionState.CollectionState( self )
        self.getState           = self.collectionState.getState
        self.setState           = self.collectionState.setState
        self.updateState        = self.collectionState.updateCollectionState

        # instantiate the collection builder class

        self.collectionBuilder = CollectionBuilder.CollectionBuilder( self )
        self.collectionBuild   = self.collectionBuilder.process

    #-----------------------------------------------------------------------------------------
    # check if the bulletin is defined in the collection_station dictionnary
    #-----------------------------------------------------------------------------------------

    def conformWithStationDictionary( self ):

        # working variables

        dict    = PXPaths.STATION_TABLE
        dictkey = self.entry.dictkey
        path    = self.entry.path
        station = self.entry.station

        # check if header found in the dictionnary

        if not dictkey in self.mapCollectionStation :
           self.logger.warning("Reject %s : (%s) not in %s" % (path,dictkey,dict) )
           self.unlink(path)
           return False

        # check if the station was found in bulletin

        if station == None :
           self.logger.warning("Reject %s : station %s not found" % (path,station) )
           self.unlink(path)
           return False

        # check if the station is defined in the dictionnary

        station_list = self.mapCollectionStation[dictkey]
        if not station in station_list :
           self.logger.warning("Reject %s : station %s not defined for %s in %s" % (path,station,dictkey,dict) )
           self.unlink(path)
           return False

        return True

    #-----------------------------------------------------------------------------------------
    # check if the bulletin is defined in the collecteur's configuration 
    #-----------------------------------------------------------------------------------------

    def conformWithSourceConfig( self ):

        # working variables

        bulltin = self.entry.bulletin
        data    = self.entry.data
        path    = self.entry.path
        type    = self.entry.type
        BBB     = self.entry.BBB

        name    = self.source.name

        # get bulletin type and check if configured collectable, if not ignore

        pos     = -1
        try     : pos = self.source.headers.index(type)
        except  :
                  # if bulletin type not configured collectable ignore it
                  self.logger.warning("Reject %s : (%s) not define in %s.conf header" % (path,type,name) )
                  self.unlink(path)
                  return False

        self.entry.sourceidx = pos

        # get the bulletin emission and check if time ok
        # specs says : if time not collectable or minute != 00  ingest NOW

        hour   = bulltin.emission[ 8:10]
        minute = bulltin.emission[10:12]

        if self.source.issue_hours[pos][0] != 'all' and not hour in self.source.issue_hours[pos] :
           self.logger.info("Forced ingestion (time) %s" % path )
           self.ingest(data)
           self.unlink(path)
           return False

        if minute != '00' :
           self.logger.info("Forced ingestion (time) %s" % path )
           self.ingest(data)
           self.unlink(path)
           return False

        # check if the bulletin is too early

        history = 3600 * self.source.history
        future  = -60  * self.source.future

        if bulltin.delay < future :
           self.logger.warning("Reject %s : arrived earlier than permitted (%d)" % (path,bulltin.delay) )
           self.unlink(path)
           return False

        # check if the bulletin is too old

        if bulltin.delay > history :
           self.logger.info("Forced ingestion (too old) %s" % path )
           self.ingestX(self.entry,'Z')
           self.unlink(path)
           return False

        # compute primary and cycle in secs

        primary = 60 * int(self.source.issue_primary[pos])
        cycle   = 60 * int(self.source.issue_cycle[pos])

        # if the bulletin is in its primary period
        # do nothing if it is not time for collection

        if bulltin.delay  < primary :
           if bulltin.age < primary :
              self.logger.debug("File %s will be primary soon" % path )
              return False
           self.entry.period = 0
           return True

        # the bulletin is in one of its cycle period : compute the period and time of collection

        self.entry.period = int((bulltin.delay - primary ) / cycle + 1)
        timeOfCollection  = primary + self.entry.period  * cycle

        # we can collect

        if bulltin.age >= timeOfCollection  : return True

        # it's not time to collect and the bulletin is regular or a repeat: do nothing

        if BBB == None or BBB[0] == 'R' :
           self.logger.debug("File %s will be cycle soon" % path )
           return False

        # still not time to collect BUT AT THIS POINT
        # we have an AMD or COR during one of its cycle... ingest !

        return True

    #-----------------------------------------------------------------------------------------
    # ingest one bulletin's data
    #-----------------------------------------------------------------------------------------

    def ingest( self, data ):

        self.bullManager.writeBulletinToDisk(data, True, True)

    #-----------------------------------------------------------------------------------------
    # ingestX : ingest one bulletin with a BBB having its last letter as X
    #-----------------------------------------------------------------------------------------

    def ingestX( self, entry, X ):

        # working variables

        bulltin = entry.bulletin
        BBB     = entry.BBB
        data    = entry.data
        header  = entry.header

        # create its new BBB

        cBBB = ''

        if   BBB    == None : cBBB = 'RR' + X
        elif BBB[0] == 'A'  : cBBB = 'AA' + X
        elif BBB[0] == 'C'  : cBBB = 'CC' + X
        else                : cBBB = 'RR' + X

        # rebuild data with new header

        data  = header[0] + ' ' + header[1] + ' ' + header[2] + ' ' + cBBB + '\n'
        data += string.join(bulltin.bulletin[1:],'\n')

        # ingest

        self.ingest(data)

    #-----------------------------------------------------------------------------------------
    # collection process
    #-----------------------------------------------------------------------------------------

    def process( self ):

        # setting current time
        # it is very important to set this only once for the duration of the process

        self.now = time.mktime(time.localtime())

        # updating the collection state map

        self.updateState(self.now)

        # read it all 
        # NOTE : it is important not to restrict the reading 
        #        so these lines don't use the batch option from config

        self.reader.read()

        self.logger.info("%d files in queue" % len(self.reader.sortedFiles))

        # no files : call the collectionBuilder for empty primary collection...

        if len(self.reader.sortedFiles) <= 0 : 
           self.collectionBuild(self.now)
           return

        # working variables

        self.data  = self.reader.getFilesContent()
        self.files = self.reader.sortedFiles

        # loop on all files

        for index in range(len(self.data)):

            # if the bulletin was already processed... skip it

            if self.cacheManager.has( self.data[index] ) :
               self.logger.info("File %s was cached earlier" % self.files[index] )
               self.unlink(self.files[index])
               continue

            # bulletinCollection is a class to hold bulletin if it has to be collected

            self.entry = CollectionEntry.CollectionEntry()

            # generate bulletin, set its arrival, its age ... save it into a list
            # TODO... if we have to set its arrival from clock than the file should
            #         be renamed with a few ":" and the arrival string date at the end

            bulltin = bulletin.bulletin(self.data[index],self.logger)

            try     : bulltin.setArrivalStr(self.files[index].split(':')[6])
            except  : bulltin.setArrivalEp (self.now)

            bulltin.compute_Age(self.now)

            # check if bulletin and all its date are ok

            if bulltin.errorBulletin != None or \
               bulltin.arrival       == None or bulltin.emission      == None or \
               bulltin.delay         == None or bulltin.age           == None or \
               bulltin.ep_arrival    ==   -1 or bulltin.ep_emission   ==   -1  :
               self.logger.warning("File %s had a problem...(most probably date)" % self.files[index] )
               self.unlink(self.files[index])
               continue

            # put info in bulletinCollection entry

            self.entry.path      = self.files[index]
            self.entry.data      = self.data[index]

            self.entry.bulletin  = bulltin
            self.entry.header    = bulltin.getHeader().split()
            self.entry.type      = bulltin.getType()
            self.entry.BBB       = bulltin.getBBB()
            self.entry.station   = bulltin.getStation()

            self.entry.dictkey   = self.entry.header[0] + ' ' + self.entry.header[1]
            self.entry.statekey  = self.entry.header[0] + '_' + self.entry.header[1]  + '_' + self.entry.header[2]

            # info initialize and set later

            self.entry.sourceidx = -1
            self.entry.period    = -1

            # check if the bulletin is defined in the collection_station dictionnary

            if not self.conformWithStationDictionary( ) : continue

            # check if the bulletin is defined in the collecteur's configuration 

            if not self.conformWithSourceConfig( ) : continue

            # check if the bulletin is not in conflict with its collection state

            self.addToCollectionState( index )

        # all files are classified... build collections if needed
        # saving the collection state map if needed

        self.collectionBuild(self.now)

    #-----------------------------------------------------------------------------------------
    # add the bulletin to the collection state map
    #-----------------------------------------------------------------------------------------

    def addToCollectionState( self, index ):

        # working variables

        path    = self.entry.path
        header  = self.entry.header
        BBB     = self.entry.BBB
        key     = self.entry.statekey

        # get MapCollectionState value

        ( period, amendement, correction, retard, Primary, Cycle ) = self.getState(key)

        # the bulletin is not a primary

        if self.entry.period >  0 :
           Cycle.append(self.entry)
           self.logger.debug("File %d %s : classified as Cycle" % (index,path) )
           self.setState( key, period, amendement, correction, retard, Primary, Cycle )
           return

        # the bulletin is primary
        # we have a problem if its primary collection was done...
        # some possibilities : we were in recovery mode and some files were moved after a collecteur iteration
        #                      we did not process enough files check the source.batch value

        if period == 0 :
           self.logger.warning("Reject %d %s : primary already done" % (index,path) )
           self.unlink(path)
           return

        # primary bulletin are splitted...
        # normal and repeated       are place in Primary
        # amendement and correction are place in Cycle
        # the primary is collected and ingested first than
        # the entries in cycle are ingested per period order 0,1,...
        # this garanty that AMD and COR (even primary) are sent after 
        # the primary collection

        if    BBB    == None :
              Primary.append(self.entry)
              self.logger.debug("File %d %s : classified as Primary" % (index,path) )

        elif  BBB[0] == 'R'  :
              Primary.append(self.entry)
              self.logger.debug("File %d %s : classified as Primary" % (index,path) )

        else                 : 
              Cycle.append(self.entry)
              self.logger.debug("File %d %s : classified as Cycle  " % (index,path) )

        self.setState( key, period, amendement, correction, retard, Primary, Cycle )

    #-----------------------------------------------------------------------------------------
    # unlink a file
    #-----------------------------------------------------------------------------------------

    def unlink( self, path ):

        try:
               os.unlink(path)
               self.logger.debug("%s has been erased", os.path.basename(path))
        except OSError, e:
               (type, value, tb) = sys.exc_info()
               self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (path, type, value))

if __name__ == '__main__':
    pass
