"""
MetPX Copyright (C) 2004-2007  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: dshLib.py
#
# Author: Daniel Lemay
#
# Date: 2007-10-11
#
# Description: Useful dsh related functions
#
# MG python3 compatible
#
#############################################################################################
"""
import sys
import fileLib


if sys.version[:1] >= '3' :
   import subprocess
else :
   import commands
   subprocess = commands


DSH_ROOT = "/etc/dsh/"
DSH_GROUP = DSH_ROOT + "group/"

def getMachines(group):
    if group == 'pxatx':
        try:
            command = 'ssh pds@pxatx hostname'
            hostname = subprocess.getoutput(command)
        except:
            hostname = None

        if hostname: machines = [hostname]
        else: machines = []

    else:
        try:
            machines = [machine.strip() for machine in fileLib.getLines(DSH_GROUP + group)]
        except:
            machines = []
    return machines
    """
    #return machines or ['userver1-new', 'userver2-new']
    machines = []
    if group.lower() == 'pxatx':
        machines = ['pxatx']
    elif group.lower() in ['px', 'userver', 'userv']:
        machines = ['userver1-new', 'userver2-new']
    """

if __name__ == '__main__':
    print(getMachines("px"))
    print(getMachines("pds"))
    print(getMachines("pxatx"))

    print(getMachines("PX"))
    print(getMachines("PDS"))
    print(getMachines("PXATX"))

    print(getMachines("toto"))
    print(getMachines("userv"))
    print(getMachines("userver"))

