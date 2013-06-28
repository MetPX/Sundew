"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: CollectionState.py
#       
# Authors: Michel Grenier
#
# Date: 2006-05-16
#
# Description: build, load and save CollectionState of a collector
#
#              The collectionState is a map
#
#              The key is the collection header Ex.: SACN31_CWAO_151200
#              The value for a key is a tuple :
#              ( period, amendement, correction, retard, Primary, Cycle )
#
#              period       : integer, -1 nothing done, 0 primary done
#              amendement   : integer, -1 none done,    0, 1, 2, ... amendements done A,B,C...
#              correction   : integer, -1 none done,    0, 1, 2, ... corrections done A,B,C...
#              retard       : integer, -1 none done,    0, 1, 2, ... retards     done A,B,C...
#              Primary list : bulletins classified for the primary collection
#              Cycle   list : bulletins classified for amendements, corrections and retards
#
#############################################################################################

"""

import os,string,time
import PXPaths
import bulletinPlain

PXPaths.normalPaths()              # Access to PX paths

# CollectionState

class CollectionState(object):
    """
    The CollectionState will load needed dictionnary/configurations for the parent collector
    """

    def __init__(self, collector ):
        
        # General Attributes

        self.collector   = collector
        self.source      = collector.source
        self.bullManager = collector.bullManager
        self.ingestor    = collector.ingestor
        self.logger      = collector.logger
        self.loaded      = False
        self.ready       = False
        self.debug       = False

        # current epocal and collection time span epocal truncated to the nearest hour

        self.now         = collector.now
        self.fin         = self.now - ( self.now            % 3600 )
        self.debut       = self.fin - ( self.source.history * 3600 )
        self.lastload    = self.fin

        # alphabet...

        self.alpha = \
        [ 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z' ]

        # build header of interest

        self.lstCollectionHeader = []
        self.getCollectionHeader()

        # the collection state...

        self.pathCollectionState = PXPaths.RXQ + self.source.name + '/' + ".state"
        self.mapCollectionState  = {}

    #-----------------------------------------------------------------------------------------
    # build collection state from db
    # TODO : there should be a better way to get the DB's path to search
    #-----------------------------------------------------------------------------------------

    def buildCollectionState(self):

        # loop on all the keys of the map

        count = 0
        map   = {}
        keys  = self.mapCollectionState.keys()
        keys.sort()

        for key in keys :

            header  = key.split("_")

            # create a fake and tiny bulletin

            bulltin = header[0] + ' ' + header[1] + ' ' + header[2] + '\n'
            if header[0][:2] == 'SI' or header[0][:2] == 'SM' :
               bulltin += 'AAXX\n'
            bulltin += 'CYUL NIL='

            unBulletin = bulletinPlain.bulletinPlain(bulltin,self.logger,'\n')
            unBulletin.doSpecificProcessing()

            # get its db name

            nomFichier = self.bullManager.getFileName(unBulletin,0)
            ingestName = self.ingestor.getIngestName(nomFichier)
            dbName     = self.ingestor.getDBName(ingestName)

            # keep only its dir

            map[os.path.dirname(dbName)] = 1

        # compute dates to scan

        fin      = self.fin   - ( self.fin   % (24*3600) )
        debut    = self.debut - ( self.debut % (24*3600) )

        # loop on all path found

        for path in map.keys() :
            parse    = path.split("/")
            specific = string.join(parse[-3:],'/')

            # loop on time

            t = debut
            while t <= fin :

                  # create DB directory

                  Dir  = PXPaths.DB
                  Dir += time.strftime("%Y%m%d",time.localtime(t)) + "/"
                  Dir += specific

                  # read and scan DB directory

                  if os.path.isdir(Dir) :
                     files = os.listdir(Dir)

                     for f in files :

                         # get map key from filename

                         parse = f.split('_')
                         key = parse[0] + '_' + parse[1] + '_' + parse[2]
                         if not key in self.mapCollectionState : continue

                         # we found entry so certainly primary was done... 

                         ( period, amendement, correction, retard, Primary, Cycle ) = self.mapCollectionState[key]

                         period = 0
                         BBB    = parse[3]

                         if BBB == '' : continue

                         # problem cases ...

                         if len(BBB) != 3 or BBB[2] < 'A' or BBB[2] > 'Z' : continue

                         # Amendement or Correction or Retard

                         value = self.alpha.index(BBB[2])

                         if BBB[0] == 'A' and amendement < value : amendement = value
                         if BBB[0] == 'C' and correction < value : correction = value
                         if BBB[0] == 'R' and retard     < value : retard     = value

                         self.mapCollectionState[key] = \
                         ( period, amendement, correction, retard, Primary, Cycle )

                         count = count + 1

                  t = t + 24*3600

        self.logger.info("Collection State had %d updates from DB",count)

    #-----------------------------------------------------------------------------------------
    # create an empty collection state 
    # the collection state generated here covers every headers and all issue time collectable
    # its going to be a reference when loading the state file
    #-----------------------------------------------------------------------------------------

    def emptyCollectionState(self):

        self.logger.debug("Empty Collection State")

        # loop on time

        t = self.debut
        while t <= self.fin :

              # current hour with its string

              hr      = (t % (24*3600)) / 3600
              current = "%.2d" % hr

              # loop on headers

              for h in self.lstCollectionHeader :

                  # if for that header this time is collectable than add it to CollectionState map
                  try    : 
                           indx  = self.source.headers.index(h[:2])
                           hours = self.source.issue_hours[indx]
                           if hours[0] != 'all' : indx2 = hours.index(current)
                  except : continue

                  # create entry for that report in dictionary

                  key = "%s_%s"%( h, time.strftime("%d%H%M",time.localtime(t)) )
                  self.mapCollectionState[key] = ( -1, -1, -1, -1, [], [] )

              t = t + 3600

              self.print_debug()

    #-----------------------------------------------------------------------------------------
    # from collection station and from source config build header of interest
    #-----------------------------------------------------------------------------------------

    def getCollectionHeader(self):

        station_conf = self.collector.mapCollectionStation
        src_headers  = self.source.headers
        lst          = []

        # get compatible headers between source.headers and stations.conf

        for key in station_conf.keys() :
            if key[:2] in src_headers  :
               parse  = key.split()
               header = parse[0] + '_' + parse[1]
               lst.append(header)

        lst.sort()

        # get that list right

        self.lstCollectionHeader = lst

    #-----------------------------------------------------------------------------------------
    # get state...
    #-----------------------------------------------------------------------------------------

    def getState(self,key):

        # if it is the first bulletin for that key just create and add an initial MapCollectionState value

        if not key in self.mapCollectionState :
           period      = -1
           amendement  = -1
           correction  = -1
           retard      = -1
           Primary     = []
           Cycle       = []

           self.mapCollectionState[key] = (period,amendement,correction,retard,Primary,Cycle)

        return self.mapCollectionState[key]

    #-----------------------------------------------------------------------------------------
    # get state keys
    #-----------------------------------------------------------------------------------------

    def getKeys(self):

        keys = self.mapCollectionState.keys()
        keys.sort()

        return keys

    #-----------------------------------------------------------------------------------------
    # print debug...
    #-----------------------------------------------------------------------------------------

    def print_debug(self):

        if not self.debug : return

        keys = self.mapCollectionState.keys()
        keys.sort()
        for key in keys :
            ( period, amendement, correction, retard, Primary, Cycle ) = self.mapCollectionState[key]
            self.logger.debug(" %s = %d %d %d %d %s %s " % \
                             ( key, period, amendement, correction, retard, Primary, Cycle) )

    #-----------------------------------------------------------------------------------------
    # loading the collection state 
    #-----------------------------------------------------------------------------------------

    def loadCollectionState(self):

        self.logger.debug("Loading Collection State")

        # read collection state config

        try   :
                f = open(self.pathCollectionState,'r')
                lignes = f.readlines()
                f.close
        except:
                self.logger.info("Could not load the collection state" )
                return

        # process all lines

        for ligne in lignes :
            parse  = ligne.split()

            # skip and warn if not already in the empty CollectionState map

            if not parse[0] in self.mapCollectionState :
               self.logger.debug(" Not collecting %s anymore " % parse[0] )
               continue

            # set key to its value

            key        =     parse[0]
            period     = int(parse[1])
            amendement = int(parse[2])
            correction = int(parse[3])
            retard     = int(parse[4])

            self.mapCollectionState[ parse[0] ] = ( period, amendement, correction, retard, [], [] )

        # yes I loaded a file

        self.loaded = True

        self.print_debug()

    #-----------------------------------------------------------------------------------------
    # save the collection state 
    #-----------------------------------------------------------------------------------------

    def saveCollectionState(self):

        self.logger.debug("Saving Collection State")

        self.print_debug()

        # sort the keys just for the beauty of the state file

        keys = self.mapCollectionState.keys()
        keys.sort()

        # open collection state config

        try   :
                f = open(self.pathCollectionState,'w')

                for key in keys :
                    ( period, amendement, correction, retard, Primary, Cycle ) = self.mapCollectionState[key]
                    line = "%s %d %d %d %d\n" % (key, period, amendement, correction, retard )
                    f.write(line)

                f.close

        except:
                self.logger.info("Could not save the collection state" )
                return

        self.logger.info("Collection State saved")

    #-----------------------------------------------------------------------------------------
    # set State...
    #-----------------------------------------------------------------------------------------

    def setState(self, key, period, amendement, correction, retard, Primary, Cycle ):

        self.mapCollectionState[key] = ( period, amendement, correction, retard, Primary, Cycle ) 

    #-----------------------------------------------------------------------------------------
    # update the collection state 
    #-----------------------------------------------------------------------------------------

    def updateCollectionState(self,now):

        # get current time... and if state was in memory for more than 1 hour
        # a reload will clean it from entries no longer needed

        self.logger.debug("Update Collection State")

        self.now  = now
        delay     = self.now - self.lastload
        if delay >= 3600 : self.ready = False

        # map ready... return it

        if self.ready :
           self.logger.debug("Collection State not refreshed")
           return

        # initialization

        self.logger.debug("Updating Collection State")

        self.mapCollectionState = {}

        # current epocal and collection time span epocal truncated to the nearest hour

        self.fin         = self.now - ( self.now            % 3600 )
        self.debut       = self.fin - ( self.source.history * 3600 )

        # construct an empty collection state

        self.emptyCollectionState()

        # tries to load the collection state

        self.loadCollectionState()

        # if CollectionState was not loaded try to build it from db and save it
 
        if not self.loaded :
           self.buildCollectionState()

        # map ready... return it

        self.ready    = True
        self.lastload = self.fin

        # save the refreshed

        self.saveCollectionState()

        # inform that we refreshed ( reloaded or rebuild ) the collectionState

        self.logger.info("Collection State refreshed")

if __name__ == '__main__':
    pass
