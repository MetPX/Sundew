"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: SenderScript.py
#
# Authors: 
#          Michel Grenier  2007-12-20
#
# Description: send files using user defined script
#
# TODO  too much things from SenderFTP   ... should make a class for common utils
#
#############################################################################################
"""
import re,sys, os, os.path, time, stat, string
import PXPaths, signal, socket

from AlarmFTP  import AlarmFTP
from AlarmFTP  import FtpTimeoutException
from URLParser import URLParser
from Logger import Logger

PXPaths.normalPaths()              # Access to PX paths

class SenderScript(object):

    def __init__(self, client, logger=None, cacheManager=None) :

        # General Attributes
        self.client       = client       # Client Object
        self.cacheManager = cacheManager # cache  Object
        self.cacheMD5     = None         # last cache Object tested/added
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'tx_' + client.name + '.log', 'INFO', 'TX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger

        self.timeout = self.client.timeout
        if self.timeout < 30 : self.timeout = 30

        if self.client.send_script == None :
           self.logger.error("The send script is not set or incorrect")
           sys.exit(1)

    def basename_parts(self,basename):
        """
        Using regexp, basename parts can become a valid directory pattern replacements
        """

        # check against the masks
        for mask in self.client.masks:
           # no match
           if not mask[3].match(basename) : continue

           # reject
           if not mask[4] : return None

           # accept... so key generation
           parts = re.findall( mask[0], basename )
           if len(parts) == 2 and parts[1] == '' : parts.pop(1)
           if len(parts) != 1 : continue

           lst = []
           if isinstance(parts[0],tuple) :
              lst = list(parts[0])
           else:
             lst.append(parts[0])

           return lst

        # fallback behavior return filename
        return None

    def dirPattern(self,file,basename,destDir,destName) :
        """
        MG 20051101
        TODO  this could be improved... bulletins could be read in and info extracted from there...
        it was decided to take possible dir info from the basename
        ex of basename = SNCN19_CWAO_011340_0001:test:CWAO:SN:3:Direct:20051101134041
        """

        BN = basename.split(":")
        EN = BN[0].split("_")
        BP = self.basename_parts(basename)

        ndestDir = ""
        DD = destDir.split("/")
        for  ddword in DD :
             if ddword == "" : continue

             nddword = ""
             DW = ddword.split("$")
             for dwword in DW :
                 nddword += self.matchPattern(BN,EN,BP,dwword,dwword)

             ndestDir += "/" + nddword 

        return ndestDir


    def matchPattern(self,BN,EN,BP,keywd,defval) :
        """
        MG 20051101
        Matching keyword with different patterns
        """

        if   keywd[:4] == "{T1}"    : return (EN[0])[0:1]   + keywd[4:]
        elif keywd[:4] == "{T2}"    : return (EN[0])[1:2]   + keywd[4:]
        elif keywd[:4] == "{A1}"    : return (EN[0])[2:3]   + keywd[4:]
        elif keywd[:4] == "{A2}"    : return (EN[0])[3:4]   + keywd[4:]
        elif keywd[:4] == "{ii}"    : return (EN[0])[4:6]   + keywd[4:]
        elif keywd[:6] == "{CCCC}"  : return  EN[1]         + keywd[6:]
        elif keywd[:4] == "{YY}"    : return (EN[2])[0:2]   + keywd[4:]
        elif keywd[:4] == "{GG}"    : return (EN[2])[2:4]   + keywd[4:]
        elif keywd[:4] == "{Gg}"    : return (EN[2])[4:6]   + keywd[4:]
        elif keywd[:5] == "{BBB}"   : return (EN[3])[6:9]   + keywd[5:]
        elif keywd[:7] == "{RYYYY}" : return (BN[6])[0:4]   + keywd[7:]
        elif keywd[:5] == "{RMM}"   : return (BN[6])[4:6]   + keywd[5:]
        elif keywd[:5] == "{RDD}"   : return (BN[6])[6:8]   + keywd[5:]
        elif keywd[:5] == "{RHH}"   : return (BN[6])[8:10]  + keywd[5:]
        elif keywd[:5] == "{RMN}"   : return (BN[6])[10:12] + keywd[5:]
        elif keywd[:5] == "{RSS}"   : return (BN[6])[12:14] + keywd[5:]

        # Matching with basename parts if given

        if BP != None :
           for i,v in enumerate(BP):
               kw  = '{' + str(i) +'}'
               lkw = len(kw)
               if keywd[:lkw] == kw : return v + keywd[lkw:]

        return defval

    # sending a list of files
    def send(self, files):
       
        filelst = None

        # process with file sending

        for filex in files:

            file = filex

            # priority 0 is retransmission and is never suppressed

            priority = file.split('/')[-3]

            # if in cache than it was already sent... nothing to do
            # caching is always done on original file for early check (before fx)

            if self.client.nodups and priority != '0' and self.in_cache( True, file ) :
               self.logger.info("suppressed duplicate send %s", os.path.basename(file))
               os.unlink(file)
               continue

            # applying the fx_script if defined redefine the file list

            if self.client.fx_execfile != None :
               fxfile = self.client.run_fx_script(file,self.logger)
               if fxfile == None :
                  self.logger.warning("FX script ignored the file : %s"    % os.path.basename(file) )
                  os.unlink(file)
                  continue
               elif fxfile == file :
                  self.logger.warning("FX script kept the file as is : %s" % os.path.basename(file) )
               else :
                  self.logger.info("FX script modified %s to %s " % (os.path.basename(file),fxfile) )
                  os.unlink(file)
                  file = fxfile

            # get files ize
            try:
                nbBytes = os.stat(file)[stat.ST_SIZE] 
            except:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to stat %s, Type: %s, Value: %s" % (file, type, value))
                continue

            # get/check destination Name
            basename = os.path.basename(file)
            destName, destDir = self.client.getDestInfos(basename)
            if not destName :
               os.unlink(file)
               self.logger.info('No destination name: %s has been erased' % file)
               continue

            # run destfn
            ldestName = self.client.run_destfn_script(destName)
            if ldestName != destName :
               self.logger.info("destfn_script : %s becomes %s "  % (destName,ldestName) )
            destName = ldestName

            # We remove the first / (if there was only one => relative path, if there was two => absolute path)
            destDir = destDir[1:]

            if self.client.dir_pattern == True :
               destDir = self.dirPattern(file,basename,destDir,destName)

            if destDir == '':
                destDirString = '/'
            elif destDir == '/':
                destDirString = '//'
            else:
                destDirString = '/' + destDir + '/'

            # add entry to file list

            if filelst == None : filelst = []
            filelst.append( (file,destDir,destName) )

        # no file to process

        if filelst == None : return

        # the alarm timeout is set at that level
        # it means that everything done for a file list under
        # within "timeout_send" seconds

        timex = AlarmFTP(self.client.protocol + ' timeout')
        if self.client.timeout_send > 0 :
           timex.alarm(self.client.timeout_send)

        # ok using script to send the file list

        try :
                  self.client.send_script( self.client, filelst, self.logger )

                  for t in filelst :
                      file,destdir,destName = t
                      latency = time.time() - os.stat(file)[stat.ST_MTIME]
                      self.logger.info("(%i Bytes) File %s delivered to %s://%s@%s%s%s (lat=%f)" %\
                                         (nbBytes, file, self.client.protocol, self.client.user, \
                                         self.client.host, destDir, destName, latency))
                      os.unlink(file)
    
                      # add data to cache if needed
                      if self.client.nodups and self.cacheMD5 != None : 
                         self.cacheManager.find( self.cacheMD5, 'standard' ) 

        except FtpTimeoutException :
                  timex.cancel()
                  self.logger.warning("SEND TIMEOUT (%i Bytes) File %s going to %s://%s@%s" % \
                                     (nbBytes, file, self.client.protocol, self.client.user,self.client.host))
                  return

        except:
                  (type, value, tb) = sys.exc_info()
                  self.logger.error("Unable to deliver to %s://%s%s, Type: %s, Value: %s" % 
                                     (self.client.protocol, self.client.user, self.client.host,type, value))
    
                  timex.cancel()
                  return

        timex.cancel()
    

    # check if data in cache... if not it is added automatically
    def in_cache(self,unlink_it,path) :

        try   :
                 self.cacheMD5 = self.cacheManager.get_md5_from_file(path)
        except:
                 self.logger.error("Suppress duplicate : could not read %s", os.path.basename(path))
                 return False

        return   self.cacheManager.has(self.cacheMD5, 'standard') 

if __name__ == '__main__':
    pass
