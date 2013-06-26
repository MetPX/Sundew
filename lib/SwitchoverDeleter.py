#!/usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: SwitchoverDeleter.py
#
# Author: Daniel Lemay
#
# Date: 2005-06-27
#
# Description: First here is a description of a DRBD pair:
#              
#   machine1:/apps/                          machine2:/apps/
#            /backupMachine2/                         /backupMachine1/
#
#   The first thing to know when using this program is the name of the mount point of the 
#   drbd partition. The name 'backupMachine?' is only an example.
#
#   When one member of a DRBD pair crash (machine1 for example), the program SwitchoverCopier.py will be used
#   to copy data from machine2:/backupMachine1/ to machine2:/apps/. The data that will
#   be copied is coming from receivers and senders directories. The job of determining which
#   directories correspond to receivers and senders is done by an appropriate manager (PDS or PX).
# 
#   The files copied will be logged and these logs (one per directory, location: /apps/{px|pds}/switchover)
#   will be used (when the dead machine is revived, it will call SwitchoverDeleter.py)
#   to erase these files on machine1:/apps/
# 
#   Usage:
#
#   SwitchoverDeleter (-s|--system) {PDS | PX} -m MACHINE\n"
#
#############################################################################################
"""

from Logger import Logger
import os, pwd, sys, getopt, ftplib

def usage():
    print("\nUsage:\n")
    print("SwitchoverDeleter (-s|--system) {PDS | PX} -m MACHINE\n")
    print("-s, --system: PDS or PX\n")
    print("-m MACHINE where MACHINE is the name of the host where we find files containing")
    print("the name of the files to delete. (These files will be obtained by ftp)\n")

class SwitchoverDeleter:

    LOG_LEVEL = "INFO"                   # Logging level

    # Make sure that user pds run this program
    if not os.getuid() ==  pwd.getpwnam('pds')[2]:
        pdsUID = pwd.getpwnam("pds")[2]
        os.setuid(pdsUID)

    def __init__(self):

        self.getOptionsParser() 

        if SwitchoverDeleter.SYSTEM == 'PX': 
            from PXManager import PXManager
            manager = PXManager(None, '/apps/px/')
            LOG_NAME = manager.LOG + 'PX_SwitchoverDeleter.log'    # Log's name
            SwitchoverDeleter.SWITCH_DIR = '/apps/px/switchover/'

        elif SwitchoverDeleter.SYSTEM == 'PDS':
            from PDSManager import PDSManager
            manager = PDSManager(None, '/apps/pds/')
            LOG_NAME = manager.LOG + 'PDS_SwitchoverDeleter.log'   # Log's name
            SwitchoverDeleter.SWITCH_DIR = '/apps/pds/switchover/'

        self.logger = Logger(LOG_NAME, SwitchoverDeleter.LOG_LEVEL, "Deleter")
        self.logger = self.logger.getLogger()
        manager.setLogger(self.logger)

        self.logger.info("Beginning program SwitchoverDeleter")
        self.manager = manager

    def getDestDir(self, sourceDir, replacement):
        parts = sourceDir.split('/', 2)
        parts[1] = replacement

        return '/'.join(parts)

    def ftpDelete(self):
         
        filenames = []
        localSwitchoverDir = SwitchoverDeleter.SWITCH_DIR[:-1] + "_from_" + SwitchoverDeleter.MACHINE + '/'
        self.manager.createDir(localSwitchoverDir)
         
        # Will be called on each line of retrlines
        def extractFilename(line):
            parts = line.split()
            if len(parts) <  8:
                pass
            else:
                filenames.append(parts[7])

        try:
            ftp = ftplib.FTP(SwitchoverDeleter.MACHINE)
            ftp.login('user', 'password')
            ftp.cwd(SwitchoverDeleter.SWITCH_DIR)
            # Equivalent to ftp.dir()
            ftp.retrlines('LIST', extractFilename)
            for file in filenames:
                fd = open(localSwitchoverDir + file, 'w')
                ftp.retrbinary("RETR " + file, fd.write)
                ftp.delete(file)

            ftp.quit()
        except:
            (type, value, tb) = sys.exc_info()
            self.logger.error("FTP Problem: Type: %s Value: %s" % (type, value))

        if os.path.isdir(localSwitchoverDir):
            files = os.listdir(localSwitchoverDir)

            for file in files:
                file = localSwitchoverDir + file
                # regular file
                if os.path.isfile(file):
                    self.manager.deleteSwitchoverFiles(file, self.logger)
                    try:
                        os.unlink(file)
                        self.logger.info("Container  %s has been deleted" % file)
                    except:
                        (type, value, tb) = sys.exc_info()
                        self.logger.error("Problem deleting %s (container file), Type: %s Value: %s" % (file, type, value))

    def delete(self):
        
        localSwitchoverDir = SwitchoverDeleter.SWITCH_DIR[:-1] + "_from_" + SwitchoverDeleter.MACHINE + '/'
        # copy remote files (these files contain the filenames of the files copied by SwitchoverCopier) to
        # loca directory.
        self.manager.copyRemoteDir('pds', SwitchoverDeleter.MACHINE, SwitchoverDeleter.SWITCH_DIR, localSwitchoverDir)
        
        if os.path.isdir(localSwitchoverDir):
            files = os.listdir(localSwitchoverDir)

            for file in files:
                file = localSwitchoverDir + file
                # regular file
                if os.path.isfile(file):
                    self.manager.deleteSwitchoverFiles(file, self.logger)

                    try:
                        os.unlink(file)
                        self.logger.info("Container  %s has been deleted" % file)
                    except:
                        (type, value, tb) = sys.exc_info()
                        self.logger.error("Problem deleting %s (container file), Type: %s Value: %s" % (file, type, value))

    def getOptionsParser(self):
        
        system = False
        machine = False
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'm:s:h', ['help', 'system='])
            #print opts
            #print args
        except getopt.GetoptError:
            # print help information and exit:
            usage()
            sys.exit(2)

        for option, value in opts:
            if option in ('-h', '--help'):
                usage()
                sys.exit()
            if option in ('-s', '--system'):
                system = True
                if value in ['PDS', 'PX']:
                    SwitchoverDeleter.SYSTEM = value
                else:
                    usage()
                    sys.exit(2)
            if option == '-m':
                machine = True
                SwitchoverDeleter.MACHINE = value

        # We must give a system
        if system is False or machine is False:  
            usage()
            sys.exit(2)

if __name__ == '__main__':

    deleter =  SwitchoverDeleter()
    #deleter.delete()
    deleter.ftpDelete()
    deleter.logger.info("Ending program SwitchoverDeleter")
