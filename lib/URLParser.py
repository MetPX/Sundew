"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: URLParser.py
#
# Author: Daniel Lemay
#
# Date: 2005-08-17
#
# Description: 
#
#############################################################################################

"""
import urlparse,string


class URLParser:

    def __init__(self, url):
        # Sample ftp url   : ftp://user:passwd@px-op.cmc.ec.gc.ca//apps/px/rxq/fromPxatx
        # Sample socket url: wmo://pxatx-priv.cmc.ec.gc.ca:24901
        # Sample socket url: am://pxatx-priv.cmc.ec.gc.ca:24901
        # Sample socket url: amis://pxatx-priv.cmc.ec.gc.ca:24901
        # Sample file url  : file://localhost/apps/px/operator
        self.url = url
        if self.url[:4] == 'amqp' : url = url.replace('amqp','ftp')
        self.protocol, self.netloc, self.path, self.param, self.query, self.frag = urlparse.urlparse(url)
        if self.url[:4] == 'amqp' : self.protocol = 'amqp'
        self.user = None
        self.passwd = None
        self.host = None
        self.port = None

    def parse(self):
        if self.protocol == 'ftp':
            # Sample ftp netloc: user:passwd@px-op.cmc.ec.gc.ca
            (self.user, rest) = self.netloc.split(':')
            (self.passwd, self.host) = rest.split('@')
        elif self.protocol == 'amqp':
            # Sample ftp netloc: user:passwd@px-op.cmc.ec.gc.ca
            print self.netloc
            (self.user, rest) = self.netloc.split(':')
            (self.passwd, self.host) = rest.split('@')
        elif self.protocol in ['am', 'wmo', 'amis']:
            # Sample socket path part: //pxatx-priv.cmc.ec.gc.ca:24901
            (self.host, self.port) = self.path[2:].split(':')
            self.path = None
        elif self.protocol == 'file':
            # Sample file path part://apps/px/operator
            self.host = self.netloc

        return (self.protocol, self.path, self.user, self.passwd, self.host, self.port)
            
    def join(protocol, path, user, passwd, host, port):
        if protocol == 'ftp':
            url = '%s://%s:%s@%s%s' % (protocol, user, passwd, host, path)
        elif protocol == 'amqp':
            url = '%s://%s:%s@%s%s' % (protocol, user, passwd, host, path)
        elif protocol == 'file':
            url = '%s://%s%s' % (protocol, host, path)
        elif protocol in ['am', 'wmo', 'amis']: 
            url = '%s://%s:%s' % (protocol, host, port)
        return url
    join = staticmethod(join)

    def printAll(self):
        print("URL = %s" % self.url)
        print("PROTOCOL = %s" % self.protocol)
        print("NETLOC = %s" % self.netloc)
        print("PATH = %s" % self.path)
        print("PARAM = %s" % self.param)
        print("QUERY = %s" % self.query)
        print("FRAG = %s" % self.frag)
        print
        print("USER= %s" % self.user)
        print("PASSWD = %s" % self.passwd)
        print("HOST = %s" % self.host)
        print("PORT = %s" % self.port)

if __name__ == '__main__':

    #parser = URLParser('wmo://pxatx-priv.cmc.ec.gc.ca:24901')
    #parser = URLParser('am://pxatx-priv.cmc.ec.gc.ca:24901')
    #parser = URLParser('amis://pxatx-priv.cmc.ec.gc.ca:24901')
    #parser = URLParser('file://localhost//apps/px/operator')
    parser = URLParser('amqp://guest:guest@grogne.cmc.ec.gc.ca//data')

    print parser.parse()
    print 
    parser.printAll()
    print parser.join(parser.protocol, parser.path, parser.user, parser.passwd, parser.host, parser.port)
    print URLParser.join(parser.protocol, parser.path, parser.user, parser.passwd, parser.host, parser.port)
