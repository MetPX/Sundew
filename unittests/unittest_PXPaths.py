# -*- coding: iso-8859-1 -*-
#############################################################################################
# Name: unittest_PXPaths.py
# Author: Jun Hu 
# Date: 2012-04-30
# Description: test cases for PXPaths class
#############################################################################################
import sys,unittest
sys.path.insert(1, '../sundew/lib/')

import PXPaths

class unittest_PXPaths(unittest.TestCase):
   
  def setUp(self):
    None

  def test_PXPaths(self):      
    PXPaths.normalPaths('')
    self.assertEqual((PXPaths.ROOT,PXPaths.LIB,PXPaths.LOG,PXPaths.ETC,PXPaths.FXQ,PXPaths.RXQ,PXPaths.TXQ,PXPaths.DB,
		      PXPaths.ROUTING_TABLE,PXPaths.STATION_TABLE,PXPaths.FX_CONF,PXPaths.RX_CONF,PXPaths.TX_CONF,PXPaths.TRX_CONF,
		      PXPaths.SCRIPTS,PXPaths.LAT,PXPaths.LAT_RESULTS,PXPaths.LAT_TMP,PXPaths.SHELL_PARSER,PXPaths.PX_DATA), 
		     ('./', './lib/', './log/', './etc/', './fxq/', './rxq/', './txq/', './db/', './etc/pxRouting.conf', './etc/stations.conf', 
		     './etc/fx/', './etc/rx/', './etc/tx/', './etc/trx/', './etc/scripts/', './latencies/', './latencies/results/', './latencies/tmp/', 
		     './lib/shellParser.py', './data/'))
    #self.assertEqual((PXPaths.ROOT,PXPaths.LIB,PXPaths.LOG,PXPaths.ETC,PXPaths.FXQ,PXPaths.RXQ,PXPaths.TXQ,PXPaths.DB,
		      #PXPaths.ROUTING_TABLE,PXPaths.STATION_TABLE,PXPaths.FX_CONF,PXPaths.RX_CONF,PXPaths.TX_CONF,PXPaths.TRX_CONF,
		      #PXPaths.SCRIPTS,PXPaths.LAT,PXPaths.LAT_RESULTS,PXPaths.LAT_TMP,PXPaths.SHELL_PARSER,PXPaths.PX_DATA), 
		     #(None,'/usr/lib/px/','/var/log/px/','/etc/px/','/var/spool/px/fxq/','/var/spool/px/rxq/','/var/spool/px/txq/',
		     #'/var/spool/px/db/','/etc/px/pxRouting.conf','/etc/px/stations.conf','/etc/px/fx/','/etc/px/rx/','/etc/px/tx/','/etc/px/trx/',
		     #'/etc/px/scripts/','/var/spool/px/latencies/','/var/spool/px/latencies/results/','/var/spool/px/latencies/tmp/','/usr/lib/px/shellParser.py','/var/spool/px/data/'))
    
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(unittest_PXPaths))
  return suite
    
if __name__ == '__main__':  
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(unittest_PXPaths)
  unittest.TextTestRunner(verbosity=2).run(suite)
