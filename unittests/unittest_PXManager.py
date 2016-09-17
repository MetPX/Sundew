# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_PXManager.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for PXManager class.
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from PXManager import PXManager

class unittest_PXManager(unittest.TestCase):
   
  def setUp(self,logFile='log/PXManager.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
    self.manager = PXManager()  
    self.manager.setLogger(self.logger)
    self.manager.initNames() 
    self.manager.initPXPaths()
    self.manager.initShouldRunNames()
    self.manager.initRunningNames()


  def test_PXManager(self):  
    self.assertEqual(self.manager.getTxNames(), ['client-am', 'client-ftp', 'client-test'])     
    self.assertEqual(self.manager.getFxNames(),['filter-am'])
    self.assertEqual(self.manager.getRxNames(),['source-am','source-ftp','source-test'])
    self.assertEqual(self.manager.getFlowType('client-am'),('TX', ['client-am']))
    self.assertEqual(self.manager.getDBName('MAPS_12Z:OCXCARTE:CMC:CHART:IMV6::20120611192817'),'./db/20120611/CHART/OCXCARTE/CMC/MAPS_12Z:OCXCARTE:CMC:CHART:IMV6::20120611192817')
    self.assertEqual(self.manager.getShouldRunFxNames(),['filter-am'])
    self.assertEqual(self.manager.getShouldRunRxNames(),['source-test'])
    self.assertEqual(self.manager.getShouldRunTxNames(),['client-test'])
    self.assertEqual(self.manager.getRunningFxNames(),['filter-am'])
    self.assertEqual(self.manager.getRunningRxNames(),[])
    self.assertEqual(self.manager.getRunningTxNames(),[])
    self.assertEqual(self.manager.getNotRunningFxNames(),[])
    self.assertEqual(self.manager.getNotRunningRxNames(),['source-test'])
    self.assertEqual(self.manager.getNotRunningTxNames(),['client-test'])
                
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_PXManager))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_PXManager)
  unittest.TextTestRunner(verbosity=2).run(suite)
