
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
import os, os.path, re

def locateDirs(rootPath=""):

    # debian defaults

    ROOT  = None
    ETC   = '/etc/px/'
    LOG   = '/var/log/px/'
    SPOOL = '/var/spool/px/'

    # use of env variable PXROOT for backwork compatibility

    if rootPath == "" :
       try:
                path = os.path.normpath(os.environ['PXROOT']) + '/'
		rootPath = path
       except : pass

    # overwrite debian defaults if requiered

    if rootPath != "" :
       if rootPath[-1] != "/" : rootPath = rootPath + '/'
       ROOT  = rootPath
       ETC   = rootPath + 'etc/'
       LOG   = rootPath + 'log/'
       SPOOL = rootPath

    # px.conf 

    pxconf  = ETC + 'px.conf'
    try:
             pxconf = os.path.normpath(os.environ['PXCONF']) + '/'
    except : pass

    # if px.conf  does not exists... try env variable PXCONF

    if not os.path.isfile(pxconf) :
       return (ROOT,ETC,LOG,SPOOL)

    # px.conf exists : read and parse only to resolve directories 

    try:
         config = open(pxconf, 'r')
    except:
         (type, value, tb) = sys.exc_info()
         print("Type: %s, Value: %s" % (type, value))
         sys.exit(1)

    for line in config.readlines():
        words = line.split()
        if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)):
            try:
                if   words[0] == 'spooldir':
                     SPOOL = words[1]
                     if SPOOL[-1] != "/" : SPOOL = SPOOL + '/'
                elif words[0] == 'logdir':
                     LOG = words[1]
                     if LOG[-1] != "/" : LOG = LOG + '/'
                elif words[0] == 'etcdir':
                     ETC = words[1]
                     if ETC[-1] != "/" : ETC = ETC + '/'

                     # MG ... hmmm !?
                     # if we have another etc...
                     # should we check for another px.conf and parse...

            except:
                    print("Problem with this line (%s) in px.conf %s" % (words, PX_CONF_FIL))

    config.close()

    return (ROOT,ETC,LOG,SPOOL)
    

def normalPaths(rootPath=""):

    global ROOT, LIB, LOG, ETC, FXQ, RXQ, TRXQ, TXQ, DB, FX_CONF, RX_CONF, TX_CONF, TRX_CONF, \
           ROUTING_TABLE, STATION_TABLE, SCRIPTS, \
           LAT, LAT_RESULTS, LAT_TMP, SHELL_PARSER, PX_DATA 

    ROOT,ETC,LOG,SPOOL = locateDirs(rootPath)

    LIB = '/usr/lib/px/' # This path was hardcoded in PXCopy.py, see dominik_db or dlema for details

    FXQ  = SPOOL + 'fxq/'
    RXQ  = SPOOL + 'rxq/'
    TXQ  = SPOOL + 'txq/'
    TRXQ = SPOOL + 'trxq/'
    DB   = SPOOL + 'db/'

    FX_CONF  = ETC + 'fx/'
    RX_CONF  = ETC + 'rx/'
    TX_CONF  = ETC + 'tx/'
    TRX_CONF = ETC + 'trx/'

    ROUTING_TABLE = ETC + 'pxRouting.conf'
    STATION_TABLE = ETC + 'stations.conf'
    SCRIPTS = ETC + 'scripts/'

    # Paths for pxLatencies
    LAT = SPOOL + 'latencies/'
    LAT_RESULTS = LAT + 'results/'
    LAT_TMP = LAT + 'tmp/'

    # pxRetrans
    SHELL_PARSER = LIB + 'shellParser.py'
    PX_DATA = SPOOL + 'data/'               # this path must be present on the MASTER (where all the config. files are stored)            

def drbdPaths(rootPath):

    global ROOT, LIB, LOG, ETC, FXQ, RXQ, TRXQ, TXQ, DB, FX_CONF, RX_CONF, TX_CONF, TRX_CONF

    ROOT = os.path.normpath(rootPath) + '/'
    LIB = '/usr/lib/px/'
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

# TEST normalPaths...
      
if __name__ == '__main__':

   import PXPaths
   PXPaths.normalPaths("")
   
   print("ROOT %s" % PXPaths.ROOT )
   print("LIB  %s" % PXPaths.LIB )
   print("LOG  %s" % PXPaths.LOG )
   print("ETC  %s" % PXPaths.ETC )
   
   print("FXQ  %s" % PXPaths.FXQ )
   print("RXQ  %s" % PXPaths.RXQ )
   print("TXQ  %s" % PXPaths.TXQ )
   print("TRXQ %s" % PXPaths.TRXQ )
   print("DB   %s" % PXPaths.DB )
   
   print("ROUTING_TABLE %s" % PXPaths.ROUTING_TABLE )
   print("STATION_TABLE %s" % PXPaths.STATION_TABLE )
   
   print("FX_CONF  %s" % PXPaths.FX_CONF )
   print("RX_CONF  %s" % PXPaths.RX_CONF )
   print("TX_CONF  %s" % PXPaths.TX_CONF )
   print("TRX_CONF %s" % PXPaths.TRX_CONF )
   print("SCRIPTS  %s" % PXPaths.SCRIPTS )
   
   print("LAT %s" % PXPaths.LAT )
   print("LAT_RESULTS %s" % PXPaths.LAT_RESULTS )
   print("LAT_TMP %s" % PXPaths.LAT_TMP )
   print("SHELL_PARSER %s" % PXPaths.SHELL_PARSER )
   print("PX_DATA  %s" % PXPaths.PX_DATA )
