#!/usr/bin/env python

"""
#############################################################################################
# Name: AMQP_Publisher.py
#
# Author: Daniel Lemay
#
# Date: 2015-03
#
# Description: 
#
#############################################################################################
"""

import sys, pika

class AMQP_Publisher(object):
    def __init__(self, hostname, exchangeName, exchangeType, key):
        self.hostname = hostname
        self.port = 5672
        self.exchangeName = exchangeName
        self.exchangeType = exchangeType
        self.key = key

        self.credentials = pika.PlainCredentials('dan', 'dan')

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.hostname, self.port, '/', self.credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchangeName, type=self.exchangeType)

    def disconnect(self):
        self.connection.close()

    def publish(self, data):
        self.channel.basic_publish(exchange=self.exchangeName, routing_key=self.key, body=data)   

    def printAll(self):
        print "%s: %s" % ('hostname', self.hostname)
        print "%s: %s" % ('exchangeName', self.exchangeName)
        print "%s: %s" % ('exchangeType', self.exchangeType)
        print "%s: %s" % ('key', self.key)


if __name__ == '__main__':
    p = AMQP_Publisher('pxs', 'px_logs', 'topic', 'px-ops1:tx_metser')
    p.printAll()
