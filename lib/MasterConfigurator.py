"""
MetPX Copyright (C) 2004-2007  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: MasterConfigurator.py
#
# Author: Daniel Lemay
#
# Date: 2007-11-15
#
# Description:
#
#############################################################################################

"""
import sys, os, os.path, commands, re, time, fnmatch
import PXPaths
from SystemManager import SystemManager
from PXManager import PXManager

class MasterConfigurator(object):

    def __init__(self, rootPath=""):
        if os.path.isdir('/users/dor/aspy/dan/data/master/'):
            self.rootPath = '/users/dor/aspy/dan/data/master/' # developpment machine
        elif rootPath:
            self.rootPath = os.path.normpath(rootPath) + '/'
        else:
            self.rootPath = '/apps/master/'   # path under wich are the clusters and all the configs. files
        self.types = ['source', 'client', 'sourlient']  # Possible type of flows
        self.initAll()

    def initAll(self):
        self.clusters = []                # cluster names (same as dsh)

        self.dupSources = []              # Duplicate sources (when you combine sources from all clusters)
        self.dupClients = []              # Duplicate clients (when you combine clients from all clusters)
        self.dupSourlients = []           # Duplicate sourlients (when you combine sourlients from all clusters)
        self.dupFlows = []                # Duplicate flows (when you combine flows (sources, clients, sourlients) from all clusters)

        self.allSources = []              # All sources from all clusters (with duplicates removed)
        self.allClients = []              # All clients from all clusters (with duplicates removed)
        self.allSourlients = []           # All sourlients from all clusters (with duplicated removed)
        self.allFlows = []                # All flows (sources, clients, sourlients) from all clusters (with duplicated removed)

        self.sourceCluster = {}           # A mapping from a source to it's cluster
        self.clientCluster = {}           # A mapping from a client to it's cluster
        self.sourlientCluster = {}        # A mapping from a sourlient to it's cluster
        self.flowCluster = {}             # A mapping from a flow to it's cluster
        
    def printClusterInfos(self, flowCluster):
        keys = flowCluster.keys()
        keys.sort()
        for key in keys:
            print "%s: %s" % (key, flowCluster[key])

    def setMachine(self, machine):
        self.machine = machine

    def setUser(self, user):
        self.user = user

    def setClusters(self, list):
        self.clusters = list

    def findClient(self, clusters=None, ip="", name=""):
        """
        clusters: a list of clusters (ex: ['pds', 'px', 'pxatx'])
        ip: IP address (ex: '192.168.1.1')
        name: hostname (ex: 'metmgr')

        Only one argument in (ip, name) must be non null
        """
        import socket

        clusters = clusters or self.clusters
        cliClust = []
        if ip:
            try:
                # get the first part of the fully qualified domain name
                name = socket.gethostbyaddr(ip)[0].split('.')[0]
            except:
                pass

        elif name:
            try:
                ip = socket.gethostbyname(name)
            except:
                pass

        for  cluster in clusters:
            clusterRoot = self.rootPath + cluster
            PXPaths.normalPaths(clusterRoot)
            if ip and name:
                command = "grep -l -E '%s|%s' %s" % (ip, name, PXPaths.TX_CONF + "*.conf")
            elif ip:
                command = "grep -l -E '%s' %s" % (ip, PXPaths.TX_CONF + "*.conf")
            elif name:
                command = "grep -l -E '%s' %s" % (name, PXPaths.TX_CONF + "*.conf")

            #print "%s" % cluster.upper()
            output = commands.getoutput(command)
            clients = [ (os.path.basename(cli)[:-5], cluster) for cli in output.split()]
            cliClust.extend(clients)


        PXPaths.normalPaths() # Reset PXPaths variables
        return cliClust

    def getTypeCluster(self, flow, init=False):
        """
        When init is not False, it is a cluster list

        flow is the name of a client, source, sourlient
        return a list of tuple
        
        getTypeCluster('aftn') => [('sourlient', 'pxatx')]
        getTypeCluster('pds5') => [('source', 'pxatx')]
        getTypeCluster('metmgr3') => [('client', 'pds'), ('client', 'pxatx')]
        """
        if init:
            self.initAll()
            self.clusters = init
            self.getAllFlows()
        return self.flowCluster.get(flow, [])

    def getType(self, flow, init=False):
        """
        When init is not False, it is a cluster list

        flow is the name of a client, source, sourlient
        return type of the flow 

        getType('aftn') => 'sourlient'
        getType('pds5') => 'source'
        getType('metmgr3') => 'client'

        """
        if init:
            self.initAll()
            self.clusters = init
            self.getAllFlows()
        type_cluster = self.flowCluster.get(flow, [])
        if len(type_cluster) == 1:
            return type_cluster[0][0]
        else:
            return len(type_cluster)

    def getCluster(self, flow, init=False):        
        """
        When init is not False, it is a cluster list

        flow is the name of a client, source, sourlient
        return the cluster's name  on which the flow is present
        or the number of clusters, if more than one. 
        
        getCluster('aftn') => 'pxatx'
        getCluster('pds5') => 'pxatx'
        gettCluster('metmgr3') => 2
        """
        if init:
            self.initAll()
            self.clusters = init
            self.getAllFlows()
        type_cluster = self.flowCluster.get(flow, [])
        if len(type_cluster) == 1:
            return type_cluster[0][1]
        else:
            return len(type_cluster)
            
    def createFlowDict(self):
        mergedDict = SystemManager.mergeTwoDict(self.sourceCluster, self.clientCluster)
        return SystemManager.mergeTwoDict(mergedDict, self.sourlientCluster) 

    def getAllFlows(self, noPrint=True):
        if noPrint:
            iprint = lambda *x: None
        else:
            iprint = lambda *x:sys.stdout.write(" ".join(map(str, x)) + '\n')

        allSources = []
        allClients = []
        allSourlients = []
        allFlows = []

        if not os.path.isdir(self.rootPath):
            return 1

        for cluster in self.clusters:
            pxm = PXManager(self.rootPath + cluster + '/')
            if pxm.initNames():
                #print (self.rootPath + cluster + " inexistant!")
                continue

            clients, sourlients, sources, aliases = pxm.getFlowNames(tuple=True)

            # Populate flowCluster for current cluster
            pxm.getFlowDict(self.sourceCluster, sources, 'source', cluster)
            pxm.getFlowDict(self.clientCluster, clients, 'client', cluster)
            pxm.getFlowDict(self.sourlientCluster, sourlients, 'sourlient', cluster)

            allSources.extend(sources)
            allClients.extend(clients)
            allSourlients.extend(sourlients)
            iprint("%s" % (80*'#'))
            iprint("CLUSTER %s" % cluster.upper())
            iprint("%s" % (80*'#'))
            iprint("sources (%s):    %s" % (len(sources), sources))
            iprint("clients (%s):    %s" % (len(clients), clients))
            iprint("sourlients (%s): %s" % (len(sourlients), sourlients))
            #print "aliases:    %s" % aliases
            iprint()

        pxm = PXManager()
        pxm.initNames()

        self.flowCluster = self.createFlowDict()
        self.dupSources = pxm.identifyDuplicate(allSources)
        self.dupClients = pxm.identifyDuplicate(allClients)
        self.dupSourlients = pxm.identifyDuplicate(allSourlients)

        self.allSources = pxm.removeDuplicate(allSources)
        self.allClients = pxm.removeDuplicate(allClients)
        self.allSourlients = pxm.removeDuplicate(allSourlients)

        self.allFlows.extend(allSources)
        self.allFlows.extend(allClients)
        self.allFlows.extend(allSourlients)
        self.dupFlows = pxm.identifyDuplicate(allFlows)
        self.allFlows = pxm.removeDuplicate(allFlows)

        iprint("Duplicate between sources from all clusters: %s" % self.dupSources)
        iprint("Duplicate between clients from all clusters: %s" % self.dupClients)
        iprint("Duplicate between sourlients from all clusters: %s" % self.dupSourlients)
        iprint("Duplicate beetween flows (sources, clients, sourlients) from all clusters: %s" % self.dupFlows)

        iprint() 
        keys = self.flowCluster.keys()
        keys.sort()
        for key in keys:
            if len(self.flowCluster[key]) > 1:
                iprint("%s: %s" % (key, self.flowCluster[key]))

        iprint("source cluster(%s)" % len(self.sourceCluster))
        iprint(self.sourceCluster)
        iprint("client cluster(%s)" % len(self.clientCluster))
        iprint(self.clientCluster)
        iprint("sourlient cluster(%s)" % len(self.sourlientCluster))
        iprint(self.sourlientCluster)
        iprint("flow cluster(%s)" % len(self.flowCluster))
        iprint()


if __name__ == '__main__':
    mc = MasterConfigurator()
    mc.setClusters(['px', 'pds', 'pxatx'])
    mc.getAllFlows(noPrint=True)
    print("%s: %s" % ('metmgr1', mc.getTypeCluster('metmgr1')))
    print mc.getType('metmgr1')
    print mc.getCluster('metmgr1')
    print("%s: %s" % ('aftn', mc.getTypeCluster('aftn')))
    print("%s: %s" % ('pds5', mc.getTypeCluster('pds5')))

    print("%s: %s" % ('metmgr3', mc.getTypeCluster('metmgr3')))
    print mc.getType('metmgr3')
    print mc.getCluster('metmgr3')

    print("%s: %s" % ('px-stage', mc.getTypeCluster('px-stage')))
    print mc.getType('px-stage')
    print mc.getCluster('px-stage')

    print("%s: %s" % ('pds_metser', mc.getTypeCluster('pds_metser')))
    print mc.getType('pds_metser')
    print mc.getCluster('pds_metser')

    #print mc.sourceCluster
    #print mc.clientCluster
    #print mc.sourlientCluster
    #print mc.flowCluster

    mc1 = MasterConfigurator()
    print mc1.getType('metmgr1', ['px', 'pds', 'pxatx'])
    print mc1.getCluster('metmgr1')

    mc1.findClient(ip='199.212.17.60', clusters=['px', 'pxatx', 'pds'])
