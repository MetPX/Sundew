
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PXPaths.py
#
# Author: Daniel Lemay
#
# Date: 2005-06-16
#
# Description: Useful PX Paths
#
#
# Revision History: 
#   2005-12-09  NSD         Added collection db path to environment.
#
#############################################################################################
"""
import os, os.path

def readConfig():
    root = '/apps'
    try:
        config = open(filePath, 'r')
        lines = config.readlines()
        for line in lines:
            if line.isspace(): # we skip blank line
                continue
            words = line.split()
            if words[0] == 'root':
                root = words[1]
        config.close()
    except:
        #(type, value, tb) = sys.exc_info()
        #print("ROOT/px/etc/px.conf must be present! Type: %s, Value: %s" % (type, value))
        pass
    
    return root


def normalPaths():

    global ROOT, BIN, LIB, LOG, ETC, RXQ, TXQ, DB, RX_CONF, TX_CONF, LAT, LAT_RESULTS, LAT_TMP, \
           COLLECTION_DB, COLLECTION_CONTROL

    try:
        envVar = os.path.normpath(os.environ['PXROOT'])
    except KeyError:
        envVar = '/apps'

    ROOT = envVar + '/px/'
    BIN = ROOT + 'bin/'
    LIB = ROOT + 'lib/'
    LOG = ROOT + 'log/'
    ETC = ROOT + 'etc/'
    RXQ = ROOT + 'rxq/'
    TXQ = ROOT + 'txq/'
    DB = ROOT + 'db/'
    RX_CONF = ETC + 'rx/'
    TX_CONF = ETC + 'tx/'
    COLLECTION_DB = ROOT + 'collection/'
    COLLECTION_CONTROL = COLLECTION_DB + 'control/'

    #Paths for pxLatencies
    LAT = ROOT + 'latencies/'
    LAT_RESULTS = LAT + 'results/'
    LAT_TMP = LAT + 'tmp/'


def drbdPaths(rootPath):

    global ROOT, BIN, LIB, LOG, ETC, RXQ, TXQ, DB, RX_CONF, TX_CONF, LAT, LAT_RESULTS, LAT_TMP, \
           COLLECTION_DB, COLLECTION_CONTROL

    ROOT = os.path.normpath(rootPath) + '/'
    BIN = ROOT + 'bin/'
    LIB = ROOT + 'lib/'
    LOG = '/apps/px/' + 'log/'
    ETC = ROOT + 'etc/'
    RXQ = ROOT + 'rxq/'
    TXQ = ROOT + 'txq/'
    DB = ROOT + 'db/'
    RX_CONF = ETC + 'rx/'
    TX_CONF = ETC + 'tx/'
    COLLECTION_DB = ROOT + 'collection'
    COLLECTION_CONTROL = COLLECTION_DB + 'control/'

    #Paths for pxLatencies
    LAT = ROOT + 'latencies/'
    LAT_RESULTS = LAT + 'results/'
    LAT_TMP = LAT + 'tmp/'
