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
import sys, os, re, time, fnmatch
import PXPaths
from SystemManager import SystemManager
from PXManager import PXManager

class MasterConfigurator(object):

    def __init__(self):
        self.clusters = []                # cluster names (same as dsh)
        self.rootPath = '/apps/master/'   # path under wich are the clusters and all the configs. files

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

        self.types = ['source', 'client', 'sourlient']  # Possible type of flows

    def setMachine(self, machine):
        self.machine = machine

    def setUser(self, user):
        self.user = user

    def setClusters(self, list):
        self.clusters = list

    def getTypeCluster(self, flow):
        return self.flowCluster.get(flow, [])

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

        for cluster in self.clusters:
            pxm = PXManager(self.rootPath + cluster + '/')
            pxm.initNames()
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
    mc.getAllFlows(noPrint=False)
    print("%s: %s" % ('metmgr1', mc.getTypeCluster('metmgr1')))
    print("%s: %s" % ('aftn', mc.getTypeCluster('aftn')))
    print("%s: %s" % ('pds5', mc.getTypeCluster('pds5')))

    #print mc.sourceCluster
    #print mc.clientCluster
    #print mc.sourlientCluster
    #print mc.flowCluster
