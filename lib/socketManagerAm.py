# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.
#
# Author:
#
#    2004/10 -- Louis-Philippe Thériault
#    2005/01 -- Pierre

"""Spécialisation pour gestion de sockets "AM" """

__version__ = '2.0'

import struct, socket, curses, curses.ascii, string, time
import socketManager

class socketManagerAm(socketManager.socketManager):
    __doc__ = socketManager.socketManager.__doc__ + \
    """
    implementation of AM protocol socket manager

    * Attributes

    patternAmRec            str
                     - Pattern pour le parsing header struct.
    sizeAmRec               int
                     - header length (in octets)
                           calculated by struct 

    """

    #def __init__(self,logger,type='slave',localPort=9999,remoteHost=None,timeout=None):
            #socketManager.socketManager.__init__(self,logger,type,localPort,remoteHost,timeout)
    def __init__(self,logger,type='slave',port=9999,remoteHost=None,timeout=None, flow=None):
        socketManager.socketManager.__init__(self,logger,type,port,remoteHost,timeout, flow)

        # The size of amRec is take from the (not included) file ytram.h, originally from
        # amtcp2file (also not included in application.) to manage the fields we use
        # python struct.
        #self.patternAmRec = '80sLL4sii4s4s20s'
        self.patternAmRec = '80sLL4siiii20s'
        self.sizeAmRec = struct.calcsize(self.patternAmRec)

    def unwrapBulletin(self):
        __doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
        """
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
        """
           wrapBulletin

           input Parameters:
               -bulletin:   a bulletinAm object

           return value:
           -a bulletin as a ready to send string.

           Purpose:
           Add appropriate AM header to input bulletin.

        """
        #initialisation des header fields
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

        #put header and content together.
        wrappedBulletin = bulletinHeader + bulletin.getBulletin()

        return wrappedBulletin

    def checkNextMsgStatus(self):
        __doc__ = socketManager.socketManager.checkNextMsgStatus.__doc__ + \
        """
           Does not detect data corruption, AM protocol weakness?

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
        input parameter:
           -bulletin:

        return value:
        -on success: 0
        -on failure: 1

        FIXME: documentation wrong about return value, also sends # bytes sent.

        Purpose:
        Send a bulletin to a socket.  Verify connection status on each send.
        
        """
        try:
            #prepare bulletin for send
            data = self.wrapBulletin(bulletin)

            #print repr(data)
            #print('=====================================================================')

            # try to send , verify connection via try/except.
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
                self.logger.error("senderAm.write(): connection broken: %s",str(e.args))
                self.connected = False
                self.logger.info("senderAm.write(): attempt to reconnect")
                self.socket.close()
                self._socketManager__establishConnection()

        except Exception, e:
            self.logger.error("socketManagerAm.sendBulletin(): send error: %s",str(e.args))
            raise

    def writetofile(self,filename,data):
           import sys, os
           import random 
           r = random.random()
           str_r = '%f' % r
           unFichier = os.open( filename + str_r, os.O_CREAT | os.O_WRONLY )
           os.write( unFichier , data )
           os.close( unFichier )
