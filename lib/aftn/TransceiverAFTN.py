"""
#############################################################################################
# Name: TransceiverAFTN.py
#
# Author: Daniel Lemay
#
# Date: 2005-10-14
#
# Description: 
#
#############################################################################################

"""
import os, sys, time, commands, socket, select, traceback

sys.path.insert(1,sys.path[0] + '/../lib')
sys.path.insert(1,sys.path[0] + '/../etc')
sys.path.insert(1,sys.path[0] + '/../../lib')
sys.path.insert(1,sys.path[0] + '/../../lib/importedLibs')

from DiskReader import DiskReader
from SystemManager import SystemManager
from MessageManager import MessageManager
from MessageParser import MessageParser
from MessageAFTN import MessageAFTN
from AckAFTN import AckAFTN
from TextSplitter import TextSplitter
import AFTNPaths, PXPaths

class TransceiverAFTN:
    """
    When started, a subscriber AFTN will listen on a port (56550), whishing to be
    connected by the AFTN provider. If this does not happen rapidly enough (before 
    the timeout expires), the subscriber will try to connect (port 5160) to the 
    provider.
    """
    def __init__(self, sourlient):

        AFTNPaths.normalPaths(sourlient.name)
        PXPaths.normalPaths()
        self.sysman = SytemManager()                       # General system manager
        self.sourlient = sourlient                         # Sourlient (Source/Client) object containing configuration infos.

        self.logger = sourlient.logger                     # Logger object
        self.subscriber = sourlient.subscriber             # Determine if it will act like a subscriber or a provider(MHS)
        self.host = sourlient.host                         # Remote host (name or ip)
        self.portR = sourlient.portR                       # Receiving port
        self.portS = sourlient.portS                       # Sending port
        
        self.batch = sourlient.batch                       # Number of files we read in a pass (20)
        self.timeout = sourlient.timeout                   # Timeout time in seconds (default = 10 seconds)
        self.sleepBetweenConnect = int('10')               # Time (in seconds) between connection trials 
        self.slow = sourlient.slow                         # Sleeps are added when we want to be able to decrypt log entries
        self.igniter = None                                # Igniter object (link to pid)

        self.mm = MessageManager(self.logger, self.sourlient)  # AFTN Protocol is implemented in MessageManager Object
        self.remoteAddress = None                          # Remote address (where we will connect())
        self.socket = None                                 # Socket object
        self.dataFromFiles = []                            # A list of tuples (content, filename) obtained from a DiskReader 

        self.writePath = AFTNPaths.RECEIVED                # Where we write messages we receive
        self.archivePath = AFTNPaths.SENT                  # Where we put sent messages
        self.specialOrdersPath = AFTNPaths.SPECIAL_ORDERS  # Where we put special orders

        # Paths creation
        self.sysman.createDir(self.writePath)
        self.sysman.createDir(self.archivePath)
        self.sysman.createDir(self.specialOrdersPath)

        self.reader = DiskReader(PXPaths.TXQ + self.sourlient.name, self.sourlient.batch,
                                 self.sourlient.validation, self.sourlient.diskReaderPatternMatching,
                                 self.sourlient.mtime, True, self.logger, eval(self.sourlient.sorter), self.sourlient)
        
        self.debug = True  # Debugging switch
        self.justConnect = False  # Boolean that indicates when a connexion just occur
        
        self.totBytes = 0

        #self.printInitInfos()
        self.makeConnection()
        #self.run()

    def setIgniter(self, igniter):
        self.igniter = igniter

    def printInitInfos(self):
        print("********************* Init. Infos ****************************")
        print("Remote Host: %s" % self.host)
        print("Port R: %s" % self.portR)
        print("Port S: %s" % self.portS)
        print("Remote Address: %s" % self.remoteAddress)
        print("Timeout: %4.1f" % self.timeout)
        print("Write Path: %s" % self.writePath)
        print("Subscriber: %s" % self.subscriber)
        print("**************************************************************")

    def reconnect(self):
        try:
            #poller.unregister(self.socket.fileno())
            self.socket.close()
        except:
            (type, value, tb) = sys.exc_info()
            self.logger.error("Unable to close the socket! Type: %s, Value: %s" % (type, value))

        # FIXME: Possibly some variable resetting should occur here?
        self.logger.info("Sleeping %d seconds (just before makeConnection())" % (self.sleepBetweenConnect))
        time.sleep(self.sleepBetweenConnect)
        self.makeConnection()

    def makeConnection(self):
        if self.subscriber:
            # The Subscriber first listens for a connection from Provider(MHS)
            self.socket = self._listen(self.portR, self.logger)
            if self.socket:
                self.logger.info("Subscriber has been connected by Provider")
                #self.run()
            else:
                # The Subscriber try to connect to the Provider(MHS)
                self.remoteAddress = (self.host, self.portS)
                self.logger.info("The subscriber will try to connect to MHS(%s)" % str(self.remoteAddress))
                self.socket = self._connect(self.remoteAddress, self.logger)
                #self.run()

        else: # Provider(MHS) case
            # The Provider first try to connect to the Subscriber
            self.remoteAddress = (self.host, self.portS)
            self.socket = self._connect(self.remoteAddress, self.logger)
            if self.socket:
                self.logger.info("Provider has completed the connection")
                #self.run()
            else:
                # The Provider(MHS) listens for a connection from Subscriber
                self.socket = self._listen(self.portR, self.logger)
                if self.socket:
                    self.logger.info("Provider has been connected by the subscriber")
                    #self.run()
                else:
                    self.logger.error("No socket (NONE)")
        self.justConnect = True
        

    def _connect(self, remoteAddress, logger):
        trials = 0
        if self.subscriber:
            maxTrials = 1000
        else:
            maxTrials = 3 

        while trials < maxTrials:
            if trials == 12:
                self.sleepBetweenConnect = 60
            socketSender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketSender.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            socketSender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socketSender.settimeout(self.timeout)
            #print socketSender.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            #socketSender.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,4096)
            #print socketSender.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            #socketSender.setblocking(True)
            trials += 1
            try:
                socketSender.connect(remoteAddress)
                logger.info("Sender is now (after %d trial(s)) connected to: %s" % (trials, str(remoteAddress)))
                break
            except socket.gaierror, e:
                logger.error("Address related error connecting to receiver: %s" % e)
                sys.exit(1)
            except socket.error, e:
                (type, value, tb) = sys.exc_info()
                logger.error("Type: %s, Value: %s, Sleeping %d seconds ..." % (type, value, self.sleepBetweenConnect))
                socketSender.close()
                socketSender = None
                time.sleep(self.sleepBetweenConnect)

        self.sleepBetweenConnect = 10
        return socketSender

    def _listen(self, port, logger):
        socketReceiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketReceiver.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        socketReceiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.subscriber:
            socketReceiver.settimeout(self.timeout)
        #print socketReceiver.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        #socketReceiver.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,4096)
        #print socketReceiver.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        #socketReceiver.setblocking(True)

        try:
            socketReceiver.bind(('', port))
            logger.info("Receiver is bound with local port %d" % port)

        except socket.gaierror, e:
            logger.error("Address related error when binding receiver port: %s" % e)
            sys.exit(1)

        except socket.error, e:
            (type, value, tb) = sys.exc_info()
            logger.error("Type: %s, Value: %s, Sleeping 5 seconds ..." % (type, value))
            time.sleep(5)

        socketReceiver.listen(1)
        logger.info("Receiver is listening")

        while True:
            try:
                logger.info("Receiver is waiting for a connection (block on accept() for %d seconds)" % self.timeout)
                conn, clientAddress = socketReceiver.accept()
                socketReceiver.close()
                socketReceiver = conn
                logger.info("Connexion established with %s" % str(clientAddress))
                break

            except socket.timeout, e:
                (type, value, tb) = sys.exc_info()
                logger.error("Type: %s, Value: %s, Timeout exceeded ..." % (type, value))
                socketReceiver.close()
                return None

            except socket.error, e:
                (type, value, tb) = sys.exc_info()
                logger.error("Type: %s, Value: %s, Sleeping 2 seconds ..." % (type, value))
                time.sleep(2)

        return socketReceiver

    def getStates(bitfield, names=False):
        # Return the good result for the bits 1,2,4,8,16,32 of the bitfield.
        # Imply that number going from 0 to 63 will be perfectly decomposed

        pollConst = {1:'POLLIN', 2:'POLLPRI', 4:'POLLOUT', 8:'POLLERR', 16:'POLLHUP', 32:'POLLNVAL'}

        bits = []
        for i in range(6):
            if bitfield >> i & 1:
                bits.append(2**i)
        if names:
            bitNames = []
            for value in bits:
                if value in pollConst:
                    bitNames.append(pollConst[value])
            return bitNames 
        else:
            return bits 
    getStates = staticmethod(getStates)

    def run(self):
        mm = self.mm
        poller = select.poll()
        poller.register(self.socket.fileno(), select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)
        firstIter = True

        while True:
            try:
                if self.justConnect:
                    # Because we wait for an ack, it means that:
                    # a) The other party has never received our message and we have to resend
                    # b) The other party has received our message and sent his ack, ack that we never received
                    # Conclusion: resend the message
                    if mm.waitingForAck is not None:
                        mm.resetSendingInfos()
                        mm.reduceCSN()
                        self.logger.debug("CSN has been reduced (%s)" % mm.CSN)

                        if firstIter:
                            mm.clearPartsToSend()
                            CSN = mm.waitingForAck[3:]
                            self.logger.debug("CSN extract from ack is %s" % CSN)
                            message = mm.unarchiveObject(self.archivePath + CSN)
                            #print message.textString

                            mm.partsToSend = [message.textString]
                            # Will add //END PART 01//\n\r  or //END PART 03/03//\n\r
                            mm.completePartsToSend(mm.partsToSend)

                        mm.setWaitingForAck(None)
                        mm.setFromDisk(False)
                        self._writeMessageToSocket([mm.partsToSend[0]], True, mm.nextPart)
                        mm.setFromDisk(True)

                    self.justConnect = False

                firstIter = False

                # If service messages are in queue and we are not waiting for an ack ...
                if len(mm.serviceQueue) and not mm.getWaitingForAck():
                   data, destAddresses = mm.serviceQueue.pop(0)
                   mm.partsToSend = [data]
                   mm.completePartsToSend(mm.partsToSend)  
                   mm.setFromDisk(False)
                   self._writeMessageToSocket([mm.partsToSend[0]], False, mm.nextPart, destAddresses)
                   mm.setFromDisk(True)
                    
                # These special orders are useful to simulate problems ...
                mm.doSpecialOrders(self.specialOrdersPath)

                # Reset the CSN if it is the time
                mm.resetCSN()
                
                pollInfos = poller.poll(100)
                if len(pollInfos):
                    states = TransceiverAFTN.getStates(pollInfos[0][1], True)
                    #print states
                    if 'POLLIN' in states:
                        # Here we read data from socket, write it on disk and write on the socket
                        # if necessary
                        self.readFromSocket()
                    if 'POLLHUP' in states:
                        self.logger.info("Socket has been hung up (POLLHUP)")
                        poller.unregister(self.socket.fileno())
                        self.reconnect()
                        poller.register(self.socket.fileno(), select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)
                        continue
                        # FIXME: Possibly some variable resetting should occur here?
                    if 'POLLERR' in states:
                        self.logger.info("Socket error (POLLERR)")
                        poller.unregister(self.socket.fileno())
                        self.reconnect()
                        poller.register(self.socket.fileno(), select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)
                        continue
    
                # Here we read a file from disk (if we're not waiting for an ack and don't have some parts of a
                # big message to send) and write it on the socket
                if not mm.getWaitingForAck():
                    # Do we have some parts of a big message to send?
                    if len(mm.partsToSend):
                        self._writeMessageToSocket([mm.partsToSend[0]], False, mm.nextPart)
                    else:
                        self.readFromDisk()
                    # For testing Ack+Mess back to back in the buffer
                    #if self.subscriber:
                    #    time.sleep(7)
    
                # Too long time without receiving an ack, we may have to resend ...
                elif time.time()-mm.getLastSendingTime() > mm.getMaxAckTime():
                    if mm.getNbSending() < mm.getMaxSending():
                        # Should never be here since maxSending is 1 (No retransmission)
                        self.logger.info("We will rewrite a message (max ack time over)")
                        self._writeMessageToSocket([mm.partsToSend[0]], True, mm.nextPart)
                    else:
                        #self.logger.error("Maximum number (%s) of retransmissions have occured without receiving an ack." % mm.getMaxSending())
                        self.logger.error("Maximum waiting time (%s seconds) has passed without receiving an ack. We will try to reconnect!" % mm.getMaxAckTime())
                        poller.unregister(self.socket.fileno())
                        self.reconnect()
                        poller.register(self.socket.fileno(), select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)
                        continue
            except:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Error in TransceiverAFTN.run()! Type: %s, Value: %s" % (type, value))
                traceback.print_exc()
                poller.unregister(self.socket.fileno())
                self.reconnect()
                poller.register(self.socket.fileno(), select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)

    def readFromDisk(self):
        # If our buffer is empty, we read data from disk
        if not len(self.dataFromFiles):
            self.reader.read()
            self.dataFromFiles = self.reader.getFilenamesAndContent(self.batch) 
        # If it is still empty, we quit
        if not len(self.dataFromFiles):
            #self.logger.warning("No data to read on the disk")
            if self.slow:
                time.sleep(2)
        else:
            # Break the bulletin in the number of appropriate parts (possibly only one)
            self.mm.partsToSend = TextSplitter(self.dataFromFiles[0][0], MessageAFTN.MAX_TEXT_SIZE, MessageAFTN.ALIGNMENT, 
                                               MessageAFTN.TEXT_SPECIFIC_OVERHEAD).breakLongText()

            # Will add //END PART 01//\n\r  or //END PART 03/03//\n\r
            self.mm.completePartsToSend(self.mm.partsToSend)

            assert self.mm.nextPart == 0, "Next part not equal to zero when sending the first part of a message"
            self._writeMessageToSocket([self.mm.partsToSend[0]], False, self.mm.nextPart)

    def readFromSocket(self):
        replyAFTN = ''
        mm = self.mm
        
        buf = self.socket.recv(32768)

        if len(buf): 
            self.logger.debug('Raw Buffer: %s' % repr(buf))
            message, type = mm.parseReadBuffer(buf) # Only to find if it is an AFTN (SVC included) or Ack message
            while message:
                if type == 'AFTN':
                    ##############################################################################################
                    # An AFTN Message has been read on the socket. It can be a SVC Message or a 
                    # Standard Message.
                    ##############################################################################################
                    self.logger.debug("AFTN Message: %s" % repr(message))
                    mm.messageIn = MessageAFTN(self.logger)
                    mm.messageIn.setMessage(message)
                    if not mm.messageIn.messageToValues():
                        # Here we have a problem because our parser is unable to parse the message. We print the message,
                        # get the next message if present and quit the method (no ack sent, no tid verification)
                        self.logger.error("Method MessageAFTN.messageToValues() has not worked correctly (returned 0)")
                        self.logger.error(mm.messageIn.textLines)
                        message, type = mm.parseReadBuffer("") # Only to find if it is an AFTN (SVC included) or Ack message
                        continue

                    self.logger.debug(mm.messageIn.textLines)

                    self.logger.debug('Message as it has been received:')
                    self.logger.debug('\n' + mm.messageIn.message)

                    status = mm.isItPart(mm.messageIn.textLines)

                    # Not part of a big message, possibly a SVC message
                    if status == 0:
                        suffix = 'NOT_SVC_NOR_AFTN'
                        mp = MessageParser(mm.messageIn.textLines)
                        textType = mp.getType()
                        if textType == "SVC": 
                            ##############################################################################################
                            # A Service  Message has been read on the socket. 
                            ##############################################################################################
                            suffix = 'SVC'
                            self.logger.info("SVC Message Received(%s): %s (%s)" % (mm.messageIn.getTransmitID(), str(mm.messageIn.getTextLines()), MessageParser.names.get(mp.serviceType,
                                              "The service type of this message is unknown. Contact NavCanada")))

                            #if mp.serviceType in [8, 9]:
                            #    self.logger.info("*********************** SERVICE MESSAGE *****************************")
                            #    self.logger.info(str(mm.messageIn.getTextLines()))
                            #    self.logger.info("********************* END SERVICE MESSAGE ***************************")

                        elif textType == "AFTN":
                            suffix = ''
                            if mp.getHeader() in ['SI', 'SM']:
                                # Only one message will be in messages
                                messages = mm.completeHeader(mm.messageIn)

                            elif mp.getHeader(): 
                                # Only one message will be in messages
                                messages = ['\n'.join(mm.messageIn.textLines) + '\n'] 
                            else:
                                # Create headers before ingesting
                                messages = mm.addHeaderToMessage(mm.messageIn)

                            # Ingest in met px
                            for m in messages:
                                mm.ingest(m)

                        elif textType in ['RQ', 'RF']:
                            suffix = textType
                            # request for amis or metser
                            from RequestReplyAFTN import RequestReplyAFTN
                            import dateLib
                            date = dateLib.getYYGGgg()
                            if textType == 'RQ': # amis
                                addOn = 'AACN02 ANIK %s\nATTN %s\n\n' % (date, mm.messageIn.originatorAddress)
                                replyAFTN = 'RQM '
                            elif textType == 'RF': # metser
                                addOn = 'AACN44 CWAO %s\nATTN %s\n\n' % (date, mm.messageIn.originatorAddress)
                                replyAFTN = 'RQF '

                            self.logger.info('AFTN Request Received: Type = %s, Value = %s' % (textType, mp.request))

                            # We want to put the answer on amis or metser.
                            try:
                                rr = RequestReplyAFTN(mp.request, addOn, mp.sendOn, self.logger)
                            except:
                                (type, value, tb) = sys.exc_info()
                                self.logger.error("In RequestReplyAFTN: Type = %s, Value = %s" % (type, value))

                            if rr.bulletin:
                                self.logger.info('Reply is not empty, we will put bulletin in the queue of receiver %s and send an OK message' % rr.receiverName)
                                # bulletin is not empty, put it in queue and create an "OK" message
                                rr.putBulletinInQueue()
                                replyAFTN += 'OK'
                            else:
                                self.logger.info('Request is empty, we will send an UNK message')
                                # bulletin is empty, create an "UNK" message
                                replyAFTN += 'UNK'

                        elif textType in ['RQM_UNK', 'RQM_OK', 'RQF_UNK', 'RQM_OK']:
                        # reply about a request. I think a request never originates from us,
                        # so we should never receive such a reply.
                            suffix = textType
                            self.logger.info("Reply received is: %s" % textType)

                        # We keep one copy of all received messages in a special AFTN directory
                        file = open(self.writePath + mm.messageIn.getName() + suffix, 'w')
                        for line in mm.messageIn.textLines:
                            file.write(line + '\n')
                        file.close()

                    # General part of a big message
                    elif status == 1:
                        self.logger.debug("We are in section 'General part of a big message'")
                        pass
                    # Last part of a big message
                    elif status == -1:
                        file = open(self.writePath + mm.messageIn.getName(), 'w')
                        for line in mm.receivedParts:
                            file.write(line + '\n')
                        file.close()

                        # We must ingest the bulletin contained in the message in the px system
                        lines = [line.strip() for line in mm.receivedParts]
                        mp = MessageParser(lines)

                        if mp.getHeader(): 
                            # Only one message will be in messages
                            messages = ['\n'.join(lines) + '\n'] 
                        else:
                            # Create headers before ingesting
                            messages = mm.addHeaderToMessage(mm.messageIn, lines)

                        # Ingest in met px
                        for m in messages:
                            mm.ingest(m)

                        mm.receivedParts = []

                    # FIXME: The number of bytes include the ones associated to the protocol overhead,
                    # maybe a simple substraction should do the job.
                    self.logger.info("(%i Bytes) Message %s has been received" % (len(mm.messageIn.getTextString()), mm.messageIn.getName()))
                    
                    if mm.ackUsed:
                        self._writeAckToSocket(mm.messageIn.getTransmitID())
                        mm.totAck += 1
                        #if mm.totAck == 5:
                        #    mm.ackUsed = False 

                    ##############################################################################################
                    # Is the CSN Order correct? Maybe Service Message would have to be sent?
                    ##############################################################################################
                    tid = mm.messageIn.getTransmitID()
                    if tid == mm.getWaitedTID():
                        self.logger.debug("The TID received (%s) is in correct order" % tid)
                    elif mm.getWaitedTID() == None:
                        self.logger.debug("Waited TID is None => the received TID (%s) is the first since the program start" % tid)
                    else:
                        self.logger.error("The TID received (%s) is not the one we were waiting for (%s)" % (tid, mm.getWaitedTID()))
                        if int(mm.getWaitedTID()[3:]) - int(tid[3:]) == 1:
                            self.logger.error("Difference is 1 => Probably my ack has been lost (or is late) and the other side has resend")
                        # FIXME: A SVC Message should be sent here. Given the fact that we receive the same message
                        # again, can we conclude that it is a retransmission (because our ack has not been received)
                        # or an error in numbering message?
                        diffCSN = int(tid[3:])- int(mm.getWaitedTID()[3:])
                        if diffCSN < 0:
                            messageText = "SVC LR %s EXP %s" % (tid, mm.getWaitedTID())

                        # FIXME: This implementation is done with only a partial comprehension of how this 
                        # message should work. Should be completed later...
                        elif diffCSN > 0: 
                            if diffCSN == 1:
                                messageText = "SVC QTA MIS %s" % mm.getWaitedTID()
                            else:
                                lastCSN = "%04d" % (int(tid[3:]) - 1)
                                messageText = "SVC QTA MIS %s-%s" % (mm.getWaitedTID(), lastCSN)

                        if not mm.getWaitingForAck():
                            mm.partsToSend = [messageText]
                            mm.completePartsToSend(mm.partsToSend)  
                            mm.setFromDisk(False)
                            self._writeMessageToSocket([mm.partsToSend[0]], False, mm.nextPart)
                            mm.setFromDisk(True)
                        else:
                            # We queue the message to send it after we receive the ack we wait for.
                            self.logger.info("A service message (%s) will be queued" % messageText)
                            mm.serviceQueue.append((messageText, []))
                            
                    mm.calcWaitedTID(tid)

                    ##############################################################################################
                    # Do we have to send a reply to a request?
                    ##############################################################################################
                    if replyAFTN:
                        if not mm.getWaitingForAck():
                            self.logger.debug("A reply (%s) to a request will be sent immediately" % replyAFTN)
                            mm.partsToSend = [replyAFTN]
                            mm.completePartsToSend(mm.partsToSend)  
                            mm.setFromDisk(False)
                            self._writeMessageToSocket([mm.partsToSend[0]], False, mm.nextPart, [mm.messageIn.originatorAddress])
                            mm.setFromDisk(True)
                        else:
                            # We queue the message to send it after we receive the ack we wait for.
                            self.logger.info("A reply (%s) to a request will be queued (because we are waiting for an ack)" % replyAFTN)
                            mm.serviceQueue.append((replyAFTN, [mm.messageIn.originatorAddress]))

                elif type == 'ACK':
                    ##############################################################################################
                    # An Ack Message has been read on the socket. 
                    ##############################################################################################
                    self.logger.debug("Ack Message: %s" % repr(message))
                    strippedMessage = message[2:9]
                    mm.setLastAckReceived(strippedMessage)
                    if mm.getLastAckReceived() == mm.getWaitingForAck():
                        mm.setWaitingForAck(None)
                        mm.resetSendingInfos()
                        mm.updatePartsToSend()
                        self.logger.info("Ack received is the ack we wait for: %s" % strippedMessage)
                    else:
                        # FIXME: When deconnexion occurs, it is possible that we received an ack for a previously sent message???
                        self.logger.error("Ack received (%s) is not the ack we wait for: %s" % (strippedMessage, mm.getWaitingForAck()))
                        if mm.getWaitingForAck() == None:
                            pass
                        elif int(mm.getWaitingForAck()[3:]) - int(strippedMessage[3:]) == 1:
                            self.logger.error("Difference is 1 => Probably my original message + the one I resend have been hacked (Timing problem)")

                # Archive State
                mm.state.fill(mm)
                mm.archiveObject(AFTNPaths.STATE, mm.state)
                self.logger.debug("State has been archived")

                message, type = mm.parseReadBuffer("") # Only to find if it is an AFTN (SVC included) or Ack message
                if not message and type:
                    self.logger.debug("Message (type=%s) uncomplete. It's ok. We will try to complete it in the next pass." % type)

        else:
            # If we are here, it normally means the other side has hung up(not sure in this case, because I use
            # select. Maybe it simply not block and return 0 bytes? Maybe it's correct to do nothing and act 
            # only when the POLLHUP state is captured?
            # FIXME: POLLHUP is never present, I don't know why?
            self.logger.error("Zero byte have been read on the socket (Means the other side has HUNG UP?)")
            raise Exception("Zero byte have been read on the socket (Means the other side has HUNG UP?)")
            
    def _writeToDisk(self, data):
        pass

    def _writeAckToSocket(self, transmitID):
        ack = AckAFTN(transmitID)
        ackMessage = ack.getAck()
        printableAck = ackMessage[2:-1]

        self.socket.send(ackMessage)
        self.logger.info("(%5d Bytes) Ack: %s sent" % (len(ackMessage), printableAck))

    def _writeMessageToSocket(self, data, rewrite=False, nextPart=0, destAddresses=None):

        def getWord(type):
            """ Used to create logging text only """
            if type:
                return '(type: %s)' % type
            else:
                return '(type: UNKNOWN)'

            """
            if type == 'SVC':
                return '(type: SVC)'
            elif type == 'AFTN':
                return '(type: AFTN)'
            elif type == 'RF':
                return '(type: RF)'
            elif type == 'RQ':
                return '(type: RQ)'
            elif type == 'RQM_OK':
                return '(type: RQM_OK)'
            elif type == 'RQM_UNK':
                return '(type: RQM_UNK)'
            elif type == 'RQF_OK':
                return '(type: RQF_OK)'
            elif type == 'RQF_UNK':
                return '(type: RQF_UNK)'
            else:
                return '(type: UNKNOWN)'
            """

        mm = self.mm
        if len(data) >= 1:
            if not rewrite:
                self.logger.info("%d new bulletin will be sent" % len(data))
            else:
                self.logger.info("%d new bulletin will be resent (ack not received / reconnexion)" % len(data))

            for index in range(len(data)):
                if nextPart == 0:
                    # We will have access to the first part of the message here (big or not)
                    mp = MessageParser(data[index], mm, self.logger, True)
                    mm.header, mm.type = mp.getHeader(), mp.getType()
                    self.logger.debug("Header: %s, Type: %s" % (mm.header, mm.type))
                if mm.header== None and mm.type==None:
                    self.logger.info(data[index])
                    self.logger.error("Header %s is not in %s" % (mm.header, mm.routingTable))
                    if self.slow:
                        time.sleep(10)
                    os.unlink(self.dataFromFiles[0][1])
                    self.logger.info("%s has been erased", os.path.basename(self.dataFromFiles[0][1]))
                    del self.dataFromFiles[0]
                    mm.clearPartsToSend()
                    continue

                elif mm.header == None and mm.type=='SVC':
                    #FIXME: Is it possible to rewrite Service Message?
                    # If so, the CSN must not change!
                    mm.setFilingTime()
                    mm.nextCSN()
                    messageAFTN = MessageAFTN(self.logger, data[index], mm.stationID, mm.address, MessageAFTN.PRIORITIES[2],
                                              destAddresses or [mm.otherAddress], mm.CSN, mm.filingTime, mm.dateTime)
                    #self.logger.debug('\n' + messageAFTN.message)
                    #messageAFTN.setLogger(None)
                    #mm.archiveObject(self.archivePath + mm.CSN, messageAFTN)

                elif mm.header == None and mm.type in ['RQ', 'RF']:
                    # We will never have to sent such a message, it is only
                    # there for tests purposes
                    mm.setFilingTime()
                    mm.nextCSN()
                    messageAFTN = MessageAFTN(self.logger, data[index], mm.stationID, mm.address, MessageAFTN.PRIORITIES[2],
                                              destAddresses or [mm.otherAddress], mm.CSN, mm.filingTime, mm.dateTime)
                    #self.logger.debug('\n' + messageAFTN.message)
                    #messageAFTN.setLogger(None)
                    #mm.archiveObject(self.archivePath + mm.CSN, messageAFTN)

                elif mm.header == None and mm.type in MessageParser.REPLY_TYPES:
                    mm.setFilingTime()
                    mm.nextCSN()
                    messageAFTN = MessageAFTN(self.logger, data[index], mm.stationID, mm.address, MessageAFTN.PRIORITIES[3],
                                              destAddresses, mm.CSN, mm.filingTime, mm.dateTime)
                    #self.logger.debug('\n' + messageAFTN.message)
                    #messageAFTN.setLogger(None)
                    #mm.archiveObject(self.archivePath + mm.CSN, messageAFTN)

                elif mm.type == 'PRI_DESTADD_TEXT':
                    mm.destAddress = mp.destAddress
                    if mm.destAddress:
                        mm.priority = mp.priority
                        mm.setFilingTime()
                        mm.nextCSN()
                        messageAFTN = MessageAFTN(self.logger, mp.text, mm.stationID, mm.address, mm.priority, mm.destAddress, mm.CSN, mm.filingTime, mm.dateTime)
                    else:
                        if mm.isFromDisk():
                            try:
                                self.logger.warning("%s has been erased (no valid destination address)", os.path.basename(self.dataFromFiles[0][1]))
                                os.unlink(self.dataFromFiles[0][1])
                            except OSError, e:
                                (type, value, tb) = sys.exc_info()
                                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (self.dataFromFiles[0][1], type, value))
                            del self.dataFromFiles[0]
                            mm.clearPartsToSend()
                        continue

                else:
                    # True if mm.header is in the routing table with destination addresses
                    #if mm.header == None: mm.header = 'SACN31 CWAO'
                    if mm.setInfos(mm.header, rewrite):
                        messageAFTN = MessageAFTN(self.logger, data[index], mm.stationID, mm.address, mm.priority,
                                              mm.destAddress, mm.CSN, mm.filingTime, mm.dateTime)
                    else:
                        if mm.isFromDisk():
                            try:
                                self.logger.warning("%s has been erased", os.path.basename(self.dataFromFiles[0][1]))
                                os.unlink(self.dataFromFiles[0][1])
                            except OSError, e:
                                (type, value, tb) = sys.exc_info()
                                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (self.dataFromFiles[0][1], type, value))
                            del self.dataFromFiles[0]
                            mm.clearPartsToSend()

                        continue
                        
                # If it is the first time we sent this message, we archive it.
                #if not rewrite:
                self.logger.debug('Message as it will be sent:')
                self.logger.debug('\n' + messageAFTN.message)
                messageAFTN.setLogger(None)
                mm.archiveObject(self.archivePath + mm.CSN, messageAFTN)

                nbBytesToSend = len(messageAFTN.message)

                while nbBytesToSend > 0:
                    nbBytesSent = self.socket.send(messageAFTN.message)
                    # This sleep is machiavelic! It permits to see many potential problems
                    #if self.subscriber:
                    #    time.sleep(5)
                    messageAFTN.message = messageAFTN.message[nbBytesSent:]
                    nbBytesToSend = len(messageAFTN.message)
                    self.totBytes += nbBytesSent

                mm.setWaitingForAck(messageAFTN.getTransmitID())
                mm.incrementSendingInfos()

                # Archive State
                mm.state.fill(mm)
                mm.archiveObject(AFTNPaths.STATE, mm.state)
                self.logger.debug("State has been archived")

                # Log the fact that the message has been sent 
                if not rewrite:
                    if mm.isFromDisk():
                        mm.filenameToSend = os.path.basename(self.dataFromFiles[0][1])
                        mm.filenameToErase = self.dataFromFiles[0][1]
                    else:
                        if mp.type == 'SVC':
                            mm.filenameToSend = mp.getServiceName(mp.getServiceType())
                        elif mp.type in MessageParser.REPLY_TYPES:
                            mm.filenameToSend = ''
                        else:
                            # We should never go here
                            self.logger.error("Unknown message type has just been sent. See code!")

                    self.logger.info("(%5d Bytes) Message %s %s (%s/%s) has been sent => delivered" % (self.totBytes, getWord(mm.type), 
                                       mm.filenameToSend, mm.nextPart+1, mm.numberOfParts))
                else:
                    self.logger.info("(%5d Bytes) Message %s %s (%s/%s) has been resent => delivered" % (self.totBytes, getWord(mm.type), 
                                       mm.filenameToSend, mm.nextPart+1, mm.numberOfParts))

                # Reset byte count
                self.totBytes = 0
                
                # If the last part of a message (big or not) has been sent, erase the file.
                # We do this even if we have not yet received the ack. At this point, we have already
                # archived all the parts with their CSN as filename.
                if mm.isLastPart(): 
                    if mm.isFromDisk() and not rewrite:
                        try:
                            os.unlink(self.dataFromFiles[0][1])
                            self.logger.debug("%s has been erased", os.path.basename(self.dataFromFiles[0][1]))
                        except OSError, e:
                            (type, value, tb) = sys.exc_info()
                            self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (self.dataFromFiles[0][1], type, value))
                        del self.dataFromFiles[0]

                if self.slow: 
                    time.sleep(1)
        else:
            time.sleep(1)

if __name__ == "__main__":
    from Logger import Logger
    from MessageAFTN import MessageAFTN
    from Sourlient import Sourlient
    import curses.ascii

    """
    #message = MessageAFTN()
    #text = 'abc' + 'def' + chr(curses.ascii.VT) + chr(curses.ascii.ETX)
    #text = 'abc' + 'def' + chr(curses.ascii.VT) + chr(curses.ascii.ETX) + 'ghi'
    #text = 'abc' + 'def' + chr(curses.ascii.VT) + chr(curses.ascii.ETX) 
    text = 'abc' + 'def' + chr(curses.ascii.VT)

    print text
    if MessageAFTN.positionOfEndOfMessage(text) != -1:
        if len(text)-2 == MessageAFTN.positionOfEndOfMessage(text):
            print  "Well placed Ending"
        else:
            print "Badly placed ending"
    else:
        print "No valid ending"

    """

    if sys.argv[1] == "sub":
        logger = Logger('/apps/px/aftn/log/subscriber.log', 'DEBUG', 'Sub')
        logger = logger.getLogger()
        sourlient = Sourlient('aftn', logger)
        #subscriber = TransceiverAFTN('localhost', 56550, 5160, logger)
        #subscriber = TransceiverAFTN('192.168.250.3', 56550, 5160, logger)
        subscriber = TransceiverAFTN(sourlient)
        subscriber.run()


        #print TransceiverAFTN.getStates(63)
        #print TransceiverAFTN.getStates(63, True)
    elif sys.argv[1] == "pro":
        logger = Logger('/apps/px/aftn/log/provider.log', 'DEBUG', 'Pro')
        logger = logger.getLogger()
        sourlient = Sourlient('aftnPro', logger)

        #provider = TransceiverAFTN('localhost', 5160, 56550, logger, False)
        provider = TransceiverAFTN(sourlient)
        provider.run()

    """
    for i in range(64):
        print TransceiverAFTN.getStates(i)
    """
   
