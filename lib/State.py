#!/usr/bin/env python
"""
#############################################################################################
# Name: State.py
#
# Author: Daniel Lemay
#
# Date: 2015-03
#
# Description: 
#
#############################################################################################
"""

import os, datetime, pickle

#statesDir = '/root/scripts/logReader/logs/.states'
statesDir = '/apps/px/log/.states'

def load(filename):
    fullName = statesDir + '/' + filename
    if os.path.isfile(fullName):
        return pickle.load(open(fullName, 'rb'))
    else:
        return False

class State(object):
    def __init__(self, name, ext, offset):
        self.name = name
        self.ext = ext
        self.offset = offset

    def setTodayExt(self):
        today = datetime.date.today()
        self.ext = today.strftime("%Y-%m-%d")

    def incrementExt(self, inc=1):
        dt = datetime.datetime.strptime(self.ext, "%Y-%m-%d").date() + datetime.timedelta(days=inc)
        self.ext = dt.strftime("%Y-%m-%d")

    def dump(self, filename):
        pickle.dump(self, open(statesDir + '/' + filename, "wb"))
            
    def printAll(self):
        print "%s: %s" % ('name', self.name)
        print "%s: %s" % ('ext', self.ext)
        print "%s: %s" % ('offset', self.offset)

if __name__ == '__main__':
    # Create a state
    name = 'tx_bc-moe'
    name = 'tx_urps-1'
    state = State(name, '2015-03-15', 0)
    state.printAll()
    state.dump(name)

    # Load a state
    state = load('tx_urps-1')
    if state != False:
        state.printAll()
        #state.incrementExt()
        #state.setTodayExt()
        #print
        #state.printAll()
