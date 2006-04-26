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
#
# Date: 2005-09-05 DL
#       2005-11-01 MG
#
# Description:
#
#############################################################################################

"""
import sys, os, os.path, time, stat
import PXPaths, signal, socket
from AlarmFTP  import AlarmFTP
from URLParser import URLParser
from Logger import Logger
import ftplib

PXPaths.normalPaths()              # Access to PX paths

class SenderFTP(object):

    def __init__(self, client, logger=None) :

        # General Attributes
        self.client = client                      # Client Object
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'tx_' + client.name + '.log', 'INFO', 'TX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger

        self.originalDir = ''

        if self.client.protocol == 'ftp':
            self.ftp = self.ftpConnect()

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
        No error check intentionnal... if we were not succesfull than
        the error will be detected when we will STOR
        """
        self.ftp.cwd(self.originalDir)

        try   :
                self.ftp.cwd(destDir)
        except:
                DD = destDir.split("/")
                if destDir[0:1] == "/" :  DD[0] = "/" + DD[0]

                for d in DD :
                    try   :
                            self.ftp.cwd(d)
                    except:
                            try   :
                                    self.ftp.mkd(d)
                                    self.ftp.cwd(d)
                            except:
                                    return False
        return True

    def ftpConnect(self, maxCount=200):
        count = 0
        while count < maxCount:
            try:
                ftp = ftplib.FTP(self.client.host, self.client.user, self.client.passwd)
                if self.client.ftp_mode == 'active':
                    ftp.set_pasv(False)
                else:
                    ftp.set_pasv(True)
                self.originalDir = ftp.pwd()
                return ftp
            except:
                count +=  1
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to connect to %s (user:%s). Type: %s, Value: %s" % (self.client.host, self.client.user, type ,value))
                time.sleep(5)   
        
        self.logger.critical("We exit SenderFTP after %i unsuccessful try" % maxCount)
        sys.exit(2) 

    # some system doesn't support chmod... so pass exception on that
    def perm(self, path):
        try    :
                 self.ftp.voidcmd('SITE CHMOD ' + str(self.client.chmod) + ' ' + path)
        except :
                 pass

    # some system doesn't permit deletion... so pass exception on that
    def rm(self, path):
        try    :
                 self.perm(path)
                 self.ftp.delete(path)
        except :
                 pass

    def send(self, files):
        currentFTPDir = ''
        for file in files:
            try:
                nbBytes = os.stat(file)[stat.ST_SIZE] 
            except:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to stat %s, Type: %s, Value: %s" % (file, type, value))
                continue
            basename = os.path.basename(file)
            destName, destDir = self.client.getDestInfos(basename)

            if destName:
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

                if self.client.protocol == 'file':
                    try:
                        if self.client.dir_mkdir == True and not os.path.isdir(destDir) : os.makedirs(destDir)
                        os.rename(file, destDir + '/' + destName)
                        self.logger.info("(%i Bytes) File %s delivered to %s://%s@%s%s%s" % (nbBytes, file, self.client.protocol, self.client.user, self.client.host, destDirString, destName))
                    except:
                        self.logger.error("Unable to do move operation to: %s" % (destDirString + destName))
                        time.sleep(1)

                elif self.client.protocol == 'ftp':
                    if currentFTPDir != destDir:
                        if self.client.dir_mkdir:
                           try:
                               if self.dirMkdir(destDir):
                                  currentFTPDir = destDir
                           except:
                               (type, value, tb) = sys.exc_info()
                               self.logger.error("Unable to mkdir to: %s, Type: %s, Value:%s" % (destDir, type, value))
                               time.sleep(1)
                               continue
                        else:
                           try:
                               self.ftp.cwd(self.originalDir)
                               self.ftp.cwd(destDir)
                               currentFTPDir = destDir
                           except ftplib.error_perm:
                               (type, value, tb) = sys.exc_info()
                               self.logger.error("Unable to cwd to: %s, Type: %s, Value:%s" % (destDir, type, value))
                               time.sleep(1)
                               continue

                    # Do the chmod or .tmp thing
                    tempName = destName
                    try:
                        if self.client.timeout_send > 0 : timex = AlarmFTP('FTP timeout')

                        # Do the .tmp thing
                        if self.client.lock[0] == '.':
                            tempName = destName + self.client.lock
                            fileObject = open(file, 'r')
                            if self.client.timeout_send > 0 :
                               timex.alarm(self.client.timeout_send)
                               self.ftp.storbinary("STOR " + tempName, fileObject)
                               timex.cancel()
                            else:
                               self.ftp.storbinary("STOR " + tempName, fileObject)
                            fileObject.close()
                            self.ftp.rename(tempName, destName)

                        # Do the chmod thing
                        else:
                            self.ftp.voidcmd('SITE UMASK 777')
                            fileObject = open(file, 'r' )
                            if self.client.timeout_send > 0 :
                               timex.alarm(self.client.timeout_send)
                               self.ftp.storbinary('STOR ' + destName, fileObject)
                               timex.cancel()
                            else :
                               self.ftp.storbinary('STOR ' + destName, fileObject)
                            fileObject.close()

                        self.perm(destName)
                        os.unlink(file)
                        self.logger.info("(%i Bytes) File %s delivered to %s://%s@%s%s%s" % (nbBytes, file, self.client.protocol, self.client.user, self.client.host, destDirString, destName))

                    except socket.error:
                        self.logger.info("SEND TIMEOUT (%i Bytes) File %s going to %s://%s@%s%s%s" % (nbBytes, file, self.client.protocol, self.client.user, self.client.host, destDirString, destName))
                        return

                    except:
                        (type, value, tb) = sys.exc_info()
                        self.logger.error("Unable to deliver to %s://%s@%s%s%s, Type: %s, Value: %s" % 
                                                    (self.client.protocol, self.client.user, self.client.host, destDirString, destName, type, value))
                        if self.client.lock[0] == '.':
                           self.rm(tempName)
                        self.rm(destName)

                        time.sleep(1)
                        
                        # FIXME: Faire des cas particuliers selon les exceptions recues
                        # FIXME: Voir le cas ou un fichier aurait les perms 000
                        # FIXME: ftp.quit() a explorer
                        # FIXME: Reutilisation de ftpConnect

                else:
                    self.logger.critical("Unknown protocol: %s" % self.client.protocol)
                    sys.exit(2) 

            else:
                os.unlink(file)
                self.logger.info('No destination name: %s has been erased' % file)

if __name__ == '__main__':
    pass
