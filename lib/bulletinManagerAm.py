# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""Gestion des bulletins "AM" """

import bulletinManager, bulletinAm, PXPaths, StationParser, os, string, sys

__version__ = '2.0'

class bulletinManagerAm(bulletinManager.bulletinManager):
    __doc__ = bulletinManager.bulletinManager.__doc__ + \
    """### Ajout de bulletinManagerAm ###

       Spécialisation et implantation du bulletinManager

       Auteur:      Louis-Philippe Thériault
       Date:        Octobre 2004
    """

    def __init__(self,pathTemp,logger,pathSource=None,\
                    maxCompteur=99999,lineSeparator='\n',extension=':', \
                    pathFichierCircuit=None, SMHeaderFormat=False, \
                    pathFichierStations=None, mapEnteteDelai=None, source=None):

        bulletinManager.bulletinManager.__init__(self,pathTemp,logger, \
                                        pathSource,maxCompteur,lineSeparator,extension,pathFichierCircuit,mapEnteteDelai,source)

        self.initMapEntetes(pathFichierStations)
        self.SMHeaderFormat = SMHeaderFormat

    def __isSplittable(self,rawBulletin):
        """__isSplittable(rawBulletin) -> bool

           Retourne vrai si le bulletin courant contient plus d'un bulletin

           Utilisation:

                Déterminer si un bulletin est séparable, avant de l'instancier.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        # Si c'est un bulletin FC/FT, possibilite de plusieurs bulletins,
        # donc découpage en fichiers et reste du traitement saute (il
        # sera effectue lors de la prochaine passe.

        # Si une erreur est détectée
        try:
            premierMot = rawBulletin.splitlines()[0].split()[0]
        except Exception, e:
            self.logger.error("Erreur lors du découpage d'entête\nBulletin:\n%s",rawBulletin)
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

           Retourne une liste de rawBulletins, séparés

           Utilisation:

                Séparer les bulletins FC/FT qui contiennent plus d'un bulletin
                par bulletin.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        entete = rawBulletin.split(self.lineSeparator)[0]

        listeBulletins = []
        unBulletin = []
        motCle = 'TAF'

        # Les bulletins FC/FT ont une entête commune, et le data de chaque
        # station commence par 'TAF'
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
        """### Ajout de bulletinManagerAm ###

           Overriding ici pour passer les bons arguments au bulletinAm

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return bulletinAm.bulletinAm(rawBulletin,self.logger,self.lineSeparator,self.mapEntetes,self.SMHeaderFormat)


    def writeBulletinToDisk(self,unRawBulletin,includeError=False):
        bulletinManager.bulletinManager.writeBulletinToDisk.__doc__ + \
        """### Ajout de bulletin manager AM ###

           Les bulletins en AM peuvent êtres divisibles, donc
           une division est effectuée et est passée à la méthode
           de la superclasse.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        if self.__isSplittable(unRawBulletin):
            for rawBull in self.__splitBulletin(unRawBulletin):
                bulletinManager.bulletinManager.writeBulletinToDisk(self,rawBull,includeError=includeError)
        else:
            bulletinManager.bulletinManager.writeBulletinToDisk(self,unRawBulletin,includeError=includeError)

    def reloadMapEntetes(self, pathFichierStations):
        """reloadMapEntetes(pathFichierStations)


           pathFichierStations: String
                                - Chemin d'accès vers le fichier de "collection"

           Recharge le fichier d'entêtes en mémoire.

           Utilisation:

                Pour le rechargement lors d'un SIGHUP.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Décembre 2004
        """
        oldMapEntetes = self.mapEntetes

        try:

            self.initMapEntetes(pathFichierStations)

            self.logger.info("Succès du rechargement du fichier d'entêtes")

        except Exception,e :

            self.mapEntetes = oldMapEntetes

            self.logger.warning("Échec du rechargement du fichier d'entêtes")

            raise

    def initMapEntetes(self, pathFichierStations):
        """initMapEntetes(pathFichierStations)

           pathFichierStations: String
                                - Chemin d'accès vers le fichier de "collection"

           mapEntetes sera un map contenant les entête à utiliser avec
           quelles stations. La clé se trouve a être une concaténation des
           2 premières lettres du bulletin et de la station, la définition
           est une string qui contient l'entête à ajouter au bulletin.

           self.mapEntetes2mapStations sera un map, avec pour chaque entête
           un map associé des stations, dont la valeur sera None.

                Ex.: mapEntetes["SPCZPC"] = "CN52 CWAO "

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """

        if pathFichierStations == None:
            self.mapEntetes = None
            return

        # read in the collection station file...with the new parser from DL

        sp = StationParser.StationParser(self.pathCollectionStation)
        sp.parse()
        self.mapCollectionStation = sp.getStationsColl()

        # proceed with the same processing except use the map instead of the file lines

        uneEntete = ""
        uneCle = ""
        unPrefixe = ""
        uneLigneParsee = ""
        self.mapEntetes = {}
        self.mapEntetes2mapStations = {}

        # Construction des 2 map en même temps
        for key in self.mapCollectionStation :

            unPrefixe = key[:2]
            uneEntete = key[2:]

            # Ajout d'un map vide pour l'entête courante
            if unPrefixe + uneEntete[:-1] not in self.mapEntetes2mapStations:
                self.mapEntetes2mapStations[unPrefixe + uneEntete[:-1]] = {}

            for station in self.mapCollectionStation[key] :
                uneCle = unPrefixe + station

                self.mapEntetes[uneCle] = uneEntete

                self.mapEntetes2mapStations[unPrefixe + uneEntete[:-1]][station] = None
