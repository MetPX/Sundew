"""
#############################################################################################
# Name: DirectRoutingParser.py
#
# Author: Louis-Philippe Theriault (original)
#         Daniel Lemay (as a class with duplicates removal, alias and subclients directives)
#
# Date: 2006-04-21
#
# Description: Use to parse the direct routing file (header2client.conf)
#
#############################################################################################
"""

import os, sys, re, __builtin__
from Logger import *

class DirectRoutingParser:

    def __init__(self, filename, pxLinkables=[], logger=None):
        self.filename = filename        # Routing filename ("/apps/px/etc/header2clients.conf")
        self.logger = logger            # Logger object
        self.routingInfos = {}          # Addressed by header name: self.routingInfos[header]['clients']
                                        #                           self.routingInfos[header]['subclients']
                                        #                           self.routingInfos[header]['priority']

        self.subClients = {}            # Addressed by client name
        self.aliasedClients = {}        # Addressed by alias
        self.goodClients = {}           # Sub group of clients that are in header2clients.conf and are px linkable.
        self.badClients = {}            # Sub group of clients that are in header2clients.conf and are not px linkable.
        self.pxLinkables = pxLinkables  # All clients to which px can link (independant of header2clients.conf)

        self.parse()

    def clearInfos(self):
        self.routingInfos = {}
        self.subClients = {}      
        self.aliasedClients = {}  
        self.goodClients = {}    
        self.badClients = {}    

    def getHeaderPriority(self, header):
        return self.routingInfos[header]['priority']

    def getHeaderClients(self, header):
        return self.routingInfos[header]['clients']

    def getHeaderSubClients(self, header):
        return self.routingInfos[header]['subclients']

    def getClientSubClients(self, client):
        return self.subclients[client]

    def getAliasClients(self, alias):
        return self.aliasedClients[alias]

    def getGoodClients(self):
        return self.goodClients.keys()

    def getBadClients(self):
        return self.badClients.keys()

    def _makeClientsGroups(self, clients, linkableClients):
        goodClientsForOneHeader = {}
        for client in clients:
            if client in linkableClients:
                self.goodClients[client] = 1
                goodClientsForOneHeader[client] = 1
            else:
                self.badClients[client] = 1

        return goodClientsForOneHeader.keys()

    def _removeDuplicate(self, list):
        set = {}
        for item in list:
            set[item] = 1
        return set.keys()

    def reparse(self):
        routingInfosOld = self.routingInfos.copy()
        subClientsOld = self.subClients.copy()
        #goodClientsOld = self.goodClients.copy()
        #badClientsOld = self.badClients.copy()
        
        try:
            self.parse()
            self.logger.info("Reparse has been done successfully")
        except:
            self.routingInfos = routingInfosOld 
            self.subClients = subClientsOld
            #self.goodClients = goodClientsOld
            #self.badClients = badClientsOld
            self.logger.warning("DirectRoutingParser.reparse() has failed")
            
    def parse(self):
        self. clearInfos()
        try:
            file = open(self.filename, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            self.logger.error("Type: %s, Value: %s" % (type, value))
            sys.exit()

        for line in file.readlines():
            line = line.strip().strip(':')
            words = line.split(':')
            # Up to here: 0.2 s of execution time
            #print words
            #if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)): # Regex costs ~ 0.35 seconds (when compare to if len(words) >= 2)
            if len(words) >= 2:
                try:
                    if words[0] == 'subclient':
                        self.subClients[words[1]] = words[2].split()
                    elif words[0] == 'clientAlias':
                        self.aliasedClients[words[1]] = self._removeDuplicate(words[2].split())
                    elif len(words[0].split()) == 2: # If replace by a simple "else" do nothing for execution time
                        # Here we have a "header line"
                        self.routingInfos[words[0]] = {}
                        self.routingInfos[words[0]]['subclients'] = {}
                        self.routingInfos[words[0]]['priority'] = words[2]
                        # Up to here: 0.6 s of execution time

                        # Replace alias by their client list
                        # The following "for" block costs ~ 0.5 s
                        clients = words[1].split()
                        for client in clients[:]:
                            if self.aliasedClients.has_key(client):
                                clients.remove(client)
                                clients.extend(self.aliasedClients[client])
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
                                            self.logger.warning("Subclient %s of client %s is present more than once for header %s" % (clientParts[1], clientParts[0], words[0]))
                                    else:
                                        # When subclient (ex: BIRDZQZZ) is not defined in the subclient directive for the client (ex: aftn)
                                        self.logger.warning("Subclient %s is not acceptable for client %s (See header %s)" % (clientParts[1], clientParts[0], words[0]))
                                        clients.remove(client)
                                else:
                                    # Subclient is not defined
                                    self.logger.warning("Client(%s) is not defined with subclient directive" % (clientParts[0]))
                                    clients.remove(client)
                        # Up to here: 1.6 s of execution time

                        # Assure us that each client is present only once for each header.
                        # Also select only clients that are linkable.
                        # This is accomplished in O(n). Costs ~ 0.5 seconds to execute.
                        goodClientsForOneHeader = self._makeClientsGroups(clients, self.pxLinkables)
                        self.routingInfos[words[0]]['clients'] = goodClientsForOneHeader
                        # Up to here: 2.1 s of execution time

                except:
                    (type, value, tb) = sys.exc_info()
                    self.logger.error("Type: %s, Value: %s" % (type, value))
                    self.logger.error("Problem with this line (%s) in the direct routing file (%s)" % (words, self.filename))
        file.close()
        # Up to here: 2.3 s of execution time


    def parse1(self):
        self. clearInfos()
        try:
            file = open(self.filename, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value))
            return 

        for line in file.readlines(): 
            line = line.strip().strip(':')
            words = line.split(':')
            # Up to here: 0.2 s of execution time
            #print words
            #if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)): # Regex costs ~ 0.35 seconds (when compare to if len(words) >= 2)
            if len(words) >= 2:
                try:
                    if words[0] == 'subclient':
                        self.subClients[words[1]] = words[2].split()
                    elif words[0] == 'clientAlias': 
                        self.aliasedClients[words[1]] = self._removeDuplicate(words[2].split())

                    elif len(words[0].split()) == 2: # If replace by a simple "else" do nothing for execution time
                        # Here we have a "header line"

                        # Assure us that each client is present only once for each header
                        # This is accomplished in O(n). Costs ~ 0.5 seconds to execute.
                        uniqueClients = self._removeDuplicate(words[1].split())
                        # Up to here: 0.8 s of execution time

                        self.routingInfos[words[0]] = {}
                        self.routingInfos[words[0]]['subclients'] = {}
                        self.routingInfos[words[0]]['clients'] = uniqueClients # This line costs 0.4 second
                        self.routingInfos[words[0]]['priority'] = words[2]
                        # Up to here: 1.4 s of execution time

                        """

                        # This check (to be sure that no duplicate are present in the clients) costs ~ 2.4 seconds (~ 31000 entries)!
                        if clientParts[0] not in self.routingInfos[words[0]]['clients']:
                            self.routingInfos[words[0]]['clients'].append(clientParts[0])

                        elif clientParts[0] not in self.routingInfos[words[0]]['subclients']:
                            print("Client %s is present more than once for header %s" % (clientParts[0], words[0]))
                        """

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
                                #print("Client %s " % client)
                                # Here we have subclients (ex: aftn.XXXXXXXX)
                                clientParts = client.split('.')
                                # Up to here: ~ 1.6 s of execution time
                                if self.subClients.has_key(clientParts[0]):
                                    if clientParts[1] in self.subClients[clientParts[0]]:
                                        if not self.routingInfos[words[0]]['subclients'].has_key(clientParts[0]):
                                            #print clientParts
                                            self.routingInfos[words[0]]['subclients'][clientParts[0]] = [clientParts[1]]
                                            self.routingInfos[words[0]]['clients'].remove(client)
                                            self.routingInfos[words[0]]['clients'].append(clientParts[0])
                                        elif clientParts[1] not in self.routingInfos[words[0]]['subclients'][clientParts[0]]:
                                            self.routingInfos[words[0]]['subclients'][clientParts[0]].append(clientParts[1]) 
                                            self.routingInfos[words[0]]['clients'].remove(client)
                                        else:
                                            self.routingInfos[words[0]]['clients'].remove(client)
                                            print("Subclient %s of client %s is present more than once for header %s" % (clientParts[1], clientParts[0], words[0]))
                                    else:
                                        # When subclient (ex: BIRDZQZZ) is not defined in the subclient directive for the client (ex: aftn)
                                        print("Subclient %s is not acceptable for client %s (See header %s)" % (clientParts[1], clientParts[0], words[0]))
                                        self.routingInfos[words[0]]['clients'].remove(client)
                                else:
                                    # Subclient is not defined
                                    print("Client(%s) is not defined with subclient directive" % (clientParts[0]))
                                    self.routingInfos[words[0]]['clients'].remove(client)

                        
                except:
                    (type, value, tb) = sys.exc_info()
                    print("Type: %s, Value: %s" % (type, value))
                    print("Problem with this line (%s) in the direct routing file (%s)" % (words, self.filename))
        file.close()
        # Up to here: 2.3 s of execution time

    def printInfos(self):
        print "#---------------------------------------------------------------#"
        for header in self.routingInfos:
            print ("%s(%s): %s, sub: %s" % (header, self.routingInfos[header]['priority'], self.routingInfos[header]['clients'], self.routingInfos[header]['subclients']))
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
        self.logger.info("#---------------------------------------------------------------#")
        for alias in self.aliasedClients:
            self.logger.info("%s: %s" % (alias, self.aliasedClients[alias]))
        self.logger.info("#---------------------------------------------------------------#")
        self.logger.info("Good clients (%i): %s" % (len(self.goodClients), self.goodClients.keys()))
        self.logger.info("Bad clients (%i): %s" % (len(self.badClients), self.badClients.keys()))


if __name__ == '__main__':

    logger = Logger('/apps/px/aftn/log/parsing.log', 'DEBUG', 'Sub')
    logger = logger.getLogger()

    pxLinkables = ['cmc', 'aftn', 'satnet-ice']
    parser = DirectRoutingParser('/apps/px/aftn/etc/header2client.conf', pxLinkables, logger)
    #parser = DirectRoutingParser('/apps/px/aftn/etc/header2client.conf.test', pxLinkables, logger)
 
    #parser.printInfos()
    print("Good clients (%i): %s" % (len(parser.goodClients), parser.goodClients.keys()))
    print("Bad clients (%i): %s" % (len(parser.badClients), parser.badClients.keys()))

