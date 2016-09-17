# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_DirectRoutingParser.py
# Author: Jun Hu 
# Date: 2012-04-11
# Description: test cases for DirectRoutingParser class
#############################################################################################
import sys,unittest
sys.path.insert(1, '../sundew/lib/')

from Logger import Logger
from DirectRoutingParser import DirectRoutingParser

class unittest_DirectRoutingParser(unittest.TestCase):
   
  def setUp(self,logFile='log/DirectRoutingParser.log', routingFile='etc/routing1.conf'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()
    self.pxLinkables = ['allproducts','cmc','aftn','satnet-ice','test6','TOTO']
    self.parser = DirectRoutingParser(routingFile, self.pxLinkables, self.logger)
    
   
  def test_DirectRoutingParser(self):    
    self.assertEqual(self.parser.parse(), None)
    self.assertEqual(self.parser.getHeaderPriority('AACN01_ANIK'), '1')
    self.assertEqual(self.parser.getClients('AACN01_ANIK'), ['test6'])
    self.assertEqual(self.parser.getHeaderSubClients('AACN02_ANIK').get('aftn', []),['CYOWFABX','CYYZWSAC','CYYZOWAC','CYYZWGAC'])
    self.assertEqual(self.parser.getHeaderPriority('MAPS_MICHEL'), '4')
    self.assertEqual(self.parser.getClients('MAPS_MICHEL'), ['allproducts','TOTO'])
    
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_DirectRoutingParser))
  return suite
    
if __name__ == '__main__':  
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_DirectRoutingParser)
  unittest.TextTestRunner(verbosity=2).run(suite)
