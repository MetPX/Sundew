"""
#############################################################################################
# Name: MessageAFTN.py
#
# Author: Daniel Lemay
#
# Date: 2005-10-27
#
# Description:
#
#############################################################################################

"""
import os, sys, re, curses.ascii

sys.path.insert(1,sys.path[0] + '/..')
sys.path.insert(1,sys.path[0] + '/../importedLibs')

class MessageAFTN:

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
    DEBUG = 1
    MAX_TOTAL_SIZE = 2100 # Total printable and non-printable character count
                          # (header + text + ender) shall not exceed 2100 char.
    MAX_TEXT_SIZE = 1800  # Text portion must not exceed 1800 characters including spacing
    MAX_TOTAL_OVERHEAD = MAX_TOTAL_SIZE - MAX_TEXT_SIZE  # <SOH> .... <VTX><ETX>
    TEXT_SPECIFIC_OVERHEAD = 5 # <STX(1)>...<VTX(2)><ETX(3)> (Maybe a <CR(4)><LF(5)> on the last line of text)

    PRIORITIES = ["SS", "DD", "FF", "GG", "KK"]                   # Priority indicators
    END_OF_MESSAGE = chr(curses.ascii.VT) + chr(curses.ascii.ETX) # <VT><ETX>
    ALIGNMENT = chr(curses.ascii.CR) + chr(curses.ascii.LF)       # <CR><LF>
    SOH = chr(curses.ascii.SOH)
    STX = chr(curses.ascii.STX)
    ETX = chr(curses.ascii.ETX)
    ACK = chr(curses.ascii.ACK)

    # For TEXT portion of the AFTN message, use only the following CAPITALIZED characters, numerals and signs
    TEXT_CHARS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                  '-', '?', ':', '(', ')', '.', ',', "'", '=', '/', '+', '"']

    def __init__(self, logger, text=None, stationID=None, originatorAddress=None, priority=None, destAddress=None,
                 CSN=None, filingTime=None, dateTime=None):

        # The logger object
        self.logger = logger

        self.header = None              # Heading line, Destination address line, Origin address line

        # Parts of Heading line (ex:<SOH> ABC0003 14033608<CR><LF>)
        self.headingLine = None
        self.stationID = stationID      # 3 Letters assigned by NavCanada for each circuit (ex: ABC)
        self.CSN = CSN                  # Channel sequence number, 4 digits (ex: 0003)
        self.transmitID = None          # stationID + CSN (ex: ABC0003)
        self.dateTime = dateTime        # 8-digits DDHHMMSS (ex:14033608)

        # Parts of Destination address line (ex:GG CYYCYFYX EGLLZRZX<CR><LF>)
        #self.regexDestinationAddressLine = re.compile(
        self.destinationAddressLine = None
        self.priority = priority             # Priority indicator (SS, DD, FF, GG or KK)
        self.destAddress = destAddress or [] # 8-letter group, max. 21 addresses

        # Parts of Origin address line (ex:140335 CYEGYFYX<CR><LF>)
        #self.regexOriginAddressLine = re.compile(r'^
        self.originAddressLine = None
        self.filingTime = filingTime        # 6-digits DDHHMM (ex:140335) indicating date and
                                            # time of filing the message for transmission.

        self.originatorAddress = originatorAddress    # 8-letter group identifying the message originator (CYEGYFYX)

        # Content of the text is mainly the responsability of the originator, the following rules apply:
        # 1) Use authorized abbreviations wherever possible.
        # 2) Only 69 printed characters per line.
        # 3) The TEXT portion of the AFTN message must not exceed 1800 characters including spacing.
        # 4) Use only the following CAPITALIZED characters, numerals and signs:
        #    ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-?:().,'=/+"
        # An alignment function <CR-LF> is required at the end of each line.
        self.textBlock = None  # String begining with <STX> and with "alignement" between lines
        self.textLines = []    # Lines of text without linefeed, or any unwanted symbols

        # The complete message(a string)
        self.message = None

        # The complete message separated in lines
        self.messageLines = []

        if text is not None:
            self.textString = text
            self.setText(text)
        else:
            self.textString = None

        if stationID and CSN is not None:
            self.transmitID = stationID + CSN

        if priority:
            self.message = self.createMessage()

    def setLogger(self, logger):
        self.logger = logger

    def getTransmitID(self):
        return self.transmitID

    def getName1(self):
        words = self.textLines[0].split()
        if len(words) >= 3:
            firstWords = words[0] + '_' + words[1] + '_' + words[2]
        elif len(words) == 2:
            firstWords = words[0] + '_' + words[1]
        elif len(words) == 1:
            firstWords = words[0]

        return "%s_%s_%s" % (self.transmitID, self.dateTime, firstWords) 

    def getName(self):
        return "%s_%s" % (self.stationID, self.CSN)

    def positionOfEndOfMessage(text, END_OF_MESSAGE=END_OF_MESSAGE):
        return text.find(END_OF_MESSAGE)
    positionOfEndOfMessage = staticmethod(positionOfEndOfMessage)

    def clearMessage(self):
        self.header = None

        self.headingLine = None
        self.stationID = None
        self.CSN = None
        self.transmitID = None
        self.dateTime = None

        self.destinationAddressLine = None
        self.priority = None
        self.destAddress = []

        self.originAddressLine = None
        self.filingTime = None
        self.originatorAddress = None

        self.textBlock = None
        self.textLines = []

        self.message = None
        self.messageLines = []

    def __repr__(self):
        return  """
Header: 
%s 
HeadingLine: %s
Transmit ID: %s
Station ID: %s
CSN: %s
DateTime: %s

Destination Address Line: %s 
Priority: %s
Destination Addresses: %s

Origin Address Line: %s 
Filing Time: %s
Originator Address: %s

Text Block:
%s

Text lines: 
%s

Message:
 %s

Message Lines: %s

Message (repr):
%s 
        """ % (self.header, self.headingLine, self.transmitID, self.stationID, self.CSN, self.dateTime, self.destinationAddressLine,
               self.priority, self.destAddress, self.originAddressLine, self.filingTime, self.originatorAddress, self.textBlock, self.textLines, 
               self.message, self.messageLines, repr(self.message))

    def printInfos(self):
        print("******************************** Infos du Message *********************************")
        print("Header: %s" % self.header)

        print("HeadingLine: %s" % self.headingLine)
        print("Station ID: %s" % self.stationID)
        print("CSN: %s" % self.CSN)
        print("Transmit ID: %s" % self.transmitID)
        print("DateTime: %s" % self.dateTime)

        print("Destination Address Line: %s" % self.destinationAddressLine)
        print("Priority: %s" % self.priority)
        print("Destination Addresses: %s" % self.destAddress)

        print("Origin Address Line: %s" % self.originAddressLine)
        print("Filing Time: %s" % self.filingTime)
        print("Originator Address: %s" % self.originatorAddress)

        print("Text Block: %s" % self.textBlock)
        print("Text lines: %s" % self.textLines)
        print("Text string: %s" % self.textString)

        print("Message: %s" % self.message)
        print("Message Lines: %s" % self.messageLines)

        print("Message (repr): \n" + repr(self.message))
        print("*********************************** Fin (Message) *********************************")
        print("\n")

    def setMessage(self, message):
        self.message = message

    def setText(self, textString):
        self.textLines = textString.splitlines()

    def getTextString(self):
        return self.textString

    def getTextLines(self):
        return self.textLines

    def messageToValues(self):
        """ 
        Used  only at RECEPTION of an AFTN Message
        """
        self.message = self.message.replace('\r\r\n', '\r\n')
        self.messageLines = self.message.splitlines()
        if self._parseHeadingLine(self.messageLines[0]):
            if self._parseDestinationAddressLine(self.messageLines[1:4]):
                if self._parseOriginAddressLine(self.messageLines[2:5]):
                    if self._parseText():
                        return 1
        return 0

    def _parseHeadingLine(self, line):
        """ 
        Used  only at RECEPTION of an AFTN Message
        """
        #print "LINE: %s" % line
        if line[0] == MessageAFTN.SOH and line[1] == ' ' and len(line) == 18:
            self.stationID = line[2:5]
            self.CSN = line[5:9]
            self.transmitID = line[2:9]
            self.dateTime = line[10:18]
            if self.logger:
                self.logger.debug("Space is present and HeadingLine's length is 18 characters")
            return 1
        elif line[0] == MessageAFTN.SOH and line[1] != ' ' and len(line) == 17:
            self.stationID = line[1:4]
            self.CSN = line[4:8]
            self.transmitID = line[1:8]
            self.dateTime = line[9:17]
            if self.logger:
                self.logger.debug("Space is absent and HeadingLine's length is 17 characters")
            return 1
        else:
            if self.logger:
                self.logger.error("Problem with HeadingLine, first char is not space or line length not equal 18")
            return 0

    def _parseDestinationAddressLine(self, lines):
        """ 
        Used  only at RECEPTION of an AFTN Message
        """
        addressLength = 8 # Length of one address
        line1 = lines[0]
        line2 = ''
        line3 = ''

        if len(lines) == 3:
            if lines[1][0].isalpha(): line2 = lines[1]
            if lines[2][0].isalpha(): line3 = lines[2]
        elif len(lines) == 2:
            if lines[1][0].isalpha() and lines[1][0]: line2 = lines[1]

        #print "Line1: %s" % line1
        #print "Line2: %s" % line2
        #print "Line3: %s" % line3

        parts = line1.split()
        addOnLine2 = line2.split()
        addOnLine3 = line3.split()
        numberOfAddress = len(parts) - 1 + len(addOnLine2) + len(addOnLine3)

        if numberOfAddress >= 1:
            if parts[0] in MessageAFTN.PRIORITIES:
                self.priority = parts[0]
            else:
                if self.logger:
                    self.logger.error("Priority %s is not acceptable (not in %s)" % (self.priority, MessageAFTN.PRIORITIES))
                return 0

            #for index in range(numberOfAddress):
            #    self.destAddress.append(line[3+index*addressLength:11+index*addressLength])
            for address in parts[1:] + addOnLine2 + addOnLine3:
                if len(address) == addressLength and address.isalpha() and address.isupper():
                    self.destAddress.append(address)
                else:
                    if self.logger:
                        self.logger.error("Address (%s) is not acceptable (Not 8 char, or char other than alpha)" % address)
            if len(self.destAddress) >= 1:
                return 1
            else:
                if self.logger:
                    self.logger.error("Zero destination address for this message (after removing the bad ones)")
                return 0
        else:
            if self.logger:
                self.logger.error("Problem with Destination Address Line, Zero Address!")
            return 0

    def _parseOriginAddressLine(self, lines):
        """ 
        Used  only at RECEPTION of an AFTN Message
        """
        for line in lines:
            if line[0].isdigit():
                theLine = line
                break

        if len(theLine) >= 15:
            self.filingTime = theLine[0:6]
            self.originatorAddress = theLine[7:15]

            #print self.filingTime
            #print self.originatorAddress
            
            if len(theLine) > 15:
                if self.logger:
                    self.logger.error("Unknown characters in Origin Address Line (length > 15 chars): %s" % line)

            return 1

    def _parseText(self):
        """ 
        Used  only at RECEPTION of an AFTN Message
        Text must begin at line 3, 4 or 5
        """
        for index in [3,4,5]:
            try:
                if self.messageLines[index][0] == MessageAFTN.STX:
                    theIndex = index
                    break
            except IndexError:
                if self.logger:
                    self.logger.error("Problem with STX")
                return 0
        
        if self.messageLines[-1] == MessageAFTN.END_OF_MESSAGE:
            self.textLines = self.messageLines[theIndex:-1]   # Remove END_OF_MESSAGE line
            self.textLines[0] = self.textLines[0][1:]  # Remove <STX> char
            self.textString = '\n'.join(self.textLines)
            return 1
        else:
            if self.logger:
                self.logger.error("Problem with STX or End of Message signal (<VT><ETX>)")
            return 0

    def createMessage(self):
        self.header = self._createHeader()
        self.textBlock = self._createText()
        return self.header + self.textBlock + MessageAFTN.END_OF_MESSAGE

    def _createHeader(self):
        self.headingLine = self._createHeadingLine()
        self.destinationAddressLine = self.createDestinationAddressLine()
        self.originAddressLine = self.createOriginAddressLine()

        return self.headingLine + self.destinationAddressLine + self.originAddressLine

    def _createHeadingLine(self):
        #print "HeadingLine: %s %s %s%s" % (MessageAFTN.SOH, self.transmitID, self.dateTime, MessageAFTN.ALIGNMENT)
        return "%s%s %s%s" % (MessageAFTN.SOH, self.transmitID, self.dateTime, MessageAFTN.ALIGNMENT)

    def createDestinationAddressLine(self):
        """
        Only used when SENDING messages
        """
        if len(self.destAddress) == 0:
            if self.logger:
                self.logger.error("No destination addresses for this AFTN Message")

        if len(self.destAddress) > 21:
            addresses = self.destAddress[:21]
            cutAddresses = self.destAddress[21:]
            
            if self.logger:
                self.logger.warning("More than 21 addresses! These addresses (%s) have been cut" % cutAddresses)

        else:
            addresses = self.destAddress[:]

        counter = 0
        addressLine = " "
        for address in addresses:
            counter += 1
            if counter%7 == 1: addressLine += address
            elif counter%7 == 0: addressLine +=  " " + address + MessageAFTN.ALIGNMENT
            else: addressLine += " " + address

        if not addressLine.endswith(MessageAFTN.ALIGNMENT): addressLine += MessageAFTN.ALIGNMENT
        return self.priority + addressLine

    def createOriginAddressLine(self):
        #print "Origin Line: %s %s%s" % (self.filingTime, self.originatorAddress, MessageAFTN.ALIGNMENT)
        return "%s %s%s" % (self.filingTime, self.originatorAddress, MessageAFTN.ALIGNMENT)

    def _createText(self):
        textBlock = MessageAFTN.STX

        for line in self.textLines:
            textBlock += line + MessageAFTN.ALIGNMENT

        return textBlock


if __name__ == "__main__":

    from Logger import Logger
    import string
    """
    from DiskReader import DiskReader

    reader = DiskReader("/apps/px/bulletins")
    reader.read()
    reader.sort()
    reader.getFilesContent()

    print reader.data[0]
    print "\n\n"

    myMessage = MessageAFTN()
    myMessage.setText(reader.data[0])
    myMessage.message = myMessage.createMessage()

    print myMessage.message

    print reader.data

    print myMessage.textLines

    """
    logger = Logger('/apps/px/aftn/log/messageAFTN.log', 'DEBUG', 'message')
    logger = logger.getLogger()
    myMessage = MessageAFTN(logger)

    myMessage.message = myMessage.SOH + " ABC0044 14033608" + myMessage.ALIGNMENT + "GG CYYCYFYX AAAABBBB CCCCDDDD" + myMessage.ALIGNMENT + \
                     "140335 CYEGYFYX" + myMessage.ALIGNMENT + myMessage.STX + "04227 NOTAMN CYYC CALGARY INTL\r\n" + \
                     "CYYC ILS 16 AND 34 U/S 049141530\r\nTIL 040914800\r\n" + myMessage.END_OF_MESSAGE


    print(myMessage.message)
    myMessage.messageToValues()

    print("=========================================")
    print(myMessage.stationID)          # 3 Letters assigned by NavCanada for each circuit (ex: ABC)
    print(myMessage.CSN)                # Channel sequence number, 4 digits (ex: 0003)
    print(myMessage.transmitID)         # stationID + CSN (ex: ABC0003)
    print(myMessage.dateTime)           # 8-digits DDHHMMSS (ex:14033608)
    print(myMessage.priority)           # Priority indicator (SS, DD, FF, GG or KK)
    print(myMessage.destAddress)        # 8-letter group, max. 21 addresses
    print(myMessage.filingTime)         # 6-digits DDHHMM (ex:140335) indicating date and time of filing the message for transmission.
    print(myMessage.originatorAddress)  # 8-letter group identifying the message originator (CYEGYFYX)
    print("=========================================")

    myMessage.destAddress = []
    addresses = [ 8*x for x in string.uppercase]
    counter = 0
    nbAdd = 9 

    for address in addresses:
        counter += 1 
        if counter > nbAdd:
            break
        else:
            myMessage.destAddress.append(address)

    print(myMessage.destAddress)

    message = myMessage.createMessage()
    print(message)

    newMessage = MessageAFTN(logger)
    newMessage.setMessage(message)
    
    if newMessage.messageToValues():
        newMessage.createMessage()
        print(newMessage)
    else:
        print("PROBLEM WITH messageToValues()")
        
