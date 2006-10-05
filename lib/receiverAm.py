# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.
#
# Author:
#    2004/10 - Louis-Philippe Thériault
#

"""ReceiverAm: socketAm -> disk, including bulletin processing"""

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
    Implementation of receiver for AM feed. It is made of
    an socketManagerAM and a bulletinManagerAM.

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
        """
           close socket and complete processing of buffer.

           Purpose:

                implement clean shutdown.

        """
        gateway.gateway.shutdown(self)

        if self.unSocketManagerAm.isConnected():
            resteDuBuffer, nbBullEnv = self.unSocketManagerAm.closeProperly()

            self.write(resteDuBuffer)

        self.logger.info("Completed processing of remaining data")

    def establishConnection(self):
        __doc__ = gateway.gateway.establishConnection.__doc__ + \
        """
           establish an AM socket connection.   
        """

        self.logger.debug("Instantiation of socketManagerAm")

        self.unSocketManagerAm = \
                socketManagerAm.socketManagerAm(self.logger, type='slave', port=self.flow.port, remoteHost=None, timeout=None, flow=self.flow)

    def read(self):
        __doc__ =  gateway.gateway.read.__doc__ + \
        """
           The reader is the tcp socket, managed by socketManagerAm.

        """
        if self.unSocketManagerAm.isConnected():
            try:
                data = self.unSocketManagerAm.getNextBulletins()
            except socketManager.socketManagerException, e:
                if e.args[0] == "la connexion est brisee":
                    self.logger.error("lost connection, processing rest of buffer")
                    data, nbBullEnv = self.unSocketManagerAm.closeProperly()
                else:
                    raise
        else:
            raise gateway.gatewayException("socket read failure")

        self.logger.veryveryverbose("%d new bulletins read" % len(data))

        return data

    def write(self,data):
        __doc__ =  gateway.gateway.write.__doc__ + \
        """
           writer is a bulletinManagerAM

        """

        self.logger.veryveryverbose("%d new bulletins to write" % len(data))

        while True:
            if len(data) <= 0:
                break

            rawBulletin = data.pop(0)

            self.unBulletinManager.writeBulletinToDisk(rawBulletin,includeError=True)

    def reloadConfig(self):
        __doc__ = gateway.gateway.reloadConfig.__doc__
        self.logger.info('configuration reload started')

        try:

            newConfig = gateway.gateway.loadConfig(self.pathToConfigFile)

            ficCircuits = newConfig.ficCircuits
            ficCollection = newConfig.ficCollection

            # reload routing config.
            self.unBulletinManager.drp.reparse()

            self.config.ficCircuits = ficCircuits

            # Reload station config.
            self.unBulletinManager.reloadMapEntetes(ficCollection)

            self.config.ficCollection = ficCollection

            self.logger.info('configuration reload successful')

        except Exception, e:

            self.logger.error('configuration reload failed')

            self.logger.debug("Error: %s", str(e.args))
