# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""ReceiverAm: socketAm -> disk, incluant traitement pour les bulletins"""

import gateway
import socketManagerAm
import bulletinManagerAm
import socketManager
from socketManager import socketManagerException
import PXPaths 

PXPaths.normalPaths()

class receiverAm(gateway.gateway):
    __doc__ = gateway.gateway.__doc__ + \
    """
    ### Ajout de receiver AM ###

    Implantation du receiver pour un feed AM. Il est constitu�
    d'un socket manager AM et d'un bulletin manager AM.

    Auteur: Louis-Philippe Th�riault
    Date:   Octobre 2004
    """

    def __init__(self, path, source, logger):
        gateway.gateway.__init__(self, path, source, logger)

        self.pathFichierStations = PXPaths.STATION_TABLE

        self.establishConnection()

        self.renewBulletinManager()

    def renewBulletinManager(self):
        self.logger.debug("renewBulletinManager() has been called (type = am)")
        self.unBulletinManager = bulletinManagerAm.bulletinManagerAm(
                                    PXPaths.RXQ + self.flow.name,
                                    self.logger,
                                    pathFichierCircuit = self.flow.routingTable, 
                                    SMHeaderFormat = self.flow.addSMHeader,
                                    pathFichierStations = self.pathFichierStations,
                                    extension = self.flow.extension, 
                                    mapEnteteDelai = self.flow.mapEnteteDelai,
                                    source= self.flow)

    def shutdown(self):
        __doc__ = gateway.gateway.shutdown.__doc__ + \
        """### Ajout de receiverAm ###

           Fermeture du socket et finalisation du tra�tement du
           buffer.

           Utilisation:

                Fermeture propre du programme via sigkill/sigterm

           Visibilit�:  Publique
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """
        gateway.gateway.shutdown(self)

        if self.unSocketManagerAm.isConnected():
            resteDuBuffer, nbBullEnv = self.unSocketManagerAm.closeProperly()

            self.write(resteDuBuffer)

        self.logger.info("Succ�s du tra�tement du reste de l'info")

    def establishConnection(self):
        __doc__ = gateway.gateway.establishConnection.__doc__ + \
        """### Ajout de receiverAm ###

           establishConnection ne fait que initialiser la connection
           socket.

           Utilisation:

                En encapsulant la connection r�seau par cette m�thode, il est plus
                facile de g�rer la perte d'une connection et sa reconnection.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """

        self.logger.debug("Instanciation du socketManagerAm")

        # Instanciation du socketManagerAm
        self.unSocketManagerAm = \
                socketManagerAm.socketManagerAm(self.logger,type='slave', \
                        port=self.flow.port)

    def read(self):
        __doc__ =  gateway.gateway.read.__doc__ + \
        """### Ajout de receiverAm ###

           Le lecteur est le socket tcp, g�r� par socketManagerAm.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004


           Modification le 25 janvier 2005: getNextBulletins()
           retourne une liste de bulletins.

           Auteur:      Louis-Philippe Th�riault
        """
        if self.unSocketManagerAm.isConnected():
            try:
                data = self.unSocketManagerAm.getNextBulletins()
            except socketManager.socketManagerException, e:
                if e.args[0] == "la connexion est brisee":
                    self.logger.error("Perte de connection, tra�tement du reste du buffer")
                    data, nbBullEnv = self.unSocketManagerAm.closeProperly()
                else:
                    raise
        else:
            raise gateway.gatewayException("Le lecteur ne peut �tre acc�d�")

        self.logger.veryveryverbose("%d nouveaux bulletins lus" % len(data))

        return data

    def write(self,data):
        __doc__ =  gateway.gateway.write.__doc__ + \
        """### Ajout de receiverAm ###

           L'�crivain est un bulletinManagerAm.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """

        self.logger.veryveryverbose("%d nouveaux bulletins seront �crits" % len(data))

        while True:
            if len(data) <= 0:
                break

            rawBulletin = data.pop(0)

            self.unBulletinManager.writeBulletinToDisk(rawBulletin,includeError=True)

    def reloadConfig(self):
        __doc__ = gateway.gateway.reloadConfig.__doc__
        self.logger.info('Demande de rechargement de configuration')

        try:

            newConfig = gateway.gateway.loadConfig(self.pathToConfigFile)

            ficCircuits = newConfig.ficCircuits
            ficCollection = newConfig.ficCollection

            # Reload du fichier de circuits
            # -----------------------------
            self.unBulletinManager.drp.reparse()

            self.config.ficCircuits = ficCircuits

            # Reload du fichier de stations
            # -----------------------------
            self.unBulletinManager.reloadMapEntetes(ficCollection)

            self.config.ficCollection = ficCollection

            self.logger.info('Succ�s du rechargement de la config')

        except Exception, e:

            self.logger.error('�chec du rechargement de la config!')

            self.logger.debug("Erreur: %s", str(e.args))
