"""
#############################################################################################
# Name: authPub.py
#
# Author: Daniel Lemay
#
# Date: 2015-03
#
# Description: 
#
#############################################################################################
"""

import sys, os, re

def isTrue(s):
    if s in ['True', 'true', 'TRUE', 'Yes', 'yes', 'YES', 'On', 'on', 'ON', '1']:
        return True
    else:
        return False

def authorizeInFlowConf(filename):
    for line in open(filename, 'r').readlines():
        words = line.split()
        if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)):
            if words[0] == 'publog':
                return isTrue(words[1])
    return False

def permitPubLog(logger, options, flowPath):
    if authorizeInFlowConf(flowPath):
        logger.info('Log publishing is authorized in the config. file')
        return
    else:
        logger.info('%s' % ('Log publishing is not authorized in the config. file'))

    if options.bypass:
        logger.info('Log publishing is authorized via command line option (-b)')
        return

    try:
        environBypass = os.environ['PX_LOGS_PUB']
    except:
        environBypass = False

    if isTrue(environBypass):
        logger.info('Log publishing is authorized via env. var. PX_LOGS_PUB')
        return

    print('%s: %s' % (os.path.basename(flowPath)[:-5], 'Log publishing is not authorized (conf. file, option, env. var.)'))
    sys.exit(0)


if __name__ == '__main__':
    pass
