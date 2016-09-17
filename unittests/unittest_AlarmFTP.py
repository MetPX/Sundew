# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_AlarmFTP.py
# Author: Jun Hu 
# Date: 2012-05-01
# Description: test cases for AlarmFTP class
#############################################################################################
import sys,unittest
sys.path.insert(1, '../sundew/lib/')

from AlarmFTP import AlarmFTP
from AlarmFTP import FtpTimeoutException

class unittest_AlarmFTP(unittest.TestCase):
    
  def setUp(self):
    self.alarm = AlarmFTP('Message AlarmFTP')
    
  def test_AlarmFTP(self):        
    self.assertEqual(self.alarm.message,'Message AlarmFTP')    
    self.alarm.alarm(5)
    self.assertEqual(self.alarm.state,True)    
    self.alarm.cancel()
    self.assertEqual(self.alarm.state,False)    
    textFtpTimeoutException = ''
    try:
      self.alarm.sigalarm('x','x')
    except FtpTimeoutException as error:
      textFtpTimeoutException = str(error)      
    self.assertEqual(textFtpTimeoutException,'Message AlarmFTP')    
    
        
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_AlarmFTP))
  return suite


if __name__ == '__main__': 
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_AlarmFTP)  
  unittest.TextTestRunner(verbosity=2).run(suite)
  
