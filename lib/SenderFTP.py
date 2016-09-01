"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: SenderFTP.py
#
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#          Michel Grenier (Path pattern and mkdir)
#          Michel Grenier (Add SFTP support)
#
# Date: 2005-09-05 DL
#       2005-11-01 MG
#       2007-05-30 MG
#
# Description: use file/ftp/sftp to send files to clients
#
#############################################################################################
"""
import re,sys, os, os.path, time, stat, string
import PXPaths, signal, socket

import ftplib
#
import paramiko
from   paramiko import *

from AlarmFTP  import AlarmFTP
from AlarmFTP  import FtpTimeoutException
from URLParser import URLParser
from Logger import Logger

PXPaths.normalPaths()              # Access to PX paths

class SenderFTP(object):

    def __init__(self, client, logger=None, cacheManager=None) :

        # General Attributes
        self.client       = client       # Client Object
        self.cacheManager = cacheManager # cache  Object
        self.cacheMD5     = None         # last cache Object tested/added
        self.partialfile  = None         # last cache Object tested/added
        self.logger       = logger
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'tx_' + client.name + '.log', 'INFO', 'TX' + name) # Enable logging
            self.logger = self.logger.getLogger()

        self.originalDir = ''

        self.ftp  = None
        self.sftp = None
        self.bytes_ps = self.client.kbytes_ps * 1024.0


        self.timeout = self.client.timeout
        if self.timeout < 30 : self.timeout = 30

        # instead of testing through out the code, overwrite functions for ftp
        if self.client.protocol == 'ftp':
           self.ftp         = self.ftpConnect()
           self.chdir       = self.ftp.cwd
           self.chmod       = self.ftp_chmod
           self.delete      = self.ftp.delete
           self.mkdir       = self.ftp.mkd
           self.quit        = self.ftp.quit

           self.put = self.ftp_put_binary
           if self.client.binary == False :
              self.put = self.ftp_put_ascii

           if self.client.kbytes_ps > 0.0 :
              self.put = self.ftp_put_binary_trottle
              if self.client.binary == False :
                 self.put = self.ftp_put_ascii_trottle

        # instead of testing through out the code, overwrite functions for sftp
        if self.client.protocol == 'sftp':
           self.sftp        = self.sftpConnect()
           self.chdir       = self.sftp.chdir
           self.chmod       = self.sftp_chmod
           self.delete      = self.sftp.remove
           self.mkdir       = self.sftp_mkdir
           self.Ochmod      = self.octal_perm(self.client.chmod)
           self.put         = self.sftp.put
           self.quit        = self.sftp_quit

           if self.client.kbytes_ps > 0.0 :
              self.put = self.sftp_put_trottle

        # First put method : use a temporary filename = filename + lock extension
        if self.client.lock[0] == '.':
           self.send_file = self.send_lock
    
        # Second put method : use UMASK to temporary lock the file
        elif self.client.lock == 'umask' :
           self.send_file = self.send_umask

        # sending one file straight No locking method  (fall back if lock type incorrect)
        else :
           if self.client.lock != 'None' :
              self.logger.warning("lock option invalid (%s) no locking used" % self.client.lock)
           self.send_file = self.send_unlock

    # close connection... 

    def close(self):

        if self.client.protocol == 'file': return

        timex = AlarmFTP(self.client.protocol + ' connection timeout')

        try    :
                  # gives 10 seconds to close the connection
                  timex.alarm(10)

                  self.quit()

                  timex.cancel()
        except :
                  timex.cancel()
                  (type, value, tb) = sys.exc_info()
                  self.logger.warning("Could not close connection")
                  self.logger.warning(" Type: %s, Value: %s" % (type ,value))

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
        elif keywd[:5] == "{BBB}"   : return (EN[3])[0:3]   + keywd[5:]
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


    def dirMkdir(self,destDir) :
        """
        MG 20080625 
        Now throw exception while creating directory
        this fix a bug that when the directory was not
        created the file could be written in the parent dir.
        """

        self.chdir(self.originalDir)

        try   :
                self.chdir(destDir)
        except:
                DD = destDir.split("/")
                if destDir[0:1] == "/" :  DD[0] = "/" + DD[0]

                for d in DD :
                    try   :
                            self.chdir(d)
                    except:
                            self.mkdir(d)
                            self.perm(d)
                            self.chdir(d)

    def ftpConnect(self, maxCount=200):
        count = 0
        while count < maxCount:

            timex = AlarmFTP('FTP connection timeout')

            try:
                # gives "timeout" seconds to open the connection
                timex.alarm(self.timeout)

                ftp = ftplib.FTP(self.client.host, self.client.user, self.client.passwd)
                if self.client.ftp_mode == 'active':
                    ftp.set_pasv(False)
                else:
                    ftp.set_pasv(True)

                self.originalDir = '.'

                try   : self.originalDir = ftp.pwd()
                except:
                        (type, value, tb) = sys.exc_info()
                        self.logger.warning("Unable to ftp.pwd (Type: %s, Value: %s)" % (type ,value))

                timex.cancel()

                return ftp

            except FtpTimeoutException :
                timex.cancel()
                self.logger.error("FTP connection timed out after %d seconds... retrying" % self.timeout )

            except:
                timex.cancel()
                count +=  1
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to connect to %s (user:%s). Type: %s, Value: %s" % (self.client.host, self.client.user, type ,value))
                time.sleep(5)   

        self.logger.critical("We exit SenderFTP after %i unsuccessful try" % maxCount)
        sys.exit(2) 

    def sftpConnect(self, maxCount=200):
        count = 0
        while count < maxCount:

            timex = AlarmFTP('SFTP connection timeout')

            # gives "timeout" seconds to open the connection
            try:
                timex.alarm(self.timeout)
                self.t = None
                if self.client.port == None : 
                   self.t = paramiko.Transport(self.client.host)
                else:
                   t_args = (self.client.host,self.client.port)
                   self.t = paramiko.Transport(t_args)

                if self.client.ssh_keyfile != None :
                   #TODO, implement password to use to decrypt the key file, if it's encrypted
                   #key=DSSKey.from_private_key_file(self.client.ssh_keyfile,password=None)
                   self.t.connect(username=self.client.user,pkey=None,key_filename=self.client.ssh_keyfile)
                else:
                   self.t.connect(username=self.client.user,password=self.client.passwd)

                self.sftp = paramiko.SFTP.from_transport(self.t)
                # WORKAROUND without going to '.' originalDir was None
                self.sftp.chdir('.')
                self.originalDir = self.sftp.getcwd()

                timex.cancel()

                return self.sftp

            except FtpTimeoutException :
                timex.cancel()
                try    : self.sftp.close()
                except : pass
                try    : self.t.close()
                except : pass
                self.logger.error("SFTP connection timed out after %d seconds... retrying" % self.timeout )

            except:
                timex.cancel()
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to connect to %s (user:%s). Type: %s, Value: %s" % (self.client.host, self.client.user, type ,value))
                try    : self.sftp.close()
                except : pass
                try    : self.t.close()
                except : pass
                count +=  1
                time.sleep(5)   

        self.logger.critical("We exit SenderSFTP after %i unsuccessful try" % maxCount)
        sys.exit(2) 

    # some system doesn't support chmod... so pass exception on that
    def perm(self, path):
        try    :
                 self.chmod(self.client.chmod,path)
        except :
                 (type, value, tb) = sys.exc_info()
                 self.logger.debug("Could not chmod  %s" % path )
                 self.logger.debug(" Type: %s, Value: %s" % (type ,value))

    # some systems do not permit deletion... so pass exception on that
    def rm(self, path):
        try    :
                 self.delete(path)
        except : 
                 (type, value, tb) = sys.exc_info()
                 self.logger.debug("Could not delete %s" % path )
                 self.logger.debug(" Type: %s, Value: %s" % (type ,value))

    # sending one file using lock extension method
    def send_lock(self, file, destName ):

        tempName = destName + self.client.lock

        if self.sftp != None :
           # does not seem to work do a straight put
           self.put(file,tempName)
           self.sftp.rename(tempName, destName)
           #self.sftp.put(file,destName)

        if self.ftp != None :
           self.partialfile = tempName
           self.put(file,tempName)
           self.ftp.rename(tempName, destName)
           self.partialfile = destName

        self.perm(destName)

    # octal permission... there must be a better way of doing this...
    def octal_perm(self, perm ):
        unit = perm % 10
        diz  = perm % 100  /  10
        cent = perm % 1000 /  100
        oct  = cent * 64 + diz * 8 + unit
        return oct

    # sending one file using umask method
    def send_umask(self, file, destName ):

        if self.sftp != None :
           newfile = self.sftp.open( destName, mode='w' )
           self.sftp.chmod(destName, 0 )
           fileObject = open(file, 'r' )
           newfile.write(fileObject.read())
           fileObject.close()
           newfile.close()
           self.sftp.chmod(destName, self.Ochmod)

        if self.ftp != None :
           self.ftp.voidcmd('SITE UMASK 777')
           self.put(file,destName)
           self.ftp.voidcmd('SITE CHMOD ' + str(self.client.chmod) + ' ' + destName)

    # sending one file straight No locking method
    def send_unlock(self, file, destName ):
        self.put(file,destName)
        self.perm(destName)

    # sending a list of files
    def send(self, files):

        # process with file sending

        currentFTPDir = ''

        for filex in files:

            file = filex

            self.partialfile = None

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
            nbBytes = 0
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

            # check protocol
            if not self.client.protocol in ['file','ftp','sftp'] :
               self.logger.critical("Unknown protocol: %s" % self.client.protocol)
               sys.exit(2) 

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

            # file protocol means file renaming
            if self.client.protocol == 'file':
               try:
                      self.logger.start_timer()
                      if self.client.dir_mkdir == True and not os.path.isdir(destDirString) : os.makedirs(destDirString)
                      os.rename(file, destDirString + destName)
                      self.logger.delivered("(%i Bytes) File %s delivered to %s://%s@%s%s%s" % (nbBytes, file, self.client.protocol, self.client.user, self.client.host, destDirString, destName),destDirString + destName)

                      # add data to cache if needed
                      if self.client.nodups and self.cacheMD5 != None : 
                         self.cacheManager.find( self.cacheMD5, 'standard' ) 

               except:
                      (type, value, tb) = sys.exc_info()
                      self.logger.error("Unable to move to: %s, Type: %s, Value:%s" % ((destDirString+destName), type, value))
                      time.sleep(1)
               continue

            # ftp or sftp protocol
            if self.client.protocol == 'ftp' or self.client.protocol == 'sftp':

               try :
                   self.logger.start_timer()

                   # the alarm timeout is set at that level
                   # it means that everything done to a file must be done
                   # within "timeout_send" seconds

                   timex = AlarmFTP(self.client.protocol + ' timeout')
                   if self.client.timeout_send > 0 :
                      timex.alarm(self.client.timeout_send)

                   # we are not in the proper directory
                   if currentFTPDir != destDir:
    
                      # create and cd to the directory
                      if self.client.dir_mkdir:
                         try:
                                 self.dirMkdir(destDir)
                                 currentFTPDir = destDir
                         except:
                                 timex.cancel()
                                 (type, value, tb) = sys.exc_info()
                                 self.logger.error("Unable to mkdir: %s, Type: %s, Value:%s" % (destDir, type, value))
                                 time.sleep(1)
                                 continue
    
                      # just cd to the directory
                      else:
                         try:
                                self.chdir(self.originalDir)
                                self.chdir(destDir)
                                currentFTPDir = destDir
                         except :
                                timex.cancel()
                                (type, value, tb) = sys.exc_info()
                                self.logger.error("Unable to cwd to: %s, Type: %s, Value:%s" % (destDir, type, value))
                                time.sleep(1)
                                continue

                   # try to write the file to the client
                   try :

                          d1,d2,d3,d4,tbegin = os.times()

                          self.partialfile    = destName
                          self.send_file( file, destName )
                          self.partialfile = None

                          d1,d2,d3,d4,tend   = os.times()

                          self.logger.delivered("(%i Bytes) File %s delivered to %s://%s@%s%s%s" % \
                                          (nbBytes, file, self.client.protocol, self.client.user, \
                                          self.client.host, destDirString, destName),file)

                          os.unlink(file)

                          if self.client.kbytes_ps > 0.0 :
                             tspan    = tend - tbegin
                             if tspan >= 1.0 : 
                                tspan  = tspan * 1024.0
                                tspeed = nbBytes/tspan
                                self.logger.debug("Speed %f Kb/s" % tspeed)
    
                          # add data to cache if needed
                          if self.client.nodups and self.cacheMD5 != None : 
                             self.cacheManager.find( self.cacheMD5, 'standard' ) 

                   except:
                          timex.cancel()
                          (type, value, tb) = sys.exc_info()
                          self.logger.error("Unable to deliver to %s://%s@%s%s%s, Type: %s, Value: %s" % 
                                           (self.client.protocol, self.client.user, self.client.host, \
                                           destDirString, destName, type, value))
    
                          # preventive delete when problem 
                          if self.partialfile != None :
                             timex.alarm(5)
                             try     :
                                       self.logger.debug("Trying preventive delete")
                                       self.rm(self.partialfile)
                             except : 
                                       self.logger.debug("Preventive delete timed out")
                             timex.cancel()

                          time.sleep(1)
                          return

                   timex.cancel()
    
               except FtpTimeoutException :
                   timex.cancel()
                   self.logger.warning("SEND TIMEOUT (%i Bytes) File %s going to %s://%s@%s%s%s" % \
                                      (nbBytes, file, self.client.protocol, self.client.user, \
                                       self.client.host, destDirString, destName))

                   return
                       
                   # FIXME: Faire des cas particuliers selon les exceptions recues
                   # FIXME: Voir le cas ou un fichier aurait les perms 000
                   # FIXME: Reutilisation de ftpConnect


    # check if data in cache... if not it is added automatically
    def in_cache(self,unlink_it,path) :

        try   :
                 self.cacheMD5 = self.cacheManager.get_md5_from_file(path)
        except:
                 self.logger.error("Suppress duplicate : could not read %s", os.path.basename(path))
                 return False

        return   self.cacheManager.has(self.cacheMD5, 'standard') 

    # ftp chmod 
    def ftp_chmod(self,chmod,path):
        self.ftp.voidcmd('SITE CHMOD ' + str(self.client.chmod) + ' ' + path)

    # ftp put ascii
    def ftp_put_ascii(self,file,destName):
        fileObject = open(file)
        self.ftp.storlines("STOR " + destName, fileObject)
        fileObject.close()

    # ftp put ascii trottle
    def ftp_put_ascii_trottle(self,file,destName):
        d1,d2,d3,d4,now = os.times()
        self.tbytes     = 0.0
        self.tbegin     = now + 0.0

        fileObject = open(file)
        self.ftp.storlines("STOR " + destName, fileObject, self.trottle)
        fileObject.close()

    # ftp put binary
    def ftp_put_binary(self,file,destName):
        fileObject = open(file, 'rb')
        self.ftp.storbinary("STOR " + destName, fileObject)
        fileObject.close()

    # ftp put binary trottle
    def ftp_put_binary_trottle(self,file,destName):
        d1,d2,d3,d4,now = os.times()
        self.tbytes     = 0.0
        self.tbegin     = now + 0.0
        blocksize       = 8192

        fileObject = open(file, 'rb')
        self.ftp.storbinary("STOR " + destName, fileObject, blocksize, self.trottle)
        fileObject.close()

    # sftp chmod 
    def sftp_chmod(self,chmod,path):
        Ochmod = self.Ochmod
        if chmod != self.client.chmod :
           Ochmod = self.octal_perm(chmod)
        self.sftp.chmod(path,Ochmod)

    # sftp mkdir 
    def sftp_mkdir(self,d):
        self.sftp.mkdir(d,self.Ochmod)

    # sftp quit = close connection... 
    def sftp_quit(self):
        self.sftp.close()
        self.t.close()

    def trottle(self,buf) :
        self.tbytes = self.tbytes + len(buf)
        span = self.tbytes / self.bytes_ps
        d1,d2,d3,d4,now = os.times()
        rspan = now - self.tbegin
        if span > rspan :
           time.sleep(span-rspan)

    # sftp put trottle
    def sftp_put_trottle(self,file,destName):
        d1,d2,d3,d4,now = os.times()
        self.tbegin     = now + 0.0
        self.sftp.put(file,destName,self.strottle)

    def strottle(self, tbytes, total) :
        span = tbytes / self.bytes_ps
        d1,d2,d3,d4,now = os.times()
        rspan = now - self.tbegin
        if span > rspan :
           time.sleep(span-rspan)

if __name__ == '__main__':
    pass
