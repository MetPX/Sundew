import sys, os, os.path, time, stat, string

# this filter parse  WMO 00 file format 
# according to the specification of the WMO 386 Vol I en .pdf
# in the chapiter where   ftp procedures are specified (page 240)
#
#  the rules are :
#      1)  each bulletin is reformatted into a message of the form
#          message = [8 char message length]  +  "00" (wmo file format is 00)
#                  + chr(curses.ascii.SOH)    + '\r\r\n'
#                  + [5 char message counter] + '\r\r\n'
#                  + bulletin  --------->  with '\r\r\n' (as line separator)
#                  + '\r\r\n' + chr(curses.ascii.ETX)
#      2)  the messages are grouped according to the following rules
#          a)  if there are 100 messages arrived ... collect and send a file
#          b)  any messages aged one minute or more... collect and send a file
#          c)  to keep everything simpler, we agreed with UKMET to mix alphanumeric and
#              binary messages and only use file extension .b  (for binary)

class Transformer(object):

      def __init__(self) :
          import curses.ascii

          self.data        = None
          self.pos         = 0
          self.logger      = None

          self.counter     = ""

          self.maxCompteur = 99999999
          self.compteur    =  0

          self.magic_begin = "" + chr(curses.ascii.SOH) + '\r\r\n'
          self.magic_end   = "" + '\r\r\n' + chr(curses.ascii.ETX)

      def getbulletin(self  ):
          import bulletinWmo

          # msg len + msg type is 10 char. that doesn't count in msglen
          # which is from SOH to ETX

          pos = self.pos

          msglen = int(self.data[pos:pos+8])
          if self.data[pos+8:pos+10] != "00" :
             self.logger.warning(" message type not 00 (%s)" % self.data[pos+8:pos+10])

          # get current message

          pos += 10
          eom = pos + msglen
          msg  = self.data[pos:eom]
          pos  += msglen
          self.pos = pos
          #print "---------- msg -------- "
          #print msg

          # ok checking that bulletin starts with magic_begin and magic_end

          if msg[0:3] != self.magic_begin[0:3] :
             self.logger.warning(" did not find SOH at pos %d" % msg[0:3])

          if msg[-4:-1] != self.magic_end[0:3] :
             self.logger.warning(" did not find ETX at end of msg %s" % msg[-4:-1])

          # keep/skip the bulletin counter  which is 3 or 5 characters in length
          for beg in range(4,9) :
              if not msg[beg] in "0123456789" : break
          self.counter = msg[4:beg+1]

          if msg[beg+1:beg+4] != '\r\r\n' :
             self.logger.warning(" did not find cr cr lf after counter")
          beg = beg + 4

          # get wmo bulletin out of message
          bul = msg[beg:-4]

          # exactly like WMO bulletins
          bulltin  = bulletinWmo.bulletinWmo(bul,self.logger,finalLineSeparator='\r\r\n')
          bulltin.doSpecificProcessing()
          fdata = bulltin.getBulletin(useFinalLineSeparator=False)

          return fdata

      def renamer(self, ipath, fdata ):
          import string

          # get directory 
          lst=ipath.split('/')
          dir='/'.join(lst[:-1])

          # get header token in a list
          lines = fdata.split('\n')
          hdrtok = lines[0].split()

          # build filename
          opath  = dir + '/' + '_'.join(hdrtok) + '_' + string.zfill(self.compteur,8)
          opath += ":cvt_ftpwmo_parser:-CCCC:-TT:3:Wmo"

          # update compteur

          self.compteur    = self.compteur + 1
          if self.compteur > self.maxCompteur: self.compteur = 0

          # return file
          return opath

      def perform(self, ipaths, logger ):
          import os,time

          opaths = []

          self.logger = logger

          # loop on the files

          for ipath in ipaths :

              # read in the file

              data=''
              try :
                    f = open(ipath, 'r')
                    data = f.read()
                    f.close()
              except :
                    (type, value, tb) = sys.exc_info()
                    logger.error("problem while reading %s" % ipath)
                    logger.error(" Type: %s, Value: %s" % (type ,value))
                    return opaths

              # if file a parsed bulletin... add ipath to output list
              # this situation may arise if the file was already parsed
              # and could not be delivered for some reasons...

              if len(data) > 13 and data[10:13] != self.magic_begin[0:3] :
                 opaths.append(ipath)
                 continue

              # start parsing bulletin from collection

              self.pos    = 0
              self.data   = data
              logger.info("parsing %s" % ipath)

              max = len(data)
              while( self.pos < max ) :

                   remain = max - self.pos
                   if remain < 21 : break

                   fdata = self.getbulletin()

                   # get a output filename
                   opath = self.renamer(ipath, fdata )

                   # write the file into its proper ftpGTS name
                   f = open( opath, 'w' )
                   f.write( fdata )
                   f.close( )
                   logger.info("file %s extracted" % opath)
                   opaths.append(opath)

              # get rid of parsed file
              os.unlink(ipath)
 
          return opaths

transformer=Transformer()
self.lx_script=transformer.perform

#from Logger import Logger
#logger = Logger("here.log", 'info', 'TX_test',1000000)
#logger = logger.getLogger()
#transformer=Transformer()
#
#flist = []
#flist.append("/tmp/mg/data/toto")
##flist.append... (give a list of files)
#print transformer.perform(flist,logger)
