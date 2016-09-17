# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_Logger.py
# Author: Jun Hu 
# Date: 2012-04-11
# Description: test cases for Logger class
#############################################################################################
import sys,unittest
sys.path.insert(1, '../sundew/lib/')

from Logger import Logger

class unittest_Logger(unittest.TestCase):
    
  def setUp(self,logFile='log/Logger.log'):
    self.logger = Logger(logFile, 'VERYVERYVERBOSE', 'CMISX')    
    self.logger = self.logger.getLogger()
   
  def test_Logger(self):    
    self.assertEqual(self.logger.exception('Ceci est exception'), None)    
    self.assertEqual(self.logger.veryverbose('Ceci est veryverbose'), None)
    self.assertEqual(self.logger.veryveryverbose('Ceci est veryveryverbose'),None)    
    
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_Logger))
  return suite


if __name__ == '__main__': 
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_Logger)  
  unittest.TextTestRunner(verbosity=2).run(suite)
  
