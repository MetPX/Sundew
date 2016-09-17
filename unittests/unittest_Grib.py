# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_Grib.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for Grib class.
#############################################################################################
import sys,unittest
sys.path.insert(1, '../sundew/lib/')

from Grib import Grib

class unittest_Grib(unittest.TestCase):
   
  def setUp(self):
    stringBulletin = "TEST_GRIB_TEST"
    self.grib = Grib(stringBulletin)

  def test_Grib(self):      
    self.assertEqual(self.grib.begin, 5)
    self.assertEqual(self.grib.last, -1)
    self.assertEqual(self.grib.validate(), False)
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_Grib))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_Grib)
  unittest.TextTestRunner(verbosity=2).run(suite)
