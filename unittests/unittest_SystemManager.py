# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_SystemManager.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for SystemManager class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from SystemManager import SystemManager

class unittest_SystemManager(unittest.TestCase):
   
  def setUp(self):
    pass  

  def test_SystemManager(self):  
    self.assertEqual(None, None)
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_SystemManager))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_SystemManager)
  unittest.TextTestRunner(verbosity=2).run(suite)
