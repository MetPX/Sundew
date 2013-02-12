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
        self.connection = amqp.Connection( self.source.host,userid=self.source.user,password=self.source.passwd,ssl=self.ssl)
        #host='localhost',
        #userid='guest',
        #password='guest',
        #login_method='AMQPLAIN',
        #login_response=None,
        #virtual_host='/',
        #locale='en_US',
        #client_properties=None,
        #ssl=False,
        #insist=False,
        #connect_timeout=None,

        self.channel = self.connection.channel()
        # channel_id = None

        self.channel.access_request(self.source.realm, active=True, read=True)
        # realm   = /data for appl resources     /admin for admin resources
        # exclusive=False,
        # passive=False
        # active=False
        # write=False
        # read=False

        self.channel.exchange_declare(self.source.exchangename, self.source.exchangetype, auto_delete=True)
        # exchange  reserved .amqp
        # type     
        # passive=False
        # durable=False
        # auto_delete=True
        # internal=False
        # nowait=False,
        # arguments=None
        # ticket=None):

        self._queuename, message_count, consumer_count = self.channel.queue_declare()
        # queue=''
        # passive=False
        # durable=False,
        # exclusive=False
        # auto_delete=True
        # nowait=False,
        # arguments=None
        # ticket=None):

        self.channel.queue_bind(self._queuename, self.source.exchangename, self.source.amqp_key)
        # queue
        # exchange
        # routing_key='',
        # nowait=False
        # arguments=None
        # ticket=None):

        self.channel.basic_consume(self._queuename, callback=self.read_callback)
        # queue=''
        # consumer_tag=''
        # no_local=False,
        # no_ack=False
        # exclusive=False
        # nowait=False,
        # callback=None
        # ticket=None):


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
        #for key, val in msg.properties.items(): 
        #    self.logger.info('message properties %s: %s' % (key, str(val)))
        #for key, val in msg.delivery_info.items():
        #    self.logger.info('message delivery_info %s: %s' % (key, str(val)))

        routing_key   = msg.delivery_info['routing_key']
        parts         = routing_key.split(':')
        self.filename = ':'.join(parts[1:])

        self.msg = msg.body

        msg.channel.basic_ack(msg.delivery_tag)
        # delivery_tag
        # multiple=False

        #
        # Cancel this callback
        #
        if msg.body == 'quit':
            msg.channel.basic_cancel(msg.consumer_tag)
            # consumer_tag
            # nowait=False)

            self.msg = None
            self.logger.error('CRITICAL ERROR...')
            self.logger.error('Requiered to quit the connection')
            sys.exit(1)
