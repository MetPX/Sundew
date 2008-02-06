
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

def normalPaths(rootPath=""):

    global ROOT, BIN, LIB, LOG, ETC, FXQ, RXQ, TXQ, DB, FX_CONF, RX_CONF, TX_CONF, TRX_CONF, \
           COLLECTION_DB, COLLECTION_CONTROL, ROUTING_TABLE, STATION_TABLE, SCRIPTS, \
           LAT, LAT_RESULTS, LAT_TMP, SHELL_PARSER, PX_DATA 
    
    if rootPath:
        if rootPath[-1] != '/': rootPath += '/'
        envVar = rootPath
    else:
        try:
            envVar = os.path.normpath(os.environ['PXROOT']) + '/'
        except KeyError:
            envVar = '/apps/px/'

    ROOT = envVar 
    BIN = ROOT + 'bin/'
    LIB = ROOT + 'lib/' # This path was hardcoded in PXCopy.py, see dominik_db or dlema for details
    LOG = ROOT + 'log/'
    ETC = ROOT + 'etc/'
    FXQ = ROOT + 'fxq/'
    RXQ = ROOT + 'rxq/'
    TXQ = ROOT + 'txq/'
    DB = ROOT + 'db/'
    FX_CONF = ETC + 'fx/'
    RX_CONF = ETC + 'rx/'
    TX_CONF = ETC + 'tx/'
    TRX_CONF = ETC + 'trx/'
    COLLECTION_DB = ROOT + 'collection/'
    COLLECTION_CONTROL = COLLECTION_DB + 'control/'
    ROUTING_TABLE = ETC + 'pxRouting.conf'
    STATION_TABLE = ETC + 'stations.conf'
    SCRIPTS = ETC + 'scripts/'

    # Paths for pxLatencies
    LAT = ROOT + 'latencies/'
    LAT_RESULTS = LAT + 'results/'
    LAT_TMP = LAT + 'tmp/'

    # pxRetrans
    SHELL_PARSER = LIB + 'shellParser.py'
    PX_DATA = ROOT + 'data/'               # this path must be present on the MASTER (where all the config. files are stored)            

def drbdPaths(rootPath):

    global ROOT, BIN, LIB, LOG, ETC, FXQ, RXQ, TXQ, DB, FX_CONF, RX_CONF, TX_CONF, TRX_CONF

    ROOT = os.path.normpath(rootPath) + '/'
    BIN = ROOT + 'bin/'
    LIB = ROOT + 'lib/'
    LOG = '/apps/px/' + 'log/'
    ETC = ROOT + 'etc/'
    FXQ = ROOT + 'fxq/'
    RXQ = ROOT + 'rxq/'
    TXQ = ROOT + 'txq/'
    DB = ROOT + 'db/'
    FX_CONF = ETC + 'fx/'
    RX_CONF = ETC + 'rx/'
    TX_CONF = ETC + 'tx/'
    TRX_CONF = ETC + 'trx/'

