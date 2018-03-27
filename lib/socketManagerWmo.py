# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.
#
# Author:
#    2004/10  Louis-Philippe Thériault
#    2004/12  Pierre Michaud
#

"""WMO protocol socket manager"""

__version__ = '2.0'

import struct, socket, curses, curses.ascii, string, crcmod
import socketManager
import time

class socketManagerWmo(socketManager.socketManager):
    __doc__ = socketManager.socketManager.__doc__ + \
    """
       * Attributes

            patternWmoRec           str

                                    - pattern for parsing header
                                      struct

            sizeWmoRec              int

                                    - header length (in octets)
                                      calculated from struct

    """

    def __init__(self,logger,type='slave',port=9999,remoteHost=None,timeout=None, flow=None):
        socketManager.socketManager.__init__(self,logger,type,port,remoteHost,timeout, flow)

        # Size of wmoHeader taken from document (WMO 386):
        # "Use of TCP/IP on the GTS", pages 28-29, et l'exemple en C
        # page 49-54
        self.patternWmoRec = '8s2s'
        self.sizeWmoRec = struct.calcsize(self.patternWmoRec)

        self.maxCompteur = 99999
        self.compteur = 0

        self.debugFile = False
        
        # CRC16 with 16 bits polynomial X16 + X15 + X2 + 1
        poly = 0x18005
        self.crc16_function = crcmod.mkCrcFun(poly)

    def unwrapBulletin(self):
        __doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
        """
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
        # message corrupt
            raise socketManagerException("Données corrompues",self.inBuffer)

    def wrapBulletin(self,bulletin):
        __doc__ = socketManager.socketManager.wrapBulletin.__doc__ + \
        """
           input parameters:
           -bulletin:   a bulletinWmo object

           output parameters:
           -returns a bulletin as a ready to send string.

           Purpose:
           Add WMO header to input bulletin.

        """
        bulletinStr = chr(curses.ascii.SOH) + '\r\r\n' + self.getNextCounter(5,bulletin) + '\r\r\n' + bulletin.getBulletin(useFinalLineSeparator=True) + '\r\r\n' + chr(curses.ascii.ETX)

        #repr(bulletinStr)

        return string.zfill(len(bulletinStr),8) + bulletin.getDataType() + bulletinStr

    def getNextCounter(self,x,bulletin):
        """getNextCounter() 

           compteur:    String
                        - counter part of bulletin

           Purpose:
                Generate ´counter´ (sequence number?) for a bulletinWmo. Must be certain that
                bulletin is in send queue. 
        """
        
        # Use crc16 instead of sequence number
        self.compteur = self.crc16_function(bulletin.getBulletin())

        return string.zfill(self.compteur,len(str(self.maxCompteur)))

    def checkNextMsgStatus(self):
        __doc__ = socketManager.socketManager.checkNextMsgStatus.__doc__ + \
        """
        """
        if len(self.inBuffer) >= self.sizeWmoRec:
            (msg_length,msg_type) = \
                     struct.unpack(self.patternWmoRec,self.inBuffer[0:self.sizeWmoRec])
        else:
            return 'INCOMPLETE'

        try:
            msg_length = int(msg_length)
            self.logger.debug("message length: %d",msg_length)
        except ValueError:
            self.logger.debug("Corruption: length decode failure ")
            return 'CORRUPT'

        if not msg_type in ['BI','AN','FX']:
            self.logger.debug("Corruption: invalid bulletin type")
            return 'CORRUPT'

        if len(self.inBuffer) >= self.sizeWmoRec + msg_length:
            if ord(self.inBuffer[self.sizeWmoRec]) != curses.ascii.SOH or ord(self.inBuffer[self.sizeWmoRec+msg_length-1]) != curses.ascii.ETX:
                self.logger.debug("Corruption: unexpected control characters")
                return 'CORRUPT'

            return 'OK'
        else:
            return 'INCOMPLETE'

    def sendBulletin(self,bulletin):
        #__doc__ = socketManager.socketManager.sendBulletin.__doc__ + \
        """
        input parameters:
        -bulletin:
                -a bulletin object

        Return value:
        -on success: 0
        -on failure: 1

        Description:
        Send the WMO bulletin to the socket.
        Each send checks the connection state.
        """
        try:
            #prepare the bulletin for send.
            data = self.wrapBulletin(bulletin)

            # debuging...!? keep the transmitted file
            if self.debugFile :
               self.writetofile("/tmp/WMO",data)

            #tentative d'envoi et controle de la connexion
            #try to send, and control connection.
            try:
                bytesSent = self.socket.send(data)

                #check if it went OK.
                if bytesSent != len(data):
                    self.connected=False
                    return (0, bytesSent)
                else:
                    return (1, bytesSent)

            except socket.error, e:
                #possible errors: 104, 107, 110 or 32
                self.logger.error("senderWmo.write(): connection broken: %s",str(e.args))
                self.connected = False
                self.logger.info("senderWmo.write(): attempt to reconnect")
                self.socket.close()
                self._socketManager__establishConnection()

        except Exception, e:
            self.logger.error("socketManagerWmo.sendBulletin(): send error: %s",str(e.args))
            raise

    # debug development module write data to file
    def writetofile(self,filename,data):
        import os,random

        r = random.random()
        str_r = '%f' % r
        unFichier = os.open( filename + str_r, os.O_CREAT | os.O_WRONLY )
        os.write( unFichier , data )
        os.close( unFichier )
