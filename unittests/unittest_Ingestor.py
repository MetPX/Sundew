# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_Ingestor.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for Ingestor class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Logger import Logger
from Ingestor import Ingestor
from Source import Source

class unittest_Ingestor(unittest.TestCase):
   
  def setUp(self,logFile='log/Template.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger() 
    self.source = Source('source-test', self.logger)
    self.ingestor = Ingestor(self.source,self.logger)
    self.ingestor.setClients()
      
  def test_Ingestor(self):  
    print self.ingestor.clients

    #filter.ingestor.ingestSingleFile(igniter)
    #filter.ingestor.ingestBulletinFile(igniter)
    #source.ingestor.ingestSingleFile(igniter)
    #source.ingestor.ingestBulletinFile(igniter)
    #source.ingestor.ingestCollection(igniter)
    #self.ingestor.setFeeds(self.feeds)
    #self.ingestor.setClients()
    #source.ingestor.createDir('/apps/px/turton', source.ingestor.dbDirsCache)
    #self.drp = DirectRoutingParser(pathFichierCircuit, self.source.ingestor.allNames, logger)
    #self.source.ingestor.ingest()
    #self.source.ingestor.getMatchingClientNamesFromMasks(nomFichier, clist)
    #self.source.ingestor.ingest(tempNom, nomFichier, clist)
    #self.source.ingestor.ingest()
    #clist = self.source.ingestor.getMatchingClientNamesFromMasks(nomFichier, clist)
    #self.source.ingestor.ingest(tempNom, nomFichier, clist)
    #self.assertEqual(None, None)
    pass
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_Ingestor))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_Ingestor)
  unittest.TextTestRunner(verbosity=2).run(suite)
