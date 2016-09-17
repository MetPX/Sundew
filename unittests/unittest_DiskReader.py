# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_DiskReader.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for DiskReader class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from DiskReader import DiskReader

class unittest_DiskReader(unittest.TestCase):
   
  def setUp(self,logFile='log/DiskReader.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
    self.reader = DiskReader('txq/test/', 20, False, 5, False,True,self.logger)


  def test_DiskReader(self):  
    
    self.reader.read()
    #print self.reader.files
    self.assertEqual(self.reader.files,['txq/test//0/2012053108/file-F', 'txq/test//1/2012053108/file-E', 'txq/test//2/2012053108/file-D', 'txq/test//3/2012053108/file-A', 'txq/test//3/2012053108/file-C', 'txq/test//4/2012053108/file-B', 'txq/test//5/2012053108/file-A'])
    #print self.reader.getFilenamesAndContent()
    self.assertEqual(self.reader.getFilenamesAndContent(),[('', 'txq/test//0/2012053108/file-F'), ('file E', 'txq/test//1/2012053108/file-E'), ('', 'txq/test//2/2012053108/file-D'), ('file A', 'txq/test//3/2012053108/file-A'), ('file C', 'txq/test//3/2012053108/file-C'), ('', 'txq/test//4/2012053108/file-B'), ('', 'txq/test//5/2012053108/file-A')])
    
    
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_DiskReader))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_DiskReader)
  unittest.TextTestRunner(verbosity=2).run(suite)
