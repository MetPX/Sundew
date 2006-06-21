# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: senderAMIS.py
#
# Author: Daniel Lemay
#
# Date: 2005-03-16
#
# Contribution: Michel Grenier segmentation of bulletins
#
#############################################################################################

"""
import os, sys, time, socket, curses.ascii, string
from DiskReader import DiskReader
from MultiKeysStringSorter import MultiKeysStringSorter
from CacheManager import CacheManager
from TextSplitter import TextSplitter

import PXPaths

PXPaths.normalPaths()

class senderAMIS: 
   
   def __init__(self, client, logger):
      self.client = client                            # Client object (give access to all configuration options)
      self.remoteHost = client.host                   # Remote host (name or ip) 
      self.port = int(client.port)                    # Port (int) to which the receiver is bind
      self.address = (self.remoteHost, self.port)     # Socket address
      self.timeout = client.timeout                   # No timeout for now
      self.logger = logger                            # Logger object
      self.socketAMIS = None                          # The socket
      self.igniter = None
      self.reader = DiskReader(PXPaths.TXQ  + self.client.name, self.client.batch,
                               self.client.validation, self.client.patternMatching,
                               self.client.mtime, True, self.logger, eval(self.client.sorter), self.client)

      self.preamble     = chr(curses.ascii.SOH) + "\r\n"
      self.endOfLineSep = "\r\r\n"
      self.endOfMessage = self.endOfLineSep + chr(curses.ascii.ETX) + "\r\n\n" + chr(curses.ascii.EOT)
      self.debugFile    = False

      self.cacheManager = CacheManager(maxEntries=120000, timeout=8*3600)

      # AMIS's maximum bulletin size is 14000

      self.set_maxLength(self.client.maxLength)

      # statistics.
      self.totBytes = 0
      self.initialTime = time.time()
      self.finalTime = None


      self._connect()
      #self.run()

   def set_maxLength(self,value)
      if value <= 0  : value = 14000
      self.maxLength = value

   def printSpeed(self):
      elapsedTime = time.time() - self.initialTime
      speed = self.totBytes/elapsedTime
      self.totBytes = 0
      self.initialTime = time.time()
      return "Speed = %i" % int(speed)


   def setIgniter(self, igniter):
      self.igniter = igniter 

   def resetReader(self):
      self.reader = DiskReader(PXPaths.TXQ  + self.client.name, self.client.batch,
                               self.client.validation, self.client.patternMatching,
                               self.client.mtime, True, self.logger, eval(self.client.sorter), self.client)

   def _connect(self):
      self.socketAMIS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socketAMIS.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
      self.socketAMIS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      #print self.socketAMIS.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
      #self.socketAMIS.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,4096)
      #print self.socketAMIS.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
      #self.socketAMIS.setblocking(True)

      while True:
         try:
            self.socketAMIS.connect(self.address)
            self.logger.info("AMIS Sender is now connected to: %s" % str(self.address))
            break
         except socket.gaierror, e:
            #print "Address related error connecting to server: %s" % e
            self.logger.error("Address related error connecting to server: %s" % e)
            sys.exit(1)
         except socket.error, e:
            (type, value, tb) = sys.exc_info()
            self.logger.error("Type: %s, Value: %s, Sleeping 5 seconds ..." % (type, value))
            #self.logger.error("Connection error: %s, sleeping ..." % e)
            time.sleep(5)

   def shutdown(self):
      pass

   def read(self):
      if self.igniter.reloadMode == True:
         # We assign the defaults and reread the configuration file (in __init__)
         self.client.__init__(self.client.name, self.client.logger)
         self.set_maxLength(self.client.maxLength)
         self.resetReader()
         self.cacheManager.clear()
         self.logger.info("Cache has been cleared")
         self.logger.info("Sender AMIS has been reloaded")
         self.igniter.reloadMode = False
      self.reader.read()
      return self.reader.getFilesContent(self.client.batch)

   def write(self, data):
      if len(data) >= 1:
         self.logger.info("%d new bulletins will be sent", len(data) )

         for index in range(len(data)):

             tosplit = self.need_split( data[index] )

             if tosplit :
                succes, nbBytesSent = self.write_segmented_data( data[index], self.reader.sortedFiles[index] )
                # all parts were cached... nothing to do
                if succes and nbBytesSent == 0 :
                   self.unlink_file( self.reader.sortedFiles[index] )
                   continue
             else:
                # if in cache than it was already sent... nothing to do
                if self.client.nodups and self.in_cache( data[index], True, self.reader.sortedFiles[index] ) :
                   #PS... same bug as in Senders AM & WMO.
                   #self.unlink_file( self.reader.sortedFiles[index] )
                   continue
                dataAmis = self.encapsulate(data[index])
                succes, nbBytesSent = self.write_data( dataAmis )
             #si le bulletin a ete envoye correctement, le fichier est efface
             if succes:
                basename = os.path.basename(self.reader.sortedFiles[index])
                self.logger.info("(%i Bytes) Bulletin %s  delivered" % (nbBytesSent, basename))
                self.unlink_file( self.reader.sortedFiles[index] )
             else:
                self.logger.info("%s: Sending problem" % self.reader.sortedFiles[index])
      else:
         time.sleep(1)

      if (self.totBytes > 108000):
         self.logger.info(self.printSpeed() + " Bytes/sec")
         # Log infos about caching
         (stats, cached, total) = self.cacheManager.getStats()
         if total:
            percentage = "%2.2f %% of the last %i requests were cached (implied %i files were deleted)" % (cached/total * 100,  total, cached)
         else:
            percentage = "No entries in the cache"
         self.logger.info("Caching stats: %s => %s" % (str(stats), percentage))

   def encapsulate(self, data ):

       dataAmis = data.strip().replace("\n", self.endOfLineSep)
      
       return self.preamble + dataAmis + self.endOfMessage

   def run(self):
      while True:
         data = self.read()
         try:
            self.write(data)
         except socket.error, e:
            (type, value, tb) = sys.exc_info()
            self.logger.error("Sender error! Type: %s, Value: %s" % (type, value))
            
            # We close the socket
            try:
                self.socketAMIS.close()
            except:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Problem in closing socket! Type: %s, Value: %s" % (type, value))

            # We try to reconnect. 
            self._connect()

         #time.sleep(0.2)

   # check if data in cache... if not it is added automatically
   def in_cache(self,data,unlink_it,path):
       already_in = False

        # If data is already in cache, we don't send it
       if self.cacheManager.find(data, 'md5') is not None:
           already_in = True
           if unlink_it :
              try:
                   os.unlink(path)
                   self.logger.info("suppressed duplicate send %s", os.path.basename(path))
              except OSError, e:
                   (type, value, tb) = sys.exc_info()
                   self.logger.info("in_cache unable to unlink %s ! Type: %s, Value: %s"
                                   % (path, type, value))

       return already_in

   # MG compule encapsulated size of data
   def encapsulated_size(self,data) :

        # AMIS bulletin has the following form :
        # preamble     = chr(curses.ascii.SOH) + "\r\n"
        # data with all \n replace by endOfLineSep
        # endOfMessage = endOfLineSep + chr(curses.ascii.ETX) + "\r\n\n" + chr(curses.ascii.EOT)

        totAmis  = len(self.preamble)
        totAmis += len(data)

        # effective count of data size when all \n  are replace by endOfLineSep
        totAmis += (len(self.endOfLineSep)-1) * string.count(data,"\n")

        totAmis += len(self.endOfMessage)

        return totAmis

   # MG a test to check if the data need splitting
   def need_split(self,data) :

       tosplit = False
       totAmis = self.encapsulated_size(data)
       if totAmis > self.maxLength : tosplit = True

       return tosplit

   # MG write data (isolated to clear code when segmentation was added)
   def write_data(self,data):

       succes  = True
       nbBytes = len(data)

       if self.debugFile:
          self.writetofile("/tmp/AMIS",data)
       else :
          bullAMIS      = data
          nbBytesToSend = len(bullAMIS)
          nbBytes       = nbBytesToSend

          while nbBytesToSend > 0: 
                nbBytesSent = self.socketAMIS.send(bullAMIS)
                bullAMIS = bullAMIS[nbBytesSent:]
                nbBytesToSend = len(bullAMIS)
                self.totBytes += nbBytesSent

       return(succes, nbBytes )

   # MG unlink file (isolated to clear code when segmentation was added)
   def unlink_file(self,path):
       try:
              os.unlink(path)
              self.logger.debug("%s has been erased", os.path.basename(path))
       except OSError, e:
              (type, value, tb) = sys.exc_info()
              self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (path, type, value))

   # MG  segmenting and writing data if possible
   def write_segmented_data(self,data,path):

       # at this point, I expect the bulletin to be ok
       # first line assumed header... terminated by \n

       pos     = string.find(data,"\n")
       header  = data[:pos]
       lheader = len(header) + 1

       # SHOULD SEGMENT BUT : At the moment BUFR are not segmented but discarded
       if data[lheader:lheader+4] == "BUFR" :
          self.logger.error("Unable to segment and send %s ! Reason : type %s, Size: %s" % (path, "BUFR", len(data) ))
          self.unlink_file(path)
          return ( False, 0 )

       # SHOULD SEGMENT BUT : At the moment GRIB are not segmented but discarded
       if data[lheader:lheader+4] == "GRIB" :
          self.logger.error("Unable to segment and send %s ! Reason : type %s, Size: %s" % (path, "GRIB", len(data) ))
          self.unlink_file(path)
          return ( False, 0 )

       # SHOULD SEGMENT BUT : the bulletin already have a BBB group -> not segmented but discarded
       # FIXME should validate that the 4th token is realy a BBB (AAa-z CCa-z RRa-z Pa-za-z AMD COR RTM)
       tokn = header.split()
       if len(tokn) == 4 :
          self.logger.error("Unable to send %s Segmented ! Reason : BBB = %s, Size: %s" % (path, tokn[3], len(data) ))
          self.unlink_file(path)
          return ( False, 0 )

       # compute block size limit

       limit  = self.maxLength
       limit -= len(self.preamble)
       limit -= lheader + 4 + len(self.endOfLineSep)
       limit -= len(self.endOfMessage)

       # replace all \n by Amis endOfLineSep

       dataAmis = data[lheader:].strip().replace("\n", self.endOfLineSep)

       # perform Segmentation

       blocks  = TextSplitter(dataAmis, limit, "\n", 0, "=\r\r\n"  ).breakMarker()
       self.logger.info("Bulletin %s segmented in %d parts" % (path,len(blocks)))
                    
       i       =  0
       totSent =  0

       alpha=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

       for part in blocks :
           rawSegment  = self.preamble
           rawSegment += header + " P" + alpha[i/24] + alpha[i%24] + self.endOfLineSep
           rawSegment += part
           rawSegment += self.endOfMessage
           i = i + 1

           if self.client.nodups and self.in_cache( rawSegment, False, None ) :
              continue

           succes, nbBytesSent = self.write_data(rawSegment)
           if succes :
              self.totBytes += nbBytesSent
              self.logger.info("(%i Bytes) Bulletin Segment number %d sent" % (nbBytesSent,i))
           else :
              return (False, totSent)

       return (True, totSent)

   # debug development module write data to file
   def writetofile(self,filename,data):
       import random

       r = random.random()
       str_r = '%f' % r
       unFichier = os.open( filename + str_r, os.O_CREAT | os.O_WRONLY )
       os.write( unFichier , data )
       os.close( unFichier )

if __name__ == "__main__":
   from Logger import Logger
   from Client import Client

   logger = Logger('/apps/px/log/amisTEST_DL.log', 'DEBUG', 'amisTEST_DL')
   logger = logger.getLogger()

   client = Client('amisTEST_DL', logger)
   #receiver = "cisco-test.test.cmc.ec.gc.ca"
   #port = 4001
   #sender = senderAMIS("cisco-test.test.cmc.ec.gc.ca", 4001)
   sender = senderAMIS(client, logger)
   sender.run()
