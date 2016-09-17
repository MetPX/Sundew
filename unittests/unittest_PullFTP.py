# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_PullFTP.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for PullFTP class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from PullFTP import PullFTP
from Source import Source

class unittest_PullFTP(unittest.TestCase):
   
  def setUp(self,logFile='log/PullFTP.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
    self.source = Source('source-ftp', self.logger)
    self.puller = PullFTP(self.source,self.logger)
    
  def test_PullFTP(self):  
    print self.source.pulls
    print self.puller.get()
    self.assertEqual(None, None)
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_PullFTP))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_PullFTP)
  unittest.TextTestRunner(verbosity=2).run(suite)
