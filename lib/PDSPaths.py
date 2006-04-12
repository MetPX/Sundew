"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PDSPaths.py
#
# Author: Daniel Lemay
#
# Date: 2005-06-16
#
# Description:
#
#############################################################################################
"""
import os.path

def normalPaths():

    global ROOT, BIN, LOG, ETC, RXQ, TXQ, DB, INFO, RX_CONF, TX_CONF
    global PROD, SWITCH, STARTUP, TOGGLE, RESEND
    global FULLPROD, FULLSWITCH, FULLSTARTUP, FULLTOGGLE

    # Useful directories
    ROOT = '/apps/pds/'
    BIN = ROOT + 'bin/'
    LOG = ROOT + 'log/'
    ETC = ROOT + 'etc/'
    RXQ = ROOT + 'RAW/'
    TXQ = ROOT + 'home/'
    DB = ROOT + 'pdsdb/'
    INFO = ROOT + 'info/'
    RX_CONF = ETC
    TX_CONF = ETC 

    # Useful files
    PROD = "pdschkprod.conf"
    SWITCH = "pdsswitch.conf"
    STARTUP = "PDSstartupinfo"
    TOGGLE = "ToggleSender"
    RESEND = "pdsresend"

    # Useful paths (directory + file)
    FULLPROD = ETC + PROD
    FULLSWITCH = ETC + SWITCH
    FULLSTARTUP = INFO + STARTUP
    FULLTOGGLE = BIN + TOGGLE

def drbdPaths(rootPath):
    """
    The only difference with normalPaths is the ROOT (apps2)
    """
    global ROOT, BIN, LOG, ETC, RXQ, TXQ, DB, INFO, RX_CONF, TX_CONF
    global PROD, SWITCH, STARTUP, TOGGLE, RESEND
    global FULLPROD, FULLSWITCH, FULLSTARTUP, FULLTOGGLE

    # Useful directories
    ROOT = os.path.normpath(rootPath) + '/'
    BIN = ROOT + 'bin/'
    LOG = '/apps/pds/' + 'log/'  # We always want to log on /apps
    ETC = ROOT + 'etc/'
    RXQ = ROOT + 'RAW/'
    TXQ = ROOT + 'home/'
    DB = ROOT + 'pdsdb/'
    INFO = ROOT + 'info/'
    RX_CONF = ETC
    TX_CONF = ETC 

    # Useful files
    PROD = "pdschkprod.conf"
    SWITCH = "pdsswitch.conf"
    STARTUP = "PDSstartupinfo"
    TOGGLE = "ToggleSender"
    RESEND = "pdsresend"

    # Useful paths (directory + file)
    FULLPROD = ETC + PROD
    FULLSWITCH = ETC + SWITCH
    FULLSTARTUP = INFO + STARTUP
    FULLTOGGLE = BIN + TOGGLE

