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
#                               retreive the resulting file matches if any
#              3- close connection
#
# Note: PullFTP is inserted in the Ingestor.py code as part of single-file and bulletin-file procession.
#       The only difference is that the source type is checked for pull-file or pull-bulletin to activate
#       the pull facility See Ingestor.py
#
#############################################################################################

"""
import commands, os, os.path, re, stat, sys, time
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
        self.diff        = '/usr/bin/diff'
        self.ftp         = None
        self.file        = None
        self.lastls      = ''
        self.newls       = ''
        self.originalDir = ''
        self.destDir     = ''

        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'rx_' + source.name + '.log', 'INFO', 'RX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger

        if self.source.protocol == 'ftp':
            self.ftp = self.ftpConnect()

    # callback to save the output from ls of directory

    def callback_line(self,block):
        self.file.write(block+'\n')

    # going to a certain directory

    def cd(self, path):

        timex = AlarmFTP('FTP change working directory timeout')

        try   :
                  # gives 10 seconds to get there
                  timex.alarm(10)
                  self.ftp.cwd(self.originalDir)
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

    # diff of 2 files containing "ls" response on a directory
    # return the newer or modified files only...

    def diff_ls(self, lastls, newls ):

        files  = []
        status = 0

        try : 
                # if lastls file does not exist... create an empty one
                if not os.path.isfile(lastls) :
                   file=open(lastls,'wb')
                   file.close()

                # proceed with the diff command

                s,o = commands.getstatusoutput( self.diff + ' ' + lastls + ' ' + newls )
                if os.WIFEXITED(s) :
                   status = (os.WEXITSTATUS(s) <= 1 )

                # 0 ok and no differences  return empty file list

                if status == 0 or len(o) == 0 :
                   return files

                # not 1 than an error when executing the diff command

                if status != 1 : 
                   self.logger.warning("diff resulted in an error")
                   return files

                # getting the filename for the modified files

                if status == 1 : 
                   lines=o.split('\n')

                   for line in lines :
                       parts = line.split()
                       if parts[0] == '>' : 
                          files.append(parts[-1])

                   return files

        except:
                self.logger.error("Unable to diff directory listings")

        return files

    # do an ls in the current directory, write in file path

    def do_ls(self,path):

        timex = AlarmFTP('FTP retrieving list')
        timex.alarm(self.source.timeout_get)

        try : 
                 self.file=open(path,'wb')
                 ls=self.ftp.retrlines('LIST',self.callback_line )
                 self.file.close()
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

    # parse a file containing an ls and return the file entries

    def file_ls(self,path):

        files  = []

        try : 
                # open/read..
                file=open(path,'wb')
                lines=file.readlines()
                file.close()

                # get filenames
                for line in lines :
                    parts = line.split()
                    files.append(parts[-1])

                return files

        except:
                self.logger.error("Unable to parse files from %s" % path )

        return files

    # pulling files and returning the list

    def get(self):

        # getting our alarm ready
 
        timex = AlarmFTP('FTP timeout')

        # files list to return

        files_pulled = []

        # connection did not work

        if self.ftp == None : return files_pulled

        # loop on all directories where there are pulls to do

        for lst in self.source.pulls :

            self.destDir = lst[0]

            # cd to that directory

            ok = self.cd(self.destDir)
            if not ok : continue

            # ls that directory

            self.lastls = PXPaths.RXQ + self.source.name + '/.ls' + self.destDir.replace('/','_')
            self.newls  = self.lastls + '.new'
            ok = self.do_ls(self.newls)
            if not ok : continue

            # get the file list from the ls
            
            filelst = []

            if self.source.delete :
                filelst = self.file_ls(self.newls)

            # or from a diff between the old and new ls

            else :
                filelst = self.diff_ls(self.lastls,self.newls)

            # keep for reference our last ls

            os.rename(self.newls,self.lastls)

            # check if files match file pattern defined in source

            flst = {}
            prim = filelst[0:]
            for pos, elem in enumerate(lst):
                if pos == 0 : continue
                sec = prim[0:]
                for indx, f in enumerate(prim) :
                    if re.compile(lst[pos]).match(f):
                       flst[f] = 0
                       sec.pop(indx)
                prim = sec

            files = flst.keys()

            if len(files) == 0 : return files_pulled

            # wait before retrieving...
            # this is just to make sure the file is completely arrived on remote server.

            if self.source.pull_wait > 0 :
               time.sleep(self.source.pull_wait)

            # retrieve the files

            for remote_file in files :
                timex.alarm(self.source.timeout_get)
                try :
                       local_file = PXPaths.RXQ + self.source.name + '/' + remote_file
                       ok = self.retrieve(remote_file, local_file)
                       if ok :
                               if self.source.delete : self.rm(remote_file)
                               files_pulled.append(local_file)
                       timex.cancel()

                except FtpTimeoutException :
                       timex.cancel()
                       self.logger.warning("FTP timed out retrieving %s " % remote_file )

                except :
                       timex.cancel()
                       (type, value, tb) = sys.exc_info()
                       self.logger.error("Unable write remote file %s in local file %s. Type: %s, Value: %s" % \
                                        (remote_file,local_filet, self.source.user, type ,value))


        return files_pulled

    # retrieve a file

    def retrieve(self, remote_file, local_file):

        try    :
                 file=open(local_file,'w')
                 self.ftp.retrbinary('RETR ' + remote_file, file.write )
                 file.close()
                 return True

        except :
                 timex.cancel()
                 (type, value, tb) = sys.exc_info()
                 self.logger.error("Unable write remote file %s in local file %s. Type: %s, Value: %s" % \
                                  (remote_file,local_filet, self.source.user, type ,value))

        return False

    # some systems do not permit deletion... so pass exception on that

    def rm(self, path):
        try    :
                 self.ftp.delete(path)
        except :
                 (type, value, tb) = sys.exc_info()
                 self.logger.warning("Could not delete %s" % path )
                 self.logger.warning(" Type: %s, Value: %s" % (type ,value))
