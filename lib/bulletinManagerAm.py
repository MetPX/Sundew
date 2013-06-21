# -*- coding: iso-8859-1 -*-
#
#MetPX Copyright (C) 2004-2006  Environment Canada
#MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#named COPYING in the root of the source directory tree.
#
# Author:
#   2004/10 - Louis-Philippe Thériault
#
# MG Python3 compatible
#

"""Manage "AM" Bulletins (whatever that means...) """

import bulletinManager, bulletinAm, os, string
import StationParser

__version__ = '2.0'

class bulletinManagerAm(bulletinManager.bulletinManager):
    __doc__ = bulletinManager.bulletinManager.__doc__ + \
    """
       AM protocol implementation of a bulletinManager.
    """

    def __init__(self,pathTemp,logger,pathSource=None,\
                    maxCompteur=99999,lineSeparator='\n',extension=':', \
                    pathFichierCircuit=None, SMHeaderFormat=False, \
                    pathFichierStations=None, mapEnteteDelai=None, source=None, addStationInFilename=False):

        bulletinManager.bulletinManager.__init__(self,pathTemp,logger, \
                                        pathSource,maxCompteur,lineSeparator,extension,pathFichierCircuit,mapEnteteDelai,source, addStationInFilename)

        self.initMapEntetes(pathFichierStations)
        self.SMHeaderFormat = SMHeaderFormat

    def __isSplittable(self,rawBulletin):
        """__isSplittable(rawBulletin) -> bool

           return true if the current bulletin contains more than one bulletin

           Purpose:

                Determine if the bulletin is separable before instatiating it.

        """
        # If it is an FC/FT, perhaps several reports, so splitting into files
        # and the rest of the processing is skipped (to be done in the next pass.)

        # on Error...
        try:
            premierMot = rawBulletin.splitlines()[0].split()[0]
        except Exception as e:
            self.logger.error("Error parsing header\nBulletin:\n%s",rawBulletin)
            return False

        if len(premierMot) == 2 and premierMot in ["FC","FT"]:
            motCle = 'TAF'
            i = 0

            for ligne in rawBulletin.split(self.lineSeparator)[1:]:
                if len(ligne.split()) > 0 and ligne.split()[0] == motCle:
                    i += 1

            return i > 1

        return False

    def __splitBulletin(self,rawBulletin):
        """__splitBulletin(rawBulletin) -> liste bulletins

           Return a list of rawBulletins, separated

           Purpose:

                Split FC/FT bulletins which have >1 report 

        """
        entete = rawBulletin.split(self.lineSeparator)[0]

        listeBulletins = []
        unBulletin = []
        motCle = 'TAF'

        # FC/FT bulletins have the same headers.  The data for each station starts with TAF.
        for ligne in rawBulletin.split(self.lineSeparator)[1:]:
            if len(ligne.split()) > 0 and ligne.split()[0] == motCle:
                listeBulletins.append(string.join(unBulletin,self.lineSeparator))

                unBulletin = list()
                unBulletin.append(entete)

            unBulletin.append(ligne)

        listeBulletins.append(string.join(unBulletin,self.lineSeparator))
        return listeBulletins[1:]

    def _bulletinManager__generateBulletin(self,rawBulletin):
        __doc__ = bulletinManager.bulletinManager._bulletinManager__generateBulletin.__doc__ + \
        """Override here to pass the correct arguments to bulletinAm 

        """
        return bulletinAm.bulletinAm(rawBulletin,self.logger,self.lineSeparator,self.mapEntetes,self.SMHeaderFormat)


    def writeBulletinToDisk(self,unRawBulletin,includeError=False):
        bulletinManager.bulletinManager.writeBulletinToDisk.__doc__ + \
        """AM bulletins can be split, so a split is done and each resulting 
           bulletin is then passed to the parent method

        """
        if self.__isSplittable(unRawBulletin):
            for rawBull in self.__splitBulletin(unRawBulletin):
                bulletinManager.bulletinManager.writeBulletinToDisk(self,rawBull,includeError=includeError)
        else:
            bulletinManager.bulletinManager.writeBulletinToDisk(self,unRawBulletin,includeError=includeError)

    def reloadMapEntetes(self, pathFichierStations):
        """reloadMapEntetes(pathFichierStations)

           pathFichierStations: String
                                - path to the stations.conf

           Reload the header table in memory.

           Purpose:

                handle SIGHUP

        """
        oldMapEntetes = self.mapEntetes

        try:

            self.initMapEntetes(pathFichierStations)

            self.logger.info("station table reloaded")

        except Exception as e :

            self.mapEntetes = oldMapEntetes

            self.logger.warning("Error reloading station table")

            raise

    def initMapEntetes(self, pathFichierStations):
        """initMapEntetes(pathFichierStations)

           pathFichierStations: String
                                - path to stations.conf

           mapEntetes is used to complete headers of AM bulletins.
           reports come in with simple, two letter headers (ie. SP)
           key of the table is the original header + station in the report.
           the value is the string to be used to complete the AHL.

                Ex.: mapEntetes["SPCZPC"] = "CN52 CWAO "

           self.mapEntetes2mapStations is a mapping from headers to stations.

        """
        if pathFichierStations == None:
            self.mapEntetes = None
            return

        sp = StationParser.StationParser(pathFichierStations, self.logger)
        sp.parse()

        uneEntete = ""
        uneCle = ""
        unPrefixe = ""
        uneLigneParsee = ""
        self.mapEntetes = {}
        self.mapEntetes2mapStations = {}

        # Construction des 2 map en meme temps
        for key in sp.stations :
            unPrefixe = key[0:2]
            uneEntete = key[2:] + ' '

            # Ajout d'un map vide pour l'entete courante
            if unPrefixe + uneEntete[:-1] not in self.mapEntetes2mapStations:
                self.mapEntetes2mapStations[unPrefixe + uneEntete[:-1]] = {}

            for station in sp.stations[key]:
                uneCle = unPrefixe + station

                self.mapEntetes[uneCle] = uneEntete

                self.mapEntetes2mapStations[unPrefixe + uneEntete[:-1]][station] = None

    def print_debug(self):

        keys = list(self.mapEntetes.keys())
        keys.sort()
        for key in keys :
            print(" mapEntetes key (%s) = (%s) " % (key,self.mapEntetes[key]) )

        keys = list(self.mapEntetes2mapStations.keys())
        keys.sort()
        for key in keys :
            print(" mapEntetes2mapStations key (%s) = (%s) " % (key,self.mapEntetes2mapStations[key]) )
