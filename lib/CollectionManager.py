# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: CollectionManager.py
#       
# Authors: Michel Grenier
#
# Date: 2006-05-16
#
# Description: yet another implementation of a collection...
#
#############################################################################################

"""

import bulletin
import os,string,time
import PXPaths

PXPaths.normalPaths()              # Access to PX paths

# CollectionManager

class CollectionManager(object):
    """
    The collectionManager reads RXQ dir, classifies the bulletins:
    If they have to be ingested do it, if they have to be collected than collect and ingest.
    Unrelated files are removed. Files that are not ready to be collected stay in the RXQ dir.
    """

    def __init__(self, ingestor, bullManager, reader ):
        
        # General Attributes

        self.ingestor    = ingestor
        self.bullManager = bullManager
        self.reader      = reader

        self.logger      = ingestor.logger

        self.data        = []

    #-----------------------------------------------------------------------------------------
    # classify bulletins
    #-----------------------------------------------------------------------------------------

    def classify( self ):

        reader = self.reader

        self.data = reader.getFilesContent(reader.batch)
        if len(self.data) == 0 : return

        self.logger.info("%d bulletins classified in collection", len(self.data))

        for index in range(len(self.data)):
            self.writeIndexBulletin(index)

    #-----------------------------------------------------------------------------------------
    # collection process
    #-----------------------------------------------------------------------------------------

    def process( self ):

        reader      = self.reader
        bullManager = self.bullManager

        reader.read()

        if len(reader.sortedFiles) >= 0 : 
           self.classify()

    #-----------------------------------------------------------------------------------------
    # write index bulletin
    #-----------------------------------------------------------------------------------------

    def writeIndexBulletin( self, index ):

        self.bullManager.writeBulletinToDisk(self.data[index], True, True)
        try:
                os.unlink(self.reader.sortedFiles[index])
                self.logger.debug("%s has been erased", os.path.basename(self.reader.sortedFiles[index]))
        except OSError, e:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (self.reader.sortedFiles[index], type, value))
    
if __name__ == '__main__':
    pass
