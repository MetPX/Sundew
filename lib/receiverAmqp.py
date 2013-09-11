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
import os

import gateway
import PXPaths 
import bulletinManager 

PXPaths.normalPaths()

class receiverAmqp(gateway.gateway):
    __doc__ = gateway.gateway.__doc__ + \
    """ amqp receiver """

    def __init__(self, path, source, logger):
        gateway.gateway.__init__(self, path, source, logger)

        self.source   = source
        self.logger   = logger
        self.ingestor = source.ingestor
        self.msg      = None
        self.ssl      = False

        self.establishConnection()
        self.renewIngestor()

    def renewIngestor(self):
        from DirectRoutingParser import DirectRoutingParser
        from PullFTP import PullFTP

        if self.source.routemask :
           self.ingestor.drp = DirectRoutingParser(self.source.routingTable, self.ingestor.allNames, self.logger, self.source.routing_version)
           self.ingestor.drp.parse()

        if self.source.nodups :
           self.ingestor.fileCache = CacheManager(maxEntries=self.source.cache_size, timeout=8*3600)

    def shutdown(self):
        self.channel.close()
        self.connection.close()

    def establishConnection(self):
        # connection
        self.connection = amqp.Connection( self.source.host,userid=self.source.user,password=self.source.passwd,ssl=self.ssl)
        self.channel = self.connection.channel()

        # exchange
        self.channel.access_request(self.source.exchange_realm, active=True, read=True)
        self.channel.exchange_declare(self.source.exchange_name, self.source.exchange_type, auto_delete=False)

        # queue and reading callback
        self._queuename, message_count, consumer_count = self.channel.queue_declare()
        self.channel.queue_bind(self._queuename, self.source.exchange_name, self.source.exchange_key)
        self.channel.basic_consume(self._queuename, callback=self.read_callback)


    def read(self):
        self.msg = None
        try:
                if self.channel.callbacks:
                   self.channel.wait()
        except:
                self.logger.error("lost connection, or reading problem")

        return self.msg

    def write(self,data):
        fname = self.source.ingestor.ingestDir + '/' + self.filename

        fp = open(fname,'w')
        fp.write(data)
        fp.close()
        os.chmod(fname,0644)

        self.source.ingestor.ingestFile(fname)

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

        hdr = msg.properties['application_headers']
        self.filename = hdr['filename']

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
