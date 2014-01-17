"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PullFTPS.py
#
# Authors: Michel Grenier  Jan 2014
#
# Description: 
#
#   Reprise de PullFTP2.py sur pxatx... 
#   Refait pour supporter ftps seulement !!!
#
#############################################################################################

"""
import commands, os, os.path, re, stat, string, sys, time
import PXPaths, signal, socket
from AlarmFTP  import AlarmFTP
from AlarmFTP  import FtpTimeoutException
from URLParser import URLParser
from Logger import Logger

from M2Crypto import ftpslib

PXPaths.normalPaths()              # Access to PX paths

class PullFTPS(object):

    def __init__(self, source, logger=None, sleeping=False) :

        # General Attributes

        self.source      = source 
        self.sleeping    = sleeping

        self.connected   = False 
        self.ftps        = None
        self.file        = None
        self.ls          = {}
        self.lsold       = {}
        self.lspath      = ''
        self.pulllst     = []
        self.originalDir = ''
        self.destDir     = ''

        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'rx_' + source.name + '.log', 'INFO', 'RX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger

        if self.source.delete and self.sleeping :
           return

        self.ftps   = self.ftpsConnect()
        if self.ftps == None : return 

        self.chdir  = self.ftps.cwd
        self.delete = self.ftps.delete

        self.fget   = self.ftps_get
        self.lsdir  = self.ftps_do_ls

        self.quit   = self.ftps.quit


    # callback to strip and save the output from ls of directory

    def callback_line(self,block):

        # strip ls line to its most important info
        fil,desc = self.ls_line_stripper(block)

        # keep only if we are interested in that file

        for filepattern in self.pulllst :
            self.logger.debug("fil = (%s)" % fil)
            if re.compile(filepattern).match(fil):
               self.logger.debug("fil = OK")
               self.ls[fil] = desc


    # going to a certain directory

    def cd(self, path):

        if path == '.' : return True

        timex = AlarmFTP('FTPS change working directory timeout')

        try   :
                  # gives 10 seconds to get there
                  timex.alarm(10)
                  self.chdir(self.originalDir)
                  self.chdir(path)
                  timex.cancel()
                  return True
        except :
                  timex.cancel()
                  (type, value, tb) = sys.exc_info()
                  self.logger.warning("Could not cd to directory %s" % path )
                  self.logger.warning(" Type: %s, Value: %s" % (type ,value))

        return False


    # close connection...

    def close(self):

        self.connected = False

        # connection did not work

        if self.ftps == None : return

        timex = AlarmFTP(self.source.protocol + ' connection timeout')

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


    # find differences between current ls and last ls
    # only the newer or modified files will be kept...

    def differ(self):

        # get new list and description
        new_lst  = self.ls.keys()
        new_desc = self.ls
        new_lst.sort()

        # get old list and description
        self.load_ls_file(self.lspath)

        old_lst  = self.lsold.keys()
        old_desc = self.lsold
        old_lst.sort()

        # compare

        filelst  = []
        desclst  = {}

        for f in new_lst :

            # keep a newer entry
            if not f in old_lst :
               filelst.append(f)
               desclst[f] = new_desc[f]
               continue

            # keep a modified entry
            if new_desc[f] != old_desc[f] :
               filelst.append(f)
               desclst[f] = new_desc[f]
               continue

        return filelst,desclst


    # check for pattern matching in directory name

    def dirPattern(self,path) :
        """
        Replace pattern in directory... 
        """

        ndestDir = ''

        DD = path.split("/")
        for  ddword in DD[1:] :
             ndestDir += '/'
             if ddword == "" : continue

             nddword = ""
             DW = ddword.split("$")
             for dwword in DW :
                 nddword += self.matchPattern(dwword,dwword)

             ndestDir += nddword

        return ndestDir

    # open connection... ftp

    def ftpsConnect(self):

        timex = AlarmFTP('FTPS connection timeout')

        try:
            # gives 30 seconds to open the connection
            timex.alarm(30)

            ftps = ftpslib.FTP_TLS()

            ftps.connect(self.source.host,21)
            # this should be an option... tls or ssl  ftps.auth_ssl()
            ftps.auth_tls()

            if self.source.ftp_mode == 'active':
                ftps.set_pasv(0)
            else:
                ftps.set_pasv(1)

            ftps.login(self.source.user, self.source.passwd)

            try   : self.originalDir = ftps.pwd()
            except:
                    (type, value, tb) = sys.exc_info()
                    self.logger.warning("Unable to ftp.pwd (Type: %s, Value: %s)" % (type ,value))

            timex.cancel()

            self.connected = True

            return ftps

        except FtpTimeoutException :
            timex.cancel()
            self.logger.warning("FTPS connection timed out after 30 seconds..." )

        except:
            timex.cancel()
            (type, value, tb) = sys.exc_info()
            self.logger.error("Unable to connect to %s (user:%s). Type: %s, Value: %s" % (self.source.host, self.source.user, type ,value))

    # ftp do an ls in the current directory, write in file path

    def ftps_do_ls(self):

        self.ls = {}

        timex = AlarmFTP('FTPS retrieving list')
        timex.alarm(self.source.timeout_get)

        try : 
                 ls=self.ftps.retrlines('LIST',self.callback_line )
                 timex.cancel()
                 return True

        except FtpTimeoutException :
                 timex.cancel()
                 self.logger.warning("FTPS doing ls timed out after %s seconds..." % self.source.timeout_get )

        except :
                 timex.cancel()
                 (type, value, tb) = sys.exc_info()
                 self.logger.warning("Could not ls directory %s" % self.destDir)
                 self.logger.warning(" Type: %s, Value: %s" % (type ,value))

        return False

    # ftp retrieve a file

    def ftps_get(self, remote_file, local_file):

        file=open(local_file,'wb')
        self.ftps.retrbinary('RETR ' + remote_file, file.write )
        file.close()


    # pulling files and returning the list

    def get(self):

        # if pull is sleeping and we delete files... nothing to do
        # if we don't delete files, we will keep the directory state

        if self.source.delete and self.sleeping : return

        # log that we are waking up

        if not self.sleeping : 
           self.logger.info("pull %s is waking up" % self.source.name )

        # getting our alarm ready
 
        timex = AlarmFTP('FTPS timeout')

        # files list to return

        files_pulled = []

        # connection did not work

        if self.ftps == None : return files_pulled

        # loop on all directories where there are pulls to do

        for lst in self.source.pulls :

            self.destDir = lst[0]
            self.pulllst = lst[1:]

            pdir = self.dirPattern(self.destDir)
            if pdir != '' : self.destDir = pdir
            self.destDir = self.destDir[1:]

            # cd to that directory

            self.logger.debug(" cd %s" % self.destDir)
            ok = self.cd(self.destDir)
            if not ok : continue

            # create ls filename for that directory

            pdir = lst[0]
            pdir = pdir.replace('${','')
            pdir = pdir.replace('}','')

            self.lspath = PXPaths.RXQ + self.source.name + '/.ls' + pdir.replace('/','_')

            # ls that directory

            ok = self.lsdir()
            if not ok : continue

            # if we are sleeping and we are here it is because
            # this pull is retrieving difference between directory content
            # so write the directory content without retrieving files

            if self.sleeping :
               ok = self.write_ls_file(self.lspath)
               continue

            # get the file list from the ls
            
            filelst = self.ls.keys()
            desclst = self.ls

            # if we dont delete, get file list from difference in ls

            if not self.source.delete :
               filelst,desclst = self.differ()

            if len(filelst) == 0 :
               ok = self.write_ls_file(self.lspath)
               continue

            # get remote file time for all files
            timelst,filelst,desclst = self.remote_time_sort(filelst,desclst)

            # retrieve the files
            files_notretrieved = []

            for idx,remote_file in enumerate(filelst) :

                timex.alarm(self.source.timeout_get)
                local_file = self.local_filename(remote_file,desclst,timelst)
                try :
                       ok = self.retrieve(remote_file, local_file)
                       if ok :
                               if self.source.delete : self.rm(remote_file)
                               files_pulled.append(local_file)

                               # setting access,modify time to remote time
                               ftime = time.mktime(timelst[remote_file])
                               os.utime(local_file,(ftime,ftime) )

                       else  :
                               files_notretrieved.extend(filelst[idx:])
                               self.logger.warning("problem when retrieving %s " % remote_file )
                               break

                       # if batch is reached stop there

                       if len(files_pulled) == self.source.batch :
                          if idx != len(filelst)-1 : files_notretrieved.extend(filelst[idx+1:])
                          break
                               
                       timex.cancel()

                except FtpTimeoutException :
                       timex.cancel()
                       files_notretrieved.extend(filelst[idx:])
                       self.logger.warning("FTPS timed out retrieving %s " % remote_file )
                       break

                except :
                       timex.cancel()
                       files_notretrieved.extend(filelst[idx:])
                       (type, value, tb) = sys.exc_info()
                       self.logger.error("Unable write remote file %s in local file %s" % (remote_file,local_file))
                       self.logger.error(" Type: %s, Value: %s" % (type ,value))
                       break

            # files not retrieved are removed from the file list
            # this allow pull to recover from error on next pass

            for f in files_notretrieved :
                del self.ls[f]

            # save ls file
            ok = self.write_ls_file(self.lspath)

            # if reached the batch limit : break here
            if len(files_pulled) == self.source.batch :
               self.logger.warning("break retrieving... batch reached")
               break

            # if we had a problem break here
            if len(files_notretrieved) > 0 :
               self.logger.warning("break retrieving... because of error")
               break

        return files_pulled

    # parse a file containing an ls and return the file entries

    def load_ls_file(self,path):

        self.lsold = {}

        if not os.path.isfile(path) : return True

        try : 
                # open/read..
                file=open(path,'rb')
                lines=file.readlines()
                file.close()

                # get filenames
                for line in lines :
                    parts = line.split()
                    fil   = parts[-1]
                    self.lsold[fil] = line

                return True

        except:
                self.logger.error("Unable to parse files from %s" % path )

        return False


    # create local filename

    def local_filename(self,filename,desclst,timelst):

        # create local filename with date/time on host... YYYYMMDDHHMM_filename

        if self.source.pull_prefix == 'HDATETIME' :

           ftime       = timelst[filename]
           datetimestr = time.strftime("%Y%m%d%H%M",ftime)

           local_file = PXPaths.RXQ + self.source.name + '/' + datetimestr + '_' + filename
           return local_file

        # create local filename with config defined prefix ... prefix_filename

        if self.source.pull_prefix != '' :
           local_file = PXPaths.RXQ + self.source.name + '/' + self.source.prefix + '_' + filename
           return local_file

        # create local filename with same name as remote file (default)

        local_file = PXPaths.RXQ + self.source.name + '/' + filename

        return local_file


    # ls line stripper
    # MG  this was realy CANNED for NESDIS
    #

    def ls_line_stripper(self,iline):
        oline  = iline
        oline  = oline.strip()
        oline  = oline.replace('\t',' ')
        opart1 = oline.split(' ')
        opart2 = []

        for p in opart1 :
            if p == ''  : continue
            opart2.append(p)

        fil  = opart2[-3]
        desc = opart2[0] + ' ' + ' '.join(opart2[-7:-2]) + '\n'

        return fil,desc


    # replace a matching pattern by its value in the directory name

    def matchPattern(self,keywd,defval) :
        """
        Matching keyword with different patterns
        """
        if keywd[:6] == "{YYYY}"         : 
                                           return   time.strftime("%Y", time.gmtime()) + keywd[6:]

        if keywd[:9] == "{YYYY-1D}"      : 
                                           epoch  = time.mktime(time.gmtime()) - 24*60*60
                                           return   time.strftime("%Y", time.localtime(epoch) ) + keywd[9:]

        if keywd[:4] == "{MM}"           : 
                                           return   time.strftime("%m", time.gmtime()) + keywd[4:]

        if keywd[:7] == "{MM-1D}"        : 
                                           epoch  = time.mktime(time.gmtime()) - 24*60*60
                                           return   time.strftime("%m", time.localtime(epoch) ) + keywd[7:]

        if keywd[:5] == "{JJJ}"          : 
                                           return   time.strftime("%j", time.gmtime()) + keywd[5:]

        if keywd[:8] == "{JJJ-1D}"       : 
                                           epoch  = time.mktime(time.gmtime()) - 24*60*60
                                           return   time.strftime("%j", time.localtime(epoch) ) + keywd[8:]

        if keywd[:10] == "{YYYYMMDD}"    : 
                                           return   time.strftime("%Y%m%d", time.gmtime()) + keywd[10:]

        if keywd[:13] == "{YYYYMMDD-1D}" :
                                           epoch  = time.mktime(time.gmtime()) - 24*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch) ) + keywd[13:]

        if keywd[:13] == "{YYYYMMDD-2D}" :
                                           epoch  = time.mktime(time.gmtime()) - 48*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch) ) + keywd[13:]

        if keywd[:13] == "{YYYYMMDD-3D}" :
                                           epoch  = time.mktime(time.gmtime()) - 72*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch) ) + keywd[13:]

        if keywd[:13] == "{YYYYMMDD-4D}" :
                                           epoch  = time.mktime(time.gmtime()) - 96*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch) ) + keywd[13:]

        if keywd[:13] == "{YYYYMMDD-5D}" : 
                                           epoch  = time.mktime(time.gmtime()) - 120*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch) ) + keywd[13:]

        return defval


    # get remote file time

    def remote_file_time(self,filename,desc):

        ftime = time.localtime()

        try :
              line  = desc[filename]
              line  = line.strip()
              parts = line.split()

              datestr=' '.join(parts[-4:-1])

              fmt4 = "%b"
              fmt3 = "%d"
              fmt2 = "%Y"

              if len(parts[-2]) == 5 :
                 fmt2 = "%H:%M %Y"
                 Y = time.strftime("%Y",time.gmtime())
                 datestr = datestr + ' ' + Y

              if parts[-3][0].isalpha() : fmt3 = "%b"

              if parts[-4][0].isdigit() : fmt4 = "%d"

              format = fmt4 + " " + fmt3 + " " + fmt2
              ftime = time.strptime(datestr,format)

        except : pass

        return ftime

    # remote time sort of file to pull

    def remote_time_sort(self,ifilelst,idesclst):

        timelst = [ self.remote_file_time(rfile,idesclst) for idx,rfile in enumerate(ifilelst) ]

        templst = [ (time.mktime(timelst[idx]),timelst[idx],rfile,idesclst[rfile]) for idx,rfile in enumerate(ifilelst) ]
        templst.sort()

        filelst = []
        desclst = {}
        timelst = {}

        for tup in templst :
            epoch, rtime, rfile, rdesc = tup
            filelst.append(rfile)
            desclst[rfile] = rdesc
            timelst[rfile] = rtime

        return timelst,filelst,desclst

    # retrieve a file

    def retrieve(self, remote_file, local_file):

        try    :
                 self.fget( remote_file, local_file) 
                 return True

        except :
                 os.unlink(local_file)
                 (type, value, tb) = sys.exc_info()
                 self.logger.error("Unable write remote file %s in local file %s. Type: %s, Value: %s" % \
                                  (remote_file,local_file,type,value))

        return False

    # some systems do not permit deletion... so pass exception on that

    def rm(self, path):
        try    :
                 self.delete(path)
        except :
                 (type, value, tb) = sys.exc_info()
                 self.logger.warning("Could not delete %s" % path )
                 self.logger.warning("Type: %s, Value: %s" % (type ,value))



    def write_ls_file(self,path):

        filelst = self.ls.keys()
        desclst = self.ls
        filelst.sort()

        try : 
                # open/write..
                file=open(path,'wb')

                for f in filelst :
                    file.write(desclst[f])

                file.close()

                return True

        except:
                self.logger.error("Unable to write ls to file %s" % path )

        return False

    # ###################################################################
    # MG 20120327
    # From the directories and get options specified create request files
    # ###################################################################

    def get_request(self):

        # if pull is sleeping and we delete files... nothing to do
        # if we don't delete files, we will keep the directory state

        if self.sleeping : return

        # log that we are waking up

        self.logger.info("pull %s is waking up" % self.source.name )

        # getting our alarm ready
 
        timex = AlarmFTP('FTP timeout')

        # files list to return

        files_pulled = []

        # connection did not work

        if self.ftps == None : return files_pulled

        # loop on all directories where there are pulls to do

        for lst in self.source.pulls :

            self.destDir = lst[0]
            self.pulllst = lst[1:]

            pdir = self.dirPattern(self.destDir)
            if pdir != '' : self.destDir = pdir
            self.destDir = self.destDir[1:]

            # cd to that directory

            self.logger.debug(" cd %s" % self.destDir)
            ok = self.cd(self.destDir)
            if not ok : continue

            # create ls filename for that directory

            pdir = lst[0]
            pdir = pdir.replace('${','')
            pdir = pdir.replace('}','')
            pdir = pdir.replace('/','_')

            self.lspath = PXPaths.RXQ + self.source.name + '/.ls' + pdir

            # ls that directory

            ok = self.lsdir()
            if not ok : continue

            # if we are sleeping and we are here it is because
            # this pull is retrieving difference between directory content
            # so write the directory content without retrieving files

            if self.sleeping :
               ok = self.write_ls_file(self.lspath)
               continue

            # get the file list from the ls
            
            filelst = self.ls.keys()
            desclst = self.ls

            # if we dont delete, get file list from difference in ls

            if not self.source.delete :
               filelst,desclst = self.differ()

            if len(filelst) == 0 :
               ok = self.write_ls_file(self.lspath)
               continue

            # get remote file time for all files
            timelst,filelst,desclst = self.remote_time_sort(filelst,desclst)

            # for all files to retrieve make a request
            files_notretrieved = []

            for idx,remote_file in enumerate(filelst) :

                local_file = self.local_filename(remote_file,desclst,timelst)

                try :
                      rpath = PXPaths.RXQ + self.source.name 
                      rpath = rpath + '/request_' + pdir + '_' + remote_file

                      base_local_file = os.path.basename(local_file)

                      f = open(rpath, 'w')
                      f.write("directory %s\n" % self.destDir )
                      if base_local_file == remote_file :
                         f.write("get %s\n" % remote_file)
                      else :
                         f.write("get %s %s\n" % (remote_file,base_local_file))
                      f.close()

                      files_pulled.append(rpath)

                      # if batch is reached stop there

                      if len(files_pulled) == self.source.batch :
                         if idx != len(filelst)-1 : files_notretrieved.extend(filelst[idx+1:])
                         break
                               
                except :
                       files_notretrieved.extend(filelst[idx:])
                       (type, value, tb) = sys.exc_info()
                       self.logger.error("Unable write request for file %s in local file %s" % (remote_file,local_file))
                       self.logger.error(" Type: %s, Value: %s" % (type ,value))
                       break

            # files not retrieved are removed from the file list
            # this allow pull to recover from error on next pass

            for f in files_notretrieved :
                del self.ls[f]

            # save ls file
            ok = self.write_ls_file(self.lspath)

            # if reached the batch limit : break here
            if len(files_pulled) == self.source.batch :
               self.logger.warning("break retrieving... batch reached")
               break

            # if we had a problem break here
            if len(files_notretrieved) > 0 :
               self.logger.warning("break retrieving... because of error")
               break

        return files_pulled



    # ###################################################################
    # MG 20120327
    # From request files created  get the files as described 
    # ###################################################################

    # pulling files and returning the list

    def get_file_from_request(self,ipath):

        # if pull is sleeping and we delete files... nothing to do
        # if we don't delete files, we will keep the directory state

        if self.sleeping : return

        # connection did not work

        if self.ftps == None : return None

        # log that we are waking up

        self.logger.info("request is %s" % os.path.basename(ipath) )

        # get request info

        try :
               f = open(ipath, 'r')
               data = f.read()
               f.close()
               data = data.split('\n')
      
               # line 0  =   directory  value
      
               lst = data[0].split(' ')
               option = lst[0]
               if option != "directory" :
                  self.logger.error("Unable to parse option directory in request file %s" % ipath )
                  return None
               self.destDir = lst[1]
      
               # line 1  =   get remote_file local_file
      
               lst = data[1].split(' ')
               option = lst[0]
               if option != "get" :
                  self.logger.error("Unable to parse option get in request file %s" % ipath )
                  return None
               remote_file  = lst[1]
               lfile        = lst[1]
               if len(lst) == 3 : lfile = lst[2]
      
               local_file = PXPaths.RXQ + self.source.name + '/' + lfile

               if remote_file == lfile :
                      self.logger.info("remote file = %s" % remote_file )
               else :
                      self.logger.info("remote file = %s (local = %s)" % (remote_file,lfile) )

        except :
               self.logger.error("Problem with request for file %s" % ipath )
               return None

        # getting our alarm ready
 
        timex = AlarmFTP('FTP timeout')

        # cd to that directory

        self.logger.debug(" cd %s" % self.destDir)
        ok = self.cd(self.destDir)
        if not ok : 
           self.logger.error("Unable to cd to directory %s" % self.destDir )
           return None

        # get the file

        timex.alarm(self.source.timeout_get)
        try :
               ok = self.retrieve(remote_file, local_file)
               if ok :
                      if self.source.delete : self.rm(remote_file)
               timex.cancel()

        except FtpTimeoutException :
               timex.cancel()
               self.logger.warning("FTP timed out retrieving %s " % remote_file )
               return None

        except :
               timex.cancel()
               (type, value, tb) = sys.exc_info()
               self.logger.error("Unable write remote file %s in local file %s" % (remote_file,local_file))
               self.logger.error(" Type: %s, Value: %s" % (type ,value))
               return None

        return local_file
