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
        self.reader        = reader

        self.source        = ingestor.source
        self.logger        = ingestor.logger

        self.bulletins     = []
        self.files         = []
        self.data          = []
        self.entry         = None

        self.now           = time.mktime(time.gmtime())

        # reading the collection dictionnary... similar to code in bulletinManagerAm.py

        self.lstCollectionHeader   = []
        self.mapCollectionStation  = {}
        self.pathCollectionStation = PXPaths.ETC + 'collection_stations.conf'
        self.loadCollectionStation()

        # reading/building the collection state...

        self.mapCollectionState = {}
        self.pathCollectionState = PXPaths.RXQ + self.source.name + ".state"
        self.loadCollectionState()

        # instantiate the collection builder class

        self.collectionBuilder = CollectionBuilder.CollectionBuilder( self )

    #-----------------------------------------------------------------------------------------
    # check if the bulletin is defined in the collection_station dictionnary
    #-----------------------------------------------------------------------------------------

    def conformWithStationDictionary( self, index ):

        bulltin = self.bulletins[index]

        # check if header found in the dictionnary

        header = bulltin.getHeader().split()
        key    = header[0] + header[1]

        if not key in self.lstCollectionHeader :
           self.ignore(index,"File %s ignored : (%s) not defined in collection_station dictionnary" % \
                      (self.files[index],key) )
           return False

        # check if the station found in the dictionnary

        station = bulltin.getStation()
        if station == None :
           self.ignore(index,"File %s ignored : station not found" % self.files[index] )
           return False

        slist = self.mapCollectionStation[key]
        if not station in slist :
           self.ignore(index,"File %s ignored : station(%s) not defined in collection_station dictionnary for %s" % \
                      (self.files[index],station,key) )
           return False

        # put info in bulletinCollection entry

        self.entry.header   = header
        self.entry.station  = station
        self.entry.dictkey  = key

        return True

    #-----------------------------------------------------------------------------------------
    # check if the bulletin is defined in the collecteur's configuration 
    #-----------------------------------------------------------------------------------------

    def conformWithSourceConfig( self, index ):

        bulltin = self.bulletins[index]

        # get bulletin type and check if configured collectable

        pos     = -1
        type    = bulltin.getType()
        try     : pos = self.source.headers.index(type)
        except  :
                  # if bulletin type not configured collectable ignore it
                  self.ignore(index,"File %s ignored : (%s)  not a collectable type" % (self.files[index],type) )
                  return False

        # get the bulletin emission and check if time ok

        hour   = bulltin.emission[ 8:10]
        if self.source.issue_hours[pos][0] != 'all' and not hour in self.source.issue_hours[pos] :
           self.ingest(index,"File %s ingested : (%s) not a collectable time" % (self.files[index],hour+minute) )
           return False

        minute = bulltin.emission[10:12]
        if minute != '00' :
           self.ingest(index,"File %s ingested : (%s) not a collectable time" % (self.files[index],hour+minute) )
           return False

        # check if the bulletin is too early or too old in regards of his emission

        history = 3600 * self.source.history
        future  = -60  * self.source.future

        if bulltin.delay > history or bulltin.delay < future :
           self.ignore(index,"File %s ignored : received (%s) emission (%s) so out of its collecting period" % \
                      (self.files[index],bulltin.arrival,bulltin.emission) )
           return False

        # if bulletin is primary but it is not the time to collect ...
        # do nothing but say False for unusable for now

        primary = 60 * int(self.source.issue_primary[pos])
        cycle   = 60 * int(self.source.issue_cycle[pos])
        period  = 0

        if bulltin.delay  < primary :
           if bulltin.age < primary : return False

        # we are into a cycle period for collection but it is not the time to transmit ...

        else :
          period  = int((bulltin.delay - primary ) / cycle + 1)
          timeforcycle = primary + period * cycle
          if bulltin.age < timeforcycle : return False

        # put info in bulletinCollection entry

        self.entry.period  = period

        return True

    #-----------------------------------------------------------------------------------------
    # ignore a file ( log a message, unlink file)
    #-----------------------------------------------------------------------------------------

    def ignore( self, index, msg  ):

        self.logger.info(msg)

        path = self.files[index]

        try:
               #os.unlink(path)
               self.logger.debug("%s has been ignored (erased)", os.path.basename(path))
        except OSError, e:
               (type, value, tb) = sys.exc_info()
               self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (path, type, value))

    #-----------------------------------------------------------------------------------------
    # direct bulletin ingestion ( log a message, ingest normally)
    #-----------------------------------------------------------------------------------------

    def ingest( self, index, msg  ):

        self.logger.info(msg)

        data = self.data[index]
        path = self.files[index]

        self.bullManager.writeBulletinToDisk(data, True, True)

        try:
                #os.unlink(path)
                self.logger.debug("%s has been erased", os.path.basename(path))
        except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (path, type, value))

    #-----------------------------------------------------------------------------------------
    # load the collection state file 
    #-----------------------------------------------------------------------------------------

    def loadCollectionState(self):

        self.mapCollectionState = {}

        # read collection state file
        try   :
                f = open( self.pathCollectionState ,'r')
                lignes = f.readlines()
                f.close()
        except: 
                # build from dbase...
                return
                 
        # process all lines into map info

        for ligne in lignes :
            parse  = ligne.split()
            self.mapCollectionState[ parse[0] ] = [ parse[1], parse[2], parse[3], parse[4], [], [] ]

        # debug
        #for key in self.mapCollectionState:
        #    print(" %s = %s " % (key,self.mapCollectionState[key]) )

    #-----------------------------------------------------------------------------------------
    # load the collection station file 
    # produce sorted header list and a map containing sorted stations
    #-----------------------------------------------------------------------------------------

    def loadCollectionStation(self):

        self.lstCollectionHeader  = []
        self.mapCollectionStation = {}

        # read collection station config
        try   :
                f = open( self.pathCollectionStation ,'r')
                lignes = f.readlines()
                f.close()
        except:
                self.logger.error("File %s : could not open or read " % self.pathCollectionStation )
                exit
                 
        # process all lines into temporary info

        for ligne in lignes :
            parse  = ligne.split()
            header = parse[0]

            # skip comments
            if header[0] == '#' : continue

            # skip undesired headers
            try    : indx = self.source.headers.index(header[0:2])
            except : continue

            # check that the header has no duplicate
            if header in self.mapCollectionStation :
               self.logger.error("File %s : duplicated header %s skipped " % (self.pathCollectionStation,header) )
               continue

            # sort station list
            slist = parse[1:]
            slist.sort()
            if len(slist) == 0 :
               self.logger.error("File %s : header %s contains no station skipped " % \
                                (self.pathCollectionStation,header) )
               continue

            # make sure stations are unique
            smap  = {}
            for s in slist :
                if s in smap :
                   self.logger.warning("File %s : header %s has duplicated station %s skipped " % \
                                      (self.pathCollectionStation,header,s) )
                   continue

            # add new entry
            self.lstCollectionHeader.append(header)
            self.mapCollectionStation[header] = slist

        # sort list of header
        self.lstCollectionHeader.sort()

        # debug
        #for header in self.lstCollectionHeader:
        #   print(" %s = %s " % (header,self.mapCollectionStation[header]) )

    #-----------------------------------------------------------------------------------------
    # collection process
    #-----------------------------------------------------------------------------------------

    def process( self ):

        # setting current time

        self.now = time.mktime(time.gmtime())

        # read it all

        self.reader.read()
        if len(self.reader.sortedFiles) <= 0 : return

        self.data  = self.reader.getFilesContent()
        self.files = self.reader.sortedFiles

        # loop on all files

        for index in range(len(self.data)):

            # bulletinCollection is a class to hold bulletin if it has to be collected

            self.entry = CollectionEntry.CollectionEntry()

            # generate bulletin, set its arrival, its age ... save it into a list

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

            # check if the bulletin is defined in the collecteur's configuration 

            if not self.conformWithSourceConfig( index ) : continue

            # check if the bulletin is defined in the collection_station dictionnary

            if not self.conformWithStationDictionary( index ) : continue

            # check if the bulletin is not in conflict with its collection state

            self.addToCollectionState( index )

            # debug
            self.entry.print_debug()

        self.collectionBuilder.process()

        sys.exit(1)

    #-----------------------------------------------------------------------------------------
    # add the bulletin to the collection state map
    #-----------------------------------------------------------------------------------------

    def addToCollectionState( self, index ):

        bulltin = self.bulletins[index]
        header  = self.entry.header
        BBB     = bulltin.getBBB()
        key     = header[0] + '_' + header[1] + '_' + header[2]

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

        # ALFRED something more with cycle checking ?

        # add it

        if self.entry.period >  0 :
           print(" *****CYCLE 1******** ")
           Cycle.append(self.entry)
        else :
           print(" ****************** BBB = %s " % BBB)
           if    BBB    == None : Primary.append(self.entry)
	   elif  BBB[0] == 'R'  : Primary.append(self.entry)
	   else                 :
                                  print(" *****CYCLE 2******** ")
                                  Cycle.append(self.entry)

        return True

if __name__ == '__main__':
    pass
