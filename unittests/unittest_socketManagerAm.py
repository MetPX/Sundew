# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_socketManagerAm.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for socketManagerAm class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from socketManagerAm import socketManagerAm

class unittest_socketManagerAm(unittest.TestCase):
   
  def setUp(self,logFile='log/socketManagerAm.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
    self.socketManager = socketManagerAm(self.logger, type='slave', port=10000, remoteHost=None, timeout=None, flow=self.flow)
    

  def test_socketManagerAm(self):  
    self.assertEqual(None, None)
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_socketManagerAm))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_socketManagerAm)
  unittest.TextTestRunner(verbosity=2).run(suite)
