"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

#############################################################################################
# Name: RoutingFileCreator.py
#
# Author: Daniel Lemay
#
# Date: 2006-07-12
#
# Description: Used to create routing file
#
#############################################################################################
"""
import sys
from FileCreator import FileCreator
import PXPaths

PXPaths.normalPaths()  # Access to PX Paths

class RoutingFileCreator(FileCreator):
    
    def __init__(self, directRoutingParser, filename=PXPaths.ETC + 'titi.conf', logger=None):
        FileCreator.__init__(self, filename)
        self.logger = logger
        self.drp = directRoutingParser
        self._appendToFile()
        self._closeFile()

    def createSubclientsSection(self):
        keys = self.drp.subClients.keys()
        keys.sort()
        for sub in keys: 
            subClients = self.drp.subClients.get(sub, [])
            subClients.sort()
            if self.drp.version == 0 :
                   self.file.write("subclient %s %s\n" % (sub, ' '.join(subClients)))
            else :
                   self.file.write("subclient %s %s\n" % (sub, ','.join(subClients)))
    
    def createAFTNMapSection(self):
        keys = self.drp.aftnMap.keys()
        keys.sort()
        for mapping in keys:
            if self.drp.version == 0 :
                   self.file.write("aftnMap %s %s\n" % (mapping, ' '.join(self.drp.aftnMap[mapping]) ))
            else :
                   self.file.write("aftnMap %s %s\n" % (mapping,self.drp.aftnMap[mapping] ))

    def createClientAliasesSection(self):
        keys = self.drp.aliasedClients.keys()
        keys.sort()
        for alias in keys:
            clients = self.drp.aliasedClients.get(alias, [])
            clients.sort()
            if self.drp.version == 0 :
                   self.file.write("clientAlias %s %s\n" % (alias, ' '.join(clients)))
            else :
                   self.file.write("clientAlias %s %s\n" % (alias, ','.join(clients)))

    def createHeadersSection(self):
        headers = self.drp.routingInfos.keys()
        headers.sort()

        for header in headers:
            clients = self.drp.originalClients[header]
            clients.sort()
            if self.drp.version == 0 :
                   self.file.write("%s:%s:%s\n" % (header, ' '.join(clients), self.drp.getHeaderPriority(header)))
            else :
                   self.file.write("key %s %s %s\n" % (header, ','.join(clients), self.drp.getHeaderPriority(header)))

    def createKeyAcceptSection(self):

        for mask in self.drp.keyMasks:
            if mask[4] :
               self.file.write ("key_accept %s %s %s" % (mask[0],','.join(mask[1]),mask[2]) )
            else :
               self.file.write ("key_reject %s " % mask[0] )

    def _appendToFile(self):
        import math
        length = 80
        bottom = length * '#' + '\n\n'

        words = {1:'SUBCLIENTS',
                 2:'AFTN MAP',
                 3:'CLIENT ALIASES',
                 4:'HEADERS',
                 5:'KEY_ACCEPT'
                }

        m = max(map(len, words.values()))

        top =  lambda x: int(math.ceil((length-(len(x)+2))/2.0)) * '#' + ' %s ' % x + (length-(len(x)+2))/2 * '#' + '\n'

        self.file.write(top(words[1]))
        self.createSubclientsSection()
        self.file.write(bottom)

        self.file.write(top(words[2]))
        self.createAFTNMapSection()
        self.file.write(bottom)

        self.file.write(top(words[3]))
        self.createClientAliasesSection()
        self.file.write(bottom)

        if self.drp.version == 1 :
           self.file.write(top(words[5]))
           self.createKeyAcceptSection()
           self.file.write(bottom)

        self.file.write(top(words[4]))
        self.createHeadersSection()
        self.file.write(bottom)

if __name__ == '__main__':
    import sys

    sys.path.insert(1, '/apps/px/lib')
    sys.path.insert(1, '/usr/lib/px')
    try:
             sys.path.insert(1, os.path.normpath(os.environ['PXLIB']) )
    except :
             pass

    from Logger import Logger 
    from DirectRoutingParser import DirectRoutingParser

    logger = Logger('/apps/px/log/RoutingFileCreator.log', 'DEBUG', 'RFC')
    logger = logger.getLogger()

    drp = DirectRoutingParser('/apps/px/aftn/etc/header2client.conf.aftn', ['cmc', 'aftn', 'satnet-ice'], logger=logger)
    drp.parseAndShowErrors()

    rfc = RoutingFileCreator(directRoutingParser=drp)
