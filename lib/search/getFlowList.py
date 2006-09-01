#!/usr/bin/env python

# Python API imports
import os
import sys
#import ConfigParser

sys.path.insert(1,sys.path[0] + '/../importedLibs')
sys.path.append(sys.path[0] + "/../")
sys.path.append("/apps/pds/tools/Columbo/lib")

# Local imports
import PXPaths; PXPaths.normalPaths()
from PXManager import PXManager
from Logger import Logger
from DirectRoutingParser import DirectRoutingParser

import ColumboPath

#config = ConfigParser.ConfigParser()
#config.readfp(open(ColumboPath.FULL_MAIN_CONF))
#logname = config.get('SEARCH_AND_RESEND', 'logname')

logname = "/tmp/tmpFlow.log"
logger = Logger(logname, 'INFO', 'SAS').getLogger()
manager = PXManager()
manager.setLogger(logger)
manager.initNames()
drp = DirectRoutingParser(PXPaths.ROUTING_TABLE, [], logger)
drp.printErrors = False
drp.parseAlias()
flows = manager.getAllFlowNames(False, drp)

print " ".join(flows)

os.remove(logname)
