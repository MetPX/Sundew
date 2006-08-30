#!/usr/bin/env python

# Python API imports
import os
import sys

sys.path.insert(1,sys.path[0] + '/../importedLibs')
sys.path.append(sys.path[0] + "/../")
sys.path.append("/apps/pds/tools/Columbo/lib")

# Local imports
import PXPaths; PXPaths.normalPaths()
import PXManager
import Logger
import DirectRoutingParser

import ColumboPath

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
logname = config.get('SEARCH_AND_RESEND', 'logname')

logger = Logger(logname, 'INFO', 'SAS').getLogger()
manager = PXManager()
manager.setLogger(logger)
manager.initNames()
drp = DirectRoutingParser(PXPaths.ROUTING_TABLE, [], logger)
drp.printErrors = False
drp.parseAlias()
flows = manager.getAllFlowNames(False, drp)

print " ".join(flows)
