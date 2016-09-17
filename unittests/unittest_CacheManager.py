# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_CacheManager.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for CacheManager class
#############################################################################################
import sys,time,unittest
sys.path.insert(1, '../sundew/lib/')

from CacheManager import CacheManager

class unittest_CacheManager(unittest.TestCase):
   
  def setUp(self):
    self.manager = CacheManager(maxEntries=3, timeout=5 * 3600)
    self.files = ['db/test-file-grib', 'db/test-file-burf', 'db/test-file-bulletin']
    #f = open(self.files[0])
    #self.data = f.read(1048576)
    #while len(self.data) :
      #print self.data
      #self.data = f.read(1048576)
    #f.close()    
    self.data = 'ceci est un test'

  def test_CacheManager(self):              
    self.assertEqual(self.manager.get_md5_from_file(self.files[0]),'57285445a1c80023b3f2e96546754d5b')    
    self.manager.find(self.data,'md5')
    self.manager.find(self.files[1])  
    #md5 of self.data = 11b35a0201513381dcdd130831f702d0
    self.assertEqual(self.manager.has('11b35a0201513381dcdd130831f702d0'),True)    
    self.assertEqual(self.manager.has(self.files[2]),False)    
    self.manager.find(self.data,'md5')
    self.manager.find(self.files[1])    
    self.manager.find(self.files[2])
    self.assertEqual(self.manager.getStats(),({1: 1, 2: 2}, 2.0, 5.0))
    self.manager.find(self.files[0])
    time.sleep(3)
    self.manager.timeoutClear(3)
    self.assertEqual(self.manager.cache,{})
    
    
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_CacheManager))
  return suite
    
if __name__ == '__main__':  
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_CacheManager)
  unittest.TextTestRunner(verbosity=2).run(suite)
