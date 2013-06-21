# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.
#
#   Auteur:      
#
#      2004/10 -- Louis-Philippe Thériault
#
# MG python3 compatible
#

"""abstract class for bulletin transfers """

import imp, time, sys
from MultiKeysStringSorter import MultiKeysStringSorter
from DiskReader import DiskReader
from Source import Source
import PXPaths
PXPaths.normalPaths()

__version__ = '2.0'

class gatewayException(Exception):
    """what is the point?  exception class for gateways"""
    pass

class gateway:
    """container for the common attributes of a gateway.
       
       Receivers and senders are derived from thie class.

       self.config module will contain the obvious.

       Terminology:

          - from a reader we can call a data reader
            (ex: disque, socket, etc...)
          - we can provide data to a write which can be written
            (ex: disque, socket, etc...)

       Instanciation:

       Gateway is instantiated with a config file.

            path            String
                            - path to config file.

            flow            - Source or Client (permits access to all options)

            logger          logging object

                            - Must be callable to write messages.   
                              this is normally the program's log file.

    """
    def __init__(self, path, flow, logger):
        self.pathToConfigFile = path
        self.logger = logger
        self.flow = flow 
        self.igniter = None
        self.reader = None

        # statistics.
        self.totBytes = 0
        self.initialTime = time.time()
        self.finalTime = None



    def resetReader(self):
        self.reader = DiskReader(PXPaths.TXQ + self.flow.name,
                                 self.flow.batch,            # Number of files we read each time
                                 self.flow.validation,       # name validation
                                 self.flow.patternMatching,  # pattern matching
                                 self.flow.mtime,            # we don't check modification time
                                 True,                       # priority tree
                                 self.logger,
                                 eval(self.flow.sorter),
                                 self.flow)

    def setIgniter(self, igniter):
        self.igniter = igniter

    def loadConfig(path):
        """loadConfig(path)

           Load the configuration file.
        """
        try:
            fic_cfg = open(path,'r')
            config = imp.load_source('config','/dev/null',fic_cfg)
            fic_cfg.close()

            return config
        except IOError:
            print("*** Error: configuration file missing !")
            sys.exit(-1)

    loadConfig = staticmethod(loadConfig)

    def establishConnection(self):
        """establishConnection()

           Establish a connection with a reader and writer (check
           that resources are available too.) is also 
           called if the connection is dropped.

        """
        raise gatewayException('Not Implemented abstract class method establishConnection')

    def read(self):
        """read() -> data

           data : Liste of objects

           This method returns a list of objects to be ingested by a writer.
           Raise an exception if there is an error.

        """
        raise gatewayException('Méthode non implantée (méthode abstraite read)')

    def write(self,data):
        """write(data)

           data : Liste d'objets

           write the data given (as returned by a read call.) while doing
           the appropriate processing.

        """
        raise gatewayException('Méthode non implantée (méthode abstraite write)')

    def run(self):
        """run()

           infinite loop to transfer data. An exception is raised
           if either the reader or writer is not available.
        """
        while True:

            try:
                data = self.read()
            except gatewayException as e:
                if e.args[0] == "Le lecteur ne peut être accédé":
                # Lecture impossible, il ne devrait plus y avoir
                # de données en attente
                    if len(data) > 0:
                        self.write(data)
                        data = []

                    self.establishConnection()
                    
                    """
                    # Intent of these lines were to reread information when a reconnexion occurs.
                    # Not useful because each time a change is done, a reload or restart (that
                    # do the reread job) must occurs. To be erased in 1 month.

                    # We need (am and wmo receivers) to reread the config file, the ROUTING_TABLE (and px clients), 
                    # and maybe the STATION_TABLE (am)
                    if isinstance(self.flow, Source):
                        if self.flow.type in ['am', 'wmo', 'amqp']:
                            self.flow.__init__(self.flow.name, self.flow.logger)
                            self.renewBulletinManager()
                    """
                else:
                    raise

            if len(data) == 0:
            # S'il n'y a pas de nouveau data
                time.sleep(0.1)
            else:
                self.write(data)

    def shutdown(self):
        """shutdown()

           close down gateway nicely.

        """
        self.logger.info("clean gateway shutdown")

    def checkLooping(self, unElementDeData):
        """checkLooping() -> bool

           detect if data given has already been received.

           Return True if the object is a repeat.
        """
        raise gatewayException("Method not implemented: gateway.gateway.checkLooping()")

    def reloadConfig(self):
        """reloadConfig()

           Reload settings from configuration files.

           Purpose:

                handle SIGHUP

        """
        self.logger.info('reload config file... not implemented!')

    def printSpeed(self):
        elapsedTime = time.time() - self.initialTime
        speed = self.totBytes/elapsedTime
        self.totBytes = 0
        self.initialTime = time.time()
        return "Speed = %i" % int(speed)

    def tallyBytes(self,bytecount):
        self.totBytes += bytecount

    
