# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_SortablesString.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for SortablesString class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')

from SortableString import SortableString

class unittest_SortableString(unittest.TestCase):
   
  def setUp(self):
    self.sortableString = SortableString('/tmp/test/SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339')
      

  def test_SortableString(self):  
    self.assertEqual(self.sortableString.data,'/tmp/test/SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339')
    self.assertEqual(self.sortableString.basename,'SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339')
    self.assertEqual(self.sortableString.priority,'3')
    self.assertEqual(self.sortableString.timestamp,'20050201200339')
    self.assertEqual(self.sortableString.concatenatedKeys,'320050201200339')
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_SortableString))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_SortableString)
  unittest.TextTestRunner(verbosity=2).run(suite)
