# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""D�finition d'une sous-classe pour les bulletins "AM" """

import time
import struct
import string
import curses
import curses.ascii
import bulletin

__version__ = '2.0'

class bulletinAm(bulletin.bulletin):
    __doc__ = bulletin.bulletin.__doc__ + \
    """
    ## Ajouts de bulletinAm ##

    Implantation pour un usage concret de la classe bulletin

            * Informations � passer au constructeur

            mapEntetes              dict (default=None)

                                    - Si autre que None, le reformattage
                                      d'ent�tes est effectu�
                                    - Une map contenant les ent�tes � utiliser
                                      avec quelles stations. La cl� se trouve �
                                      �tre une concat�nation des 2 premi�res
                                      lettres du bulletin et de la station, la
                                      d�finition est une string qui contient
                                      l'ent�te � ajouter au bulletin.

                                      Ex.: TH["SPCZPC"] = "CN52 CWAO "
                                    - Si est � None, aucun tra�tement sur
                                      l'ent�te est effectu�

            SMHeaderFormat          bool (default=False)

                                    - Si True, ajout de la ligne "AAXX jjhhmm4\\n"
                                      � la 2i�me ligne du bulletin

    Auteur: Louis-Philippe Th�riault
    Date:   Octobre 2004
    """


    def __init__(self,stringBulletin,logger,lineSeparator='\n',mapEntetes=None,SMHeaderFormat=False):
        bulletin.bulletin.__init__(self,stringBulletin,logger,lineSeparator='\n')
        self.mapEntetes = mapEntetes
        self.SMHeaderFormat = SMHeaderFormat

    def doSpecificProcessing(self):
        __doc__ = bulletin.bulletin.doSpecificProcessing.__doc__ + \
        """### Ajout de bulletinAm ###

           Modifie les bulletins provenant de stations, transmis
           par protocole Am, nomm�s "Bulletins Am"

           Visibilit�:  Publique
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """
        self.replaceChar('\r','')

        unBulletin = self.bulletin

        if len(self.getHeader().split()) < 1:
        # Si la premi�re ligne est vide, bulletin erron�, aucun tra�tement
            bulletin.bulletin.verifyHeader(self)
            return

        # Si le bulletin est � modifier et que l'ent�te doit �tre renom�e
        if self.mapEntetes != None and len(self.getHeader().split()[0]) == 2:
            # Si le premier token est 2 lettres de long

            uneEnteteDeBulletin = None

            premierMot = self.getType()

            station = self.getStation()

            # Fetch de l'ent�te
            if station != None:
                # Construction de la cle
                if premierMot != "SP":
                    uneCle = premierMot + station
                else:
                    uneCle = "SA" + station

                # Fetch de l'entete a inserer
                if premierMot in ["CA","MA","RA"]:
                    uneEnteteDeBulletin = "CN00 CWAO "
                else:
                    try:
                        uneEnteteDeBulletin = self.mapEntetes[uneCle]
                    except KeyError:
                    # L'ent�te n'a pu �tre trouv�e
                        uneEnteteDeBulletin = None

            # Construction de l'ent�te
            if station != None and uneEnteteDeBulletin != None:
                if len(unBulletin[0].split()) == 1:
                    uneEnteteDeBulletin = premierMot + uneEnteteDeBulletin + self.getFormattedSystemTime()
                elif len(unBulletin[0].split()) == 2:
                    uneEnteteDeBulletin = premierMot + uneEnteteDeBulletin + unBulletin[0].split()[1]
                else:
                    uneEnteteDeBulletin = premierMot + uneEnteteDeBulletin + unBulletin[0].split()[1] + ' ' + unBulletin[0].split()[2]

                # Assignement de l'entete modifiee
                self.setHeader(uneEnteteDeBulletin)

                # Si le bulletin est � modifier et que l'on doit tra�ter les SM/SI
                # (l'ajout de "AAXX jjhhmm4\n")
                if self.SMHeaderFormat and self.getType() in ["SM","SI"]:
                    self.bulletin.insert(1, "AAXX " + self.getHeader().split()[2][0:4] + "4")

            if station == None or uneEnteteDeBulletin == None:
                if station == None:
                    self.setError("Pattern de station non trouve ou non specifie")

                    self.logger.warning("Pattern de station non trouve")
                    self.logger.warning("Bulletin:\n"+self.getBulletin())

                # L'ent�te n'a pu �tre trouv�e dans le fichier de collection, erreur
                elif uneEnteteDeBulletin == None:
                    self.setError("Entete non trouvee dans le fichier de collection")

                    self.logger.warning("Station <" + station + "> non trouvee avec prefixe <" + premierMot + ">")
                    self.logger.warning("Bulletin:\n"+self.getBulletin())

        if self.getType() in ['UG','UK','US'] and self.bulletin[1] == '':
            self.bulletin.remove('')

        if self.bulletin[0][0] == '\x01':
            self.replaceChar('\x01','')
            self.replaceChar('\x03\x04','')

        if self.bulletin[0][:6] in ['RACN00']:
            self.replaceChar('\x02','')
            self.replaceChar('\x03','')
            self.replaceChar('\x04','')

        if self.bulletin[0][:4] in ['SACN']:
            self.replaceChar('\x0e','')
            self.replaceChar('\x0f','')


        bulletin.bulletin.verifyHeader(self)

    def getFormattedSystemTime(self):
        """getFormattedSystemTime() -> heure

           heure:       String

           Retourne une string de l'heure locale du systeme, selon
           jjhhmm : jour/heures(24h)/minutes

           Utilisation:

                G�n�rer le champ jjhhmm pour l'ent�te du bulletin avec
                l'heure courante.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre
        """
        return time.strftime("%d%H%M",time.localtime())

    def verifyHeader(self):
        __doc__ = bulletin.bulletin.verifyHeader.__doc__ + \
        """### Ajout de bulletinAm ###

           Overriding ici pour que lors de l'instanciation, le bulletin
           ne soit pas v�rifi�.
        """
        return
