"""
#############################################################################################
# Name: wmoid.py
#
# Author:  Michel Grenier 
#
# Date: 2009-06-19
#
# Description: parse the wmo_id.conf file
#              this file is used to force the station name into the ingested filename
#
#############################################################################################
"""

import os, os.path, sys

import PXPaths

class wmoid:

    def __init__(self, logger ):
        self.logger = logger
        self.wmo_ids = []
	PXPaths.normalPaths()
        self.path = PXPaths.ETC + 'wmo_id.conf'

    def parse(self):

        if not os.path.isfile(self.path) : return self.wmo_ids

        try :
               file = open(self.path,'r')
               lines = file.readlines()
               file.close()

               for line in lines:
                   if len(line) <= 0   : continue
                   if line[0] == '#'   : continue
                   if line[0] == '\n'  : continue
                   words = line.split()
                   if len(words) == 0 : continue
                   self.wmo_ids.extend(words)
        except:
                  (type, value, tb) = sys.exc_info()
                  self.logger.error("Type: %s, Value: %s" % (type, value))
                  self.logger.error("Problem with parsing the wmo_id.conf")
                  return []

        #self.logger.info("wmo_id.conf gives %s" % self.wmo_ids)
        return self.wmo_ids
      
if __name__ == '__main__':

    print wmoid(None).parse()
