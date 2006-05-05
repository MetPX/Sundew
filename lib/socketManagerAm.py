# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""Spécialisation pour gestion de sockets "AM" """

__version__ = '2.0'

import struct, socket, curses, curses.ascii, string, time
import socketManager

class socketManagerAm(socketManager.socketManager):
    __doc__ = socketManager.socketManager.__doc__ + \
    """
    --- Spécialisation concrète pour la gestion de sockets AM ---

    ### Ajout de socketManagerAm ###

    * Attributs

    patternAmRec            str

                            - Pattern pour le découpage d'entête
                              par struct

    sizeAmRec               int

                            - Longueur de l'entête (en octets)
                              calculée par struct

    Auteur: Louis-Philippe Thériault
    Date:   Octobre 2004
    """

    #def __init__(self,logger,type='slave',localPort=9999,remoteHost=None,timeout=None):
            #socketManager.socketManager.__init__(self,logger,type,localPort,remoteHost,timeout)
    def __init__(self,logger,type='slave',port=9999,remoteHost=None,timeout=None):
        socketManager.socketManager.__init__(self,logger,type,port,remoteHost,timeout)

        # La taille du amRec est prise d'a partir du fichier ytram.h, à l'origine dans
        # amtcp2file. Pour la gestion des champs l'on se refere au module struct
        # de Python.
        #self.patternAmRec = '80sLL4sii4s4s20s'
        self.patternAmRec = '80sLL4siiii20s'
        self.sizeAmRec = struct.calcsize(self.patternAmRec)

    def unwrapBulletin(self):
        __doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
        """### Ajout de socketManagerAm ###

           Définition de la méthode

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        status = self.checkNextMsgStatus()

        if status == 'OK':
            (header,src_inet,dst_inet,threads,start,length,firsttime,timestamp,future) = \
                     struct.unpack(self.patternAmRec,self.inBuffer[0:self.sizeAmRec])

            length = socket.ntohl(length)

            bulletin = self.inBuffer[self.sizeAmRec:self.sizeAmRec + length]

            return (bulletin,self.sizeAmRec + length)
        else:
            return '',0

    def wrapBulletin(self,bulletin):
        __doc__ = socketManager.socketManager.wrapBulletin.__doc__ + \
        """### Ajout de socketManagerAm ###
           Nom:
           wrapBulletin

           Parametres d'entree:
           -bulletin:   un objet bulletinAm

           Parametres de sortie:
           -Retourne le bulletin pret a envoyer en format string

           Description:
           Ajoute l'entete AM appropriee au bulletin passe en parametre.

           Auteur:      Pierre Michaud
           Date:        Janvier 2005
        """
        #initialisation des parametres de l'entete
        #char header[80]
        tmp = bulletin.getBulletin()
        size = struct.calcsize('80s')

        nulList = [chr(curses.ascii.NUL) for x in range(size)]
        header = list(tmp[0:size])

        paddedHeader = header + nulList[len(header):]

        header = string.join(paddedHeader,'')
        header = header.replace(chr(curses.ascii.LF), chr(curses.ascii.NUL), 1)

        #unsigned long src_inet, dst_inet
        src_inet = 0
        dst_inet = 0

        #unsigned char threads[4]
        #threads='0'+chr(255)+'0'+'0'
        threads= chr(0) + chr(255) + chr(0) + chr(0)

        #unsigned int start, length
        start = 0
        length = socket.htonl( len(bulletin.getBulletin()) )

        #time_t firsttime, timestamp
        #firsttime = chr(curses.ascii.NUL)
        #timestamp = chr(curses.ascii.NUL)
        firsttime = socket.htonl(int(time.time()))
        timestamp = socket.htonl(int(time.time()))

        #char future[20]
        future = chr(curses.ascii.NUL)

        #construction de l'entete
        bulletinHeader = struct.pack(self.patternAmRec,header,src_inet,dst_inet,threads,start \
                                ,length,firsttime,timestamp,future)

        #assemblage de l'entete avec le contenu du bulletin
        wrappedBulletin = bulletinHeader + bulletin.getBulletin()

        return wrappedBulletin

    def checkNextMsgStatus(self):
        __doc__ = socketManager.socketManager.checkNextMsgStatus.__doc__ + \
        """### Ajout de socketManagerAm ###

           Définition de la méthode

           Ne détecte pas si les données sont corrompues, limitations du
           protocole AM ?

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        if len(self.inBuffer) >= self.sizeAmRec:
            (header,src_inet,dst_inet,threads,start,length,firsttime,timestamp,future) = \
                    struct.unpack(self.patternAmRec,self.inBuffer[0:self.sizeAmRec])
        else:
            return 'INCOMPLETE'

        length = socket.ntohl(length)

        if len(self.inBuffer) >= self.sizeAmRec + length:
            return 'OK'
        else:
            return 'INCOMPLETE'

    def sendBulletin(self,bulletin):
        #__doc__ = socketManager.socketManager.sendBulletin.__doc__ + \
        """
        ###Methode concrete pour socketManagerAm###

        Nom:
        sendBulletin

        Parametres d'entree:
        -bulletin:
                -un objet bulletin

        Parametres de sortie:
        -si succes: 0
        -sinon: 1

        Description:
        Envoi au socket correspondant un bulletin AM et indique
        si le bulletin a ete transfere totalement ou non.  Chaque
        envoi s'assure de l'etat de la connexion.

        Auteur:
        Pierre Michaud

        Date:
        Decembre 2005
        """
        try:
            #preparation du bulletin pour l'envoi
            data = self.wrapBulletin(bulletin)

            #print repr(data)
            #print('=====================================================================')

            #tentative d'envoi et controle de la connexion
            #mettre le try/except dans un while(1)????
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
                self.logger.error("senderAm.write(): la connexion est rompue: %s",str(e.args))
                #modification du statut de la connexion
                #tentative de reconnexion
                self.connected = False
                self.logger.info("senderAm.write(): tentative de reconnexion")
                self.socket.close()
                self._socketManager__establishConnection()

        except Exception, e:
            self.logger.error("socketManagerAm.sendBulletin(): erreur d'envoi: %s",str(e.args))
            raise

    def writetofile(self,filename,data):
           import sys, os
           import random 
           r = random.random()
           str_r = '%f' % r
           unFichier = os.open( filename + str_r, os.O_CREAT | os.O_WRONLY )
           os.write( unFichier , data )
           os.close( unFichier )
