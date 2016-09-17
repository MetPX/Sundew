# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_MultiKeysStringSorter.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for MultiKeysStringSorter class
#############################################################################################
import sys,unittest,os
sys.path.insert(1, '../sundew/lib/')

from MultiKeysStringSorter import MultiKeysStringSorter

class unittest_MultiKeysStringSorter(unittest.TestCase):
   
  def setUp(self):
    listString = ['/tmp/SACN43:ncp1:CWAO:SA:3.A.I.E::2012',
		  '/tmp/SACN42:ncp1:CWAO:SA:2.A.I.E::2012',
		  '/tmp/SACN42:ncp1:CWAO:SA:1.A.I.E::2012',
		  '/tmp/SACN41:ncp1:CWAO:SA:2.A.I.E::2012']
    self.multiKeysStringSorter = MultiKeysStringSorter(listString)

  def test_MultiKeysStringSorter(self):  
    self.assertEqual(self.multiKeysStringSorter.sort(), 
		     ['/tmp/SACN42:ncp1:CWAO:SA:1.A.I.E::2012', '/tmp/SACN41:ncp1:CWAO:SA:2.A.I.E::2012', '/tmp/SACN42:ncp1:CWAO:SA:2.A.I.E::2012', '/tmp/SACN43:ncp1:CWAO:SA:3.A.I.E::2012'])
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_MultiKeysStringSorter))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_MultiKeysStringSorter)
  unittest.TextTestRunner(verbosity=2).run(suite)
