#!/usr/bin/env python
"""
#############################################################################################
# Name: LogPublisher.py
#
# Author: Daniel Lemay
#
# Date: 2015-03
#
# Description: 
#
#############################################################################################
"""

import os, sys, time, datetime, socket

from State import statesDir
from State import load
from State import State
from AMQP_Publisher import AMQP_Publisher

class LogPublisher(object):
    def __init__(self, name, logger, startAtTheEnd=True):
        self.hostname = socket.gethostname()
        self.key = '%s.%s' % (self.hostname, name)
        self.logger = logger
        self.logDir = '/apps/px/log'
        self.state = load(name)

        if self.state == False:
            # 2 choices
            # 1) we will start at the last byte of the current log
            if startAtTheEnd:
                nbBytes = os.stat("%s/%s.log" % (self.logDir, name)).st_size
                state = State(name, datetime.date.today().strftime("%Y-%m-%d"), nbBytes)
            # 2) we will take all the current log
            else:
                state = State(name, datetime.date.today().strftime("%Y-%m-%d"), 0)
            state.dump(name)
            self.state = load(name)
        self.sleep = 10
        self.publisher = AMQP_Publisher('pxs', 'px_logs', 'topic', self.key)
        self.publisher.connect()
        self.logger.info('Publisher is now connected')

    def readOldLogs(self, logDir, logName):
        try:
            #print logName
            #print
            f = open(logDir + '/' + logName)
            f.seek(self.state.offset)
            data = f.read()
            nbBytes = len(data)
            if nbBytes != 0:
                self.publisher.publish(data)
                self.logger.info('%s bytes have been published' % (len(data)))
            else:
                self.logger.debug('%s bytes from %s => no need to published' % (nbBytes, logName))
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value)) 
            return 

        # set new state
        self.state.offset = 0
        self.state.incrementExt()
        self.state.dump(self.state.name)

        logName = self.state.name + '.log.' + self.state.ext
        self.readOldLogs(self.logDir, logName)
        
    def readCurrentLog(self):
        logName = self.state.name + '.log'    
        fullName = self.logDir + '/' + logName
        try:
            #print logName
            #print self.state.offset
            f = open(fullName)
            f.seek(self.state.offset)
            data = f.read()
            newPos = f.tell()
            oldPos = self.state.offset
            self.state.offset = newPos
            nbBytes = len(data)
            if nbBytes != 0:
                self.publisher.publish(data)
                self.logger.info('%s bytes have been published' % (nbBytes))
            else:
                self.logger.debug('%s bytes => no need to published' % (nbBytes))
        except: 
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value)) 
            return 

        # set new state
        self.state.setTodayExt()
        self.state.dump(self.state.name)

    def readLogs(self):
        logName = self.state.name + '.log.' + self.state.ext
        fullName = self.logDir + '/' + logName
        
        if os.path.isfile(fullName):
            self.readOldLogs(self.logDir, logName)
        self.readCurrentLog()

    def run(self):
        while True:
            try:
                self.readLogs()
                time.sleep(self.sleep)
            except:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Publisher error! Type: %s, Value: %s" % (type, value))

                try:
                    self.publisher.disconnect()
                    self.logger.info('Publisher is now disconnected')
                except:
                    (type, value, tb) = sys.exc_info()
                    self.logger.info("Publisher error! Type: %s, Value: %s" % (type, value))

                # We try to reconnect. 
                self.publisher.connect()
                self.logger.info('Publisher is now reconnected')

            
if __name__ == '__main__':
    import logging, logging.handlers

    logName = 'amqp_pub.log'
    logging.basicConfig(filename='/tmp/' + logName, format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    lp = LogPublisher('tx_urps-1', logger)
    #lp = LogPublisher('tx_geomet-dev-1', logger)
    lp.state.printAll()
    print
    lp.run()
