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

        self.bulletins     = []
        self.files         = []
        self.data          = []
        self.entry         = None

        self.now           = time.mktime(time.localtime())

        # reading the collection station config file...

        self.pathCollectionStation = PXPaths.ETC + 'stations.conf'
        sp = StationParser.StationParser(self.pathCollectionStation)
        sp.parse()
        self.mapCollectionStation = sp.getStationsColl()

        # instantiate the collection state class

        self.mapCollectionState = {}
        self.collectionState    = CollectionState.CollectionState( self )
        self.mapCollectionState = self.collectionState.getCollectionState()

        # instantiate the collection builder class

        self.collectionBuilder = CollectionBuilder.CollectionBuilder( self )

    #-----------------------------------------------------------------------------------------
    # check if the bulletin is defined in the collection_station dictionnary
    #-----------------------------------------------------------------------------------------

    def conformWithStationDictionary( self, index ):

        # check if header found in the dictionnary

        if not self.entry.dictkey in self.mapCollectionStation :
           self.ignore(index,"File %s ignored : (%s) not defined in collection_station dictionnary" % \
                      (self.files[index],self.entry.dictkey) )
           return False

        # check if the station was found in bulletin

        if self.entry.station == None :
           self.ignore(index,"File %s ignored : station not found" % self.files[index] )
           return False

        # check if the station is defined in the dictionnary

        slist = self.mapCollectionStation[self.entry.dictkey]
        if not self.entry.station in slist :
           self.ignore(index,"File %s ignored : station(%s) not defined in collection_station dictionnary for %s" % \
                      (self.files[index],self.entry.station,self.entry.dictkey) )
           return False

        return True

    #-----------------------------------------------------------------------------------------
    # check if the bulletin is defined in the collecteur's configuration 
    #-----------------------------------------------------------------------------------------

    def conformWithSourceConfig( self, index ):

        bulltin = self.bulletins[index]

        # get bulletin type and check if configured collectable, if not ignore

        pos     = -1
        type    = bulltin.getType()
        try     : pos = self.source.headers.index(type)
        except  :
                  # if bulletin type not configured collectable ignore it
                  self.ignore(index,"File %s ignored : (%s)  not a collectable type" % (self.files[index],type) )
                  return False

        # get the bulletin emission and check if time ok
        # specs says : if time not collectable or minute != 00  ingest NOW

        hour   = bulltin.emission[ 8:10]
        minute = bulltin.emission[10:12]

        if self.source.issue_hours[pos][0] != 'all' and not hour in self.source.issue_hours[pos] :
           self.ingest(index,None,"File %s ingested : (%s) not a collectable time" % (self.files[index],hour+minute) )
           return False

        if minute != '00' :
           self.ingest(index,None,"File %s ingested : (%s) not a collectable time" % (self.files[index],hour+minute) )
           return False

        # check if the bulletin is too early or too old in regards of his emission

        history = 3600 * self.source.history
        future  = -60  * self.source.future

        if bulltin.delay < future :
           self.ignore(index,"File %s ignored : received (%s) emission (%s) so out of its collecting period" % \
                      (self.files[index],bulltin.arrival,bulltin.emission) )
           return False

        header = self.entry.header
        BBB    = self.entry.BBB

        if bulltin.delay > history :

           cBBB = ''
           if bulltin.delay > history :
              if   BBB    == None : cBBB = 'RRZ'
              elif BBB[0] == 'A'  : cBBB = 'AAZ'
              elif BBB[0] == 'C'  : cBBB = 'CCZ'
              else                : cBBB = 'RRZ'

           data = header[0] + ' ' + header[1] + ' ' + header[2] + ' ' + cBBB + '\n'

           istart = 1
           if header[0][:2] == 'SM' or header[0][:2] == 'SI' :
              data += 'AAXX\n'
              if bulltin.bulletin[1][0:4] == 'AAXX' : istart = 2

           data += string.join(bulltin.bulletin[istart:],'\n')

           self.ingest(index,data,"File %s ingested but out received more than %s hours late "  % \
                      (self.files[index],self.source.history) )
           return False

        # if bulletin is primary but it is not the time to collect ...
        # do nothing but say False because it is unusable for now

        primary = 60 * int(self.source.issue_primary[pos])
        cycle   = 60 * int(self.source.issue_cycle[pos])
        period  = 0

        if bulltin.delay  < primary :
           if bulltin.age < primary : return False

        # we are into a cycle period for collection but it is not the time to transmit ...
        # do nothing but say False because it is unusable for now

        else :
          period  = int((bulltin.delay - primary ) / cycle + 1)
          timeforcycle = primary + period * cycle
          if bulltin.age < timeforcycle : 
             if BBB == None or BBB[0] == 'R' : return False

        # still collectable...
        # put info in bulletinCollection entry

        self.entry.period = period

        return True

    #-----------------------------------------------------------------------------------------
    # ignore a file ( log a message, unlink file)
    #-----------------------------------------------------------------------------------------

    def ignore( self, index, msg  ):

        self.logger.info(msg)

        path = self.files[index]

        try:
               os.unlink(path)
               self.logger.debug("%s has been ignored (erased)", os.path.basename(path))
        except OSError, e:
               (type, value, tb) = sys.exc_info()
               self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (path, type, value))

    #-----------------------------------------------------------------------------------------
    # direct bulletin ingestion ( log a message, ingest normally)
    #-----------------------------------------------------------------------------------------

    def ingest( self, index, data, msg  ):

        self.logger.info(msg)

        path = self.files[index]

        if data == None : data = self.data[index]

        self.bullManager.writeBulletinToDisk(data, True, True)

        try:
                os.unlink(path)
                self.logger.debug("%s has been erased", os.path.basename(path))
        except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (path, type, value))

    #-----------------------------------------------------------------------------------------
    # collection process
    #-----------------------------------------------------------------------------------------

    def process( self ):

        # setting current time
        # it is very important to set this only once for the duration of the process

        self.now = time.mktime(time.localtime())

        # setting the collection state map

        self.mapCollectionState = self.collectionState.getCollectionState()

        # read it all 
        # NOTE : it is important not to restrict the reading 
        #        so these lines don't use the batch option from config

        self.reader.read()

        if len(self.reader.sortedFiles) <= 0 : 
           changed = self.collectionBuilder.process()
           if changed :
              self.collectionState.mapCollectionState = self.mapCollectionState
              self.collectionState.saveCollectionState()
           return

        self.bulletins = []
        self.data      = self.reader.getFilesContent()
        self.files     = self.reader.sortedFiles

        # loop on all files

        for index in range(len(self.data)):

            # bulletinCollection is a class to hold bulletin if it has to be collected

            self.entry = CollectionEntry.CollectionEntry()

            # generate bulletin, set its arrival, its age ... save it into a list
            # TODO... if we have to set its arrival from clock than the file should
            #         be renamed with a few ":" and the arrival string date at the end

            bulltin = bulletin.bulletin(self.data[index],self.logger)

            try     : bulltin.setArrivalStr(self.files[index].split(":")[6])
            except  : bulltin.setArrivalEp (self.now)

            bulltin.compute_Age(self.now)

            self.bulletins.append(bulltin)

            # put info in bulletinCollection entry

            self.entry.path     = self.files[index]
            self.entry.data     = self.data[index]
            self.entry.bulletin = bulltin
            self.entry.index    = index

            self.entry.header   = bulltin.getHeader().split()
            self.entry.BBB      = bulltin.getBBB()
            self.entry.station  = bulltin.getStation()
            self.entry.dictkey  = self.entry.header[0] + ' ' + self.entry.header[1]

            # check if the bulletin is defined in the collection_station dictionnary

            if not self.conformWithStationDictionary( index ) : continue

            # check if the bulletin is defined in the collecteur's configuration 

            if not self.conformWithSourceConfig( index ) : continue

            # check if the bulletin is not in conflict with its collection state

            self.addToCollectionState( index )

        # all files are classified... build collections if needed

        changed = self.collectionBuilder.process()

        # saving the collection state map

        if changed :
                     self.collectionState.mapCollectionState = self.mapCollectionState
                     self.collectionState.saveCollectionState()

    #-----------------------------------------------------------------------------------------
    # add the bulletin to the collection state map
    #-----------------------------------------------------------------------------------------

    def addToCollectionState( self, index ):

        bulltin = self.bulletins[index]
        header  = self.entry.header
        BBB     = bulltin.getBBB()
        key     = header[0] + '_' + header[1] + '_' + header[2]

        self.entry.BBB      = BBB
        self.entry.statekey = key

        # if first bulletin for that state just create and add MapCollectionState value

        if not key in self.mapCollectionState :

           period      = -1
           amendement  = -1
           correction  = -1
           retard      = -1
           Primary     = []
           Cycle       = []

           self.mapCollectionState[key] = (period,amendement,correction,retard,Primary,Cycle)

        # get MapCollectionState value and make some verifications
        # if the bulletin is in the primary period and the primary was ingested
        # we have a problem... recovery mode did not work properly or 
        # we did not process enough files check source.batch value

        ( period, amendement, correction, retard, Primary, Cycle ) = self.mapCollectionState[key]

        if period == 0 and self.entry.period == 0 :
           self.ignore(index,"File %s ignored : primary collection already done, maybe batch not big enough" % \
                       self.files[index] )
           return False

        # the bulletin is not in the primary period ... put it in Cycle

        if self.entry.period >  0 :
           Cycle.append(self.entry)

        # the bulletin is in Primary period :
        # normal and repeated       are place in Primary
        # amendement and correction are place in Cycle

        else :
           if    BBB    == None : Primary.append(self.entry)
           elif  BBB[0] == 'R'  : Primary.append(self.entry)
           else                 : Cycle.append(self.entry)

        return True

if __name__ == '__main__':
    pass
