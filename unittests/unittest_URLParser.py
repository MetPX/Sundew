# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_URLParser.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for URLParser class
#############################################################################################
import sys,unittest
sys.path.insert(1, '../sundew/lib/')

from Logger import Logger
from URLParser import URLParser

class unittest_URLParser(unittest.TestCase):
   
  def setUp(self,logFile='log/URLParser.log'):
    self.logger = Logger(logFile, 'DEBUG', 'Sub')    
    self.logger = self.logger.getLogger()    
    self.parser1 = URLParser('am://test.cmc.ec.gc.ca:24901')    
    self.parser2 = URLParser('wmo://192.108.62.1:24901')    
    self.parser3 = URLParser('file://localhost//apps/px/operator')
    self.parser4 = URLParser('amqp://guest:guestpw@test.cmc.ec.gc.ca//data')
    self.parser5 = URLParser('amis://test.cmc.ec.gc.ca:24901')
    self.parser6 = URLParser('ftp://guest:guestpw@192.108.62.1//data')    

  def test_URLParser(self):          
    self.assertEqual(self.parser1.parse(), ('am', None, None, None, 'test.cmc.ec.gc.ca', '24901'))
    self.assertEqual(self.parser1.join(self.parser1.protocol, self.parser1.path, self.parser1.user, self.parser1.passwd, self.parser1.host, self.parser1.port),'am://test.cmc.ec.gc.ca:24901')
    self.assertEqual(self.parser2.parse(), ('wmo', None, None, None, '192.108.62.1', '24901'))
    self.assertEqual(self.parser3.parse(), ('file', '//apps/px/operator', None, None, 'localhost', None))    
    self.assertEqual(self.parser4.parse(), ('amqp', '//data', 'guest', 'guestpw', 'test.cmc.ec.gc.ca', None))    
    self.assertEqual(self.parser4.join(self.parser4.protocol, self.parser4.path, self.parser4.user, self.parser4.passwd, self.parser4.host, self.parser4.port),'amqp://guest:guestpw@test.cmc.ec.gc.ca//data')    
    self.assertEqual(self.parser5.parse(), ('amis', None, None, None, 'test.cmc.ec.gc.ca', '24901'))    
    self.assertEqual(self.parser6.parse(), ('ftp', '//data', 'guest', 'guestpw', '192.108.62.1', None))    
    self.assertEqual(self.parser6.join(self.parser6.protocol, self.parser6.path, self.parser6.user, self.parser6.passwd, self.parser6.host, self.parser6.port),'ftp://guest:guestpw@192.108.62.1//data')
    
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_URLParser))
  return suite
    
if __name__ == '__main__':  
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_URLParser)
  unittest.TextTestRunner(verbosity=2).run(suite)
