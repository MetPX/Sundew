# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.

""" bulletin manager

 Authors: Louis-Philippe Thériault, NSD, 

"""

# MG Python3 compatible

import math, re, string, os, bulletinPlain, traceback, sys, time
import PXPaths

from DirectRoutingParser import DirectRoutingParser
from wmoid import wmoid
import bulletinAm
import bulletinWmo

PXPaths.normalPaths()

__version__ = '2.0'

class bulletinManagerException(Exception):
    pass

class bulletinManager:
    """Manipulates bulletins as entities.  Does not modify contents.
       Bulletin Managers take care of reading bulletins from and writing them
       to disk.

       pathTemp             path
           - Required, must be on the same file system as pathSource.

       pathSource           path
           - Directory from which bulletins are read (if necessary.)

       mapEnteteDelai       map

            - maps bulletin headers to valid reception times.

                   the elements are tuples, 
                       -- element[0] is number of max. minutes before the hour, 
                       -- element[1] is number of max. minutes after the hour.

                       -- Set the map to None to turn off header validity checking.

                    sample: mapEnteteDelai = { 'CA':(5,20),'WO':(20,40)}

       SMHeaderFormat       Bool

            - if true, Add a line "AAXX jjhh4\\n" to SM/SI bulletins.

       ficCollection        path
        
            - Collection configuration file.
                Set to None to deactivate message collection.

       pathFichierCircuit   path
             - The routing table.  (Header2circuit.conf)
             - set to None to disable. 

       maxCompteur          Int
             - Maximum number before rollover of unique numbers in file names.


    """

    def __init__(self,
            pathTemp,
            logger,
            pathSource=None,
            maxCompteur=99999, \
            lineSeparator='\n',
            extension=':',
            pathFichierCircuit=None,
            mapEnteteDelai=None,
            source=None,
            addStationInFilename=False):

        self.pathTemp = self.__normalizePath(pathTemp)
        self.logger = logger
        self.pathSource = self.__normalizePath(pathSource)
        self.maxCompteur = maxCompteur
        self.lineSeparator = lineSeparator
        self.finalLineSeparator = '\n'
        self.extension = extension
        self.mapEnteteDelai = mapEnteteDelai
        self.source = source
        self.addStationInFilename = addStationInFilename

        self.wmo_id = []
        wmo = wmoid(self.logger)
        self.wmo_id = wmo.parse()
        self.logger.warning("wmo id = %s"%self.wmo_id)

        # FIXME: this should be read from a config file, haven't understood enough yet.
        self.compteur = 0

        #map du contenu de bulletins en format brut
        #associe a leur arborescence absolue
        #map raw contents of bulletins to the absolute tree (FIXME wtf?)
        self.mapBulletinsBruts = {}

        # setup routing table.
        self.drp = DirectRoutingParser(pathFichierCircuit, self.source.ingestor.allNames, logger)
        self.drp.parse()
        #self.drp.logInfos()

    def effacerFichier(self,nomFichier):
        try:
            os.remove(nomFichier)
        except:
            self.logger.error("(BulletinManager.effacerFichier(): Error removing bulletin.")
            raise

    def writeBulletinToDisk(self,unRawBulletin,compteur=True,includeError=True):
        """writeBulletinToDisk(bulletin [,compteur,includeError])

           unRawBulletin        String

                     - unRawBulletin is a string, instantiated
                       as a bulletin before it is written to disk 
                     - modifications to the contents are done via a
                       unObjetBulletin.doSpecificProcessing() call
                       before writing.

           compteur             Bool

                     - If true, include counter in file name.

           includeError         Bool

                     - If true, and the bulletin is problematic, prepend
                       the bulletin data with a diagnostic message.

        """
        
        if self.compteur >= self.maxCompteur:
            self.compteur = 0

        self.compteur += 1
        
        unBulletin = self.__generateBulletin(unRawBulletin)
        unBulletin.doSpecificProcessing()

        # check arrival time.
        self.verifyDelay(unBulletin)

        # generate a file name.
        nomFichier = self.getFileName(unBulletin,compteur=compteur)

        # add date/time stamp
        nomFichier = nomFichier + ':' + time.strftime( "%Y%m%d%H%M%S", time.gmtime(time.time()) )

        tempNom = self.pathTemp + nomFichier
        try:
            unFichier = os.open( tempNom , os.O_CREAT | os.O_WRONLY )

        except (OSError,TypeError) as e:
            # bad file name, make up a new one. 

            self.logger.warning("cannot write file! (bad file name)")
            self.logger.error("Exception: " + ''.join(traceback.format_exception(Exception,e,sys.exc_info()[2])))

            nomFichier = self.getFileName(unBulletin,error=True,compteur=compteur)
            tempNom = self.pathTemp + nomFichier
            unFichier = os.open( tempNom, os.O_CREAT | os.O_WRONLY )
        
        os.write( unFichier , unBulletin.getBulletin(includeError=includeError) )
        os.close( unFichier )
        os.chmod(tempNom,0o644)

        entete = ' '.join(unBulletin.getHeader().split()[:2])

        # MG use filename for Pattern File Matching from source ...  (As Proposed by DL )
        if self.source.patternMatching:
            if not self.source.fileMatchMask(nomFichier) :
                self.logger.warning("Bulletin file rejected because of RX mask: " + nomFichier)
                os.unlink(tempNom)
                return

            """
            transfo = self.source.getTransformation(nomFichier)
            if transfo:
                newNames = Transformations.transfo(tempNom)

                for name in newNames:
                    self.source.ingestor.ingest()
            """

        key   = self.drp.getKeyFromHeader(entete)
        clist = self.drp.getClients(key)
        if clist == None :
           clist = []

        if self.source.clientsPatternMatching:
            clist = self.source.ingestor.getMatchingClientNamesFromMasks(nomFichier, clist)

        self.source.ingestor.ingest(tempNom, nomFichier, clist)

        os.unlink(tempNom)

    def _writeBulletinToDisk(self,unRawBulletin,compteur=True,includeError=True):
        
        if self.compteur >= self.maxCompteur:
            self.compteur = 0

        self.compteur += 1

        unBulletin = self.__generateBulletin(unRawBulletin)
        unBulletin.doSpecificProcessing()

        # check arrival time.
        self.verifyDelay(unBulletin)

        # generate a file name.
        nomFichier = self.getFileName(unBulletin,compteur=compteur)

        nomFichier = nomFichier + ':' + time.strftime( "%Y%m%d%H%M%S", time.gmtime(time.time()) )

        tempNom = self.pathTemp + nomFichier
        try:
            unFichier = os.open( tempNom , os.O_CREAT | os.O_WRONLY )

        except (OSError,TypeError) as e:
            # bad file name. Make up a new one.

            self.logger.warning("Cannot write file! (bad file name)")
            self.logger.error("Exception: " + ''.join(traceback.format_exception(Exception,e,sys.exc_info()[2])))

            nomFichier = self.getFileName(unBulletin,error=True,compteur=compteur)
            tempNom = self.pathTemp + nomFichier
            unFichier = os.open( tempNom, os.O_CREAT | os.O_WRONLY )

        os.write( unFichier , unBulletin.getBulletin(includeError=includeError) )
        os.close( unFichier )
        os.chmod(tempNom,0o644)

        entete = ' '.join(unBulletin.getHeader().split()[:2])

        # MG use filename for Pattern File Matching from source ...  (As Proposed by DL )
        if self.source.patternMatching:
            if not self.source.fileMatchMask(nomFichier) :
                self.logger.warning("Bulletin file rejected because of RX mask: " + nomFichier)
                os.unlink(tempNom)
                return

            """
            transfo = self.source.getTransformation(nomFichier)
            if transfo:
                newNames = Transformations.transfo(tempNom)

                for name in newNames:
                    self.source.ingestor.ingest()
            """

        key   = self.drp.getKeyFromHeader(entete)
        clist = self.drp.getClients(key)
        if clist == None :
           clist = []

        if self.source.clientsPatternMatching:
            clist = self.source.ingestor.getMatchingClientNamesFromMasks(nomFichier, clist)

        #fet.directIngest( nomFichier, clist, tempNom, self.logger )
        self.source.ingestor.ingest(tempNom, nomFichier, clist)

        os.unlink(tempNom)

    def __generateBulletin(self,rawBulletin):
        """__generateBulletin(rawBulletin) -> objetBulletin

           Retourne un objetBulletin d'à partir d'un bulletin
           "brut".

        """
        return bulletinPlain.bulletinPlain(rawBulletin,self.logger,self.lineSeparator)

    def getListeNomsFichiersAbsolus(self):
        return list(self.mapBulletinsBruts.keys())

    def __normalizePath(self,path):
        """normalizePath(path) -> path

           Retourne un path avec un '/' à la fin
        """

        if path != None:
            if path != '' and path[-1] != '/':
                path = path + '/'

        return path

    def createWhatFn(self,bulletin,compteur=True ):
        """createWhatFn(bulletin[,compteur]) -> whatfn

           Return the first token of the filename. Build out of the
           bulletin header, the station (if defined) and a counter
           the WHATFN should looked like (if all the informations needed
           are available)

           SACN31_CWAO_121435_RRA_CYUL_045440 

           Missing info are going to be left empty
           possible outcome are :

           SACN31_CWAO_121435__CYUL_045440
           SACN31_CWAO_121435_CCA__045440


        """

        # header : 1- get header from bulletin
        #          2- must be alphanumeric
        #          3- consider an empty BBB to add an '_'

        header = bulletin.getHeader()
        if (header.replace(' ','')).isalnum() :
           parts  = header.split()
           header = header.replace(' ','_')
           if len(parts) < 4 : header = header + '_'
        else :
           header = None

        # station name :  1- bulletin header must be good
        #                 2- get station from bulletin
        #                 3- must be alphanumeric
        #                 4- station in WhatFn is conditional to some bulletin type
        #                    bulletinAm      always have the station name in the WhatFn (if found)
        #                    bulletinWmo     SRCN40 have the station name in the WhatFn (if found)
        #                    bulletin-file ? SRCN40 have the station name in the WhatFn (if found)
        #                    collector       Don't place station in the filename

        station = ''
        if header != None :
           if not (self.source.type == 'collector'):
              station = bulletin.getStation()
           if station == None       : station = ''
           if not station.isalnum() : station = ''
           if not self.addStationInFilename:
              if not (bulletin.getHeader())[:6] in self.wmo_id : station = ''
           
        # adding a counter to the file name insure its uniqueness

        strCompteur = ''
        if compteur :
           strCompteur = string.zfill(self.compteur, len(str(self.maxCompteur)))

        # correct header if needed

        if header == None : header = 'UNPRINTABLE_HEADER'

        # whatfn

        whatfn = header + '_' + station + '_' + strCompteur

        return whatfn


    def getFileName(self,bulletin,error=False, compteur=True ):
        """getFileName(bulletin[,error, compteur]) -> fileName

           return the a file name for a bulletin.  
             IF error=True, the header has some nasty characters in it.  
                 return a "safe" file name.
           if not, but there is something wrong with the headers so
           no file name can be generated, then put ERROR in a bunch
           of fields.
           compteur is a boolean to determine whether to add a random
            counter on the end of the file name.

           Purpose:

                Generate a file name for a given bulletin.
        """

        # whatfn
        whatfn = self.createWhatFn(bulletin,compteur)

        # the bulletin is ok
        if bulletin.getError() == None and not error:
            # a correctly formatted bulletin...
            try:
                return  whatfn + self.getExtension(bulletin,self.extension,False).replace(' ','_')

            # extension problem...
            except Exception as e:
                w = whatfn.split('_')
                self.logger.warning(" %s not in routing table" % '_'.join(w[:2]) )
                return 'PROBLEM_BULLETIN_' + whatfn + self.getExtension(bulletin,self.extension,True).replace(' ','_')

        # extract error string if any
        word0    = None
        errorStr = bulletin.getError()
        if errorStr != None :
           errorStr = errorStr[0]
           word0    = errorStr.split()[0]

        # the bulletin had arrival problem
        if word0 == 'arrival' and self.source.arrival_extension != None and not error:
            # a correctly formatted bulletin...
            try:
                return  whatfn + self.getExtension(bulletin,self.source.arrival_extension,False).replace(' ','_')

            # extension problem... probably routing or station
            except Exception as e:
                w = whatfn.split('_')
                self.logger.warning(" %s not in routing table" % '_'.join(w[:2]) )
                return 'PROBLEM_BULLETIN_' + whatfn + self.getExtension(bulletin,self.extension,True).replace(' ','_')


        if errorStr != None and not error:
            self.logger.warning("bulletin problem " + bulletin.getError()[0] )
            return 'PROBLEM_BULLETIN_' + whatfn + self.getExtension(bulletin,self.extension,True).replace(' ','_')
        else:
            self.logger.warning("unprintable header" )
            return ('PROBLEM_BULLETIN ' + 'UNPRINTABLE HEADER ' + self.getExtension(bulletin,self.extension,True)).replace(' ','_')

    def getExtension(self,bulletin,extension,error=False):
        """getExtension(bulletin) -> extension

           Returns the extension to suffix to a bulletin header to create a file name.
           if error=TRUE, 'dynamic' fields are set to PROBLEM.

           -TT:         bulletin type TT in AHL (first 2 letters)
           -CCCC:       bulletin origin CCCC in AHL (second header field) 
           -CIRCUIT:    FIXME: OBSOLETE FIELD... use -PRIORITY
           -PRIORITY:   bulletin priority (set by pxRouting.conf entry.)

           Exceptions raised:
                bulletinManagerException:       if the extension cannot be generated
                                                correctly and error was not initially 
                                                set.

           Purpose:

                Generate the extention portion of the file name.
        """
        newExtension = extension

        if not error :
            newExtension = newExtension.replace('-TT',bulletin.getType())\
                                       .replace('-CCCC',bulletin.getOrigin())

            if self.drp != None:
            # Si les circuits sont activés
            # NB: Lève une exception si l'entête est introuvable
                entete = ' '.join(bulletin.getHeader().split()[:2])
                key = self.drp.getKeyFromHeader(entete)
                #FIXME: remove -CIRCUIT after transition period.
                newExtension = newExtension.replace('-CIRCUIT', self.drp.getHeaderPriority(key))
                newExtension = newExtension.replace('-PRIORITY', self.drp.getHeaderPriority(key))

            return newExtension
        else:
            # error detected in bulletin
            newExtension = newExtension.replace('-TT','PROBLEM')\
                                       .replace('-CCCC','PROBLEM')\
                                       .replace('-PRIORITY','PROBLEM')\
                                       .replace('-CIRCUIT','PROBLEM')

            return newExtension

    def lireFicTexte(self,pathFic):
        """
           lireFicTexte(pathFic) -> liste des lignes

           pathFic:        String
                           - path to text file

           liste des lignes:       [str]
                                   - list of lines in the file.

        Purpose:

                return the lines in a file. useful for reading small 
                config files.
        """
        if os.access(pathFic,os.R_OK):
            f = open(pathFic,'r')
            lignes = f.readlines()
            f.close
            return lignes
        else:
            self.logger.error("Unable to access:" + pathFic )
            raise IOError

    def getPathSource(self):
        """getPathSource() -> Path_source

           Path_source:         String
                                -source path containing the manager (FIXME: wtf?)
        """
        return self.pathSource

    def verifyDelay(self,unBulletin):
        """verifyDelay(unBulletin)

           Check that the bulletin reception time is within specification
           if the 'arrival' settings are active. Flag as an error
           if out of spec.

           requires a valid self.mapEnteteDelai (arrival mapping structure.)

           Purpose: implement arrival time filtering.
           
           MG : rewritten 19-06-2007
                FIX       25-07-2007  catch exception when delay is computed
                                      header may not be good
        """

        # check delai if asked for ...

        if self.mapEnteteDelai == None : return

        # check delai if no error in bulletin

        if unBulletin.getError() != None : return

        try:
            type = unBulletin.getHeader()[:2]
            if not type in list(self.mapEnteteDelai.keys()) : return

            (future,history) = self.mapEnteteDelai[type]

            # limits in seconds (in future ... delay is negative)

            future  = -60 * future
            history =  60 * history

            # set bulletin arrival to current time

            now = time.mktime(time.localtime())
            unBulletin.setArrivalEp(now)

        except Exception:
            unBulletin.setError('cannot parse header')
            return


        # Evaluate if bulletin is within interval.

        if unBulletin.delay < future or unBulletin.delay > history :
            self.logger.warning("arrival time outside permitted interval: "+unBulletin.getHeader()+", delay %d (Secs)"%unBulletin.delay )
            unBulletin.setError('arrival time outside permitted interval')
