# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""Spécialisation pour gestion de sockets "WMO" """

__version__ = '2.0'

import struct, socket, curses, curses.ascii, string
import socketManager
import time

class socketManagerWmo(socketManager.socketManager):
    __doc__ = socketManager.socketManager.__doc__ + \
    """
       ### Ajout de socketManagerWmo ###

       * Attributs

            patternWmoRec           str

                                    - Pattern pour le découpage d'entête
                                      par struct

            sizeWmoRec              int

                                    - Longueur de l'entête (en octets)
                                      calculée par struct

       Auteur: Louis-Philippe Thériault
       Date:   Octobre 2004
       Modifications: Decembre2004, Pierre Michaud
    """

    def __init__(self,logger,type='slave',port=9999,remoteHost=None,timeout=None, flow=None):
        socketManager.socketManager.__init__(self,logger,type,port,remoteHost,timeout, flow)

        # La taille du wmoHeader est prise d'a partir du document :
        # "Use of TCP/IP on the GTS", pages 28-29, et l'exemple en C
        # page 49-54
        self.patternWmoRec = '8s2s'
        self.sizeWmoRec = struct.calcsize(self.patternWmoRec)

        self.maxCompteur = 99999
        self.compteur = 0

        self.debugFile = False

    def unwrapBulletin(self):
        __doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
        """### Ajout de socketManagerWmo ###

           Définition de la méthode

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        status = self.checkNextMsgStatus()

        if status == 'OK':
            (msg_length,msg_type) = \
                     struct.unpack(self.patternWmoRec,self.inBuffer[0:self.sizeWmoRec])

            msg_length = int(msg_length)

            bulletin = self.inBuffer[self.sizeWmoRec:self.sizeWmoRec + msg_length]

            return (bulletin[12:-4],self.sizeWmoRec + msg_length)
        elif status == 'INCOMPLETE':
            return '',0
        else:
        # Donc message corrompu
            raise socketManagerException("Données corrompues",self.inBuffer)

    def wrapBulletin(self,bulletin):
        __doc__ = socketManager.socketManager.wrapBulletin.__doc__ + \
        """### Ajout de socketManagerWmo ###
           Nom:
           wrapBulletin

           Parametres d'entree:
           -bulletin:   un objet bulletinWmo

           Parametres de sortie:
           -Retourne le bulletin pret a envoyer en format string

           Description:
           Ajoute l'entete WMO approprie au bulletin passe en parametre.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
           Modifications: Decembre 2004, Pierre Michaud
        """
        bulletinStr = chr(curses.ascii.SOH) + '\r\r\n' + self.getNextCounter(5) + '\r\r\n' + bulletin.getBulletin(useFinalLineSeparator=True) + '\r\r\n' + chr(curses.ascii.ETX)

        #repr(bulletinStr)

        return string.zfill(len(bulletinStr),8) + bulletin.getDataType() + bulletinStr

    def getNextCounter(self,x):
        """getNextCounter() -> compteur

           compteur:    String
                        - Portion "compteur" du bulletin

           Utilisation:

                Générer le compteur pour un bulletinWmo. L'on doit être sur que le bulletin
                sera dans le queue de bulletins à envoyer.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        if self.compteur > self.maxCompteur:
            self.compteur = 0

        self.compteur = self.compteur + 1

        return string.zfill(self.compteur,len(str(self.maxCompteur)))

    def checkNextMsgStatus(self):
        __doc__ = socketManager.socketManager.checkNextMsgStatus.__doc__ + \
        """### Ajout de socketManagerAm ###

           Définition de la méthode

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        if len(self.inBuffer) >= self.sizeWmoRec:
            (msg_length,msg_type) = \
                     struct.unpack(self.patternWmoRec,self.inBuffer[0:self.sizeWmoRec])
        else:
            return 'INCOMPLETE'

        try:
            msg_length = int(msg_length)
            self.logger.debug("Longueur du message: %d",msg_length)
        except ValueError:
            self.logger.debug("Corruption: longueur n'est pas lisible")
            return 'CORRUPT'

        if not msg_type in ['BI','AN','FX']:
            self.logger.debug("Corruption: Type de message est incorrec")
            return 'CORRUPT'

        if len(self.inBuffer) >= self.sizeWmoRec + msg_length:
            if ord(self.inBuffer[self.sizeWmoRec]) != curses.ascii.SOH or ord(self.inBuffer[self.sizeWmoRec+msg_length-1]) != curses.ascii.ETX:
                self.logger.debug("Corruption: Caractères de contrôle incorrects")
                return 'CORRUPT'

            return 'OK'
        else:
            return 'INCOMPLETE'

    def sendBulletin(self,bulletin):
        #__doc__ = socketManager.socketManager.sendBulletin.__doc__ + \
        """
        ###Methode concrete pour socketManagerWmo###

        Nom:
        sendBulletin

        Parametres d'entree:
        -bulletin:
                -un objet bulletin

        Parametres de sortie:
        -si succes: 0
        -sinon: 1

        Description:
        Envoi au socket correspondant un bulletin WMO et indique
        si le bulletin a ete transfere totalement ou non.  Chaque
        envoi s'assure de l'etat de la connexion.

        Auteur:
        Pierre Michaud

        Date:
        Decembre 2004
        """
        try:
            #preparation du bulletin pour l'envoi
            data = self.wrapBulletin(bulletin)

            # debuging...!? keep the transmitted file
            if self.debugFile :
               self.writetofile("/tmp/WMO",data)

            #tentative d'envoi et controle de la connexion
            try:
                #envoi du bulletin
                bytesSent = self.socket.send(data)

                #verifier si l'envoi est un succes
                if bytesSent != len(data):
                    self.connected=False
                    return (0, bytesSent)
                else:
                    return (1, bytesSent)

            except socket.error, e:
                #erreurs potentielles: 104, 107, 110 ou 32
                self.logger.error("senderWmo.write(): la connexion est rompue: %s",str(e.args))
                #modification du statut de la connexion
                #tentative de reconnexion
                self.connected = False
                self.logger.info("senderWmo.write(): tentative de reconnexion")
                self.socket.close()
                self._socketManager__establishConnection()

        except Exception, e:
            self.logger.error("socketManagerWmo.sendBulletin(): erreur d'envoi: %s",str(e.args))
            raise

    # debug development module write data to file
    def writetofile(self,filename,data):
        import os,random

        r = random.random()
        str_r = '%f' % r
        unFichier = os.open( filename + str_r, os.O_CREAT | os.O_WRONLY )
        os.write( unFichier , data )
        os.close( unFichier )
