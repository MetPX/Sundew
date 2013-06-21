"""
MetPX Copyright (C) 2004-2007  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: generalLib.py
#
# Author: Daniel Lemay
#
# Date: 2007-11-29
#
# Description: Useful general functions
#
# MG python3 compatible
#
#############################################################################################
"""
import sys

def isTrue(value):
    if value in ['y', 'Y', 'yes', 'YES', 'o', 'O', 'oui', 'OUI']:
        return True
    else:
        return False

def isIPAddress(value):
    min = 0
    max = 255
    numbers = value.split('.')
    if len(numbers) == 4:
        for number in numbers:
            try:
                if int(number) >= 0 and int(number)<= 255: pass
                else: return False
            except:
                return False
        return True
    else: return False

if __name__ == '__main__':
    print("%s: %s" % ("awws", isIPAddress("awws"))    )
    print("%s: %s" % ("awws.awws.awws.awws", isIPAddress("awws.awws.awws.awws"))    )
    print("%s: %s" % ("192.168.1.10", isIPAddress("192.168.1.10"))    )
    print("%s: %s" % ("192.168.1.1.1", isIPAddress("192.168.1.1.1"))    )
    print("%s: %s" % ("192.168.256.1", isIPAddress("192.168.256.1"))    )
