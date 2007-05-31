# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.

"""
#############################################################################################
# Name: senderWmo.py
#
# Author: Pierre Michaud
#
# Date: Novembre 2004
#
# Contributors: Daniel Lemay
#
# Description:
#
#############################################################################################
"""
import sys, os.path, time, string
import gateway
import socketManagerWmo
import bulletinManagerWmo
import bulletinWmo

from MultiKeysStringSorter import MultiKeysStringSorter
from DiskReader import DiskReader
from CacheManager import CacheManager
import PXPaths

from TextSplitter import TextSplitter

PXPaths.normalPaths()

class senderWmo(gateway.gateway):

    def __init__(self,path,client,logger):
        gateway.gateway.__init__(self, path, client, logger)
        self.client = client
        self.establishConnection()

        self.reader = DiskReader(PXPaths.TXQ + self.client.name, 
                                 self.client.batch,            # Number of files we read each time
                                 self.client.validation,       # name validation
                                 self.client.patternMatching,  # pattern matching
                                 self.client.mtime,            # we don't check modification time
                                 True,                         # priority tree
                                 self.logger,
                                 eval(self.client.sorter),
                                 self.client)

        # Mechanism to eliminate multiple copies of a bulletin
        self.cacheManager = CacheManager(maxEntries=120000, timeout=8*3600)

        # WMO's maximum bulletin size is 500 000 bytes
        self.set_maxLength( self.client.maxLength )

    def set_maxLength(self,value):
        if value <= 0  : value = 500000
        self.maxLength = value

    def shutdown(self):
        gateway.gateway.shutdown(self)

        resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()

        self.write(resteDuBuffer)

        self.logger.info("Le senderWmo est mort.  Traitement en cours reussi.")

    def establishConnection(self):
        # Instanciation du socketManagerWmo
        self.logger.debug("Instanciation du socketManagerWmo")

        self.unSocketManagerWmo = \
                 socketManagerWmo.socketManagerWmo(
                         self.logger,type='master', \
                         port=self.client.port,\
                         remoteHost=self.client.host,
                         timeout=self.client.timeout,
                         flow=self.client)

    def read(self):
        if self.igniter.reloadMode == True:
            # We assign the defaults and reread the configuration file (in __init__)
            self.client.__init__(self.client.name, self.client.logger)
            self.set_maxLength( self.client.maxLength )
            self.resetReader()
            self.cacheManager.clear()
            self.logger.info("Cache has been cleared")
            self.logger.info("Sender WMO has been reloaded") 
            self.igniter.reloadMode = False
        self.reader.read()
        return self.reader.getFilesContent(self.client.batch)

    def write(self,data):
        #self.logger.info("%d nouveaux bulletins sont envoyes",len(data))
        self.logger.info("%d new bulletins will be sent", len(data))

        for index in range(len(data)):

            try:
                tosplit = self.need_split( data[index] )

                # need to be segmented...
                if tosplit :
                   succes, nbBytesSent = self.write_segmented_data( data[index], self.reader.sortedFiles[index] )
                   # all parts were cached... nothing to do
                   if succes and nbBytesSent == 0 :
                      self.unlink_file( self.reader.sortedFiles[index] )
                      continue

                # send the entire bulletin
                else :

                   # if in cache than it was already sent... nothing to do
                   # priority 0 are retransmission and no check for duplicate
                   path     = self.reader.sortedFiles[index]
                   priority = path.split('/')[5]

                   if self.client.nodups and priority != '0' and self.in_cache( data[index], True, path ) :
                      #PS... same extra unlink as in AM sender call above is true, should it be false?
                      #self.unlink_file( self.reader.sortedFiles[index] )
                      continue
                   succes, nbBytesSent = self.write_data( data[index] )

                #If the bulletin was sent successfully, erase the file.
                if succes:
                   basename = os.path.basename(self.reader.sortedFiles[index])
                   self.logger.info("(%i Bytes) Bulletin %s  delivered" % (nbBytesSent, basename))
                   self.unlink_file( self.reader.sortedFiles[index] )
                else:
                   self.logger.info("%s: Sending problem" % self.reader.sortedFiles[index])

            except Exception, e:
            # e==104 or e==110 or e==32 or e==107 => connection broken
                (type, value, tb) = sys.exc_info()
                self.logger.error("Type: %s, Value: %s" % (type, value))

        # Log infos about tx speed 
        if (self.totBytes > 1000000):
            self.logger.info(self.printSpeed() + " Bytes/sec")
            # Log infos about caching 
            (stats, cached, total) = self.cacheManager.getStats()
            if total:
                percentage = "%2.2f %% of the last %i requests were cached (implied %i files were deleted)" % (cached/total * 100,  total, cached)
            else:
                percentage = "No entries in the cache"
            self.logger.info("Caching stats: %s => %s" % (str(stats), percentage))

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

    # MG unlink file (isolated to clear code when segmentation was added)
    def unlink_file(self,path):
        try:
               os.unlink(path)
               self.logger.debug("%s has been erased", os.path.basename(path))
        except OSError, e:
               (type, value, tb) = sys.exc_info()
               self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (path, type, value))

    # MG define if the data needs to be segmented
    def need_split(self,data) :

        # check if the bulletin needs to be segmented
        # WMO bulletin has the following form 

        # preamble : 8 characters representing the bulletin's size right justified and zero filled
        #            2 characters representing the data type  AN (alphanumeric)  BI (binary)
        #            followed by chr(curses.ascii.SOH) + '\r\r\n' +  a 5 digit counter + '\r\r\n'
        #            so a preamble len of 22  bytes

        totWmo   = 22

        # bulletin : all '\n' are replaced by '\r\r\n'
        # effective count of data size when all \n  are replace by endOfLineSep
        totWmo  += len(data)
        totWmo  += (len("\r\r\n")-1) * string.count(data,"\n")

        # endOfMessage : 4 characters  '\r\r\n' + chr(curses.ascii.ETX)
        totWmo  += 4

        tosplit = False
        if  totWmo  > self.maxLength :
            tosplit = True

        return tosplit

    # MG write data (isolated to clear code when segmentation was added)
    def write_data(self,data):
        unBulletinWmo = bulletinWmo.bulletinWmo(data,self.logger,finalLineSeparator='\r\r\n')

        # C'est dans l'appel a sendBulletin que l'on verifie si la connexion doit etre reinitialisee ou non
        succes, nbBytesSent = self.unSocketManagerWmo.sendBulletin(unBulletinWmo)

        #si le bulletin a ete envoye correctement, le fichier est efface
        if succes:
           self.totBytes += nbBytesSent

        return (succes, nbBytesSent)

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

        # compute block size limit = maxLength - preamble(22) - endofMessage(4) - bulletinheader with "\r\r\n"

        limit  = self.maxLength -26 - (lheader + 2)

        # replace all \n by Amis endOfLineSep

        dataWmo = data[lheader:].strip().replace("\n", "\r\r\n" )

        # perform Segmentation

        blocks  = TextSplitter(dataWmo, limit, "\n", 0, "=\r\r\n"  ).breakMarker()
        self.logger.info("Bulletin %s segmented in %d parts" % (path,len(blocks)))

        i       =  0
        totSent =  0

        priority = path.split('/')[5]

        alpha=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

        for part in blocks :
            rawSegment = header + "\n" + part
            rawSegment = rawSegment.replace("\r\r\n", "\n" )
            i = i + 1

            if self.client.nodups and priority != '0' and self.in_cache( rawSegment, False, None ) :
               continue

            succes, nbBytesSent = self.write_data(rawSegment)
            if succes :
               totSent += nbBytesSent
               self.logger.info("(%i Bytes) Bulletin Segment number %d sent" % (nbBytesSent,i))
            else :
               return (False, totSent)

        return (True, totSent)
