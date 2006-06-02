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

            if BBB[0] == 'A' :
               self.amendement = self.amendement + 1
               cBBB = 'AA' + self.alpha[self.amendement%25]

            if BBB[0] == 'C' :
               self.correction = self.correction + 1
               cBBB = 'CC' + self.alpha[self.correction%25]

            data = entry.header[0] + ' ' + entry.header[1] + ' ' + entry.header[2] + ' ' + cBBB + '\n'
            if entry.header[0][:2] == 'SM' or entry.header[0][:2] == 'SI' : data += 'AAXX\n'
            data += string.join(entry.bulletin.bulletin[1:],'\n')

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

        # start building a retarded collection

        self.retard = self.retard + 1
        cBBB = 'RR' + self.alpha[self.retard%25]

        data = header[0] + ' ' + header[1] + ' ' + header[2] + ' ' + cBBB + '\n'

        if header[0][:2] == 'SM' or header[0][:2] == 'SI' : data += 'AAXX\n'

        # add retarded by ordered station ... 

        info=[]

        for station in stationlist :
            best = self.getBestStationReport(station,picked)
            if best == None : continue

            # add report to the collection

            data += string.join(best.bulletin.bulletin[1:],'\n')
            info.append(best.path)

        # ingest that collection

        self.bullManager.writeBulletinToDisk(data, True, True)

        # log how many files used for that collection

        self.logger.info("Used %d files for that collection" % len(picked) )

        for entry in picked :
            if entry.path in info : self.logger.debug("File collected  : %s "  % os.path.basename(entry.path))
            else :                  self.logger.debug("File considered : %s "  % os.path.basename(entry.path))

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

        # loop on all the collected state map

        for self.key in self.mapCollectionState :

            # extract collection state info 

            lst = self.mapCollectionState[self.key]
            ( self.period, self.amendement, self.correction, self.retard, self.Primary, self.Cycle ) = lst

            # process primary

            if len(self.Primary) != 0 :
               self.processPrimary()
               self.period  = 0
               self.Primary = []

            # process cycle

            if len(self.Cycle) != 0 :
               self.processCycle()
               self.Cycle = []

            # check if it is due and period == -1 than send a primary with all NILS


            # update collection state info 

            self.mapCollectionState[self.key] =  \
            [ self.period, self.amendement, self.correction, self.retard, self.Primary, self.Cycle ]


        return True

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
               data += string.join(best.bulletin.bulletin[1:],'\n')
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
            if entry.path in info : self.logger.debug("File collected  : %s "  % os.path.basename(entry.path))
            else :                  self.logger.debug("File considered : %s "  % os.path.basename(entry.path))

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
    # processing cycle collection
    #-----------------------------------------------------------------------------------------

    def processCycle( self ):

        for entry in self.Cycle :
            entry.print_debug()

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

            # if we are ready to write an amendement,correction or retarded
            # and the primary was not done... ingest an empty one

            if self.period < 0 : self.processPrimary()

            # ingest amendements and corrections right away if any

            self.ingest_AMD_COR(list)

            # ingest retarded

            self.ingest_retarded(list)

#   if the collector is down for an hour... than the empty primary will get ingested
#   at the first arrival of an amemdement,correction,retard bulletin... so not on time
#   def primary_due( self, index ):
#
#       self.now
#       hour  = ... self.now...
#       delay = now - hour
#
#       for pos,header in enumerate(self.source.headers) :
#
#           if self.source.issue_hours[pos][0] != 'all' and not hour in self.source.issue_hours[pos] : continue
#           primary = 60 * int(self.source.issue_primary[pos])
#           if delay < primary : continue
#
#           due.append(header_DDHHMM)
#
#       if len(due) == 0 : return
#
#       for key in mapCollectionState :
#           header_DDHHMM = key[:2] + '_' + key[-6:]
#           if not header_DDHHMM in due : continue
#           ( period, amendement, correction, retard, Primary, Cycle ) = self.mapCollectionState[key]
#            if period >= 0 : continue
#
#           # ingest empty primary
#           self.processPrimary()

if __name__ == '__main__':
    pass
