# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_Template.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: template for unittest class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from Source import Source

class unittest_Source(unittest.TestCase):
   
  def setUp(self,logFile='log/Source.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
    self.source1 = Source('source-test', self.logger)
    self.source2 = Source('source-am', self.logger)

  def test_Source(self):  
    self.source1.readConfig('etc/rx/source-test.conf')    
    self.assertEqual(self.source1.name,'source-test')
    self.assertEqual(self.source1.batch,1000)
    self.assertEqual(self.source1.fx_script(),'Done')
    self.assertEqual(self.source1.pull_script(self.source1,self.logger,10),'Done')
    
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_Source))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_Source)
  unittest.TextTestRunner(verbosity=2).run(suite)
