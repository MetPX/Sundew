"""
#############################################################################################
# Name: RequestReplyAFTN.py
#
# Author: Daniel Lemay
#
# Date: 2006-08-07
#
# Description: 
#
#############################################################################################

"""
import os, sys, re, curses.ascii

sys.path.insert(1,sys.path[0] + '/..')
sys.path.insert(1,sys.path[0] + '/../importedLibs')

from DBSearcher import DBSearcher
from DirectRoutingParser import DirectRoutingParser
from PXManager import PXManager
import PXPaths; PXPaths.normalPaths()
import dateLib

class RequestReplyAFTN:

    def __init__(self, request, addOn, sendOn, logger):
        self.logger = logger
        self.addOn = addOn
        self.sendOn = sendOn
        self.drp = DirectRoutingParser(PXPaths.ROUTING_TABLE, [], logger)
        self.drp.printErrors = False
        self.drp.parseAndShowErrors()
        self.dbs = DBSearcher(request, False)
        self.results = self.dbs.results
        self.receiverName = 'request-reply'
        self.pxManager = PXManager()
        self.pxManager.setLogger(self.logger)
        self.pxManager.initNames()
        self.bulletin = ''
        self.constructBulletin()

    def putBulletinInQueue(self):
        try:
            filename = 'reply.' + dateLib.getTodayFormatted('%Y%m%d%H%M%S')
            path = self.pxManager.getFlowQueueName(self.receiverName, self.drp)
            file = open(path + '/' + filename, 'w')
            file.write(self.bulletin)
            file.close()
        except:
            (type, value, tb) = sys.exc_info()
            self.logger.error('In putBulletinInQueue: Type = %s, Value = %s' % (type, value))

    def constructBulletin(self):
        self.bulletin = ''
        speciResult = ''

        if self.dbs.requestType == 1:
            try:
                file = open(self.results, 'r')
                self.bulletin = file.read()
            except:
                (type, value, tb) = sys.exc_info()
                self.logger.error('In constructBulletin(): Type =  %s, Value = %s' % (type, value))

        elif self.dbs.requestType == 2:
           for result in self.results:
               if self.dbs.type == 'SA':
                   station, theLine, bestHeaderTime, theFile, bestFileTime, speciLine, speciHeaderTime, speciFile, speciFileTime = result
               else:
                   station, theLine, bestHeaderTime, theFile, bestFileTime = result
               
               if theFile:
                   parts = os.path.basename(theFile).split('_')
                   header = parts[0] + ' ' + parts[1]
                   new_header = self.drp.getKeyFromHeader(header)
                   # We verify if we can include the result in the reply (consult the routing table)
                   try:
                       if self.sendOn not in self.drp.getHeaderClients(new_header):
                           self.logger.warning("%s has been excluded of reply for %s" % (new_header, self.sendOn))
                           continue
                       else:
                           pass
                           """
                           clients = self.drp.getHeaderClients(header) 
                           clients.sort()
                           self.logger.info("%s has been accepted in the reply for %s (in %s)" % (header, self.sendOn, str(clients)))
                           """
                   except:
                       (type, value, tb) = sys.exc_info()
                       self.logger.error("Type: %s, Value: %s" % (type, value))
                       self.logger.warning("%s has been excluded of reply for %s" % (new_header, self.sendOn))
                       continue
   
                   self.bulletin =  self.bulletin + header + ' ' + bestHeaderTime + '\n' + theLine.strip() + '\n\n'
                   #print repr(theLine)
                   if self.dbs.type == 'SA' and speciLine:
                       speciHeader = header[0] + 'P' + header[2:]
                       speciResult = speciHeader + ' ' + speciHeaderTime + '\n' + speciLine.strip() + '\n\n'
                       self.bulletin = speciResult + self.bulletin
            
        if self.bulletin:
            self.bulletin = self.addOn + self.bulletin

        #print self.bulletin
        return self.bulletin

if __name__ == '__main__':
    import dateLib
    from Logger import *

    logger = Logger('/apps/px/log/RequestReplyAFTN.log.notb', 'DEBUG', 'requ')
    logger = logger.getLogger()

    addOn = 'AACN44 CWAO %s\nATTN %s\n\n' % (dateLib.getYYGGgg(), 'FAKEADDR')
    addOn = 'AACN02 ANIK %s\nATTN %s\n\n' % (dateLib.getYYGGgg(), 'FAKEADDR')
    
    sendOn = 'amis'

    request = RequestReplyAFTN(' '.join(sys.argv[1:]), addOn, sendOn, logger)
    request.putBulletinInQueue()
