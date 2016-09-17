# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_senderAm.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for senderAm class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from Client import Client
from CacheManager import CacheManager
from senderAm import sendeAm

class unittest_Template(unittest.TestCase):
   
  def setUp(self,logFile='log/Template.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
      

  def test_Template(self):  
    self.assertEqual(None, None)
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_Template))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_Template)
  unittest.TextTestRunner(verbosity=2).run(suite)
