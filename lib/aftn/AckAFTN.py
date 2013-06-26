"""
#############################################################################################
# Name: AckAFTN.py
#
# Author: Daniel Lemay
#
# Date: 2005-12-06
#
# Description: Acknowledge Message for AFTN protocol.
#
#############################################################################################
"""
import os, re, curses.ascii

class AckAFTN:

    """
    <SOH> ABC0003 14033608<CR><LF>                               <-- Heading line
    GG CYYCYFYX EGLLZRZX<CR><LF>                                 <-- Destination address line
    140335 CYEGYFYX<CR><LF>                                      <-- Origin address line

    <STX>040227 NOTAMN CYYC CALGARY INTL<CR><LF>                 <-- Start of text signal (<STX>)
    CYYC ILS 16 AND 34 U/S 0409141530<CR><LF>                    <-- Message text
    TIL 0409141800<CR><LF>

    <VT><ETX>                                                    <-- End of message signal
    

    General format for ack is:

    <SOH><ACK><transmissionIdentifcation><ETX>

    A particular ack for the preceding AFTN Message is:

    <SOH><ACK><ABC0003><ETX>
    """

    END_OF_MESSAGE = chr(curses.ascii.ETX) # <ETX>
    SOH = chr(curses.ascii.SOH)
    ACK = chr(curses.ascii.ACK)

    def __init__(self, transmitID=None):

        self.transmitID = transmitID
        self.ackMessage = AckAFTN.SOH + AckAFTN.ACK + self.transmitID + AckAFTN.END_OF_MESSAGE

    def getAck(self):
        return self.ackMessage

    def positionOfEndOfMessage(text, END_OF_MESSAGE=END_OF_MESSAGE):
        return text.find(END_OF_MESSAGE)
    positionOfEndOfMessage = staticmethod(positionOfEndOfMessage)

if __name__ == "__main__":

    ack = AckAFTN('WWW1023')
    while ack.getAck():
        print(ack.ackMessage)


