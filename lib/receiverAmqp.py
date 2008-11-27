# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.
#
# Author:
#    2008/11 - Michel Grenier
#

"""ReceiverAmqp: amqp bulletins received, ingested and processed"""

import amqplib.client_0_8 as amqp

import gateway
import PXPaths 
import bulletinManager 

PXPaths.normalPaths()

class receiverAmqp(gateway.gateway):
    __doc__ = gateway.gateway.__doc__ + \
    """ amqp receiver """

    def __init__(self, path, source, logger):
        gateway.gateway.__init__(self, path, source, logger)

        self.source = source
        self.logger = logger
        self.msg    = None
        self.qname  = None
        self.realm  = None
        self.ssl    = False

        lst         = self.source.pulls[0]
        self.realm  = lst[0]
        if self.realm[:2] == "//" : self.realm = self.realm[1:]

        self.establishConnection()
        self.renewBulletinManager()

    def renewBulletinManager(self):
        self.unBulletinManager = bulletinManager.bulletinManager(
                               PXPaths.RXQ + self.source.name,
                               self.logger,
                               PXPaths.RXQ + self.source.name,
                               99999,
                               '\n',
                               self.source.extension,
                               PXPaths.ROUTING_TABLE,
                               self.source.mapEnteteDelai,
                               self.source)

    def shutdown(self):
        self.channel.close()
        self.connection.close()

    def establishConnection(self):
        self.connection = amqp.Connection( self.source.host,userid=self.source.user,password=self.source.passwd,ssl=self.ssl)
        self.channel = self.connection.channel()
        self.channel.access_request(self.realm, active=True, read=True)
        self.channel.exchange_declare('myfan', 'fanout', auto_delete=True)
        self.qname, _, _ = self.channel.queue_declare()
        self.channel.queue_bind(self.qname, 'myfan')
        self.channel.basic_consume(self.qname, callback=self.read_callback)


    def read(self):
        self.msg = None
        try:
                if self.channel.callbacks:
                   self.channel.wait()
        except:
                self.logger.error("lost connection, or reading problem")

        return self.msg

    def write(self,data):
        self.unBulletinManager.writeBulletinToDisk(data,includeError=True)

    def reloadConfig(self):
        self.logger.info('configuration reload started')
        try:
            newConfig = gateway.gateway.loadConfig(self.pathToConfigFile)
            self.unBulletinManager.drp.reparse()
            self.logger.info('configuration reload successful')
        except Exception, e:
            self.logger.error('configuration reload failed')
            self.logger.debug("Error: %s", str(e.args))

    def read_callback(self,msg):
        #for key, val in msg.properties.items(): 
        #print '%s: %s' % (key, str(val))
        #for key, val in msg.delivery_info.items():
        #print '> %s: %s' % (key, str(val))

        self.msg = msg.body

        msg.channel.basic_ack(msg.delivery_tag)

        #
        # Cancel this callback
        #
        if msg.body == 'quit':
            msg.channel.basic_cancel(msg.consumer_tag)
            self.msg = None
            self.logger.error('CRITICAL ERROR...')
            self.logger.error('Requiered to quit the connection')
            sys.exit(1)
