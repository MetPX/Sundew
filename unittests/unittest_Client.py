# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_Client.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for Client class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from Client import Client

class unittest_Client(unittest.TestCase):
   
  def setUp(self,logFile='log/Client.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
    self.client1 = Client('client-ftp',self.logger)
    self.client2 = Client('client-am',self.logger)
   

  def test_Client(self):  
    self.client1.readConfig()    
    self.assertEqual(self.client1.name,'client-ftp')
    self.assertEqual(self.client1.protocol,'ftp')
    self.assertEqual(self.client1.getDestInfos('TOTO'), (None, None))
    self.assertEqual(self.client1.getDestInfos('iceglbgrib2:iceglb:CMC:GRIB:BIN:2012061800'),('iceglbgrib2:iceglb:CMC:GRIB:BIN:2012061800', '//isis_feed/ftp/cmc_grib2'))    
    self.assertEqual(self.client1.fx_script(),'Done')
    self.assertEqual(self.client1.destfn_script(),'Done')    
    self.assertEqual(self.client1.getDestInfos('MAPS_GFACN:GFA:CMC:CHART:PNG:2012061800'),('MAPS_GFACN:GFA:CMC:CHART:PNG:2012061800', '//isis_feed/ftp/prdnamed'))
    self.assertEqual(self.client1.destfn_execfile,'script3.py')
   
    
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_Client))
  return suite
    
if __name__ == '__main__':  
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_Client)
  unittest.TextTestRunner(verbosity=2).run(suite)
