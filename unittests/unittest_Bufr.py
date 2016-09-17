# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_Bufr.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for Bufr class.
#############################################################################################
import sys,unittest
sys.path.insert(1, '../sundew/lib/')

from Bufr import Bufr

class unittest_Bufr(unittest.TestCase):
   
  def setUp(self):
    f = file('etc/ISAA51_CWXS_211500___60968:ncp1deb-bufr:CWXS:IS:3:ncpdeb_bufr:20120821150803')     
    self.bufr = Bufr(f.read())
    f.close()
    
  def test_Burf(self):      
    self.assertEqual(self.bufr.begin,19)
    self.assertEqual(self.bufr.last,699)
    self.assertEqual(self.bufr.valid,True)
    self.assertEqual(self.bufr.observation,'201208211500')
    self.assertEqual(self.bufr.ep_observation,1345561200.0)

            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_Bufr))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_Bufr)
  unittest.TextTestRunner(verbosity=2).run(suite)
