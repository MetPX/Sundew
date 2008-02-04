"""
#############################################################################################
# Name: StateAFTN.py
#
# Author: Daniel Lemay
#
# Date: 2006-06-06
#
# Description: Keep the AFTN state in this object
#
#############################################################################################

"""
import os, sys, pickle

sys.path.insert(1,sys.path[0] + '/../lib')
sys.path.insert(1,sys.path[0] + '/../etc')
sys.path.insert(1,sys.path[0] + '/../../lib')
sys.path.insert(1,sys.path[0] + '/../../lib/importedLibs')

class StateAFTN:

    def __init__(self):
        self.CSN = None
        self.waitedTID = None

        self.lastAckReceived = None
        self.waitingForAck = None

    def fill(self, messageManager):
        self.CSN = messageManager.CSN
        self.waitedTID = messageManager.waitedTID

        self.lastAckReceived = messageManager.lastAckReceived
        self.waitingForAck = messageManager.waitingForAck

    def clear(self):
        self.CSN = None
        self.waitedTID = None

        self.lastAckReceived = None
        self.waitingForAck = None

    def infos(self):
        return """  
        CSN = %s
        waitedTID = %s

        lastAckReceived = %s
        waitingForAck = %s
        """ % (self.CSN, self.waitedTID, self.lastAckReceived, self.waitingForAck)


if __name__ == "__main__":
    state = StateAFTN()
    print(state.infos())
