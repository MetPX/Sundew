"""
#############################################################################################
# Name: AFTNPaths.py
#
# Author: Daniel Lemay
#
# Date: 2006-03-27
#
# Description: Useful AFTN Paths
#
#############################################################################################
"""
import sys, os, os.path

sys.path.insert(1, sys.path[0] + '/../../sundew/lib')
import PXPaths

def normalPaths(name, rootPath=""):
    
    PXPaths.normalPaths(rootPath)

    global ROOT, LIB, TO_SEND, RECEIVED, SENT, SPECIAL_ORDERS,  STATE

    if rootPath:
        if rootPath[-1] != '/': rootPath += '/'
        envVar = rootPath
    else:
        try:
            envVar = os.path.normpath(os.environ['PXROOT']) + '/'
        except KeyError:
            envVar = '/apps/px/'

    ROOT = envVar
    LIB = ROOT + 'lib/%s/' % name

    RECEIVED = PXPaths.TXQ + name + '/.receivedAFTN/'
    SENT = PXPaths.TXQ + name + '/.sentAFTN/'
    SPECIAL_ORDERS = PXPaths.TXQ + name + '/.specialOrders/'

    STATE = PXPaths.TXQ + name + '/.state.obj'

if __name__ == "__main__":
    normalPaths('toto')
    print ROOT
    print LIB

    print RECEIVED
    print SENT
    print SPECIAL_ORDERS

    print STATE
