# -*- coding: iso-8859-1 -*-
#
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.
#
# Author
#    2004/10 -- Louis-Philippe Thériault
#    2005/12 -- Pierre Michaud
#
# MG python3 compatible
#

"""Generic socket manager"""

import socket, time, string, sys, traceback

__version__ = '2.0'

class socketManagerException(Exception):
    """generic socket manager exception class"""
    pass

class socketManager:
    """
       Abstract class with all the functionalist needed for a socket manager.
       methods raising an exception must be implemented in derived classes.

       Arguments to initialize a socketManager:

            type            'master','slave' (default='slave')

                            - if master, then connect to remote host
                            - if slave, then bind and wait for connection.

            port    int (default=9999)

                            - Port to bind (slave) 

            remoteHost      (str hostname,int port)

                            - tuple (hostname,port) for master connection.
                              after timeout seconds, an exception is raised.

                            - required for type=master
                            - must not be specified for type=slave.

            timeout         int (default=None)

                            - connection timeout

            log             Objet Log (default=None)

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

        self.__establishConnection()

    def __establishConnection(self):
        """
           input Parameters:
           -none

           output Parameters:
           -none

           Description:
           establish connection according to object attributes.
           return established connection as self.socket.

        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
                    raise socketManagerException('timeout exceeded')
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
            self.socket.listen(1)


            while True:
                # Commented by DL (2005-03-30) at the request of AMB
                """
                if self.timeout != None and (time.time() - then) > self.timeout:
                    self.socket.close()
                    raise socketManagerException('timeout exceeded')
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

        #trying to use of non-blocking will break senders and receivers in seconds.
        self.socket.setblocking(True)

        self.logger.info("Connexion established with %s",str(self.remoteHost))
        self.connected = True

    def closeProperly(self):
        """closeProperply() -> ([bulletinsReçus],nbBulletinsEnvoyés)

           [bulletinsReçus]:    liste of str
                                - returns list of bulletins in buffer at close.

           Close socket and complete processing of pending bulletins.

           Purpose:

                Process remaining data, the cleanly shutdown socket.

        """
        self.logger.info("Fermeture du socket et copie du reste du buffer")

        # Close the connection.
        try:
            self.socket.shutdown(2)
            self.logger.debug("Shutdown socket: [OK]")
        except Exception as e:
            self.logger.debug("Shutdown socket: [ERROR]\n %s",str(e))

        # Copy rest of input buffer 
        # bulletin must be put in non-blocking if we want to close
        # the connection cleanly.
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

        # process rest of buffer, slicing into individual bulletins.
        bulletinsRecus = self.getNextBulletins()


        self.logger.info("socket closed successfully")
        self.logger.debug("bulletins in the buffer: %d",len(bulletinsRecus))

        return (bulletinsRecus, 0)

    def getNextBulletins(self):
        """getNextBulletins() -> [bulletin]

           bulletin     : [String]

           Return the rest of the bulletins in the buffer, on empty list.

        """
        if self.isConnected():
        # if not connected, do not check, because we might want bulletins in the 
        # buffer without being connected.
            self.__syncInBuffer()

        nouveauxBulletins = []

        while True:

            status = self.checkNextMsgStatus()

            self.logger.debug("status of next bulletin in the buffer: %s", status )

            if status == 'INCOMPLETE':
                break

            if status ==  'OK':
                (bulletin,longBuffer) = self.unwrapBulletin()

                self.inBuffer = self.inBuffer[longBuffer:]

                nouveauxBulletins.append(bulletin)
            elif status == 'CORRUPT':
                raise socketManagerException('data corrupt','CORRUPT',self.inBuffer)
            else:
                raise socketManagerException('unknown buffer status',status,self.inBuffer)

        return nouveauxBulletins

    def sendBulletin(self):
        # FIXME: wtf like this means something?
        raise socketManagerException('socketManager.sendBulletin() pure virtual method')

    def __syncInBuffer(self,onlySynch=False):
        """__syncInBuffer()

           onlySynch:   Booleen
                        - if true, do not check if connection is working.
                          just sync buffer.

           Copy data from buffer to socket, if there is some.

           raise an exception if connection lost.

           Purpose:

                Copy the new received data to socketManager attribute.

        """
        while True:
            try:
                temp = self.socket.recv(32768)

                if temp == '':
                    self.connected = False

                    if not onlySynch:
                        self.logger.error("connection lost")
                        raise socketManagerException('connection lost')

                self.logger.veryverbose("Data received: %s" % temp)

                self.inBuffer = self.inBuffer + temp
                break

            except socket.error as inst:
                (type, value, tb) = sys.exc_info()
                # Normally, this error is generated when a SIGHUP signal is sent and the system call (socket.recv(32768))
                # is interrupted
                if value[0] == 4: 
                    self.logger.warning("Type: %s, Value: %s, [socket.recv(32768)]" % (type, value))
                    break

                if not onlySynch:
                # La connexion est brisée
                    self.connected = False

                    self.logger.error("connection broken")
                    raise socketManagerException('connection broken')

    def __transmitOutBuffer(self):
        pass

    def wrapBulletin(self,bulletin):
        """wrapbulletin(bulletin) -> wrappedBulletin

           bulletin             : String
           wrappedBulletin      : String

           Return the bulletin with header & data in protocol format
           as a string.  The bulletin must be a Bulletin object.
           Wrap bulletin must only be called if we are sure to send it,
           because of a counter that will have to follow.
         
        """
        raise socketManagerException("not implemented (abstract method wrapBulletin)")

    def unwrapBulletin(self):
        """unwrapBulletin() -> (bulletin,longBuffer)

           bulletin     : String
           longBuffer   : int

           Returns the next bulletin in the buffer, after checking
           integrity, without modifying the buffer.
           longBuffer will be as long as we need to remove from
           the buffer to place us at the beginning of the next bulletin.

           Return empty string if there is not enough data to complete
           the next bulletin.

        """
        raise socketManagerException("method not implemented (abstract method unwrapBulletin)")

    def isConnected(self):
        """isConnected() -> bool

           Return True if the connection is established.

        """
        return self.connected

    def checkNextMsgStatus(self):
        """checkNextMsgStatus() -> status

           status       : String  choice of ('OK','INCOMPLETE','CORRUPT')

           Status of next bulletin in the buffer.

        """
        raise socketManagerException("method not implemented (abstract method checkNextMsgStatus)")

    def setConnected(self,valeur):
        """
        Description: set the connected attribute value
        """
        self.connected = valeur
