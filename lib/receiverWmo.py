# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.
#
# Author:
#     2004/10 Louis-Philippe Thériault
#

"""ReceiverWmo: socketWmo -> disk, including bulletin processing"""

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
    Implement receiver for a WMO socket. Consists of a
    socketManagerAm and a bulletinManagerAm.

    """

    def __init__(self,path,source,logger):
        gateway.gateway.__init__(self,path,source,logger)

        self.establishConnection()

        self.renewBulletinManager()

    def renewBulletinManager(self):
        self.logger.debug("renewBulletinManager() has been called (type = wmo)")
        self.unBulletinManager = bulletinManagerWmo.bulletinManagerWmo(
                                    PXPaths.RXQ + self.flow.name,
                                    self.logger,
                                    pathFichierCircuit = self.flow.routingTable,
                                    extension = self.flow.extension,
                                    mapEnteteDelai = self.flow.mapEnteteDelai,
                                    source = self.flow)

    def shutdown(self):
        __doc__ = gateway.gateway.shutdown.__doc__ + \
        """
           Close socket and complete processing of buffer.

           Purpose:

                Clean shutdown of connection.

        """
        gateway.gateway.shutdown(self)

        if self.unSocketManagerWmo.isConnected():
            resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()

            self.write(resteDuBuffer)

        self.logger.info("completed processing of remaining data")

    def establishConnection(self):
        __doc__ = gateway.gateway.establishConnection.__doc__ + \
        """
           Purpose:
                encapsulating network connection makes it easier to 
                manager the loss of a connection, and reestablishment.        

        """

        self.logger.debug("Instantiation of socketManagerWmo")

        # Instanciation du socketManagerWmo

        self.unSocketManagerWmo = \
                  socketManagerWmo.socketManagerWmo(self.logger, type='slave', port=self.flow.port, remoteHost=None, timeout=None, flow=self.flow)

    def read(self):
        __doc__ =  gateway.gateway.read.__doc__ + \
        """
           The reader is a tcp socket, managed by a socketManagerWmo.

           if corruption in the data is detected, the connection is re-initialized.

        """
        if self.unSocketManagerWmo.isConnected():
            try:
                data = self.unSocketManagerWmo.getNextBulletins()
            except socketManager.socketManagerException, e:
                if e.args[0] == 'la connexion est brisee':
                    self.logger.error("lost connection, processing rest of buffer")
                    data, nbBullEnv = self.unSocketManagerWmo.closeProperly()
                elif e.args[0] == 'corruption dans les données':
                    self.logger.error("corrupt data\nbuffer contents:\n%s" % e.args[2])
                    data, nbBullEnv = self.unSocketManagerWmo.closeProperly()
                else:
                    raise
        else:
            raise gateway.gatewayException("cannot read socket")

        self.logger.veryveryverbose("%d new bulletins read" % len(data))

        return data

    def write(self,data):
        __doc__ =  gateway.gateway.write.__doc__ + \
        """
           Writer is a bulletinManagerWmo.

        """

        self.logger.veryveryverbose("%d new bulletins to write" % len(data))

        while True:
            if len(data) <= 0:
                break

            rawBulletin = data.pop(0)

            self.unBulletinManager.writeBulletinToDisk(rawBulletin)

    def reloadConfig(self):
        __doc__ = gateway.gateway.reloadConfig.__doc__
        self.logger.info('configuration reload start')

        try:

            newConfig = gateway.gateway.loadConfig(self.pathToConfigFile)

            ficCircuits = newConfig.ficCircuits

            # Reload routing config
            self.unBulletinManager.drp.reparse()

            self.config.ficCircuits = ficCircuits

            self.logger.info('configuration reload successful')

        except Exception, e:

            self.logger.error('configuraton reload failed')

            self.logger.debug("Error: %s", str(e.args))
