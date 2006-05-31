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
        self.bullManager   = collManager.bullManager
        self.ingestor      = collManager.ingestor
        self.source        = collManager.source
        self.logger        = collManager.logger

        self.now           = collManager.now

        self.period        = -1
        self.amendement    = -1
        self.correction    = -1
        self.retard        = -1
        self.Primary       = []
        self.Cycle         = []

        # collection dictionnary... 

        self.lstCollectionHeader   = collManager.lstCollectionHeader
        self.mapCollectionStation  = collManager.mapCollectionStation

        # collection state...

        self.mapCollectionState    = collManager.mapCollectionState

        # alphabet...

        self.alpha = \
        [ 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z' ]

    #-----------------------------------------------------------------------------------------
    # getBestStationReport to put in primary 
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

            # if the station more than once... pich the most recent i.e the biggest delay

            if entry.bulletin.delay > best.bulletin.delay : best = entry

        # return the best

        return best

    #-----------------------------------------------------------------------------------------
    # getMostRecentCycle to put in cycle 
    #-----------------------------------------------------------------------------------------


    def getMostRecentCycle( self ):

        cycle = 999999
        clist = []

        # loop on all entry : create a list of the most recent Cycle

        for entry in self.Cycle :

            if entry.period > cycle : continue
            if entry.period < cycle :
                                      clist = []
                                      cycle = entry.period
            clist.append(entry)

        # comparaison module : concatenated str = reception date + BBB

        def compare(x, y):

            a  = x.bulletin.arrival
            BBB= x.bulletin.getBBB()
            if BBB != None : a += BBB

            b  = y.bulletin.arrival
            BBB= y.bulletin.getBBB()
            if BBB != None : b += BBB

            return cmp(a, b)

        # sort this list according to reception date and BBB value

        clist.sort(compare)

        return clist

    #-----------------------------------------------------------------------------------------
    # ingest amendements and corrections if any
    #-----------------------------------------------------------------------------------------

    def ingest_AMD_COR( self, list ):

        print(" *** AMD COR ***************** LIST LEN = %s " % len(list) )
        for entry in list :
            entry.print_debug()

        picked = []
        for entry in list :

            BBB = entry.bulletin.getBBB()
            if BBB == None : continue
            if BBB[0] != 'A' and BBB[0] != 'C' : continue

            cBBB = ''

            if BBB[0] == 'A' :
               self.amendement = self.amendement + 1
               cBBB = 'AA' + self.alpha[self.amendement%25]

            if BBB[0] == 'C' :
               self.correction = self.correction + 1
               cBBB = 'CC' + self.alpha[self.correction%25]

            data = entry.header[0] + ' ' + entry.header[1] + ' ' + entry.header[2] + ' ' + cBBB + '\n'
            if entry.header[0][:2] == 'SM' or entry.header[0][:2] == 'SI' : data += 'AAXX\n'
            data += string.join(entry.bulletin.bulletin[1:],'\n')

            print ( "data = %s " % data )
            self.bullManager.writeBulletinToDisk(data, True, True)

            picked.append(entry)

        for entry in picked :
            try:
                #os.unlink(entry.path)
                self.logger.debug("%s has been erased", os.path.basename(entry.path))
            except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (entry.path, type, value))

            self.Cycle.remove(entry)
            list.remove(entry)

    #-----------------------------------------------------------------------------------------
    # ingest retarded
    #-----------------------------------------------------------------------------------------

    def ingest_retarded( self, list ):

        if len(list) <= 0 : return
        print(" *** RETARD ****************** LIST LEN = %s " % len(list) )
        for entry in list :
            entry.print_debug()

        # prepare retarded collection header

        entry       = list[0]
        stationlist = self.mapCollectionStation[entry.dictkey]

        self.retard = self.retard + 1
        cBBB = 'RR' + self.alpha[self.retard%25]

        data = entry.header[0] + ' ' + entry.header[1] + ' ' + entry.header[2] + ' ' + cBBB + '\n'
        if entry.header[0][:2] == 'SM' or entry.header[0][:2] == 'SI' : data += 'AAXX\n'

        # add all files

        print(" ***************************** stationlist %s " % stationlist )
        picked = []
        for station in stationlist :
            best  = self.getBestStationReport(station,list)
            if best == None : continue
	    picked.append(best)
            print(" ***************************** add " )
            data += string.join(best.bulletin.bulletin[1:],'\n')

        # ingest

        print ( "data = %s " % data )
        self.bullManager.writeBulletinToDisk(data, True, True)

        # clean

        for entry in picked :
            try:
                #os.unlink(entry.path)
                self.logger.debug("%s has been erased", os.path.basename(entry.path))
            except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (entry.path, type, value))

            self.Cycle.remove(entry)
            list.remove(entry)



    #-----------------------------------------------------------------------------------------
    # process : create and ingest collected bulletins
    #-----------------------------------------------------------------------------------------

    def process( self ):

        # loop on all the collected state map

        for key in self.mapCollectionState :

            # extract info 

            lst = self.mapCollectionState[key]
            ( self.period, self.amendement, self.correction, self.retard, self.Primary, self.Cycle ) = lst

            # process primary

            if len(self.Primary) != 0 : self.processPrimary(self.Primary[0],self.Primary)

            # process cycle

            if len(self.Cycle)   != 0 : self.processCycle()

        return True

    #-----------------------------------------------------------------------------------------
    # processing primary collection
    #-----------------------------------------------------------------------------------------

    def processPrimary( self, entry, list ):

        # get the lists of stations for that collection

        stationlist = self.mapCollectionStation[entry.dictkey]

        # start building the collection by its header

        data     = entry.header[0] + ' ' + entry.header[1] + ' ' + entry.header[2] + '\n'

        if entry.header[0][:2] == 'SM' or entry.header[0][:2] == 'SI' :
           data += 'AAXX\n'

        # loop on stations to put into collection

        for station in stationlist :
            best = self.getBestStationReport(station,list)

            if best == None :

               if entry.header[0][:2] == 'SA' :
                                                data += 'METAR ' + station + ' NIL=\n'
               else :                           data +=            station + ' NIL=\n'

            else :                              data += string.join(best.bulletin.bulletin[1:],'\n')

        # ingest that collection

        self.bullManager.writeBulletinToDisk(data, True, True)

        # acknowledge in collection state

        self.period = 0

        # unlink all the files
 
        for entry in list :
            try:
                #os.unlink(entry.path)
                self.logger.debug("%s has been erased", os.path.basename(entry.path))
            except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (entry.path, type, value))

    #-----------------------------------------------------------------------------------------
    # processing cycle collection
    #-----------------------------------------------------------------------------------------

    def processCycle( self ):

        # proceed with most recent cycles until no one left

        while len(self.Cycle) > 0 :

              # get a list of entries of the most recent cycle

              list = self.getMostRecentCycle()

              # proceed with most recent cycles until no one left

              entry=list[0]
              if self.period < 0 : self.processPrimary(entry,[])

              # ingest amendements and corrections right away if any

              self.ingest_AMD_COR(list)

              # ingest retarded

              self.ingest_retarded(list)

if __name__ == '__main__':
    pass
