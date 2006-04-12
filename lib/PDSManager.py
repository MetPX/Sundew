"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PDSManager.py
#
# Author: Daniel Lemay
#
# Date: 2005-06-14
#
# Description:
#
#############################################################################################
"""

import os, os.path, sys, commands, re, pickle, time, logging
import SystemManager, PDSPaths
from SystemManager import SystemManager

class PDSManager(SystemManager):
    
    def __init__(self, drbdPath=False):
        """
        drbdPath: drbd path or False, drbd path if we use other root than /apps
        """

        if drbdPath:
            PDSPaths.drbdPaths(drbdPath) 
        else:
            PDSPaths.normalPaths() 

        SystemManager.__init__(self)
        self.LOG = PDSPaths.LOG  # Will be used by DirCopier

    def afterInit(self):
        
        if not os.path.isdir(PDSPaths.ROOT):
            self.logger.error("This directory: %s does not exist!" % (PDSPaths.ROOT))
            sys.exit(15)

        self.setRxNames()
        self.setTxNames()
        self.setRxPaths()
        self.setTxPaths()

        #print self.getRxNames()

    def setRunningRxNames(self):
        """
        Set a list of receivers' name. We choose receivers that have a .conf file in RX_CONF
        and we verify that these receivers have a process associated to them.
        """
        pass

    def setRunningTxNames(self):
        """
        Set a list of senders' name. We choose senders that have a .conf file in TX_CONF 
        and we verify that these senders have a process associated to them.
        """
        pass

    def setRxNames(self):
        """
        Set a list of input directories' name. We choose directories that are STARTED in RX_CONF.
        We don't verify if these directories have a process (pdschkprod) associated to them.
        """
        rxNames = []

        prodfile = open (PDSPaths.FULLPROD, "r")
        lines = prodfile.readlines()

        for line in lines:
            match = re.compile(r"^in_dir\s+(\S+)").search(line)
            if (match):
                # We skip the RAW/ part
                rxNames.append(match.group(1)[4:])
        self.rxNames = rxNames
        prodfile.close()

    def setTxNames(self):
        """
        Set a list of client's name. We choose clients that are STARTED in TX_CONF.
        We don't verify if these clients have a process associated to them.
        """
        txNames = []

        startup = open(PDSPaths.FULLSTARTUP, "r")
        lines = startup.readlines()

        for line in lines:
            if (re.compile(r"pdssender").search(line)):
                match = re.compile(r".* (\d+) (\S+) (\S+) (\d+) info/(\S+) log/(\S+) .*").search(line)
                (pid, name, status, date, config, logfile) =  match.group(1, 2, 3, 4, 5, 6)
                txNames.append(name)
        self.txNames = txNames
        startup.close()

    def setRxPaths(self):
        """
        Set a list of input directories' path. We choose directories that have a .conf file in RX_CONF.
        We don't verify if these directories have a process associated to them.
        """
        rxPaths = []
        for name in self.rxNames:
            rxPaths.append(PDSPaths.RXQ + name + '/')
        self.rxPaths = rxPaths

    def setTxPaths(self):
        """
        Set a list of input directories' path. We choose directories that have a .conf file in RX_CONF.
        We don't verify if these directories have a process associated to them.
        """
        txPaths = []
        for name in self.txNames:
            txPaths.append(PDSPaths.TXQ + name + '/incoming/')
        self.txPaths = txPaths


if __name__ == '__main__':
  
    manager = PDSManager()
    #print manager.getRxNames()
    #print manager.getTxNames()
    print manager.getRxPaths()
    print manager.getTxPaths()
