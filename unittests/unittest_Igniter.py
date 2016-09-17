# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_Igniter.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for Igniter class
#############################################################################################
import sys,os,unittest,subprocess
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from Igniter import Igniter

class unittest_Igniter(unittest.TestCase):
   
  def setUp(self):
    self.igniter = Igniter('ping localhost', '/tmp/')
    self.process = subprocess.Popen(['ping', 'localhost'], shell=False, stdout=subprocess.PIPE)
    #file = open('/tmp/.lock','w')
    #file.write(str(self.process.pid))   
    #file.close()
    #self.igniter.lock = '/tmp/.lock'
    #self.igniter.lockpid = self.process.pid    
    
  def test_Igniter(self):      
    self.assertEqual(self.igniter.makeLock(),None)
    self.igniter.lock = '/tmp/.lock'
    self.igniter.lockpid = self.process.pid    
    file = open('/tmp/.lock','w')
    file.write(str(self.process.pid))   
    file.close()    
    print '\n'
    self.assertEqual(self.igniter.isLocked(),self.process.pid)
    try:      
      self.igniter.start()
      self.igniter.lockpid =''
    except:
      self.assertEqual(self.igniter.lockpid,self.process.pid)
    try:      
      self.igniter.status()
      self.igniter.lockpid =''
    except:
      self.assertEqual(self.igniter.lockpid,self.process.pid)
    try:      
      self.igniter.stop()
      self.igniter.lockpid =''
    except:
      self.assertEqual(self.igniter.lockpid,self.process.pid)    
    try:      
      self.igniter.status()
      self.igniter.lockpid =''
    except:
      self.assertEqual(self.igniter.lockpid,self.process.pid)      
    #try:      
      #self.igniter.start()
      #self.igniter.lockpid =''
    #except:
      #self.assertEqual(self.igniter.lockpid,self.process.pid)        
    try:
      self.process.terminate()
    except:
      pass
            
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_Igniter))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_Igniter)
  unittest.TextTestRunner(verbosity=2).run(suite)
