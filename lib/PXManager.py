
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PXManager.py
#
# Author: Daniel Lemay
#
# Date: 2005-06-14
#
# Description:
#
# Revision History: 
#   2005-12-09  NSD         Created collection db dir.
#
#############################################################################################

"""
import os, os.path, sys, commands, re, pickle, time, logging, fnmatch
import SystemManager, PXPaths
from SystemManager import SystemManager

class PXManager(SystemManager):

    def __init__(self, drbdPath=False):

        """
        drbdPath: drbd path or False, drbd path if we use other root than /apps
        """

        if drbdPath:
            PXPaths.drbdPaths(drbdPath) 
        else:
            PXPaths.normalPaths() 

        SystemManager.__init__(self)
        self.LOG = PXPaths.LOG          # Will be used by DirCopier

    def afterInit(self):
        if not os.path.isdir(PXPaths.ROOT):
            self.logger.error("This directory: %s does not exist!" % (PXPaths.ROOT))
            sys.exit(15)

        self.setRxNames()           
        self.setTxNames()
        self.setRxPaths()
        self.setTxPaths()
        #self.rxPaths = ['/apps/px/toto/', '/apps/px/titi/', '/apps/px/tata/']

    def initPXPaths(self):
        # ROOT, BIN, LIB, LOG, ETC, RXQ, TXQ, DB, RX_CONF, TX_CONF, COLLECTION_DB, COLLECTION_CONTROL
        self.createDir(PXPaths.BIN)
        self.createDir(PXPaths.LIB)
        self.createDir(PXPaths.LOG)
        self.createDir(PXPaths.RX_CONF)
        self.createDir(PXPaths.TX_CONF)
        self.createDir(PXPaths.RXQ)
        self.createDir(PXPaths.TXQ)
        self.createDir(PXPaths.DB)
        self.createDir(PXPaths.COLLECTION_DB)
        self.createDir(PXPaths.COLLECTION_CONTROL)

    def initNames(self):
        if not os.path.isdir(PXPaths.ROOT):
            self.logger.error("This directory: %s does not exist!" % (PXPaths.ROOT))
            sys.exit(15)

        self.setRxNames()           
        self.setTxNames()

    def initShouldRunNames(self):
        if not os.path.isdir(PXPaths.ROOT):
            self.logger.error("This directory: %s does not exist!" % (PXPaths.ROOT))
            sys.exit(15)

        self.setShouldRunRxNames()           
        self.setShouldRunTxNames()

    def initRunningNames(self):
        if not os.path.isdir(PXPaths.ROOT):
            self.logger.error("This directory: %s does not exist!" % (PXPaths.ROOT))
            sys.exit(15)

        self.setRunningRxNames()
        self.setRunningTxNames()

    def getNotRunningRxNames(self):
        return self.notRunningRxNames

    def getNotRunningTxNames(self):
        return self.notRunningTxNames
        
    ##########################################################################################################
    # Running Names (sources and clients):
    # 1) Have a .conf file in /apps/px/etc/[rt]x
    # 2) Have a lock file (.lock) in /apps/px/[rt]xq/NAME
    # 3) A ps confirm that the pid contained in the .lock file is running 
    ##########################################################################################################
    def setRunningRxNames(self):
        """
        Set a list of receivers' name. We choose receivers that have a .conf file in RX_CONF
        and we verify that these receivers have a .lock and a process associated to them.
        """
        runningRxNames = []
        notRunningRxNames = []
        shouldRunRxNames = self.getShouldRunRxNames()
        for name in shouldRunRxNames:
            try:
                pid = open(PXPaths.RXQ + name + '/' + '.lock', 'r').read()
                if not commands.getstatusoutput('ps -p ' + pid)[0]:
                    # Process is running
                    runningRxNames.append(name)
                else:
                    notRunningRxNames.append(name)
            except:
                #FIXME 
                pass

        self.runningRxNames = runningRxNames
        self.notRunningRxNames = notRunningRxNames
    
    def setRunningTxNames(self):
        """
        Set a list of senders' name. We choose senders that have a .conf file in TX_CONF 
        and we verify that these senders have a .lock and a process associated to them.
        """
        runningTxNames = []
        notRunningTxNames = []
        shouldRunTxNames = self.getShouldRunTxNames()
        for name in shouldRunTxNames:
            try:
                pid = open(PXPaths.TXQ + name + '/' + '.lock', 'r').read()
                if not commands.getstatusoutput('ps -p ' + pid)[0]:
                    # Process is running
                    runningTxNames.append(name)
                else:
                    notRunningTxNames.append(name)
            except:
                #FIXME 
                pass

        self.runningTxNames = runningTxNames
        self.notRunningTxNames = notRunningTxNames

    ##########################################################################################################
    # Should be running names (sources and clients):
    # 1) Have a .conf file in /apps/px/etc/[rt]x
    # 2) Have a lock file (.lock) in /apps/px/[rt]xq/NAME
    ##########################################################################################################
    def setShouldRunRxNames(self):
        """
        Set a list of receivers' name. We choose receivers that have a .conf file in RX_CONF
        and we verify that these receivers have a .lock  associated to them.
        """
        shouldRunRxNames = []
        rxNames =  self.getRxNames()
        for name in rxNames:
            if os.path.isfile(PXPaths.RXQ + name + '/' + '.lock'):
                shouldRunRxNames.append(name)
        self.shouldRunRxNames = shouldRunRxNames

    def setShouldRunTxNames(self):
        """
        Set a list of senders' name. We choose senders that have a .conf file in TX_CONF 
        and we verify that these senders have a .lock associated to them.
        """
        shouldRunTxNames = []
        txNames =  self.getTxNames()
        for name in txNames:
            if os.path.isfile(PXPaths.TXQ + name + '/' + '.lock'):
                shouldRunTxNames.append(name)
        self.shouldRunTxNames = shouldRunTxNames

    ##########################################################################################################
    # Names and paths (sources and clients):
    # 1) Have a .conf file in /apps/px/etc/[rt]x
    ##########################################################################################################
    def setRxNames(self):
        """
        Set a list of receivers' name. We choose receivers that have a .conf file in RX_CONF.
        We don't verify if these receivers have a process associated to them.
        """
        rxNames = []
        for file in os.listdir(PXPaths.RX_CONF):
            if file[-5:] != '.conf':
                continue
            else:
                rxNames.append(file[:-5])
        self.rxNames = rxNames
                
    def setTxNames(self):
        """
        Set a list of senders' name. We choose senders that have a .conf file in TX_CONF.
        We don't verify if these senders have a process associated to them.
        """
        txNames = []
        for file in os.listdir(PXPaths.TX_CONF):
            if file[-5:] != '.conf':
                continue
            else:
                txNames.append(file[:-5])
        self.txNames = txNames

    def setRxPaths(self):
        """
        Set a list of receivers' path. We choose receivers that have a .conf file in RX_CONF.
        We don't verify if these receivers have a process associated to them.
        """
        rxPaths = []
        for name in self.rxNames:
            rxPaths.append(PXPaths.RXQ + name + '/')
        self.rxPaths = rxPaths

    def setTxPaths(self):
        """
        Set a list of clients' path. We choose clients that have a .conf file in TX_CONF.
        We don't verify if these clients have a process associated to them.
        """
        txPaths = []
        txPathsPri = []
        txPathsPriDate = []
        priorities = [str(x) for x in range(1,10)]

        for name in self.txNames:
            txPaths.append(PXPaths.TXQ + name + '/')

        for path in txPaths:
            for priority in [pri for pri in os.listdir(path) if pri in priorities]: 
                if os.path.isdir(path + priority):
                    txPathsPri.append(path + priority + '/')

        for path in txPathsPri:
            for date in fnmatch.filter(os.listdir(path), '20[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'):
                if os.path.isdir(path + date):
                    txPathsPriDate.append(path + date + '/')

        #print txPathsPri
        #print txPathsPriDate

        self.txPaths = txPathsPriDate

    def getDBDirs(self):
        dates = os.listdir(PXPaths.DB)
        if 'today' in dates: dates.remove('today')
        if 'yesterday' in dates: dates.remove('yesterday')
        return dates


if __name__ == '__main__':
  
    manager = PXManager()
    #print manager.getRxNames()
    #print manager.getTxNames()
    #print manager.getRxPaths()
    #print manager.getTxPaths()

    manager.initNames()
    manager.initShouldRunNames()
    manager.initRunningNames()

    print manager.getRxNames()
    print manager.getTxNames()
    print manager.getShouldRunRxNames()
    print manager.getShouldRunTxNames()
    print "**************Running names*************"
    print manager.getRunningRxNames()
    print manager.getRunningTxNames()
    print "**************Not Running names*************"
    print manager.getNotRunningRxNames()
    print manager.getNotRunningTxNames()
