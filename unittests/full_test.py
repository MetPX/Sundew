# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: full_test.py
# Author: Jun Hu 
# Date: 2012-04-11
# Description: Running a full test for metpx sundew.
#############################################################################################
import sys
sys.path.insert(1, '../sundew/lib/')

import unittest
import unittest_Logger
import unittest_PXPaths
import unittest_URLParser
import unittest_AlarmFTP
import unittest_DirectRoutingParser
import unittest_CacheManager
import unittest_Client
import unittest_SortableString
import unittest_MultiKeysStringSorter
import unittest_DiskReader
import unittest_Igniter
import unittest_TextSplitter
import unittest_Source
import unittest_PXManager
import unittest_SenderFTP
import unittest_Grib
import unittest_Bufr

suite = unittest.TestSuite()
suite.addTest(unittest_Logger.suite())
suite.addTest(unittest_PXPaths.suite())
suite.addTest(unittest_URLParser.suite())
suite.addTest(unittest_AlarmFTP.suite())
suite.addTest(unittest_DirectRoutingParser.suite())
suite.addTest(unittest_CacheManager.suite())
suite.addTest(unittest_Client.suite())
suite.addTest(unittest_SortableString.suite())
suite.addTest(unittest_MultiKeysStringSorter.suite())
suite.addTest(unittest_DiskReader.suite())
suite.addTest(unittest_Igniter.suite())
suite.addTest(unittest_TextSplitter.suite())
suite.addTest(unittest_Source.suite())
suite.addTest(unittest_PXManager.suite())
suite.addTest(unittest_SenderFTP.suite())
suite.addTest(unittest_Grib.suite())
suite.addTest(unittest_Bufr.suite())

unittest.TextTestRunner(verbosity=2).run(suite)


