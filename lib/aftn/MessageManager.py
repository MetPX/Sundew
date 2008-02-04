"""
#############################################################################################
# Name: MessageManager.py
#
# Author: Daniel Lemay
#
# Date: 2005-10-27
#
# Description:
#
#############################################################################################

"""
import os, sys, time, commands, re, curses.ascii, re, pickle

sys.path.insert(1,sys.path[0] + '/..')

from MessageAFTN import MessageAFTN
from bulletinManager import bulletinManager
from DiskReader import DiskReader
from StateAFTN import StateAFTN
import AFTNPaths, PXPaths
from  StationParser import StationParser
import dateLib

class MessageManager:

    """
    A typical message:

    <SOH> ABC0003 14033608<CR><LF>                               <-- Heading line
    GG CYYCYFYX EGLLZRZX<CR><LF>                                 <-- Destination address line
    140335 CYEGYFYX<CR><LF>                                      <-- Origin address line

    <STX>040227 NOTAMN CYYC CALGARY INTL<CR><LF>                 <-- Start of text signal (<STX>)
    CYYC ILS 16 AND 34 U/S 0409141530<CR><LF>                    <-- Message text
    TIL 0409141800<CR><LF>

    <VT><ETX>                                                    <-- End of message signal

    """

    def __init__(self, logger=None, sourlient=None, reloadMode=False):
        
        AFTNPaths.normalPaths()
        PXPaths.normalPaths()

        self.logger = logger         # Logger object
        self.sourlient = sourlient   # Sourlient object

        self.name = sourlient.name                       # Transceiver's name
        self.stationID = sourlient.stationID             # Value read from config. file
        self.otherStationID = sourlient.otherStationID   # Provider (MHS) Station ID
        self.address = sourlient.address                 # 8-letter group identifying the message originator (CYHQUSER)
        self.otherAddress = sourlient.otherAddress       # 8-letter group identifying the provider's address (CYHQMHSN)
        self.routingTable = sourlient.routingTable       # Routing table name
        self.subscriber = sourlient.subscriber           # Boolean indicating if this is a subscriber or a provider

        self.bullManager = bulletinManager(PXPaths.RXQ + self.name,
                                      self.logger,
                                      PXPaths.RXQ + self.name,
                                      9999,
                                      '\n',
                                      self.sourlient.extension,
                                      self.routingTable, 
                                      None,
                                      self.sourlient,
                                      True) 

        self.drp = self.bullManager.drp
        self.sp = StationParser(PXPaths.STATION_TABLE, logger)
        self.sp.parse()
        self.priorities = {'1':'FF', '2':'FF', '3':'GG', '4':'GG', '5':'GG'}

        if not reloadMode:
            self.afterInit()

    def afterInit(self):
        self.messageIn = None  # Last AFTN message received
        self.messageOut = None # Last AFTN message sent
        self.fromDisk = True   # Changed to False for Service Message created on the fly
        self.filenameToSend = None  # Filename of the file we want to send or just sent
        self.filenameToErase = None # Path + filename of the file we want to erase (ack just received) 

        self.type = None       # Message type. Value must be in ['AFTN', 'SVC', 'RF', 'RQ', 'PRI_DESTADD_TEXT', None]
        self.header = None     # Message WMO Header
        self.priority = None   # Priority indicator (SS, DD, FF, GG or KK)
        self.destAddress = []  # 8-letter group, max. 21 addresses
        self.CSNJustReset = False 
        try:
            self.CSN = self.state.CSN
            self.logger.info("CSN (%s) has been taken from AFTN State" % self.CSN)
        except: 
            self.CSN = '0000'      # Channel sequence number, 4 digits (ex: 0003)
        self.filingTime = None # 6-digits DDHHMM (ex:140335) indicating date and time of filing the message for transmission.
        self.dateTime = None   # 8-digits DDHHMMSS (ex:14033608)
        self.readBuffer = ''   # Buffer where we put stuff read from the socket
        
        # Queueing Service Messages when waiting for an ack before sending
        self.serviceQueue = []

        # Big message support (sending)
        self.partsToSend = []                       # Text parts of the broken message
        self.numberOfParts = len(self.partsToSend)  # Number of parts in which a long message has been divided.
        self.nextPart = 0                           # Always 0 for message that are not bigger than the defined max. 

        # Big message support (receiving)
        self.receivedParts = []
        self.notCompletelyReceived = False
        self.generalPartsRegex = re.compile(r"//END PART \d\d//")
        self.lastPartRegex = re.compile(r"//END PART \d\d/\d\d//")

        # Ack support (ack we receive because of the message we have sent)
        try:
            self.lastAckReceived = self.state.lastAckReceived  
            self.logger.info("lastAckReceived (%s) has been taken from AFTN State" % self.lastAckReceived)

            self.waitingForAck = self.state.waitingForAck 
            self.logger.info("waitingForAck (%s) has been taken from AFTN State" % self.waitingForAck)
        except:
            self.lastAckReceived = None   # None or the transmitID
            self.waitingForAck = None     # None or the transmitID 

        self.sendingInfos = (0, None) # Number of times a message has been sent and the sending time.
        self.maxAckTime =  self.sourlient.maxAckTime  # Maximum time (in seconds) we wait for an ack, before resending.
        self.maxSending = 1   # Maximum number of sendings of a message
        self.ackUsed =  self.sourlient.ackUsed  # We can use ack or not (testing purposes only)
        self.totAck = 0       # Count the number of ack (testing purpose only)

        # CSN verification (receiving)
        try:
            self.waitedTID = self.state.waitedTID
        except:
            self.waitedTID = self.otherStationID + '0001'  # Initially (when the program start) we are not sure what TID is expected
            

        # Functionnality testing switches
        self.resendSameMessage = True

        # Read Buffer management
        self.unusedBuffer = ''        # Part of the buffer that was not used

        # Persistent state
        min = 60
        now = time.mktime(time.gmtime())

        if self.subscriber:
            try:
                lastUpdate = os.stat(AFTNPaths.STATE)[8]
                diff = now - lastUpdate
                if diff < 60 * min:
                    self.state = self.unarchiveObject(AFTNPaths.STATE)
                    self.updateFromState(self.state)
                else: 
                    self.logger.warning("Archive state not read because too old (%i minutes)" % int(diff/60))
                    raise
            except:
                self.state = StateAFTN()
                self.state.fill(self)
                self.archiveObject(AFTNPaths.STATE, self.state)
        else:
            try:
                self.state = self.unarchiveObject(AFTNPaths.STATE)
                self.updateFromState(self.state)
            except:
                self.state = StateAFTN()
                self.state.fill(self)
                self.archiveObject(AFTNPaths.STATE, self.state)

    def resetCSN(self):
        hhmm = dateLib.getTodayFormatted('%H%M')
        hh = hhmm[:2]
        mm = hhmm[2:]

        if hh == '00' and mm <= '05' and not self.CSNJustReset:
            self.CSN = '0000'
            self.CSNJustReset = True
            self.logger.info('CSN has been reset to 0001')
        elif mm > '05':
            self.CSNJustReset = False
        
    def updateFromState(self, state):
        self.CSN = state.CSN
        self.waitedTID = state.waitedTID

        self.lastAckReceived = state.lastAckReceived
        self.waitingForAck = state.waitingForAck
    
    def ingest(self, bulletin):
        self.bullManager.writeBulletinToDisk(bulletin)

    def completeHeader(self, message):
        import dateLib
        wmoMessage = ''
        theHeader = ''
        allLines = []
        # We remove blank lines
        for  line in message.textLines:
            if line:
                allLines.append(line)
        
        # We don't have enough lines
        if len(allLines) < 2:
            return ['\n'.join(message.textLines) + '\n']

        messageType = allLines[0][:2]
        station = allLines[1].split()[0]

        headers = self.sp.headers.get(station, [])
        for header in headers:
            if header[:2] == messageType:
                theHeader = header

        if theHeader:
            BBB = ''
            firstLine = allLines[0].split()
            timestamp = firstLine[1]
            if len(firstLine) >= 3:
                BBB = firstLine[2]

            self.logger.debug("Type: %s, Station: %s, Headers: %s, TheHeader: %s, Timestamp: %s, BBB = %s" % (messageType, station, headers, theHeader, timestamp, BBB))
            allLines[0] = theHeader + ' ' + timestamp
            if BBB:
                allLines[0] += ' ' + BBB
            allLines.insert(1, 'AAXX ' + timestamp[:4] + '4')
        else:
            return ['\n'.join(message.textLines) + '\n']
            
        return ['\n'.join(allLines) + '\n']

    def addHeaderToMessage(self, message, textLines=None):
        """
        When no WMO header is present in the text part of an AFTN Message, we will create one 
        for each destination address in the message.
        ex: if self.drp.aftnMap['CWAOWXYZ'] == 'SACN32', the header will be 'SACN32 CWAO YYGGgg'
        where YY= day of the month, GG=hours and gg=minutes
        This method is only used at reception.

        textLines is not None for big messages (text is not in the message, but in a supplementary 
        variable.
        """
        import dateLib
        wmoMessages = []
        addresses = message.destAddress
        default = self.drp.aftnMap.get('DEFAULT')
        timestamp = dateLib.getYYGGgg()

        destLine = message.createDestinationAddressLine().strip() 
        originLine = message.createOriginAddressLine().strip() 

        destOriginLines = [destLine, originLine]

        self.logger.debug("Addresses: %s" % addresses)

        for address in addresses:
            header = self.drp.aftnMap.get(address, default) + " " + address[0:4] + " " + timestamp
            headerBlock = [header] + destOriginLines

            #self.logger.info("Header in addHeader: %s" % header)
            if textLines:
                wmoMessages.append('\n'.join(headerBlock + textLines) + '\n')
            else:
                wmoMessages.append('\n'.join(headerBlock + message.textLines) + '\n')
        return wmoMessages

    def doSpecialOrders(self, path):
        # Stop, restart, reload, deconnect, connect could be put here?
        reader = DiskReader(path)
        reader.read()
        dataFromFiles = reader.getFilenamesAndContent()
        for index in range(len(dataFromFiles)): 
            words = dataFromFiles[index][0].strip().split() 
            self.logger.info("Special Order: %s" % (dataFromFiles[index][0].strip()))

            if words[0] == 'outCSN':
                if words[1] == '+':
                    self.nextCSN()
                    self.logger.info("CSN = %s" % self.CSN)
                elif words[1] == '-':
                    # This case is only done for testing purpose. It is not complete and not correct when CSN 
                    # value is 0 or 1
                    self.nextCSN(str(int(self.CSN) - 2))
                    self.logger.info("CSN = %s" % self.CSN)
                elif words[1] == 'print':
                    self.logger.info("CSN = %s" % self.CSN)
                else:
                    # We suppose it's a number, we don't verify!!
                    self.nextCSN(words[1])
                    self.logger.info("CSN = %s" % self.CSN)

            elif words[0] == 'inCSN':
                if words[1] == '+':
                    self.calcWaitedTID(self.waitedTID)
                    self.logger.info("Waited TID = %s" % self.waitedTID)
                elif words[1] == '-':
                    # This case is only done for testing purpose. It is not complete and not correct when waited TID
                    # value is 0 or 1
                    self.calcWaitedTID(self.otherStationID + "%04d" % (int(self.waitedTID[3:]) - 2))
                    self.logger.info("Waited TID = %s" % self.waitedTID)
                elif words[1] == 'print':
                    self.logger.info("Waited TID = %s" % self.waitedTID)
                else:
                    # We suppose it's a number, we don't verify!!
                    self.calcWaitedTID(self.otherStationID + "%04d" % int(words[1]))
                    self.logger.info("Waited TID = %s" % self.waitedTID)

            elif words[0] == 'ackWaited':
                if words[1] == 'print':
                    self.logger.info("Waiting for ack: %s" % self.getWaitingForAck())
                else:
                    self.setWaitingForAck(words[1])
                    self.incrementSendingInfos()
            elif words[0] == 'ackNotWaited':
                self.setWaitingForAck(None)
                self.resetSendingInfos()
                self.updatePartsToSend()
            elif words[0] == 'ackUsed':
                self.ackUsed = words[1] == 'True' or words[1] == 'true'
            elif words[0] == 'printState':
                self.logger.info(self.state.infos()) 
            else:
                pass

            try:
                os.unlink(dataFromFiles[0][1])
                self.logger.debug("%s has been erased", os.path.basename(dataFromFiles[index][1]))
            except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (dataFromFiles[index][1], type, value))

    def deleteFile(self,file):
        try:
            os.unlink(dataFromFiles[0][1])
            self.logger.debug("%s has been erased", os.path.basename(dataFromFiles[index][1]))
        except OSError, e:
            (type, value, tb) = sys.exc_info()
            self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (dataFromFiles[index][1], type, value))

    def isFromDisk(self):
        return self.fromDisk

    def setFromDisk(self, value):
        self.fromDisk = value

    def archiveObject(self, filename, object):
        file = open(filename, "wb")
        pickle.dump(object, file)
        file.close()

    def unarchiveObject(self, filename):
        file = open(filename, "rb")
        object = pickle.load(file)
        file.close()
        return object

    def calcWaitedTID(self, tid):
        self.setWaitedTID(tid[:3] + self.calcNextCSNString(tid[3:]))

    def setWaitedTID(self, tid):
        self.waitedTID = tid
    def getWaitedTID(self):
        return self.waitedTID

    def parseReadBuffer(self, readBuffer):
        buffer =  self.unusedBuffer + readBuffer
        # It's the beginning of a message (AFTN or ACK)
        if len(buffer):
            if buffer[0] == MessageAFTN.SOH:
                # This is an ACK message ...
                if buffer[1] == MessageAFTN.ACK:
                    endPos = buffer.find(MessageAFTN.ETX)
                    # We find the end of the ACK
                    if endPos != -1:
                        self.unusedBuffer = buffer[endPos+1:]
                        return (buffer[:endPos+1], 'ACK')
                    else:
                        self.unusedBuffer = buffer
                        return ("", 'ACK')
    
                # This is an AFTN message ...
                else:
                    endPos = buffer.find(MessageAFTN.END_OF_MESSAGE)
                    # We find the end of the AFTN Message 
                    if endPos != -1:
                        self.unusedBuffer = buffer[endPos+2:]
                        return (buffer[:endPos+2], 'AFTN')
                    else:
                        self.unusedBuffer = buffer
                        return ("", 'AFTN')
    
            # We should never go here ...
            else:
                self.unusedBuffer = ""
                self.logger.error("Our buffer doest'n begin with <SOH>: %s" % buffer)
        else: 
            self.logger.debug("Our buffer is empty")
            return ("", "")

    def isItPart(self, lines):
        # If someone resend because he has not received the ack? 
        # What do we want to do with this case?
        if self.generalPartsRegex.search(lines[-1]):
            self.receivedParts.extend(lines[:-1])
            self.notCompletelyReceived = True
            return 1
        elif self.notCompletelyReceived and self.lastPartRegex.search(lines[-1]):
            self.receivedParts.extend(lines[:-1])
            self.notCompletelyReceived = False
            return -1
        else:
            return 0

    def completePartsToSend(self, parts):
        self.nextPart = 0
        self.numberOfParts = len(parts)
        numberOfPartsString = str(self.numberOfParts)
        if self.numberOfParts == 1:
            return
        elif self.numberOfParts > 1:
            firstChar = (lambda x: x<10 and '0' or '')(self.numberOfParts)
            parts[-1] += '//END PART %s/%s//' % (firstChar + numberOfPartsString, firstChar + numberOfPartsString) + MessageAFTN.ALIGNMENT
            for i in range(self.numberOfParts-1):
                parts[i] += '//END PART %s//' % ((lambda x: x<10 and '0' or '')(i+1) + str(i+1)) + MessageAFTN.ALIGNMENT
    
    def isLastPart(self):
        if self.nextPart + 1 == self.numberOfParts:
            return True
        else:
            return False

    def updatePartsToSend(self):
        # Some more parts to send
        if self.nextPart + 1 < self.numberOfParts:
            del self.partsToSend[0]
            self.nextPart += 1
        else:
            self.clearPartsToSend()

    def clearPartsToSend(self):
        self.partsToSend = []
        self.numberOfParts = 0
        self.nextPart = 0

    def messageEndReceived(self, text, type):
        if type == 'AFTN':
            position = MessageAFTN.positionOfEndOfMessage(text)
        elif type == 'ACK':
            position = AckAFTN.positionOfEndOfMessage(text)

        if position != -1:
            if type == 'AFTN':
                if len(text)-2 == position:
                    #print  "Well placed Ending"
                    return True
                else:
                    print "Badly placed ending"
                    return False
            elif type == 'ACK':
                if len(text)-1 == position:
                    #print  "Well placed Ending"
                    return True
                else:
                    print "Badly placed ending"
                    return False

        else:
            print "No valid ending"
            print "Type=%s, Text=%s" % (type, text)
        return False

    def getMaxAckTime(self):
        return self.maxAckTime
    def getMaxSending(self):
        return self.maxSending

    def getNbSending(self):
        return self.sendingInfos[0]
    def getLastSendingTime(self):
        return self.sendingInfos[1]
    def resetSendingInfos(self):
        self.sendingInfos = (0, None)
    def incrementSendingInfos(self):
        self.sendingInfos = (self.sendingInfos[0] + 1, time.time())

    def getWaitingForAck(self):
        return self.waitingForAck
    def setWaitingForAck(self, tid):
        self.waitingForAck = tid
    
    def getLastAckReceived(self):
        return self.lastAckReceived
    def setLastAckReceived(self, tid):
        self.lastAckReceived = tid 

    def readConfig(self, filename):
        try:
            config = open(filename, 'r')
        except IOError:
            (type, value, tb) = sys.exc_info()
            print "Type: %s Value: %s (Try to open %s)" % (type, value, filename)
            sys.exit(103)

        configLines = config.readlines()

        for line in configLines:

            if line.isspace(): # we skip blank line
                continue

            words = line.split()

            if words[0] == 'stationID':
                self.stationID = words[1]
            elif words[0] == 'otherStationID':
                self.otherStationID = words[1]
            elif words[0] == 'originatorAddress':
                self.originatorAddress = words[1]
            elif words[0] == 'otherAddress':
                self.otherAddress = words[1]
            elif words[0] == '':
                pass
            elif words[0] == 'titi':
                pass

        config.close()

    def validateAddresses(self, addresses):
        goodAddresses = []
        addressLength = 8
        for address in addresses:
            if len(address) == addressLength and address.isalpha():
                goodAddresses.append(address)
            elif len(address) != addressLength:
                self.logger.warning("Address %s rejected (Not %d characters)" % (address, addressLength))
            elif not address.isalpha():
                self.logger.warning("Address %s rejected (Not entirely alpha)" % (address))
        return goodAddresses

    def setInfos(self, header, rewrite=False):
        """
        Informations obtained in the DirectRoutingParser object are assigned to instance variables.
        This method is only used when SENDING messages.
        """
        header = self.drp.getKeyFromHeader(header)
        if header in self.drp.routingInfos:
            self.priority = self.priorities[self.drp.getHeaderPriority(header)]
            self.destAddress = self.validateAddresses(self.drp.getHeaderSubClients(header).get(self.name, []))
            if self.destAddress == []:
                self.logger.warning("No destination address for header %s and client %s" % (header, self.name))
                return False
            #if not rewrite:
            self.setFilingTime()
            self.nextCSN()
            return True
        elif header == None:
            self.logger.warning("No header found in the message")
            return False
        else:
            self.logger.warning("Header %s is not in the routing table" % (header))
            return False

    def printInfos(self):
        print "**************************** Infos du Message Manager *****************************"
        print "Header: %s" % self.header
        print "Station ID: %s" % self.stationID
        print "Other Station ID: %s" % self.otherStationID
        print "Originator Address: %s" % self.address
        print "Other Address: %s" % self.otherAddress
        print "Priority: %s" % self.priority
        print "Destination Addresses: %s" % self.destAddress
        print "Filing Time: %s" % self.filingTime
        print "Date Time: %s" % self.dateTime
        print "CSN: %s" % self.CSN
        print "********************************** Fin(Manager) ***********************************"
        print "\n"

    def reduceCSN(self):
        if self.CSN == '0000':
            self.CSN = '9999'
        else: 
            self.CSN = "%04d" % (int(self.CSN.lstrip('0')) - 1)

    def calcNextCSNString(self, CSNString):

        if CSNString == '0000':
            CSNString = '0001'

        elif CSNString == '9999':
            CSNString = '0000'

        else:
            number = int(CSNString.lstrip('0'))
            number += 1
            CSNString = "%04d" % number

        return CSNString

    def nextCSN(self, number=None):
        """
        The CSN sequence number is comprised of four (4) digits, and shall run from
        0001 to 0000 (representing 10000), then start over at 0001. The number series and
        configuration shall be discrete for each destination. A new series, starting at 0001,
        shall begin at the start of a new day (0001Z UTC) for each destination.
        """
        #FIXME: We will have to check time before setting the CSN
        if number:
            self.CSN = self.calcNextCSNString(number)
        else:
            self.CSN = self.calcNextCSNString(self.CSN)

    def setFilingTime(self):
        self.filingTime = time.strftime("%d%H%M")
        self.dateTime = time.strftime("%d%H%M%S")


if __name__ == "__main__":

    import sys
    sys.path.insert(1,sys.path[0] + '/../../lib/importedLibs')

    from Logger import *
    from MessageAFTN import MessageAFTN
    from DiskReader import DiskReader
    from MessageParser import MessageParser
    from Sourlient import Sourlient

    logger = Logger('/apps/px/aftn/log/mm.log', 'DEBUG', 'mm')
    logger = logger.getLogger()

    sourlient = Sourlient('aftn', logger)

    print "Longueur Max = %d" % MessageAFTN.MAX_TEXT_SIZE

    mm = MessageManager(logger, sourlient)

   
    reader = DiskReader("/apps/px/bulletins", 8)
    reader.read()
    reader.sort()
    """
    for file in reader.getFilesContent(8):
       print file
       mm.setInfos(MessageParser(file).getHeader())
       mm.printInfos()
       if mm.header:
          myMessage = MessageAFTN(logger, file, mm.stationID, mm.originatorAddress,mm.priority,
                                  mm.destAddress, mm.CSN, mm.filingTime, mm.dateTime)

          myMessage.printInfos()

    """
    for file in reader.getFilesContent(8):
          #mm.setInfos('AACN02 CWAO13')
          myMessage = MessageAFTN(logger, file, mm.stationID, mm.address, 'GG',
                                  ['BIRDZQZZ', 'CYYZOWAC'], mm.CSN, '121800' , '12180001')
          #myMessage = MessageAFTN(logger, file, mm.stationID, mm.address, mm.priority,
          #                        mm.destAddress, mm.CSN, mm.filingTime, mm.dateTime)

          myMessage.printInfos()
          print mm.addHeaderToMessage(myMessage)
          
