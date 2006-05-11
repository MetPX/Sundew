# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""ReceiverWmo: socketWmo -> disk, incluant traitement pour les bulletins"""

import gateway
import socketManagerWmo
import bulletinManagerWmo
import socketManager
from socketManager import socketManagerException
import PXPaths

PXPaths.normalPaths()

class receiverWmo(gateway.gateway):
    __doc__ = gateway.gateway.__doc__ + \
    """
    ### Ajout de receiver WMO ###

    Implantation du receiver pour un feed Wmo. Il est constitué
    d'un socket manager Wmo et d'un bulletin manager Wmo.

    Auteur: Louis-Philippe Thériault
    Date:   Octobre 2004
    """

    def __init__(self,path,source,logger):
        gateway.gateway.__init__(self,path,source,logger)

        self.source = source 
        self.establishConnection()

        self.logger.debug("Instanciation du bulletinManagerWmo")

        # Instanciation du bulletinManagerWmo avec la panoplie d'arguments.
        self.unBulletinManager = \
                  bulletinManagerWmo.bulletinManagerWmo(
                     PXPaths.RXQ + source.name, logger, \
                     pathFichierCircuit = '/dev/null', \
                     extension = source.extension, \
                     mapEnteteDelai = source.mapEnteteDelai,
                     source = source)

    def shutdown(self):
        __doc__ = gateway.gateway.shutdown.__doc__ + \
        """### Ajout de receiverWmo ###

           Fermeture du socket et finalisation du traîtement du
           buffer.

           Utilisation:

                Fermeture propre du programme via sigkill/sigterm

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        gateway.gateway.shutdown(self)

        if self.unSocketManagerWmo.isConnected():
            resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()

            self.write(resteDuBuffer)

        self.logger.info("Succès du traîtement du reste de l'info")

    def establishConnection(self):
        __doc__ = gateway.gateway.establishConnection.__doc__ + \
        """### Ajout de receiverWmo ###

           establishConnection ne fait que initialiser la connection
           socket.

           Utilisation:

                En encapsulant la connection réseau par cette méthode, il est plus
                facile de gérer la perte d'une connection et sa reconnection.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """

        self.logger.debug("Instanciation du socketManagerWmo")

        # Instanciation du socketManagerWmo

        self.unSocketManagerWmo = \
                  socketManagerWmo.socketManagerWmo(self.logger,type='slave', \
                                                         port=self.source.port)

    def read(self):
        __doc__ =  gateway.gateway.read.__doc__ + \
        """### Ajout de receiverWmo ###

           Le lecteur est le socket tcp, géré par socketManagerWmo.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004


           Modification le 25 janvier 2005: getNextBulletins()
           retourne une liste de bulletins.

           Modification le 7 Fév 2005: Si une corruption est détectée dans les
           données, la connection se réinitialise. (LP)

           Auteur:      Louis-Philippe Thériault
        """
        if self.unSocketManagerWmo.isConnected():
            try:
                data = self.unSocketManagerWmo.getNextBulletins()
            except socketManager.socketManagerException, e:
                if e.args[0] == 'la connexion est brisee':
                    self.logger.error("Perte de connection, traîtement du reste du buffer")
                    data, nbBullEnv = self.unSocketManagerWmo.closeProperly()
                elif e.args[0] == 'corruption dans les données':
                    self.logger.error("Corruption détectée dans les données\nContenu du buffer:\n%s" % e.args[2])
                    data, nbBullEnv = self.unSocketManagerWmo.closeProperly()
                else:
                    raise
        else:
            raise gateway.gatewayException("Le lecteur ne peut être accédé")

        self.logger.veryveryverbose("%d nouveaux bulletins lus" % len(data))

        return data

    def write(self,data):
        __doc__ =  gateway.gateway.write.__doc__ + \
        """### Ajout de receiverWmo ###

           L'écrivain est un bulletinManagerWmo.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """

        self.logger.veryveryverbose("%d nouveaux bulletins seront écrits" % len(data))

        while True:
            if len(data) <= 0:
                break

            rawBulletin = data.pop(0)

            self.unBulletinManager.writeBulletinToDisk(rawBulletin)

    def reloadConfig(self):
        __doc__ = gateway.gateway.reloadConfig.__doc__
        self.logger.info('Demande de rechargement de configuration')

        try:

            newConfig = gateway.gateway.loadConfig(self.pathToConfigFile)

            ficCircuits = newConfig.ficCircuits

            # Reload du fichier de circuits
            # -----------------------------
            self.unBulletinManager.drp.reparse()

            self.config.ficCircuits = ficCircuits

            self.logger.info('Succès du rechargement de la config')

        except Exception, e:

            self.logger.error('Échec du rechargement de la config!')

            self.logger.debug("Erreur: %s", str(e.args))
