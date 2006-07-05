# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: CollectionBuilder.py
#       
# Authors: Michel Grenier
#
# Date: 2006-05-16
#
# Description: now that we have classified the collections to do process it
#
#############################################################################################

"""

import bulletin
import os,string,sys,time
import PXPaths
import CollectionEntry

PXPaths.normalPaths()              # Access to PX paths

# CollectionBuilder

class CollectionBuilder(object):
    """
    The collectionBuilder builds and ingest collected bulletins
    """

    def __init__(self, collManager ):
        
        # General Attributes

        self.collManager   = collManager
        self.source        = collManager.source
        self.logger        = collManager.logger
        self.now           = collManager.now
        self.cacheManager  = collManager.cacheManager

        self.ingest        = collManager.ingest
        self.ingestX       = collManager.ingestX
        self.unlink        = collManager.unlink

        self.key           = None
        self.header        = None

        self.period        = -1
        self.amendement    = -1
        self.correction    = -1
        self.retard        = -1
        self.Primary       = []
        self.Cycle         = []

        # collection station and state

        self.mapCollectionStation  = collManager.mapCollectionStation
        self.mapCollectionState    = collManager.mapCollectionState
        self.collectionState       = collManager.collectionState
        self.mapChanged            = False

        # alphabet...

        self.alpha = \
        [ 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z' ]

        # AAXX...

        self.AAXX = [ 'SI', 'SM' ]

        # metar...

        self.metar = \
        [ 'SACN31',  \
          'SACN40', 'SACN41', 'SACN42', 'SACN43', 'SACN44', 'SACN45', 'SACN46', 'SACN47', 'SACN48', 'SACN49', \
          'SACN51', 'SACN52'  ]

    #-----------------------------------------------------------------------------------------
    # cache used files
    #-----------------------------------------------------------------------------------------

    def cache( self, entry ):

        found = self.cacheManager.find(entry.data, 'md5')
        if found != None : 
           self.logger.info("%s used more than once" % entry.path )

    #-----------------------------------------------------------------------------------------
    # getBestStationReport : if we have many bulletins for the same station to put in
    #                        the collection : use the most recent
    #-----------------------------------------------------------------------------------------

    def getBestStationReport( self, station, list ):

        # working variables

        best  =  None
        delay = -99999

        # if the station report more than once... 
        # than pick the most recent i.e the biggest delay

        for entry in list :
            if entry.station == station and entry.bulletin.delay > delay :
               best  = entry
               delay = entry.bulletin.delay

        # return the best

        return best

    #-----------------------------------------------------------------------------------------
    # getCurrentCycle from the Cycle list
    #-----------------------------------------------------------------------------------------

    def getCurrentCycle( self, cycle ):

        clist = []

        # loop on all entry : create a list of the current Cycle

        for entry in self.Cycle :
            if entry.period == cycle : clist.append(entry)

        # comparaison module : concatenated str = reception date + BBB

        def compare(x, y):

            a = x.bulletin.arrival
            b = y.bulletin.arrival

            if x.BBB != None : a += x.BBB
            if y.BBB != None : b += y.BBB

            return cmp(a, b)

        # sort this list according to reception date and BBB value

        clist.sort(compare)

        return clist

    #-----------------------------------------------------------------------------------------
    # increment state for an entry... state can be AMD COR RET
    #-----------------------------------------------------------------------------------------

    def incState( self, entry, kind, state ):

        new_state = state + 1

        #  if we reach 24 its 'Y' ... we are confused so Y is good

        if new_state >= 24 :
           self.logger.debug("%s reached %s limit" % (entry.statekey,kind) )
           new_state  = 24 

        #  if we have no history... we are confused so Y is good

        if self.period < 0 :
           self.logger.debug("%s state confusion for %s no history" % (entry.statekey,kind) )
           new_state  = 24

        return new_state

    #-----------------------------------------------------------------------------------------
    # ingest amendements and corrections if any
    #-----------------------------------------------------------------------------------------

    def ingest_AMD_COR( self, list ):

        # get Amendement and Corrections only

        picked   = []

        for entry in list :
            if entry.BBB == None or entry.BBB[0] == 'R' : continue
            picked.append(entry)

        if len(picked) <= 0 : return

        # ingestion order : ideal world suggest reception time should respect the report's BBB order
        # we hope its mostly true... if not a more complex sorting should be done...

        def compare(x, y):
            a  = x.bulletin.arrival + x.BBB + x.station
            b  = y.bulletin.arrival + y.BBB + y.station
            return cmp(a, b)

        picked.sort(compare)

        # ingest them in that order

        for entry in picked :

            if   entry.BBB[0] == 'A' : 
                 amendement = self.incState(entry,"amendement",self.amendement)
                 if amendement <  24 : self.amendement = amendement
                 X = self.alpha[amendement]

            elif entry.BBB[0] == 'C' :
                 correction = self.incState(entry,"correction",self.correction)
                 if correction <  24 : self.correction = correction
                 X = self.alpha[correction]

            self.ingestX(entry,X)

    #-----------------------------------------------------------------------------------------
    # ingest retarded
    #-----------------------------------------------------------------------------------------

    def ingest_retarded( self, list ):

        # working variables

        header   = self.header
        picked   = []
        stations = {}

        # get retard entries and keep station in list

        for entry in list :
            if entry.BBB == None or entry.BBB[0] == 'R' :
               picked.append(entry)
               stations[entry.station] = 1

        if len(picked) <= 0 : return

        # get the sorted list of unique stations for that collection

        stationlist = stations.keys()
        stationlist.sort()

        # build header

        retard = self.incState(picked[0],"retard",self.retard)
        if retard < 24 : self.retard = retard

        cBBB   = 'RR' + self.alpha[retard]
        data   = header[0] + ' ' + header[1] + ' ' + header[2] + ' ' + cBBB + '\n'

        if header[0][:2] in self.AAXX : data += 'AAXX ' + header[2][:4] + '4\n'

        # add retarded by ordered station ... 

        info=[]

        for station in stationlist :
            best = self.getBestStationReport(station,picked)
            if best == None : continue

            # add report to the collection

            istart = 1
            if header[0][:2] in self.AAXX and best.bulletin.bulletin[1][0:4] == 'AAXX' : istart = 2

            data += string.join(best.bulletin.bulletin[istart:],'\n')
            info.append(best.path)

        # ingest that collection

        self.ingest(data)

        # log how many files used for that collection

        self.logger.info("Used %d files for that collection" % len(picked) )

        if len(picked) > 1 :
           for entry in picked :
               if entry.path in info : self.logger.info("File collected  : %s "  % os.path.basename(entry.path))
               else :                  self.logger.info("File considered : %s "  % os.path.basename(entry.path))

    #-----------------------------------------------------------------------------------------
    # process : create and ingest collected bulletins
    #-----------------------------------------------------------------------------------------

    def process( self ):

        self.mapChanged = False

        # set now

        self.now = self.collManager.now

        # loop on all the collected state map

        for self.key in self.mapCollectionState :

            # get needed info from the collection state key

            self.header = self.key.split("_")

            # extract collection state info 

            ( self.period, self.amendement, self.correction, self.retard, self.Primary, self.Cycle ) = \
            self.mapCollectionState[self.key]

            # process primary

            if len(self.Primary) != 0 : self.processPrimary()

            # process an empty primary if needed

            self.processEmptyPrimary()

            # process cycle

            if len(self.Cycle) != 0 : self.processCycle()

            # update collection state info 

            self.mapCollectionState[self.key] =  \
            ( self.period, self.amendement, self.correction, self.retard, self.Primary, self.Cycle )


        return self.mapChanged

    #-----------------------------------------------------------------------------------------
    # processing primary collection
    #-----------------------------------------------------------------------------------------

    def processPrimary( self ):

        # working variables

        info        = []
        header      = self.header
        dictkey     = header[0] + ' ' + header[1]
        stationlist = self.mapCollectionStation[dictkey]

        # build the collection's header

        data = header[0] + ' ' + header[1] + ' ' + header[2] + '\n'
        if header[0][:2] in self.AAXX : data += 'AAXX ' + header[2][:4] + '4\n'

        # loop on stations to put into collection

        for station in stationlist :
            best = self.getBestStationReport(station,self.Primary)

            # station not found : add with NIL 

            if best == None :
               if header[0][:6] in self.metar : data += 'METAR ' + station + ' NIL=\n'
               else :                           data +=            station + ' NIL=\n'
               continue

            # add station to the collection

            istart = 1
            if header[0][:2] in self.AAXX : 
               if best.bulletin.bulletin[1][0:4] == 'AAXX' : istart = 2

            data += string.join(best.bulletin.bulletin[istart:],'\n')
            info.append(best.path)


        # ingest that collection

        self.ingest(data)

        # log how many files used for that collection

        self.logger.info("Used %d files for that collection" % len(self.Primary) )

        for entry in self.Primary :
            if entry.path in info : self.logger.info("File collected  : %s "  % os.path.basename(entry.path))
            else :                  self.logger.info("File considered : %s "  % os.path.basename(entry.path))

        # cache and unlink all the files
 
        for entry in self.Primary :
            self.cache(entry)
            self.unlink(entry.path)

        # update collection state

        self.period  = 0
        self.Primary = []
        self.mapChanged = True

    #-----------------------------------------------------------------------------------------
    # processing empty primary : when collection has past its primary and none ingested...
    #                            create and ingest an empty one
    #-----------------------------------------------------------------------------------------

    def processEmptyPrimary( self ):

        # primary already done

        if self.period >= 0 : return

        # current hour and current delay after that hour

        delay  = self.now % 3600
        ddhhmm = time.strftime('%d%H%M',time.localtime(self.now-delay))

        # not the current emission

        if self.key[-6:] != ddhhmm : return

        # if for that header this time is collectable than add it to CollectionState map

        indx = -1
        try     : indx  = self.source.headers.index(self.key[:2])
        except  : return

        # give a time range to create an empty primary : range is ]primary,primary+cycle[

        iprimary =  int(self.source.issue_primary[indx]) * 60
        icycle   =  int(self.source.issue_cycle  [indx]) * 60

        if delay <= iprimary or  delay >= (iprimary+icycle) : return

        # ok make an empty Primary

        self.processPrimary()

    #-----------------------------------------------------------------------------------------
    # processing cycle collection
    #-----------------------------------------------------------------------------------------

    def processCycle( self ):

        # get all available cycles and sort them

        map = {}
        for entry in self.Cycle :
            map[entry.period] = 1

        cycles = map.keys()
        cycles.sort()

        # loop on cycles : recent towards ntil no one left

        for cycle in cycles :

            # get a list of entries of the most recent cycle

            list = self.getCurrentCycle(cycle)

            # ingest amendements and corrections right away if any

            self.ingest_AMD_COR(list)

            # ingest retarded

            self.ingest_retarded(list)

        # cache and unlink all the files
 
        for entry in self.Cycle :
            self.cache(entry)
            self.unlink(entry.path)

        # update collection state

        self.Cycle = []
        self.mapChanged = True

if __name__ == '__main__':
    pass
