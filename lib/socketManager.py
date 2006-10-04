# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""Gestionnaire de sockets générique"""

import socket, time, string, sys, traceback

__version__ = '2.0'

class socketManagerException(Exception):
    """Classe d'exception spécialisés relatives au socket managers"""
    pass

class socketManager:
    """Classe abstraite regroupant toutes les fonctionnalitées
       requises pour un gestionnaire de sockets. Les méthodes
       qui ne retournent qu'une exception doivent êtres redéfinies
       dans les sous-classes (il s'agit de méthodes abstraites).

       Les arguments à passer pour initialiser un socketManager sont les
       suivants:

            type            'master','slave' (default='slave')

                            - Si master est fourni, le programme se
                              connecte à un hôte distant, si slave,
                              le programme écoute pour une
                              connexion.

            port    int (default=9999)

                            - Port local ou se 'bind' le socket.

            remoteHost      (str hostname,int port)

                            - Couple de (hostname,port) pour la
                              connexion. Lorsque timeout secondes
                              est atteint, un socketManagerException
                              est levé.

                            - Doit être absolument fourni si type='master',
                              et non fourni si type='slave'.

            timeout         int (default=None)

                            - Lors de l'établissement d'une connexion
                              à un hôte distant, délai avant de dire
                              que l'hôte de réponds pas.

            log             Objet Log (default=None)

                            - Objet de la classe Log

       Auteur:      Louis-Philippe Thériault
       Date:        Septembre 2004
    """
    def __init__(self,logger,type='slave',port=9999,remoteHost=None,timeout=None, flow=None):
        self.type = type
        self.port = port
        self.remoteHost = remoteHost
        self.timeout = timeout
        self.logger = logger

        self.inBuffer = ""
        self.outBuffer = []
        self.connected = False

        self.flow = flow

        # Établissement de la connexion
        self.__establishConnection()

    def __establishConnection(self):
        """
           Nom:
           __establishConnection()

           Parametres d'entree:
           -Aucun

           Parametres de sortie:
           -Aucun

           Description:
           Établit la connexion selon la valeur des attributs de l'objet.
           self.socket sera, après l'exécution, la connexion.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
           Modifications: Pierre Michaud, 2004-12-15
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Binding avec le port local
        # Si ce n'est pas un master - Pierre Michaud 2004-12-15
        if self.type == 'slave':
            self.logger.info("Socket binding with port %d",self.port)
            while True:
                try:
                    self.socket.bind(('',self.port))
                    break
                except socket.error:
                    self.logger.info(" Bind failed")
                    time.sleep(10)

        # KEEP_ALIVE à True, pour que si la connexion tombe, la notification
        # soit immédiate
        # nb: Ne semble pas fonctionner
        if self.flow.keepAlive:
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1)
        else:
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,0)
            self.logger.info('SO_KEEPALIVE set to 0')

        # Snapshot du temps
        then = time.time()

        # Tentative de connexion
        #connexion type client (exemple PDS-NCCS: un sender)
        if self.type == 'master':
            # La connexion doit se faire a un hôte distant
            if self.remoteHost == None:
                raise socketManagerException('remoteHost (host,port) n\'est pas spécifié')

            self.logger.info("Trying to connect remote host %s", str(self.remoteHost) )

            while True:
                # Commented by DL (2005-03-30) at the request of AMB
                """
                if self.timeout != None and (time.time() - then) > self.timeout:
                    self.socket.close()
                    raise socketManagerException('timeout dépassé')
                """

                try:
                    self.socket.connect((
                            socket.gethostbyname(self.remoteHost),
                            int(self.port) ))
                    break

                except socket.error:
                    (type, value, tb) = sys.exc_info()
                    self.logger.error("Type: %s, Value: %s, Sleeping 30 seconds ..." % (type, value))
                    time.sleep(30)

        #connexion type serveur (exemple PDS-NCCS: un receiver) ou bidirectionnelle
        else:
            # En attente de connexion
            self.socket.listen(1)


            while True:
                # Commented by DL (2005-03-30) at the request of AMB
                """
                if self.timeout != None and (time.time() - then) > self.timeout:
                    self.socket.close()
                    raise socketManagerException('timeout dépassé')
                """
                self.logger.info("Waiting for a connexion (listen mode)")
                try:
                    conn, self.remoteHost = self.socket.accept()
                    break
                except TypeError:
                    time.sleep(1)
                except socket.error:
                    (type, value, tb) = sys.exc_info()
                    # Normally, this error is generated when a SIGHUP signal is sent and the system call (socket.accept())
                    # is interrupted
                    if value[0] == 4: 
                       self.logger.warning("Type: %s, Value: %s, [socket.accept()]" % (type, value))
                       #self.logger.error(''.join(traceback.format_exception(type, value, tb)))
                    # For case we are not aware at this time, we raise the exception
                    else:
                       raise

            self.socket.close()
            self.socket = conn

        #L'ensemble des protocoles implantes ici n'ont pas besoin du non-blocking
        #Si le non-blocking est utilise, les sender sont en probleme et aptes
        #a mettre un receiver a terre en moins de deux...
        self.socket.setblocking(True)

        self.logger.info("Connexion established with %s",str(self.remoteHost))
        self.connected = True

    def closeProperly(self):
        """closeProperply() -> ([bulletinsReçus],nbBulletinsEnvoyés)

           [bulletinsReçus]:    liste de str
                                - Retourne les bulletins dans le buffer lors
                                  de la fermeture

           Ferme le socket et finit de traîter le socket d'arrivée et de
           sortie.

           Utilisation:

                Traîter l'information restante, puis éliminer le socket
                proprement.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        self.logger.info("Fermeture du socket et copie du reste du buffer")

        # Coupure de la connexion
        try:
            self.socket.shutdown(2)
            self.logger.debug("Shutdown du socket: [OK]")
        except Exception, e:
            self.logger.debug("Shutdown du socket: [ERREUR]\n %s",str(e))

        # Copie du reste du buffer entrant après la connexion
        # Le bulletin doit être mis à non blocking si on
        # veut fermer la connection proprement.
        try:
            self.socket.setblocking(False)
            self.__syncInBuffer(onlySynch = True)
            self.socket.setblocking(True)
        except Exception:
            pass

        # Fermeture du socket
        try:
            self.socket.close()
        except Exception:
            pass

        self.connected = False

        # Traîtement du reste du buffer pour découper les bulletins
        bulletinsRecus = self.getNextBulletins()


        self.logger.info("Succès de la fermeture de la connexion socket")
        self.logger.debug("Nombre de bulletins dans le buffer : %d",len(bulletinsRecus))

        return (bulletinsRecus, 0)

    def getNextBulletins(self):
        """getNextBulletins() -> [bulletin]

           bulletin     : [String]

           Retourne les prochains bulletin reçus, une liste vide sinon.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004

           Modifiée le 25 janvier 2005, retourne maintenant une liste, et
           le socket est bloquant.

           Auteur:      Louis-Philippe Thériault
        """
        if self.isConnected():
        # Si n'est pas connecté, ne fais pas le check, car l'on peut vouloir avoir les
        # bulletins dans le buffer sans être connecté.
            self.__syncInBuffer()

        nouveauxBulletins = []

        while True:

            status = self.checkNextMsgStatus()

            self.logger.debug("Statut du prochain bulletin dans le buffer: %s", status )

            if status == 'INCOMPLETE':
                break

            if status ==  'OK':
                (bulletin,longBuffer) = self.unwrapBulletin()

                self.inBuffer = self.inBuffer[longBuffer:]

                nouveauxBulletins.append(bulletin)
            elif status == 'CORRUPT':
                raise socketManagerException('corruption dans les données','CORRUPT',self.inBuffer)
            else:
                raise socketManagerException('status de buffer inconnu',status,self.inBuffer)

        return nouveauxBulletins

    def sendBulletin(self):
        raise socketManagerException('socketManager.sendBulletin() est une methode virtuelle pure')

    def __syncInBuffer(self,onlySynch=False):
        """__syncInBuffer()

           onlySynch:   Booleen
                        - Si est à True, ne vérifie pas que la connexion fonctionne,
                          Ne fait que syncher le buffer

           Copie l'information du buffer du socket s'il y a lieu

           Lève une exception si la connexion est perdue.

           Utilisation:

                Copier le nouveau data reçu du socket dans l'attribut
                du socketManager.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004


           Modification:        Modification du code pour que le socket soit non-bloquant.
        """
        while True:
            try:
                temp = self.socket.recv(32768)

                if temp == '':
                    self.connected = False

                    if not onlySynch:
                        self.logger.error("La connexion est brisée")
                        raise socketManagerException('la connexion est brisee')

                self.logger.veryverbose("Data reçu: %s" % temp)

                self.inBuffer = self.inBuffer + temp
                break

            except socket.error, inst:
                (type, value, tb) = sys.exc_info()
                # Normally, this error is generated when a SIGHUP signal is sent and the system call (socket.recv(32768))
                # is interrupted
                if value[0] == 4: 
                    self.logger.warning("Type: %s, Value: %s, [socket.recv(32768)]" % (type, value))
                    break

                if not onlySynch:
                # La connexion est brisée
                    self.connected = False

                    self.logger.error("La connexion est brisée")
                    raise socketManagerException('la connexion est brisee')

    def __transmitOutBuffer(self):
        pass

    def wrapBulletin(self,bulletin):
        """wrapbulletin(bulletin) -> wrappedBulletin

           bulletin             : String
           wrappedBulletin      : String

           Retourne le bulletin avec les entetes/informations relatives
           au protocole sous forme de string. Le bulletin doit etre un
           objet Bulletin. Wrap bulletin doit être appelé seulement si
           ce bulletin est sûr d'être envoyé, étant donné la possibilité
           d'un compteur qui doit se suivre.

           Statut:      Abstraite
           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        raise socketManagerException("Méthode non implantée (méthode abstraite wrapBulletin)")

    def unwrapBulletin(self):
        """unwrapBulletin() -> (bulletin,longBuffer)

           bulletin     : String
           longBuffer   : int

           Retourne le prochain bulletin contenu dans le buffer,
           après avoir vérifié son intégrité, sans modifier le buffer.
           longBuffer sera égal à la longueur de ce que l'on doit enlever
           au buffer pour que le prochain bulletin soit en premier.

           Retourne une chaîne vide s'il n'y a pas assez de données
           pour compléter le prochain bulletin.

           Statut:      Abstraite
           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        raise socketManagerException("Méthode non implantée (méthode abstraite unwrapBulletin)")

    def isConnected(self):
        """isConnected() -> bool

           Retourne True si la connexion est établie.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return self.connected

    def checkNextMsgStatus(self):
        """checkNextMsgStatus() -> status

           status       : String élément de ('OK','INCOMPLETE','CORRUPT')

           Statut du prochain bulletin dans le buffer.

           Statut:      Abstraite
           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        raise socketManagerException("Méthode non implantée (méthode abstraite checkNextMsgStatus)")

    def setConnected(self,valeur):
        """
        Description: modifie le statut de l'attribut connected
        Auteur: PM
        Date: janvier 2005
        """
        self.connected = valeur
