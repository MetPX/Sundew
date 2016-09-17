# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_TextSplitter.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for TextSplitter class
#############################################################################################
import sys,os,unittest
sys.path.insert(1, '../sundew/lib/')
os.environ['PXROOT']="."

from TextSplitter import TextSplitter

class unittest_TextSplitter(unittest.TestCase):
   
  def setUp(self):    
    f = open('db/test-file-bulletin','r')   
    text = f.read(8192)
    f.close()   
    self.splitter = TextSplitter(text, 40,' ', 5)
    
  def test_TextSplitter(self):   
    self.assertEqual(self.splitter.breakLongText(), ['FNCN55 CWAO 040800 ', 'Extended forecasts for Wednesday T ', 'hursday Friday Saturday and Sunday ', 'for the Maritimes and Iles de la M ', 'adeleine issued by Environment ', 'Canada at 5.00 am adt Monday 4 Jun ', 'e 2012. ', 'Mon Jun  4 04:00:01 EDT 2012  '])
    self.assertEqual(self.splitter.breakMarker(), ['FNCN55 CWAO 040800\nExtended forecasts fo', 'r Wednesday Thursday Friday Saturday and', ' Sunday\nfor the Maritimes and Iles de la', ' Madeleine issued by Environment\nCanada ', 'at 5.00 am adt Monday 4 June 2012.\nMon J', 'un  4 04:00:01 EDT 2012\n\n'])
    
        
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_TextSplitter))
  return suite
    
if __name__ == '__main__':  
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_TextSplitter)
  unittest.TextTestRunner(verbosity=2).run(suite)
