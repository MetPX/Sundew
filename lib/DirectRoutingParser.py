"""
#############################################################################################
# Name: DirectRoutingParser.py
#
# Author: Louis-Philippe Theriault (original)
#         Daniel Lemay (as a class with duplicates removal, alias and subclients directives)
#         Michel Grenier (Routing 1 algo)
#
# Date: 2006-04-21
#
# Description: Use to parse the direct routing file (header2client.conf)
#
#############################################################################################
"""

import os, os.path, sys, re, fnmatch
from FileParser import FileParser

class DirectRoutingParser(FileParser):

    def __init__(self, filename, pxLinkables=[], logger=None, version = 0):
        FileParser.__init__(self, filename) # Routing filename ("/apps/px/etc/pxroute.conf")
        self.logger = logger            # Logger object
        self.version = version          # Routing file version  (0 or 1)

        self.version = 1                # FORCING VERSION 1

        self.routingInfos = {}          # Addressed by header name: self.routingInfos[header]['clients']
                                        #                           self.routingInfos[header]['subclients']
                                        #                           self.routingInfos[header]['priority']
        self.keyInfos = {}              # Addressed by key pattern: self.keyInfos[key]['clients']
                                        #                           self.keyInfos[key]['priority']

        self.subClients = {}            # Addressed by client name
        self.aliasedClients = {}        # Addressed by alias
        self.aftnMap = {}               # Addressed by AFTN address. aftnMap['DEFAULT'] give the default
        self.goodClients = {}           # Sub group of clients that are in header2clients.conf and are px linkable.
        self.badClients = {}            # Sub group of clients that are in header2clients.conf and are not px linkable.
        self.pxLinkables = pxLinkables  # All clients to which px can link (independant of header2clients.conf)

        self.originalClients = {}       # Indexed by header, remove duplicate, no alias expansion, subclients as is.
                                        # Only used to reconstruct the routing file

        if self.logger:
            self.logger.info("Routing table used: %s" % filename)

        #self.parse()

    def clearInfos(self):
        self.routingInfos = {}
        self.keyInfos = {}
        self.subClients = {}      
        self.aliasedClients = {}  
        self.aftnMap = {}
        self.goodClients = {}    
        self.badClients = {}    

    def getKeyFromHeader(self, header):
        key = header
        if self.version != 0 : key = header.replace(' ','_')
        return key

    def getHeaderPriority(self, header):
        return self.routingInfos[header]['priority']

    def getHeaderClients(self, header):
        return self.routingInfos[header]['clients']

    def getHeaderSubClients(self, header):
        return self.routingInfos[header]['subclients']

    def getClientSubClients(self, client):
        return self.subClients.get(client, [])

    def getAliasClients(self, alias):
        return self.aliasedClients.get(alias, [])

    def getGoodClients(self):
        return self.goodClients.keys()

    def getBadClients(self):
        return self.badClients.keys()

    # if the key match a certain key pattern (defined using key_accept)
    # than add this key in the routingInfos with the clients and priority
    # defined with that key pattern
    def getKeyClients(self,key):
        for keyp in self.keyInfos :
            parts = re.findall( keyp, key )
            if len(parts) == 2 and parts[1] == '' : parts.pop(1)
            if len(parts) == 1 :
               self.routingInfos[key] = {}
               self.routingInfos[key]['clients']    = self.keyInfos[keyp]['clients']
               self.routingInfos[key]['subclients'] = {}
               self.routingInfos[key]['priority']   = self.keyInfos[keyp]['priority']
               self.logger.debug("ADDED : key %s %s %s" % (key,','.join(self.keyInfos[keyp]['clients']),self.keyInfos[keyp]['priority']) )
               return self.routingInfos[key]['clients']

        self.logger.debug("Key %s did not match any pattern " % key )
        return None

    def getWordsFromLine(self,linex):
        line = linex.strip()
        words = line.split()

        if self.version == 0 :
           line = linex.strip().strip(':')
           words = line.split(':')

        return words

    def getClientsFromWord(self,word):
        clients = word.split(',')

        if self.version == 0 :
           clients = word.split()

        return clients

    def isRoutable(self, key):
        if self.routingInfos.has_key(key): return True
        for keyp in self.keyInfos :
            parts = re.findall( keyp, key )
            if len(parts) == 2 and parts[1] == '' : parts.pop(1)
            if len(parts) == 1 : return True
        return False

    def getClients(self,key):
        if self.routingInfos.has_key(key):
           self.logger.debug("Key %s had direct routing : %s " % (key,self.routingInfos[key]['clients']) )
           return self.routingInfos[key]['clients']
        return self.getKeyClients(key)

    def _makeClientsGroups(self, clients, linkableClients):
        goodClientsForOneHeader = {}
        for client in clients:
            if client in linkableClients:
                self.goodClients[client] = 1
                goodClientsForOneHeader[client] = 1
            else:
                self.badClients[client] = 1

        return goodClientsForOneHeader.keys()

    def parseAlias(self):
        self.clearInfos()
        file = self.openFile(self.filename)

        for line in file:
            if line[0] == '#' : continue
            words = self.getWordsFromLine(line)
            if len(words) == 3: 
                try:
                    if words[0] == 'clientAlias':
                        clients = self.getClientsFromWord(words[2])
                        if len(clients) == 0:
                           self.logger.warning("Line ignored : %s" % line )
                           return
                        clients = self.removeDuplicate(clients)

                        for client in clients[:]:
                            if self.aliasedClients.has_key(client):
                                clients.remove(client)
                                clients.extend(self.aliasedClients[client])

                        self.aliasedClients[words[1]] = self.removeDuplicate(clients)

                except:
                    (type, value, tb) = sys.exc_info()
                    self.logger.error("Type: %s, Value: %s" % (type, value))
                    self.logger.error("Problem with this line (%s) in the direct routing file (%s)" % (words, self.filename))

    def reparse(self):
        routingInfosOld = self.routingInfos.copy()
        keytInfosOld = self.keyInfos.copy()
        subClientsOld = self.subClients.copy()
        #goodClientsOld = self.goodClients.copy()
        #badClientsOld = self.badClients.copy()
        
        try:
            self.parse()
            self.logger.info("Reparse has been done successfully")
        except:
            self.routingInfos = routingInfosOld 
            self.keyInfos = keyInfosOld 
            self.subClients = subClientsOld
            #self.goodClients = goodClientsOld
            #self.badClients = badClientsOld
            self.logger.warning("DirectRoutingParser.reparse() has failed")

    def parse(self):
        self.clearInfos()
        file = self.openFile(self.filename)

        for line in file:
            if line[0] == '#' : continue
            words = self.getWordsFromLine(line)
            # Up to here: 0.2 s of execution time
            #print words
            #if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)): # Regex costs ~ 0.35 seconds (when compare to if len(words) >= 2)
            if len(words) >= 2:
                try:
                    if words[0] == 'subclient':
                        clients = self.getClientsFromWord(words[2])
                        if len(clients) == 0:
                           self.logger.warning("Line ignored : %s" % line )
                           continue
                        clients = self.removeDuplicate(clients)
                        self.subClients[words[1]] = clients
                    elif words[0] == 'aftnMap':
                        self.aftnMap[words[1]] = words[2]
                    elif words[0] == 'clientAlias':
                        clients = self.getClientsFromWord(words[2])
                        if len(clients) == 0:
                           self.logger.warning("Line ignored : %s" % line )
                           continue
                        clients = self.removeDuplicate(clients)
                        for client in clients[:]:
                            if self.aliasedClients.has_key(client):
                                clients.remove(client)
                                clients.extend(self.aliasedClients[client])
                        self.aliasedClients[words[1]] = self.removeDuplicate(clients)

                    # Here we have an "accepted key pattern"
                    elif words[0] == 'key_accept':

                         # the line had the form  key_accept key_pattern client1,client2,... priority
                         if len(words) == 4:
                            words.pop(0)
                            keyI     = words[0]
                            clients  = self.getClientsFromWord(words[1])
                            clients  = self.removeDuplicate(clients)
                            priority = words[2]

                         # the line had the form  key_accept key_pattern priority
                         elif len(words) == 3:
                            words.pop(0)
                            keyI     = words[0]
                            clients  = []
                            priority = words[1]

                         # the line had an erroneous form for a key_accept entry
                         else :
                            self.logger.warning("Line ignored : %s" % line )
                            continue

                         # Replace alias by their client list

                         for client in clients[:]:
                             if self.aliasedClients.has_key(client):
                                clients.remove(client)
                                clients.extend(self.aliasedClients[client])

                         # Assure us that each client is present only once for each header.
                         # Also select only clients that are linkable.

                         clients = self.removeDuplicate(clients)
                         clients = self._makeClientsGroups(clients, self.pxLinkables)

                         # Add all infos in KeyInfos

                         self.keyInfos[keyI] = {}
                         self.keyInfos[keyI]['clients']  = clients
                         self.keyInfos[keyI]['priority'] = priority

                    # Here we have a "header line"
                    elif words[0] == 'key' or (self.version == 0 and len(words[0].split()) == 2) :

                        if self.version != 0 : words.pop(0)

                        if len(words) == 3:
                           entete   = words[0]
                           clients  = self.getClientsFromWord(words[1])
                           clients  = self.removeDuplicate(clients)
                           priority = words[2]

                        elif len(words) == 2:
                           entete   = words[0]
                           clients  = []
                           priority = words[1]

                        else :
                           self.logger.warning("Line ignored : %s" % line )
                           continue

                        self.routingInfos[entete] = {}
                        self.routingInfos[entete]['subclients'] = {}
                        self.routingInfos[entete]['priority'] = priority

                        # Up to here: 0.6 s of execution time

                        # Replace alias by their client list
                        # The following "for" block costs ~ 0.5 s
                        for client in clients[:]:
                            if self.aliasedClients.has_key(client):
                                clients.remove(client)
                                clients.extend(self.aliasedClients[client])
                        clients = self.removeDuplicate(clients)
                        # Up to here: 1.1 s of execution time

                        # Costs ~ 0.5 seconds to execute this block
                        for client in clients[:]:
                            if client.find('.') != -1:
                                # Here we have subclients (ex: aftn.XXXXXXXX)
                                clientParts = client.split('.')
                                if self.subClients.has_key(clientParts[0]):
                                    if clientParts[1] in self.subClients[clientParts[0]]:
                                        if not self.routingInfos[words[0]]['subclients'].has_key(clientParts[0]):
                                            #print clientParts
                                            self.routingInfos[words[0]]['subclients'][clientParts[0]] = [clientParts[1]]
                                            clients.remove(client)
                                            clients.append(clientParts[0])
                                        elif clientParts[1] not in self.routingInfos[words[0]]['subclients'][clientParts[0]]:
                                            self.routingInfos[words[0]]['subclients'][clientParts[0]].append(clientParts[1])
                                            clients.remove(client)
                                        else:
                                            clients.remove(client)
                                            self.logger.warning("%s has duplicate: %s" % (words[0], client))
                                    else:
                                        # When subclient (ex: BIRDZQZZ) is not defined in the subclient directive for the client (ex: aftn)
                                        self.logger.warning("%s has subclient %s that is not acceptable for client %s" %
                                                             (words[0], clientParts[1], clientParts[0]))
                                        clients.remove(client)
                                else:
                                    # Subclient is not defined
                                    self.logger.warning("%s has client %s and %s is not defined with a subclient directive" % 
                                                         (words[0], client, clientParts[0]))
                                    clients.remove(client)
                        # Up to here: 1.6 s of execution time

                        # Assure us that each client is present only once for each header.
                        # Also select only clients that are linkable.
                        # This is accomplished in O(1). Costs ~ 0.5 seconds to execute.
                        goodClientsForOneHeader = self._makeClientsGroups(clients, self.pxLinkables)
                        self.routingInfos[words[0]]['clients'] = goodClientsForOneHeader
                        # Up to here: 2.1 s of execution time

                except:
                    (type, value, tb) = sys.exc_info()
                    self.logger.error("Type: %s, Value: %s" % (type, value))
                    self.logger.error("Problem with this line (%s) in the direct routing file (%s)" % (words, self.filename))
                    try:
                        del self.routingInfos[words[0]]
                        self.logger.error("%s won't be included in the routing table" % words[0])
                    except:
                        self.logger.error("Problem seems to be with a special directive line (not a header line)")

        file.close()
        # Up to here: 2.3 s of execution time

        badClients = self.badClients.keys()
        badClients.sort()
        for client in badClients:
            if client == '' : continue
            self.logger.warning("Client %s is in %s but not in px" % (client, os.path.basename(self.filename)))

    def parseAndShowErrors(self):
        self.clearInfos()
        file = self.openFile(self.filename)

        if self.printErrors:
            myprint = lambda *x:sys.stdout.write(" ".join(map(str, x)) + '\n')
        else:
            myprint = lambda *x: None

        uniqueHeaders = {}
        duplicateHeaders = {}

        for line in file: 
            if line[0] == '#' : continue
            words = self.getWordsFromLine(line)
            #print words
            # Up to here: 0.2 s of execution time
            #myprint words
            #if len(words) >= 2:
            if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)): # Regex costs ~ 0.35 seconds (when compare to if len(words) >= 2)
                try:
                    if words[0] == 'subclient':
                        subclients = self.getClientsFromWord(words[2])
                        if len(subclients) == 0:
                           self.logger.warning("Line ignored : %s" % line )
                           continue
                        self.subClients[words[1]] = self.removeDuplicate(subclients)
                        duplicateForSubclient = self.identifyDuplicate(subclients)
                        if duplicateForSubclient:
                            myprint("Subclient %s has duplicate(s): %s" % (words[1], duplicateForSubclient))
                        #print(" subclient %s %s " % (words[1], self.subClients[words[1]] ) )

                    elif words[0] == 'aftnMap':
                        self.aftnMap[words[1]] = words[2]
                        #print(" aftnMap %s %s " % (words[1], self.aftnMap[words[1]] ) )

                    elif words[0] == 'clientAlias': 
                        clients = self.getClientsFromWord(words[2])
                        if len(clients) == 0:
                           self.logger.warning("Line ignored : %s" % line )
                           continue
                        for client in clients[:]:
                            if self.aliasedClients.has_key(client):
                                clients.remove(client)
                                clients.extend(self.aliasedClients[client])
                        self.aliasedClients[words[1]] = self.removeDuplicate(clients)
                        duplicateForAlias = self.identifyDuplicate(clients)
                        if duplicateForAlias:
                            myprint("Alias %s has duplicate(s): %s" % (words[1], duplicateForAlias))
                        #print(" clientAlias %s %s " % (words[1], self.aliasedClients[words[1]] ) )

                    # Here we have an "accepted key pattern"
                    elif words[0] == 'key_accept':

                        # the line had the form  key_accept key_pattern client1,client2,... priority
                        if len(words) == 4:
                           words.pop(0)
                           keyI     = words[0]
                           clients  = self.getClientsFromWord(words[1])
                           priority = words[2]

                        # the line had the form  key_accept key_pattern priority
                        elif len(words) == 3:
                           words.pop(0)
                           keyI     = words[0]
                           clients  = []
                           priority = words[1]

                         # the line had an erroneous form for a key_accept entry
                        else :
                           myprint("ERROR LINE : %s" % line)
                           continue

                        # check that the key was not already given
                        if self.keyInfos.has_key(keyI):
                            myprint("The key_accept pattern %s was already defined" % keyI )

                        # check for duplicated clients
                        duplicateForHeader = self.identifyDuplicate(clients)
                        if duplicateForHeader:
                            myprint("%s has duplicate(s): %s" % (keyI, duplicateForHeader))

                        # Replace alias by their client list

                        for client in clients[:]:
                            if self.aliasedClients.has_key(client):
                               clients.remove(client)
                               clients.extend(self.aliasedClients[client])

                        # Assure us that each client is present only once for each header.
                        # Also select only clients that are linkable.

                        clients = self.removeDuplicate(clients)
                        clients = self._makeClientsGroups(clients, self.pxLinkables)

                        # Add all infos in KeyInfos

                        self.keyInfos[keyI] = {}
                        self.keyInfos[keyI]['clients']  = clients
                        self.keyInfos[keyI]['priority'] = priority
                        #print(" key_accept %s %s %s" % (keyI, self.keyInfos[keyI]['clients'],self.keyInfos[keyI]['priority']))

                    # Here we have a "header line"
                    elif words[0] == 'key' or (self.version == 0 and len(words[0].split()) == 2) :

                        if self.version != 0 : words.pop(0)

                        if len(words) == 3:
                           entete   = words[0]
                           clients  = self.getClientsFromWord(words[1])
                           priority = words[2]

                        elif len(words) == 2:
                           entete   = words[0]
                           clients  = []
                           priority = words[1]

                        else :
                           myprint("ERROR LINE : %s" % line)
                           continue

                        if uniqueHeaders.has_key(words[0]):
                            duplicateHeaders[words[0]] = 1
                        else:
                            uniqueHeaders[words[0]] = 1
                        
                        # Assure us that each client is present only once for each header
                        # This is accomplished in O(1). Costs ~ 0.5 seconds to execute.
                        uniqueClients = self.removeDuplicate(clients)
                        duplicateForHeader = self.identifyDuplicate(clients)
                        if duplicateForHeader:
                            myprint("%s has duplicate(s): %s" % (words[0], duplicateForHeader))

                        # Up to here: 0.8 s of execution time
                        self.originalClients[words[0]] = uniqueClients[:]

                        self.routingInfos[words[0]] = {}
                        self.routingInfos[words[0]]['subclients'] = {}
                        self.routingInfos[words[0]]['clients'] = uniqueClients # This line costs 0.4 second
                        self.routingInfos[words[0]]['priority'] = priority
                        # Up to here: 1.4 s of execution time

                        # Replace alias by their client list
                        # The following "for" block costs ~ 0.4 s
                        clients = self.routingInfos[words[0]]['clients'][:]
                        for client in clients:
                            if self.aliasedClients.has_key(client):
                                self.routingInfos[words[0]]['clients'].remove(client)
                                self.routingInfos[words[0]]['clients'].extend(self.aliasedClients[client])
                        # Up to here: 1.8 s of execution time

                        # Costs ~ 0.5 seconds to execute this block
                        for client in self.routingInfos[words[0]]['clients'][:]:
                            if client.find('.') != -1:
                                #myprint("Client %s " % client)
                                # Here we have subclients (ex: aftn.XXXXXXXX)
                                clientParts = client.split('.')
                                # Up to here: ~ 1.6 s of execution time
                                if self.subClients.has_key(clientParts[0]):
                                    if clientParts[1] in self.subClients[clientParts[0]]:
                                        if not self.routingInfos[words[0]]['subclients'].has_key(clientParts[0]):
                                            #myprint clientParts
                                            self.routingInfos[words[0]]['subclients'][clientParts[0]] = [clientParts[1]]
                                            self.routingInfos[words[0]]['clients'].remove(client)
                                            self.routingInfos[words[0]]['clients'].append(clientParts[0])
                                        elif clientParts[1] not in self.routingInfos[words[0]]['subclients'][clientParts[0]]:
                                            self.routingInfos[words[0]]['subclients'][clientParts[0]].append(clientParts[1]) 
                                            self.routingInfos[words[0]]['clients'].remove(client)
                                        else:
                                            # Should never arrived here because of uniqueClients
                                            self.routingInfos[words[0]]['clients'].remove(client)
                                            myprint("%s has duplicate: %s" % (words[0], client))
                                    else:
                                        # When subclient (ex: BIRDZQZZ) is not defined in the subclient directive for the client (ex: aftn)
                                        myprint("%s has subclient %s that is not acceptable for client %s" % (words[0], clientParts[1], clientParts[0]))
                                        self.routingInfos[words[0]]['clients'].remove(client)
                                else:
                                    # Subclient is not defined
                                    myprint("%s has client %s and %s is not defined with a subclient directive" % (words[0], client, clientParts[0]))
                                    self.routingInfos[words[0]]['clients'].remove(client)
                        #print(" key %s %s %s" % (words[0], self.routingInfos[words[0]]['clients'],self.keyInfos[keyI]['priority']))

                        
                except:
                    (type, value, tb) = sys.exc_info()
                    myprint("Type: %s, Value: %s" % (type, value))
                    myprint("Problem with this line (%s) in the direct routing file (%s)" % (words, self.filename))

        if len(duplicateHeaders):
            myprint("Duplicate header line(s): %s" % duplicateHeaders.keys())
        file.close()
        # Up to here: 2.3 s of execution time

    def printInfos(self):
        print "#---------------------------------------------------------------#"
        for header in self.routingInfos:
            print ("%s(%s): %s, sub: %s" % (header, self.routingInfos[header]['priority'], self.routingInfos[header]['clients'], self.routingInfos[header]['subclients']))
        print "#---------------------------------------------------------------#"
        for keyI   in self.keyInfos:
            print ("%s(%s): %s" % (keyI, self.keyInfos[keyI]['priority'], self.keyInfos[keyI]['clients']))
        print "#---------------------------------------------------------------#"
        for client in self.subClients:
            print("%s: %s" % (client, self.subClients[client]))
        print "#---------------------------------------------------------------#"
        for alias in self.aliasedClients:
            print("%s: %s" % (alias, self.aliasedClients[alias]))
        print "#---------------------------------------------------------------#"
        print("Good clients (%i): %s" % (len(self.goodClients), self.goodClients.keys()))
        print("Bad clients (%i): %s" % (len(self.badClients), self.badClients.keys()))

    def logInfos(self):
        self.logger.info("#---------------------------------------------------------------#")
        for header in self.routingInfos:
            self.logger.info("%s(%s): %s, sub: %s" % (header, self.routingInfos[header]['priority'], self.routingInfos[header]['clients'], self.routingInfos[header]['subclients']))
        self.logger.info("#---------------------------------------------------------------#")
        for client in self.subClients:
            self.logger.info("%s: %s" % (client, self.subClients[client]))
        for alias in self.aliasedClients:
            self.logger.info("%s: %s" % (alias, self.aliasedClients[alias]))
        self.logger.info("#---------------------------------------------------------------#")
        self.logger.info("Good clients (%i): %s" % (len(self.goodClients), self.goodClients.keys()))
        self.logger.info("Bad clients (%i): %s" % (len(self.badClients), self.badClients.keys()))


if __name__ == '__main__':
    import sys
    import PXPaths

    sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')
    from Logger import *

    PXPaths.normalPaths()
    logger = Logger(PXPaths.LOG+'parsing.log', 'DEBUG', 'Sub')
    logger = logger.getLogger()

    pxLinkables = ['cmc', 'aftn', 'satnet-ice']
    parser = DirectRoutingParser(PXPaths.ETC+'pxRouting.conf', pxLinkables, logger)
    parser.parseAndShowErrors()
    #parser.parse()
    parser.printInfos()
    print parser.getHeaderPriority('AACN01_CWAO')
    print parser.getHeaderClients('AACN01_CWAO')
    print parser.getHeaderSubClients('AACN01_CWAO')
    print parser.getHeaderSubClients('AACN01_CWAO').get('aftn', [])
    print("Good clients (%i): %s" % (len(parser.goodClients), parser.goodClients.keys()))
    print("Bad clients (%i): %s" % (len(parser.badClients), parser.badClients.keys()))
