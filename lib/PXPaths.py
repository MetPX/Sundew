
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

    global ROOT, BIN, LIB, LOG, ETC, RXQ, TXQ, DB, RX_CONF, TX_CONF, TRX_CONF, LAT, LAT_RESULTS, LAT_TMP, \
           COLLECTION_DB, COLLECTION_CONTROL, ROUTING_TABLE, STATION_TABLE, STATS, PICKLES, GRAPHS, SEARCH

    try:
        envVar = os.path.normpath(os.environ['PXROOT']) + '/'
    except KeyError:
        envVar = '/apps/px/'

    ROOT = envVar 
    BIN = ROOT + 'bin/'
    LIB = ROOT + 'lib/' # This path was hardcoded in PXCopy.py, see dominik_db or dlema for details
    LOG = ROOT + 'log/'
    ETC = ROOT + 'etc/'
    RXQ = ROOT + 'rxq/'
    TXQ = ROOT + 'txq/'
    DB = ROOT + 'db/'
    RX_CONF = ETC + 'rx/'
    TX_CONF = ETC + 'tx/'
    TRX_CONF = ETC + 'trx/'
    COLLECTION_DB = ROOT + 'collection/'
    COLLECTION_CONTROL = COLLECTION_DB + 'control/'
    ROUTING_TABLE = ETC + 'pxRouting.conf'
    STATION_TABLE = ETC + 'stations.conf'

    # Paths for pxLatencies
    LAT = ROOT + 'latencies/'
    LAT_RESULTS = LAT + 'results/'
    LAT_TMP = LAT + 'tmp/'

    # Paths for "stats" and graphics
    STATS = ROOT + 'stats/'
    PICKLES = STATS + 'pickles/'
    GRAPHS = STATS + 'graphs/'

    # Paths to the search directory
    SEARCH = LIB + 'search/'

def drbdPaths(rootPath):

    global ROOT, BIN, LIB, LOG, ETC, RXQ, TXQ, DB, RX_CONF, TX_CONF, TRX_CONF, LAT, LAT_RESULTS, LAT_TMP, \
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
    TRX_CONF = ETC + 'trx/'
    COLLECTION_DB = ROOT + 'collection'
    COLLECTION_CONTROL = COLLECTION_DB + 'control/'

    #Paths for pxLatencies
    LAT = ROOT + 'latencies/'
    LAT_RESULTS = LAT + 'results/'
    LAT_TMP = LAT + 'tmp/'
