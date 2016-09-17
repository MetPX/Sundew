# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_SenderFTP.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for SenderFTP class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from Client import Client
from CacheManager import CacheManager
from SenderFTP import SenderFTP

class unittest_SenderFTP(unittest.TestCase):
   
  def setUp(self,logFile='log/SenderFTP.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
    self.client = Client('client-test',self.logger)  
    self.cacheManager = CacheManager(maxEntries=3, timeout=5 * 3600)
    #Le sender doit etre capable de connecter au serveur ftp pour continuer le test.
    self.sender = SenderFTP(self.client, self.logger, self.cacheManager)
    file1 = open("txq/client-test/3/test","w")
    file1.close()
    self.files = ['txq/client-test/3/test']
    

  def test_SenderFTP(self):  
    #print self.client.masks
    self.assertEqual(self.sender.basename_parts("toto"),None)
    self.assertEqual(self.sender.basename_parts("test:neverwinter:cmc:grib:bin"),['test:neverwinter:cmc:grib:bin'])
    self.assertEqual(self.sender.basename_parts("iceglbgrib2_12:iceglb:CMC:GRIB:BIN:2012"),['12', 'CMC', 'GRIB'])
    self.assertEqual(self.sender.dirPattern(file,"iceglbgrib2_12:iceglb:CMC:GRIB:BIN:2012","/tmp/test/${0}/${1}/${2}",""),'/tmp/test/12/CMC/GRIB')   
    self.assertEqual(self.sender.send(self.files),None)
    self.sender.close()
    self.assertEqual(os.listdir('txq/client-test/3/'),[])
    
    
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_SenderFTP))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_SenderFTP)
  unittest.TextTestRunner(verbosity=2).run(suite)
