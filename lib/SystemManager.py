"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: SystemManager.py
#
# Author: Daniel Lemay
#
# Date: 2005-06-14
#
# Description: General System Manager. Regroup functionalities common to all managers.
#              PXManager and PDSManager will implement features particular to them.
#
#############################################################################################

"""
import os, os.path, sys, shutil, commands, re, pickle, time, logging

class SystemManagerException(Exception):
    pass

class SystemManager:

    def __init__(self):
        self.logger = None                     # self.setLogger will be used by the application using a Manager 
        self.rxNames = []                      # Names are based on filenames found in RX_CONF
        self.txNames = []                      # Names are based on filenames found in TX_CONF
        self.shouldRunRxNames = []             # Names are based on filenames found in RX_CONF and the presence of a .lock
        self.shouldRunTxNames = []             # Names are based on filenames found in TX_CONF and the presence of a .lock
        self.runningRxNames = []               # We only keep the Rx for which we can find a PID
        self.runningTxNames = []               # We only keep the Tx for which we can find a PID 
        self.rxPaths = []                      # Receivers (input directories in PDS parlance) paths
        self.txPaths = []                      # Transmitters (clients in PDS parlance, senders in PX parlance) paths

    def setLogger(self, logger):
        self.logger = logger

    ##########################################################################################################
    # Should be running Names (sources and clients): 
    ##########################################################################################################
    def getShouldRunRxNames(self):
        return self.shouldRunRxNames

    def setShouldRunRxNames(self):
        """
        Set a list of receivers' name. We choose receivers that have a .conf file in RX_CONF
        and we verify that these receivers have a .lock associated to them.
        """
        raise SystemManagerException('Abstract method: not implemented in SystemManager Class')

    def getShouldRunTxNames(self):
        return self.shouldRunTxNames

    def setShouldRunTxNames(self):
        """
        Set a list of senders' name. We choose senders that have a .conf file in TX_CONF 
        and we verify that these senders have a .lock associated to them.
        """
        raise SystemManagerException('Abstract method: not implemented in SystemManager Class')

    ##########################################################################################################
    # Running Names (sources and clients): 
    ##########################################################################################################
    def getRunningRxNames(self):
        return self.runningRxNames

    def setRunningRxNames(self):
        """
        Set a list of receivers' name. We choose receivers that have a .conf file in RX_CONF
        and we verify that these receivers have a .lock and a process associated to them.
        """
        raise SystemManagerException('Abstract method: not implemented in SystemManager Class')

    def getRunningTxNames(self):
        return self.runningTxNames

    def setRunningTxNames(self):
        """
        Set a list of senders' name. We choose senders that have a .conf file in TX_CONF 
        and we verify that these senders have a .lock and a process associated to them.
        """
        raise SystemManagerException('Abstract method: not implemented in SystemManager Class')

    ##########################################################################################################
    # Names (sources and clients)
    ##########################################################################################################
    def getRxNames(self):
        return self.rxNames

    def setRxNames(self):
        raise SystemManagerException('Abstract method: not implemented in SystemManager Class')
                
    def getTxNames(self):
        return self.txNames

    def setTxNames(self):
        raise SystemManagerException('Abstract method: not implemented in SystemManager Class')

    def getRxPaths(self):
        return self.rxPaths

    def setRxPaths(self):
        raise SystemManagerException('Abstract method: not implemented in SystemManager Class')
                
    def getTxPaths(self):
        return self.txPaths

    def setTxPaths(self):
        raise SystemManagerException('Abstract method: not implemented in SystemManager Class')

    ##########################################################################################################
    def copyRemoteDir(self, user, machine, sourceDir, targetDir):
        source = user + "@" + machine + ":" + sourceDir + '*'
        target = targetDir

        self.createDir(targetDir)

        command = "scp " + source + " " + target

        (status, output) = commands.getstatusoutput(command)

        if output == "scp: /apps/px/switchover/*: No such file or directory":
            # No files in the directory
            pass    
            
    def copyFiles(self, sourceDir, targetDir, copyLog=None):
        """
        Copy all files (no directories) under the given sourceDir to the targetDir on the
        same machine. copyLog is the absolute name of a log file which contains the absolute
        name of all the copied files.
        """
        if os.path.normpath(sourceDir) == os.path.normpath(targetDir):
            if self.logger is None:
                print "Source and target are identical. We do nothing!"
            else:
                self.logger.error("Source and target are identical. We do nothing!")
            return

        if os.path.isdir(sourceDir):
            files = os.listdir(sourceDir)
        else:
            if self.logger is None:
                print "This is not a directory (%s)" % (sourceDir)
            else:
                self.logger.error("This is not a directory (%s)" % (sourceDir))
            return

        if not os.path.isdir(targetDir):
            try:
                self.createDir(targetDir)
            except: 
                if self.logger is None:
                    print "Unable to create directory (%s)" % (targetDir)
                else:
                    (type, value, tb) = sys.exc_info()
                    self.logger.error("Unable to create directory (%s)" % (targetDir))
                    self.logger.error("Type: %s, Value: %s" % (type, value))
                return

        if copyLog is not None:
            self.createDir(os.path.dirname(copyLog))
            cpLog = open(copyLog, 'w')

        for file in files:
            # We are not interessed in directory, file beginning with a dot or ending in .tmp
            if os.path.isdir(sourceDir + file) or file[0] == '.' or file[-4:] == ".tmp":
                continue
            try:
                # FIXME
                # Should create a file with all the files that are copied
                shutil.copyfile(sourceDir + file, targetDir + file)
                os.chmod(targetDir + file, 0644)

                if copyLog is not None:
                    cpLog.write(targetDir + file + '\n')
            except:
                # FIXME: Find the correct exceptions that can arrive here
                (type, value, tb) = sys.exc_info()
                if self.logger is None:
                    print "Problem while shutil.copyfile(%s, %s)" % (sourceDir + file, targetDir + file)
                else:
                    self.logger.error("Problem with shutil.copyfile(%s, %s) => Type: %s, Value: %s" % 
                                                     (sourceDir + file, targetDir + file, type, value))
                                                     
        if copyLog is not None:
            os.chmod(copyLog, 0644)
            cpLog.close()

    def createDir(self, dir):
        oldUmask = os.umask(0022)
        if not os.path.isdir(dir):
            os.makedirs(dir, 0755)
        os.umask(oldUmask)

    def changePrefixPath(self, path):
        if path[0:7] == '/apps2/':
            path = '/apps/' + path[7:]
            print path
            return path
        else:
            if self.logger is None:
                print "This directory (%s) doesn't begin  by /apps2/" % (path)
                return None
            else:
                self.logger.warning("This directory (%s) doesn't begin  by /apps2/" % (path))
                return None

    def deleteSwitchoverFiles(self, copyLog, deleteLog=None):
        """
        Delete all files listed in the copyLog
        """
        try:
            cpLog = open(copyLog, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            if deleteLog is None:
                print "Problem opening %s , Type: %s Value: %s" % (cpLog, type, value)
            else:
               deleteLog.error("Problem opening %s , Type: %s Value: %s" % (cpLog, type, value))

        filesToDelete = cpLog.readlines()
        cpLog.close()

        for file in filesToDelete:
            file = file.strip()
            try:
                os.unlink(file)
                if deleteLog is not None:
                    deleteLog.info("%s has been deleted" % file)
            except:
                (type, value, tb) = sys.exc_info()
                if deleteLog is None:
                    print "Problem deleting %s , Type: %s Value: %s" % (file, type, value)
                else:
                    deleteLog.error("Problem deleting %s , Type: %s Value: %s" % (file, type, value))
                    
if __name__ == '__main__':
  
    manager = SystemManager()
    #print manager.getRxNames()
    #print manager.getTxNames()
    #manager.createDir('/apps/px/tutu/')
    #manager.createDir('/apps/px/tata/')
    manager.changePrefixPath('/apps/px/toto/')
    manager.changePrefixPath('/apps/px/tutu/')
    manager.copyFiles('/apps/px/toto/', '/apps/px/tarteau/', '/apps/px/tarteau/copy.log')
    #manager.deleteFiles('/apps/px/tarteau/copy.log', '/apps/px/tarteau/delete.log')

