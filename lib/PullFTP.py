"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PullFTP.py
#
# Authors: Michel Grenier 
#
# Description: Pull capabilities ... the source defines the protocol/host/user/password/port
#              followed by the directories and file pattern to pull... The process flow is roughly
#              1- open connection
#              2- get the files :
#                               for each directory get the ls -al in RXQ/name/.ls_"directory_name".new
#                               if retreived files are not deleted 
#                                  files we may retreive are the diff with last ls : .ls_"directory_name"
#                               if retreived files are deleted 
#                                  consider all files in ls
#                               try matching files from ls and the regex defined in source with get option
#                               try a diff with another ls see if some of the files are currently modified
#                                   if some are modified put them in the "not retrieve list"
#                               retrieve the resulting file matches if any... file with problems are put
#                                   in the "not retrieve list"
#                               files in the "not retrieve list" are removed from the kept ls...
#              3- close connection
#
# Note: PullFTP is inserted in the Ingestor.py code as part of single-file and bulletin-file procession.
#       The only difference is that the source type is checked for pull-file or pull-bulletin to activate
#       the pull facility See Ingestor.py
#
# Note: self.source.pull contains a list : the DIRECTORY, followed by the get patterns...
#       ex.:   self.source.pull = [ '/data/dir1/toto', 'titi*.gif', 'toto*.jpg' ] 
#
#############################################################################################

"""
import commands, os, os.path, re, stat, string, sys, time
import PXPaths, signal, socket
from AlarmFTP  import AlarmFTP
from AlarmFTP  import FtpTimeoutException
from URLParser import URLParser
from Logger import Logger
import ftplib

PXPaths.normalPaths()              # Access to PX paths

class PullFTP(object):

    def __init__(self, source, logger=None) :

        # General Attributes

        self.source      = source 

        self.connected   = False 
        self.ftp         = None
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

        if self.source.protocol == 'ftp':
            self.ftp = self.ftpConnect()


    # callback to strip and save the output from ls of directory

    def callback_line(self,block):

        # strip ls line to its most important info
        fil,desc = self.ls_line_stripper(block)

        # keep only if we are interested in that file

        for filepattern in self.pulllst :
            if re.compile(filepattern).match(fil):
               self.ls[fil] = desc


    # going to a certain directory

    def cd(self, path):

        timex = AlarmFTP('FTP change working directory timeout')

        try   :
                  # gives 10 seconds to get there
                  timex.alarm(10)
                  self.logger.warning("self.original directory %s" % self.originalDir )
                  self.ftp.cwd(self.originalDir)
                  self.logger.warning("relative path %s" % path )
                  self.ftp.cwd(path)
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

        if self.ftp == None : return

        timex = AlarmFTP('FTP connection close timeout')

        try    :
                  # gives 10 seconds to close the connection
                  timex.alarm(10)

                  self.ftp.quit()

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
        for  ddword in DD :
             if ddword == "" : continue

             nddword = ""
             DW = ddword.split("$")
             for dwword in DW :
                 nddword += self.matchPattern(dwword,dwword)

             ndestDir += "/" + nddword 

        return ndestDir


    # do an ls in the current directory, write in file path

    def do_ls(self):

        self.ls = {}

        timex = AlarmFTP('FTP retrieving list')
        timex.alarm(self.source.timeout_get)

        try : 
                 ls=self.ftp.retrlines('LIST',self.callback_line )
                 timex.cancel()
                 return True

        except FtpTimeoutException :
                 timex.cancel()
                 self.logger.warning("FTP doing ls timed out after %s seconds..." % self.source.timeout_get )

        except :
                 timex.cancel()
                 (type, value, tb) = sys.exc_info()
                 self.logger.error("Unable to list directory %s on %s (user:%s). Type: %s, Value: %s" % \
                                  (self.destDir,self.source.host, self.source.user, type ,value))

        return False


    # open connection... 

    def ftpConnect(self):

        timex = AlarmFTP('FTP connection timeout')

        try:
            # gives 30 seconds to open the connection
            timex.alarm(30)

            ftp = ftplib.FTP(self.source.host, self.source.user, self.source.passwd)
            if self.source.ftp_mode == 'active':
                ftp.set_pasv(False)
            else:
                ftp.set_pasv(True)
            self.originalDir = ftp.pwd()

            timex.cancel()

            self.connected = True

            return ftp

        except FtpTimeoutException :
            timex.cancel()
            self.logger.warning("FTP connection timed out after 30 seconds..." )

        except:
            timex.cancel()
            (type, value, tb) = sys.exc_info()
            self.logger.error("Unable to connect to %s (user:%s). Type: %s, Value: %s" % (self.source.host, self.source.user, type ,value))


    # pulling files and returning the list

    def get(self):

        self.logger.info("pull %s is waking up" % self.source.name )

        # getting our alarm ready
 
        timex = AlarmFTP('FTP timeout')

        # files list to return

        files_pulled = []

        # connection did not work

        if self.ftp == None : return files_pulled

        # loop on all directories where there are pulls to do

        for lst in self.source.pulls :

            self.destDir = lst[0]
            self.pulllst = lst[1:]

            pdir = self.dirPattern(self.destDir)
            if pdir != '' : self.destDir = pdir
            self.destDir = self.destDir[1:]

            # cd to that directory

            ok = self.cd(self.destDir)
            if not ok : continue

            # create ls filename for that directory

            pdir = lst[0]
            pdir = pdir.replace('${','')
            pdir = pdir.replace('}','')

            self.lspath = PXPaths.RXQ + self.source.name + '/.ls' + pdir.replace('/','_')

            # ls that directory

            ok = self.do_ls()
            if not ok : continue

            # get the file list from the ls
            
            filelst = self.ls.keys()
            desclst = self.ls
            filelst.sort()

            # if we dont delete, get file list from difference in ls

            if not self.source.delete :
               filelst,desclst = self.differ()

            if len(filelst) == 0 :
               ok = self.write_ls_file(self.lspath)
               continue

            # retrieve the files

            files_notretrieved = []

            for remote_file in filelst :

                timex.alarm(self.source.timeout_get)
                local_file = self.local_filename(remote_file,desclst)
                try :
                       ok = self.retrieve(remote_file, local_file)
                       if ok :
                               if self.source.delete : self.rm(remote_file)
                               files_pulled.append(local_file)
                       else  :
                               files_notretrieved.append(remote_file)
                               self.logger.warning("problem when retrieving %s " % remote_file )
                               
                       timex.cancel()

                except FtpTimeoutException :
                       timex.cancel()
                       files_notretrieved.append(remote_file)
                       self.logger.warning("FTP timed out retrieving %s " % remote_file )

                except :
                       timex.cancel()
                       files_notretrieved.append(remote_file)
                       (type, value, tb) = sys.exc_info()
                       self.logger.error("Unable write remote file %s in local file %s. Type: %s, Value: %s" % \
                                        (remote_file,local_file,type,value))

            # files not retrieved are removed from the file list
            # this allow pull to recover from error on next pass

            for f in files_notretrieved :
                del self.ls[f]

            # save ls file
            ok = self.write_ls_file(self.lspath)

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

    def local_filename(self,filename,desc):

        # create local filename with date/time on host... YYYYMMDDHHMM_filename

        if self.source.pull_prefix == 'HDATETIME' :
           line = desc[filename]
           line  = line.strip()
           parts = line.split()

           datestr=' '.join(parts[-4:-1])
           if len(parts[-2]) == 5 and parts[-2][2] == ':' :
              Y = time.strftime("%Y",time.gmtime())
              datestr = Y + ' ' + datestr
              ftime = time.strptime(datestr,"%Y %b %d %H:%M")
           else :
              ftime = time.strptime(datestr,"%b %d %Y")

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

    def ls_line_stripper(self,iline):
        oline  = iline
        oline  = oline.strip()
        oline  = oline.replace('\t',' ')
        opart1 = oline.split(' ')
        opart2 = []

        for p in opart1 :
            if p == ''  : continue
            opart2.append(p)

        fil  = opart2[-1]
        desc = opart2[0] + ' ' + ' '.join(opart2[-5:]) + '\n'

        return fil,desc


    # replace a matching pattern by its value in the directory name

    def matchPattern(self,keywd,defval) :
        """
        Matching keyword with different patterns
        """

        if keywd[:10] == "{YYYYMMDD}"    : 
                                           return   time.strftime("%Y%m%d", time.gmtime())

        if keywd[:13] == "{YYYYMMDD-1D}" :
                                           epoch  = time.mktime(time.gmtime()) - 24*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch)  )

        if keywd[:13] == "{YYYYMMDD-2D}" :
                                           epoch  = time.mktime(time.gmtime()) - 48*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch)  )

        if keywd[:13] == "{YYYYMMDD-3D}" :
                                           epoch  = time.mktime(time.gmtime()) - 72*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch)  )

        if keywd[:13] == "{YYYYMMDD-4D}" :
                                           epoch  = time.mktime(time.gmtime()) - 96*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch)  )

        if keywd[:13] == "{YYYYMMDD-5D}" : 
                                           epoch  = time.mktime(time.gmtime()) - 120*60*60
                                           return   time.strftime("%Y%m%d", time.localtime(epoch)  )

        return defval

    # retrieve a file

    def retrieve(self, remote_file, local_file):

        try    :
                 file=open(local_file,'wb')
                 self.ftp.retrbinary('RETR ' + remote_file, file.write )
                 file.close()
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
                 self.ftp.delete(path)
        except :
                 (type, value, tb) = sys.exc_info()
                 self.logger.warning("Could not delete %s" % path )
                 self.logger.warning("Type: %s, Value: %s" % (type ,value))


    # write ls file

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
