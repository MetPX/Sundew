
import sys, os, os.path, time, stat, string

# this filter collects  WMO 00 file format 
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

          self.maxCompteur = 99999999
          self.compteur    =  0
          self.ext         = 'b'

      def compteur_next(self,ipath):
          import os,string

          # fxq directory 

          lst=ipath.split('/')
          dir='/'.join(lst[:-1])

          # read in directory content
          files = os.listdir(dir)
          files.sort()

          # get sequence from file

          fseq = None
          try :
                     for f in files :
                         lst = f.split('/')
                         seq = lst[-1]
                         if len(seq) == 12 and seq[0:4] == '.seq' :
                            fseq = seq
                            os.unlink(dir + '/' + seq)

                     if fseq != None :
                        self.compteur = int(fseq[4:])

          except :
                    pass

          # ajust counter
          self.compteur    = self.compteur + 1
          if self.compteur > self.maxCompteur: self.compteur = 0

          fseq = ".seq" + string.zfill(self.compteur,8)
          f = open( dir + '/' + fseq, "w")
          f.close()


      def date_file_sort(self,ipaths):
          import os,time

          now   = time.mktime(time.localtime())

          stups = []
          for ipath in ipaths :
              stats = os.stat(ipath)
              mdate = int( stats[8] )
              age   = int(now - mdate)
              stup  = age, ipath
              stups.append(stup)

          stups.sort()
          stups.reverse()

          return stups

      def no_file_creation_condition(self,stups):

          # we have at least 100 files, we will create file(s)

          if len(stups) >= 100 : return False

          # find a file older than a minute, we will create file(s)

          for tup in stups :
              age, path = tup
              if age > 60 : return False

          return True

      def renamer(self,ipath):
          import string

          # directory and file
          lst=ipath.split('/')
          dir='/'.join(lst[:-1])

          new_name  = "CWAO" + string.zfill(self.compteur,8) + '.' + self.ext

          return dir + '/' + new_name

      def perform(self, ipaths, logger ):
          import os,time

          opaths = []

          # check if some files were already collected files
          # add to opaths and remove from ipaths

          for ipath in ipaths :
              lst=ipath.split('/')
              fil=lst[-1]
              if fil[0:4] == "CWAO" :
                 opaths.append(ipath)

          for opath in opaths :
              ipaths.remove(opath)

          if len(ipaths) == 0 :
             if len(opaths) == 0 :
                logger.info("no ready to collect sleep 10 secs")
                time.sleep(10)
             return opaths

          # sort according to file age

          stups = self.date_file_sort(ipaths)

          # should we create some files out of that file list ?

          if self.no_file_creation_condition(stups) :
             if len(opaths) == 0 :
                logger.info("no ready to collect sleep 10 secs")
                time.sleep(10)
             return opaths

          # ok lets go create the one collected file

          if len(stups) > 100 : stups = stups[:100]

          # read in the files

          data=''
          for i,tup in enumerate(stups) :
              age, ipath = tup
              try :
                    f = open(ipath, 'r')
                    fdat = f.read()
                    f.close()

                    # max len of 2000000 bytes
                    # if reached stop there

                    newlen = len(data) + len(fdat) 
                    if newlen > 2000000 :
                       logger.info("reaching 2Mb limit")
                       stups = stups[:i]
                       break

                    data += fdat

              except :
                    (type, value, tb) = sys.exc_info()
                    logger.error("problem while reading %s" % ipath)
                    logger.error(" Type: %s, Value: %s" % (type ,value))
                    return opaths

          # write the file into its proper ftpGTS name

          age, ipath = stups[0]
          self.compteur_next(ipath)
          opath = self.renamer(ipath)
          f = os.open( opath, os.O_CREAT | os.O_WRONLY )
          os.write( f , data )
          os.close( f )

          opaths.append(opath)

          # unlink all files forming the collection
          logger.info("collected file created %s" % opath)
          logger.info("from the following %d files" % len(stups))
          for tup in stups :
              age, ipath = tup
              os.unlink(ipath)
              logger.info("file inserted and unlinked %s" % ipath)

          # log a message

          return opaths

transformer=Transformer()
self.lx_script=transformer.perform

#from Logger import Logger
#logger = Logger("here.log", 'info', 'TX_test',1000000)
#logger = logger.getLogger()
#transformer=Transformer()
#
#flist = []
#flist.append... (give a list of files)
#print transformer.perform(flist,logger)
