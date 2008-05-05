
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
import SystemManager, PXPaths, fileLib
from SystemManager import SystemManager

class PXManager(SystemManager):

    def __init__(self, rootPath=""):

        self.rootPath = rootPath
        PXPaths.normalPaths(self.rootPath) 
        SystemManager.__init__(self)
        self.LOG = PXPaths.LOG          # Will be used by DirCopier
        self.debug = 0

    def getLastFiles(self, type, flows, startDate, endDate, timestamp="", regex=".*", format="%Y-%m-%d %H:%M:%S",
                     verbose=True, priority=0, basename=False):
        """
        Function that can be used to find files to retransmit.
        Unix commands (awk, grep, cut, etc.) have been used in this
        function only because I want to practice them.
        """

        LOGS = self.LOG
        ALL = 'all'
        MATCH = 'MATCH'
        DEBUG = 0

        hostname = os.uname()[1]
        matchingFiles = []
    
        flows = flows.replace(' ', '').strip(',').split(',')
        flowsCol = ":".join(flows)
    
        regex = re.compile(regex)
        startDateFormatted = time.strftime(format, time.gmtime(startDate))
        endDateFormatted = time.strftime(format, time.gmtime(endDate))
        date = timestamp or time.strftime("%Y%m%d%H%M%S", time.gmtime())
    
        for flow in flows:
            filename = "%s/toRetransmit.%s.%s.%s" % (LOGS, flow, hostname, date)
            files = self.getLogNames(type=type, flowName=flow, date="*", fullPath=True)
            files = fileLib.sortFilesByTime(files, (type=='rx' and 'Ingested') or (type=='tx' and 'delivered'))
    
            for file in files:
                if type=='rx':
                    commands.getoutput('grep Ingested %s | cut -d" " -f1,2,10 | \
                    awk \'{date = $1 " " $2}; date >= "%s" && date <= "%s" {print $1, substr($2, 1, 8), $3, "%s"}\' >> %s.%s' %
                    (file, startDateFormatted, endDateFormatted, hostname, filename, ALL))
                elif type=='tx':
                    commands.getoutput('grep delivered %s | cut -d" " -f1,2,7 | \
                    awk \'{date = $1 " " $2}; date >= "%s" && date <= "%s" {print $1, substr($2, 1, 8), $3, "%s"}\' >> %s.%s' %
                    (file, startDateFormatted, endDateFormatted, hostname, filename, ALL))

                if DEBUG: print file
    
            if os.path.isfile("%s.%s" % (filename, ALL)):
                matchingFiles.append("%s.%s" % (filename, MATCH))
                goodTimes = open("%s.%s" % (filename, ALL), 'r')
                goodWords = open("%s.%s" % (filename, MATCH), 'w')
                for line in goodTimes.readlines():
                    words = line.split()
                    fields = words[2].split(":")
                    match = regex.search(os.path.basename(words[2]))
                    if (match) and fields[4] != "PROBLEM":
                        goodWords.write(line)
    
                goodTimes.close()
                goodWords.close()
    
        matchingFile = "%s/toRetransmit.%s.%s.%s" % (LOGS, flowsCol, hostname, date)
        fileLib.mergeFiles(matchingFiles, matchingFile)
    
        return matchingFile

    def getFlowDict(self, theDict, flows, type, cluster=""):
        """
        adict = {}
        sourceNames = ['source1', 'source2', ...]
        type must be in ['source', 'client', 'sourlient']
        cluster is a cluster name ('pds', 'px', 'pxatx', ...)
        ex: getFlowDict(adict, sourceNames, 'source', 'pds')
        """
        for flow in flows:
            if cluster:
                theDict.setdefault(flow, []).append((type, cluster)) 
            else:
                theDict.setdefault(flow, []).append((type)) 
        return theDict 

    def getDBName(self, filename):
        """
        This method will be used to extract the DB name from the filename
        found in a tx log.
        
        ex: TVE-cartes_2007111300_317_P45.gif:TVE:CMOI:CARTES:4:GIF:20071113033933
        should give /apps/px/db/20071113/CARTES/TVE/CMOI/TVE-cartes_2007111300_317_P45.gif:TVE:CMOI:CARTES:4:GIF:20071113033933
        """
        words = filename.split(':')
        if len(words) == 7:
            return PXPaths.DB + words[6][:8] + '/' + words[3] + '/' + words[1] + '/' + words[2] + '/' + filename
        else:
            return ""

    def getLogNames(self, type='rx', flowName='*', date="", fullPath=True):
        dot = ""
        if date not in ["", "*"]: dot = '.'

        if fullPath:
            return [self.LOG + file for file in fnmatch.filter(os.listdir(self.LOG), "%s_%s.log%s%s" % (type, flowName, dot, date))]
        else:
            return [file for file in fnmatch.filter(os.listdir(self.LOG), "%s_*.log%s%s" % (type, dot, date))]

    def getFlowNames(self, tuple=False, drp=None):
        clientNames =  self.getTxNames()
        sourlientNames = self.getTRxNames()
        filterNames = self.getFxNames()
        sourceNames = self.getRxNames()

        if drp:
            aliases = drp.aliasedClients.keys()
        else:
            aliases = []

        if tuple:
            return clientNames, sourlientNames, sourceNames, aliases
        else:
            return clientNames + sourlientNames + sourceNames + aliases

    def getFlowQueueName(self, flow, drp=None, filename=None, priority=None):
        types = {'TX': PXPaths.TXQ, 'FX':PXPaths.FXQ, 'RX':PXPaths.RXQ, 'TRX': PXPaths.TXQ}
        type, flowNames = self.getFlowType(flow, drp)

        if self.debug:
            print type
            print flowNames

        # No type or flow is an alias
        if not type or len(flowNames) != 1: return None

        if filename:
            parts = filename.split(':')
            if not priority:
                priority = parts[4].split('.')[0]

        flowQueueName = types[type] + flow 
        if filename:
            if types[type] == PXPaths.TXQ:
                flowQueueName += '/' + str(priority) + '/' + time.strftime("%Y%m%d%H", time.gmtime()) + '/' + filename
            elif types[type] == PXPaths.FXQ:
                flowQueueName += '/' + filename
            elif types[type] == PXPaths.RXQ:
                flowQueueName += '/' + filename

        return flowQueueName

    def getFlowType(self, name, drp=None):
        """
        The search will procede in the following order: clientNames -> sourlientNames -> sourceNames.
        This can have an impact if a name is in more than one category.
        """
        clientNames =  self.getTxNames()
        sourlientNames = self.getTRxNames()
        sourceNames = self.getRxNames()
        filterNames = self.getFxNames()

        # clientNames first, sourlientNames second, sourcesNames third and finally, aliases fourth
        flowType = None
        flowNames = [name]

        if name in clientNames:
            flowType = 'TX'
        elif name in sourlientNames:
            flowType = 'TRX'
        elif name in filterNames:
            flowType = 'FX'
        elif name in sourceNames:
            flowType = 'RX'
        elif drp:
            flowNames = drp.getAliasClients(name)
            if flowNames:
                # For now, only TX aliases exist
                flowType = 'TX'
        return  flowType, flowNames

    def afterInit(self):
        if not os.path.isdir(PXPaths.ETC):
            if self.logger: self.logger.error("This directory: %s does not exist!" % (PXPaths.ETC))
            sys.exit(15)

        self.setFxNames()           
        self.setRxNames()           
        self.setTxNames()
        self.setTRxNames()

        self.setFxPaths()
        self.setRxPaths()
        self.setTxPaths()
        #self.rxPaths = ['/apps/px/toto/', '/apps/px/titi/', '/apps/px/tata/']

    def initPXPaths(self):
        # ROOT, LIB, LOG, ETC, RXQ, TXQ, DB, RX_CONF, TX_CONF, COLLECTION_DB, COLLECTION_CONTROL
        self.createDir(PXPaths.LIB)
        self.createDir(PXPaths.LOG)
        self.createDir(PXPaths.FX_CONF)
        self.createDir(PXPaths.RX_CONF)
        self.createDir(PXPaths.TX_CONF)
        self.createDir(PXPaths.TRX_CONF)
        self.createDir(PXPaths.FXQ)
        self.createDir(PXPaths.RXQ)
        self.createDir(PXPaths.TXQ)
        self.createDir(PXPaths.DB)

    def initNames(self):
        if not os.path.isdir(PXPaths.ETC):
            if self.logger: self.logger.error("This directory: %s does not exist!" % (PXPaths.ETC))
            return 1
        
        try:
            self.setFxNames()           
        except OSError:
            pass

        try:
            self.setRxNames()           
        except OSError:
            pass

        try:
            self.setTxNames()
        except OSError:
            pass

        try:
            self.setTRxNames()
        except OSError:
            pass

    def initShouldRunNames(self):
        if not os.path.isdir(PXPaths.ETC):
            if self.logger: self.logger.error("This directory: %s does not exist!" % (PXPaths.ETC))
            sys.exit(15)

        self.setShouldRunFxNames()           
        self.setShouldRunRxNames()           
        self.setShouldRunTxNames()
        self.setShouldRunTRxNames()

    def initRunningNames(self):
        if not os.path.isdir(PXPaths.ETC):
            if self.logger: self.logger.error("This directory: %s does not exist!" % (PXPaths.ETC))
            sys.exit(15)

        self.setRunningFxNames()
        self.setRunningRxNames()
        self.setRunningTxNames()
        self.setRunningTRxNames()

    def getNotRunningFxNames(self):
        return self.notRunningFxNames

    def getNotRunningRxNames(self):
        return self.notRunningRxNames

    def getNotRunningTxNames(self):
        return self.notRunningTxNames

    def getNotRunningTRxNames(self):
        return self.notRunningTRxNames
        
    ##########################################################################################################
    # Running Names (sources and clients):
    # 1) Have a .conf file in /apps/px/etc/[rt]x
    # 2) Have a lock file (.lock) in /apps/px/[frt]xq/NAME
    # 3) A ps confirm that the pid contained in the .lock file is running 
    ##########################################################################################################
    def setRunningFxNames(self):
        """
        Set a list of filters' name. We choose filters that have a .conf file in FX_CONF
        and we verify that these filters have a .lock and a process associated to them.
        """
        runningFxNames = []
        notRunningFxNames = []
        shouldRunFxNames = self.getShouldRunFxNames()
        for name in shouldRunFxNames:
            try:
                pid = open(PXPaths.FXQ + name + '/' + '.lock', 'r').read().strip()
                if not commands.getstatusoutput('ps -p ' + pid)[0]:
                    # Process is running
                    runningFxNames.append(name)
                else:
                    notRunningFxNames.append(name)
            except:
                #FIXME 
                pass

        self.runningFxNames = runningFxNames
        self.notRunningFxNames = notRunningFxNames

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
                pid = open(PXPaths.RXQ + name + '/' + '.lock', 'r').read().strip()
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
                pid = open(PXPaths.TXQ + name + '/' + '.lock', 'r').read().strip()
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

    def setRunningTRxNames(self):
        """
        Set a list of transceivers' name. We choose transceivers that have a .conf file in TRX_CONF 
        and we verify that these transceivers have a .lock and a process associated to them.
        """
        runningTRxNames = []
        notRunningTRxNames = []
        shouldRunTRxNames = self.getShouldRunTRxNames()
        for name in shouldRunTRxNames:
            try:
                #We read the pid from the RXQ (we could have used TXQ)
                pid = open(PXPaths.RXQ + name + '/' + '.lock', 'r').read().strip()
                if not commands.getstatusoutput('ps -p ' + pid)[0]:
                    # Process is running
                    runningTRxNames.append(name)
                else:
                    notRunningTRxNames.append(name)
            except:
                #FIXME 
                pass

        self.runningTRxNames = runningTRxNames
        self.notRunningTRxNames = notRunningTRxNames


    ##########################################################################################################
    # Should be running names (sources and clients):
    # 1) Have a .conf file in /apps/px/etc/[rt]x
    # 2) Have a lock file (.lock) in /apps/px/[rt]xq/NAME
    ##########################################################################################################
    def setShouldRunFxNames(self):
        """
        Set a list of receivers' name. We choose receivers that have a .conf file in RX_CONF
        and we verify that these receivers have a .lock  associated to them.
        """
        shouldRunFxNames = []
        fxNames =  self.getFxNames()
        for name in fxNames:
            if os.path.isfile(PXPaths.FXQ + name + '/' + '.lock'):
                shouldRunFxNames.append(name)
        self.shouldRunFxNames = shouldRunFxNames

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

    def setShouldRunTRxNames(self):
        """
        Set a list of transceivers' name. We choose transceivers that have a .conf file in TRX_CONF 
        and we verify that these transceivers have a .lock associated to them.
        """
        shouldRunTRxNames = []
        trxNames =  self.getTRxNames()
        for name in trxNames:
            if os.path.isfile(PXPaths.RXQ + name + '/' + '.lock'):
                shouldRunTRxNames.append(name)
        self.shouldRunTRxNames = shouldRunTRxNames

    ##########################################################################################################
    # Names and paths (sources and clients):
    # 1) Have a .conf file in /apps/px/etc/[rt]x
    ##########################################################################################################
    def setFxNames(self):
        """
        Set a list of filters' name. We choose filters that have a .conf file in FX_CONF.
        We don't verify if these filters have a process associated to them.
        """
        fxNames = []
        for file in os.listdir(PXPaths.FX_CONF):
            if file[-5:] != '.conf':
                continue
            else:
                fxNames.append(file[:-5])
        fxNames.sort()
        self.fxNames = fxNames
                
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
        rxNames.sort()
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
        txNames.sort()
        self.txNames = txNames

    def setTRxNames(self):
        """
        Set a list of receivers' name. We choose receivers that have a .conf file in TX_CONF.
        We don't verify if these senders have a process associated to them.
        """
        trxNames = []
        for file in os.listdir(PXPaths.TRX_CONF):
            if file[-5:] != '.conf':
                continue
            else:
                trxNames.append(file[:-5])
        trxNames.sort()
        self.trxNames = trxNames

    def setFxPaths(self):
        """
        Set a list of receivers' path. We choose receivers that have a .conf file in FX_CONF.
        We don't verify if these receivers have a process associated to them.
        """
        fxPaths = []
        for name in self.fxNames:
            fxPaths.append(PXPaths.FXQ + name + '/')

        self.fxPaths = fxPaths

    def setRxPaths(self):
        """
        Set a list of receivers' path. We choose receivers that have a .conf file in RX_CONF.
        We don't verify if these receivers have a process associated to them.
        """
        rxPaths = []
        for name in self.rxNames:
            rxPaths.append(PXPaths.RXQ + name + '/')
        for name in self.trxNames:
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
        for name in self.trxNames:
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
    #print manager.getFxNames()
    #print manager.getRxNames()
    #print manager.getTxNames()
    #print manager.getRxPaths()
    #print manager.getTxPaths()

    manager.initPXPaths()
    manager.initNames()
    manager.initShouldRunNames()
    manager.initRunningNames()

    print
    print "**************************************************************"
    print("FX Names: %s" % manager.getFxNames())
    print("RX Names: %s" % manager.getRxNames())
    print("TX Names: %s" % manager.getTxNames())
    print("TRX Names: %s" % manager.getTRxNames())
    print "********************* Should run names ***********************"
    print("FX that should run: %s" % manager.getShouldRunFxNames())
    print("RX that should run: %s" % manager.getShouldRunRxNames())
    print("TX that should run: %s" % manager.getShouldRunTxNames())
    print("TRX that should run: %s" % manager.getShouldRunTRxNames())
    print "********************** Running names *************************"
    print manager.getRunningFxNames()
    print manager.getRunningRxNames()
    print manager.getRunningTxNames()
    print manager.getRunningTRxNames()
    print "************* Not Running names (that should run) ************"
    print manager.getNotRunningFxNames()
    print manager.getNotRunningRxNames()
    print manager.getNotRunningTxNames()
    print manager.getNotRunningTRxNames()
    print "**************************************************************"
    print
    
    print manager.getDBName("TVE-cartes_2007111300_317_P45.gif:TVE:CMOI:CARTES:4:GIF:20071113033933")

    print manager.getFlowType("pds_metser")
    print manager.getFlowQueueName(flow='pds_metser', filename="200801151910~NAV9_ONT_ECHOTOP~ECHOTOP,2.0,100M,AGL,78,N:URP:NAV9_ONT:RADAR:IMV6::20080115191243", priority=2)
