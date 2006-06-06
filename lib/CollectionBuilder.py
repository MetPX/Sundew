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

        self.bullManager   = collManager.bullManager
        self.source        = collManager.source
        self.logger        = collManager.logger
        self.now           = collManager.now

        self.key           = None
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

        # metar...

        self.metar = \
        [ 'SACN31',  \
          'SACN40', 'SACN41', 'SACN42', 'SACN43', 'SACN44', 'SACN45', 'SACN46', 'SACN47', 'SACN48', 'SACN49', \
          'SACN51', 'SACN52'  ]

    #-----------------------------------------------------------------------------------------
    # getBestStationReport : if we have many bulletins for the same station to put in
    #                        the collection : use the most recent
    #-----------------------------------------------------------------------------------------

    def getBestStationReport( self, station, list ):

        # loop on all entry

        best = None
        for entry in list :
            if entry.station != station : continue

            # first station found

            if best == None :
               best = entry
               continue

            # if the station report more than once... 
            # than pick the most recent i.e the biggest delay

            if entry.bulletin.delay > best.bulletin.delay : best = entry

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

            a  = x.bulletin.arrival
            if x.BBB != None : a += x.BBB

            b  = y.bulletin.arrival
            if y.BBB != None : b += y.BBB

            return cmp(a, b)

        # sort this list according to reception date and BBB value

        clist.sort(compare)

        return clist

    #-----------------------------------------------------------------------------------------
    # ingest amendements and corrections if any
    #-----------------------------------------------------------------------------------------

    def ingest_AMD_COR( self, list ):

        # get Amendement and Corrections only

        picked   = []

        for entry in list :
            if entry.BBB == None : continue
            if entry.BBB[0] != 'A' and entry.BBB[0] != 'C' : continue
            picked.append(entry)

        if len(picked) <= 0 : return

        # ingestion order : ideal world suggest reception time should respect the report's BBB order
        # we hope its mostly true... if not a more complex sorting should be done...

        def compare(x, y):
            a  = x.bulletin.arrival + x.BBB + x.station
            b  = y.bulletin.arrival + y.BBB + y.station
            return cmp(a, b)

        picked.sort(compare)

        # we are ready to ingest...

        for entry in picked :

            cBBB = ''

            BBB = entry.BBB

            # amendement's BBB : if primary was not done... we are all confused... make it a Y

            if BBB[0] == 'A' :
               self.amendement = self.amendement + 1
               cBBB = 'AA' + self.alpha[self.amendement%25]
               if self.period < 0 :
                  cBBB = 'AAY'
               elif self.amendement == 24 :
                  self.logger.info("This amendement has reach the limit so set it to AAZ" )
                  cBBB = 'AAZ'

            # correction's BBB : if primary was not done... we are all confused... make it a Y

            if BBB[0] == 'C' :
               self.correction = self.correction + 1
               cBBB = 'CC' + self.alpha[self.correction%25]
               if self.period < 0 :
                  cBBB = 'CCY'
               elif self.correction == 24 :
                  self.logger.info("This correction has reach the limit so set it to CCZ" )
                  cBBB = 'CCZ'

            data    = entry.header[0] + ' ' + entry.header[1] + ' ' + entry.header[2] + ' ' + cBBB + '\n'

            istart = 1
            if entry.header[0][:2] == 'SM' or entry.header[0][:2] == 'SI' : 
               data += 'AAXX\n'
               if entry.bulletin.bulletin[1][0:4] == 'AAXX' : istart = 2

            data += string.join(entry.bulletin.bulletin[istart:],'\n')

            if cBBB[0] == 'A' and cBBB[2] == 'Y' :
               self.logger.info("This amendement had no primary collection" )

            if cBBB[0] == 'C' and cBBB[2] == 'Y' :
               self.logger.info("This correction had no primary collection" )

            self.bullManager.writeBulletinToDisk(data, True, True)

            self.logger.info("Used 1 file for that collection" )
            self.logger.debug("File collected  : %s ", entry.path )

            try:
                os.unlink(entry.path)
                self.logger.debug("%s has been erased", os.path.basename(entry.path))
            except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (entry.path, type, value))

    #-----------------------------------------------------------------------------------------
    # ingest retarded
    #-----------------------------------------------------------------------------------------

    def ingest_retarded( self, list ):

        # get retarded only

        picked   = []
        stations = {}

        for entry in list :
            if entry.BBB == None or entry.BBB[0] == 'R' :
               picked.append(entry)
               stations[entry.station] = 1

        if len(picked) <= 0 : return

        # get the sorted list of stations for that collection

        stationlist = stations.keys()
        stationlist.sort()

        # get needed info from the collection state key

        header  = self.key.split("_")

        # retarded's BBB : if primary was not done... we are all confused... make it a Y

        self.retard = self.retard + 1
        cBBB = 'RR' + self.alpha[self.retard%25]
        if self.period < 0 :
           cBBB = 'RRY'
           self.logger.info("Late bulletin(s) with no primary collection" )

        data = header[0] + ' ' + header[1] + ' ' + header[2] + ' ' + cBBB + '\n'

        if header[0][:2] == 'SM' or header[0][:2] == 'SI' : data += 'AAXX\n'

        # add retarded by ordered station ... 

        info=[]

        for station in stationlist :
            best = self.getBestStationReport(station,picked)
            if best == None : continue

            # add report to the collection

            istart = 1
            if header[0][:2] == 'SM' or header[0][:2] == 'SI' : 
               if best.bulletin.bulletin[1][0:4] == 'AAXX' : istart = 2

            data += string.join(best.bulletin.bulletin[istart:],'\n')
            info.append(best.path)

        # ingest that collection

        self.bullManager.writeBulletinToDisk(data, True, True)

        # log how many files used for that collection

        self.logger.info("Used %d files for that collection" % len(picked) )

        if len(picked) > 1 :
           for entry in picked :
               if entry.path in info : self.logger.info("File collected  : %s "  % os.path.basename(entry.path))
               else :                  self.logger.info("File considered : %s "  % os.path.basename(entry.path))

        # unlink all the files
 
        for entry in picked :
            try:
                os.unlink(entry.path)
                self.logger.debug("%s has been erased", os.path.basename(entry.path))
            except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (entry.path, type, value))

    #-----------------------------------------------------------------------------------------
    # process : create and ingest collected bulletins
    #-----------------------------------------------------------------------------------------

    def process( self ):

        self.mapChanged = False

        # loop on all the collected state map

        for self.key in self.mapCollectionState :

            # extract collection state info 

            ( self.period, self.amendement, self.correction, self.retard, self.Primary, self.Cycle ) = \
            self.mapCollectionState[self.key]

            # process primary

            if len(self.Primary) != 0 :
               self.processPrimary()
               self.period     = 0
               self.Primary    = []
               self.mapChanged = True

            # process an empty primary if needed

            self.processEmptyPrimary()

            # process cycle

            if len(self.Cycle) != 0 :
               self.processCycle()
               self.Cycle      = []
               self.mapChanged = True

            # update collection state info 

            self.mapCollectionState[self.key] =  \
            ( self.period, self.amendement, self.correction, self.retard, self.Primary, self.Cycle )


        return self.mapChanged

    #-----------------------------------------------------------------------------------------
    # processing primary collection
    #-----------------------------------------------------------------------------------------

    def processPrimary( self ):

        # get needed info from the collection state key

        header  = self.key.split("_")
        dictkey = header[0] + ' ' + header[1]

        # get the lists of stations for that collection

        stationlist = self.mapCollectionStation[dictkey]

        # start building the collection by its header

        data = header[0] + ' ' + header[1] + ' ' + header[2] + '\n'

        if header[0][:2] == 'SM' or header[0][:2] == 'SI' : data += 'AAXX\n'

        # loop on stations to put into collection

        info=[]

        for station in stationlist :
            best = self.getBestStationReport(station,self.Primary)

            # add report to the collection

            if best != None :

               istart = 1
               if header[0][:2] == 'SM' or header[0][:2] == 'SI' : 
                  if best.bulletin.bulletin[1][0:4] == 'AAXX' : istart = 2

               data += string.join(best.bulletin.bulletin[istart:],'\n')
               info.append(best.path)

            # add station with NIL because it is missing

            else :
               if header[0][:6] in self.metar : data += 'METAR ' + station + ' NIL=\n'
               else :                           data +=            station + ' NIL=\n'

        # ingest that collection

        self.bullManager.writeBulletinToDisk(data, True, True)

        # log how many files used for that collection

        self.logger.info("Used %d files for that collection" % len(self.Primary) )

        for entry in self.Primary :
            if entry.path in info : self.logger.info("File collected  : %s "  % os.path.basename(entry.path))
            else :                  self.logger.info("File considered : %s "  % os.path.basename(entry.path))

        # unlink all the files
 
        for entry in self.Primary :
            try:
                os.unlink(entry.path)
                self.logger.debug("%s has been erased", os.path.basename(entry.path))
            except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (entry.path, type, value))

        # update collection state

        self.period  = 0
        self.Primary = []

    #-----------------------------------------------------------------------------------------
    # processing empty primary : when collection has past its primary and none ingested...
    #                            create and ingest an empty one
    #-----------------------------------------------------------------------------------------

    def processEmptyPrimary( self ):

        # current hour and current delay after that hour

        delay  = self.now % 3600
        ddhhmm = time.strftime('%d%H%M',time.localtime(self.now-delay))

        # primary already done

        if self.period >= 0 : return

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

        self.period     = 0
        self.Primary    = []
        self.mapChanged = True

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

if __name__ == '__main__':
    pass
