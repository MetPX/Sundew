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
#############################################################################################
"""
import sys

def isTrue(value):
    if value in ['y', 'Y', 'yes', 'YES', 'o', 'O', 'oui', 'OUI']:
        return True
    else:
        return False

if __name__ == '__main__':
    pass    
