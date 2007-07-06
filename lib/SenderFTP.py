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
import sys, os, os.path, time, stat
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
        self.cacheData    = None         # last cache Object tested/added
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'tx_' + client.name + '.log', 'INFO', 'TX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger

        self.originalDir = ''

        self.ftp  = None
        self.sftp = None

        if self.client.protocol == 'ftp':
           self.ftp    = self.ftpConnect()
           self.chdir  = self.ftp.cwd

        if self.client.protocol == 'sftp':
           self.sftp   = self.sftpConnect()
           self.chdir  = self.sftp.chdir

    # close connection... 

    def close(self):

        if self.ftp == None and self.sftp == None : return

        timex = AlarmFTP(self.client.protocol + ' connection timeout')

        try    :
                  # gives 10 seconds to close the connection
                  timex.alarm(10)

                  if self.sftp != None :
                     self.sftp.close()
                     self.t.close()

                  if self.ftp != None :
                     self.ftp.quit()

                  timex.cancel()
        except :
                  timex.cancel()
                  (type, value, tb) = sys.exc_info()
                  self.logger.warning("Could not close connection")
                  self.logger.warning(" Type: %s, Value: %s" % (type ,value))

    def dirPattern(self,file,basename,destDir,destName) :
        """
        MG 20051101
        TODO  this could be improved... bulletins could be read in and info extracted from there...
        it was decided to take possible dir info from the basename
        ex of basename = SNCN19_CWAO_011340_0001:test:CWAO:SN:3:Direct:20051101134041
        """

        BN = basename.split(":")
        EN = BN[0].split("_")

        ndestDir = ""
        DD = destDir.split("/")
        for  ddword in DD :
             if ddword == "" : continue

             nddword = ""
             DW = ddword.split("$")
             for dwword in DW :
                 nddword += self.matchPattern(BN,EN,dwword,dwword)

             ndestDir += "/" + nddword 

        return ndestDir


    def matchPattern(self,BN,EN,keywd,defval) :
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

        return defval


    def dirMkdir(self,destDir) :
        """
        MG 20051101
        No error check intentional... if we were not succesful then
        the error will be detected when we STOR
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
                            try   :
                                    if self.sftp != None :
                                       self.sftp.mkdir(d,self.client.chmod)
                                    if self.ftp != None :
                                       self.ftp.mkd(d)
                                       self.perm(d)

                                    self.chdir(d)
                            except:
                                    return False
        return True

    def ftpConnect(self, maxCount=200):
        count = 0
        while count < maxCount:

            timex = AlarmFTP('FTP connection timeout')

            try:
                # gives 30 seconds to open the connection
                timex.alarm(30)

                ftp = ftplib.FTP(self.client.host, self.client.user, self.client.passwd)
                if self.client.ftp_mode == 'active':
                    ftp.set_pasv(False)
                else:
                    ftp.set_pasv(True)
                self.originalDir = ftp.pwd()

                timex.cancel()

                return ftp

            except FtpTimeoutException :
                timex.cancel()
                self.logger.error("FTP connection timed out after 30 seconds... retrying" )

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

            # gives 30 seconds to open the connection
            try:
                timex.alarm(30)
                self.t = paramiko.Transport(self.client.host)
                key=DSSKey.from_private_key_file(self.client.ssh_keyfile,self.client.passwd)
                self.t.connect(username=self.client.user,pkey=key)
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
                self.logger.error("SFTP connection timed out after 30 seconds... retrying" )

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
                 if self.sftp != None : self.sftp.chmod(path,self.client.chmod)
                 if self.ftp  != None : self.ftp.voidcmd('SITE CHMOD ' + str(self.client.chmod) + ' ' + path)
        except :
                 (type, value, tb) = sys.exc_info()
                 self.logger.debug("Could not chmod  %s" % path )
                 self.logger.debug(" Type: %s, Value: %s" % (type ,value))

    # some systems do not permit deletion... so pass exception on that
    def rm(self, path):
        try    :
                 if self.sftp != None : self.sftp.remove(path)
                 if self.ftp  != None : self.ftp.delete(path)
        except :
                 (type, value, tb) = sys.exc_info()
                 self.logger.warning("Could not delete %s" % path )
                 self.logger.warning(" Type: %s, Value: %s" % (type ,value))

    # sending one file using lock extension method
    def send_lock(self, file, destName ):

        tempName = destName + self.client.lock

        if self.sftp != None :
           # does not seem to work do a straight put
           #self.sftp.put(file,tempName)
           #self.sftp.rename(tempName, destName)
           self.sftp.put(file,destName)

        if self.ftp != None :
           fileObject = open(file, 'r')
           self.ftp.storbinary("STOR " + tempName, fileObject)
           fileObject.close()
           self.ftp.rename(tempName, destName)

        self.perm(destName)


    # sending one file using umask method
    def send_umask(self, file, destName ):

        if self.sftp != None :
           #    sftp.umask(777) does not exist
           self.sftp.put(file,destName)
           self.sftp.chmod(destName,self.client.chmod)

        if self.ftp != None :
           self.ftp.voidcmd('SITE UMASK 777')
           fileObject = open(file, 'r' )
           self.ftp.storbinary('STOR ' + destName, fileObject)
           fileObject.close()
           self.ftp.voidcmd('SITE CHMOD ' + str(self.client.chmod) + ' ' + destName)


    # sending one file straight No locking method
    def send_unlock(self, file, destName ):

        if self.sftp != None :
           self.sftp.put(file,destName)

        if self.ftp != None :
           fileObject = open(file, 'r')
           self.ftp.storbinary("STOR " + destName, fileObject)
           fileObject.close()

        self.perm(destName)


    # sending a list of files
    def send(self, files):

        # process with file sending

        currentFTPDir = ''

        for filex in files:

            file = filex

            # priority 0 is retransmission and is never suppressed

            priority = file.split('/')[5]

            # if in cache than it was already sent... nothing to do
            # caching is always done on original file for early check (before fx)

            if self.client.nodups and priority != '0' and self.in_cache( True, file ) :
               self.logger.info("suppressed duplicate send %s", os.path.basename(file))
               os.unlink(file)
               continue

            # applying the fx_script if defined redefine the file list

            if self.client.execfile2 != None :
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
                      if self.client.dir_mkdir == True and not os.path.isdir(destDirString) : os.makedirs(destDirString)
                      os.rename(file, destDirString + destName)
                      self.logger.info("(%i Bytes) File %s delivered to %s://%s@%s%s%s" % (nbBytes, file, self.client.protocol, self.client.user, self.client.host, destDirString, destName))

                      # add data to cache if needed
                      if self.client.nodups and self.cacheData != None : 
                         self.cacheManager.find( self.cacheData, 'md5' ) 

               except:
                      (type, value, tb) = sys.exc_info()
                      self.logger.error("Unable to move to: %s, Type: %s, Value:%s" % ((destDirString+destName), type, value))
                      time.sleep(1)
               continue

            # ftp or sftp protocol
            if self.client.protocol == 'ftp' or self.client.protocol == 'sftp':

               try :

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
                                 if self.dirMkdir(destDir):
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

                          # First put method : use a temporary filename = filename + lock extension
                          if self.client.lock[0] == '.':
                             self.send_lock( file,destName )
    
                          # Second put method : use UMASK to temporary lock the file
                          elif self.client.lock == 'umask' :
                             self.send_umask( file,destName )

                          # third no special locking mechanism (fall back if lock type incorrect)
                          else :
                             if self.client.lock != 'None' :
                                self.logger.warning("lock option invalid (%s) no locking used" % self.client.lock)
                             self.send_unlock( file,destName )
    
                          # add data to cache if needed
                          if self.client.nodups and self.cacheData != None : 
                             self.cacheManager.find( self.cacheData, 'md5' ) 

                          os.unlink(file)
                          self.logger.info("(%i Bytes) File %s delivered to %s://%s@%s%s%s" % \
                                          (nbBytes, file, self.client.protocol, self.client.user, \
                                          self.client.host, destDirString, destName))

                   except:
                          (type, value, tb) = sys.exc_info()
                          self.logger.error("Unable to deliver to %s://%s@%s%s%s, Type: %s, Value: %s" % 
                                           (self.client.protocol, self.client.user, self.client.host, \
                                           destDirString, destName, type, value))
    
                          # preventive delete when umask 
                          if self.client.lock[0] != '.' :
                             self.rm(destName)

                          timex.cancel()
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

        self.cacheData=None

        try   :

                 f=open(path,'r')
                 self.cacheData=f.read()
                 f.close()
        except:
                 self.logger.error("Suppress duplicate : could not read %s", os.path.basename(path))
                 return False

        return   self.cacheManager.has(self.cacheData, 'md5') 

if __name__ == '__main__':
    pass
