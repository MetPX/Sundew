# -*- coding: UTF-8 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: CollectionBuilder.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-19
#
# Description:  This module handles creating Collections from various inputs.
#               You could consider it a way of abstracting collection constructor
#               overloading.
#
# Revision History: 
#   Feb. 9, 2006  KA.  Moved buildImmediateCollectionFromReport here.
#               
#############################################################################################
"""
__version__ = '1.1'

import BulletinCollection
import CollectionUtils
from Logger import Logger

class CollectionBuilder:
    """ CollectionBuilder():

        This class is responsible for creating BulletinCollection objects from various.

        This class will add the following attributes to a bulletin:

            b1SubField          string
            b2SubField          string
            b3SubField          string 
                                -Represents the corresponding B in the BBB field for 
                                a report or bulletin

            bulletinTimeStamp   string
                                -Timestamp for this bulletin
            

    """

    def __init__(self,logger):
        self.logger = logger            # Logger object
        self.lineSeparator = '\n'       # Liner separator used when generating bulletin


    def buildBulletinFromFile(self,fileName):
        """ buildBulletinFromFile(fileName) -> :BulletinCollection

            This method loads the information in the given file into a 
            bulletin object and returns it

        """
        #-----------------------------------------------------------------------------------------
        # Open the file and read contents
        #-----------------------------------------------------------------------------------------
        try:
            file = open(fileName, 'r')
        except IOError:
            self.logger.exception("Cannot open file: %s for reading" % fileName)
        rawBulletin = file.read()

        #-----------------------------------------------------------------------------------------
        # Call upon BulletinCollection to produce a bulletin object based on the info
        # read from the file
        #-----------------------------------------------------------------------------------------
        bulletinObject = BulletinCollection.BulletinCollection(rawBulletin, self.logger, self.lineSeparator)
        
        #-----------------------------------------------------------------------------------------
        # Returning a bulletin object based on info in given filename
        #-----------------------------------------------------------------------------------------
        return bulletinObject


    def appendToCollectionFromFile(self, aCollection, fileName):
        """ appendToCollectionFromFile(collection, fileName) -> :BulletinCollection

            This method appends the report body given in 'fileName' to the 
            collection bulletin object given in 'aCollection' and returns the 
            new and updated 'aCollection' object.

        """
        #-----------------------------------------------------------------------------------------
        # The bulleting looks like ['SACN48 CWAO 171600', 'METAR CYWK 171600Z 01005KT 15SM SCT011 
        #                            M20/M26 A3002 RMK SF2 SLP228=', '']
        # But the number of elements may change. Get rid of the first element because it's the
        # header (element [0])
        #-----------------------------------------------------------------------------------------
        bulletinBody = self.buildBulletinFromFile(fileName).bulletin
        bulletinBody.pop(0)

        #-----------------------------------------------------------------------------------------
        # Append bulletin elements to the body of the collection and return collection.
        #-----------------------------------------------------------------------------------------
        for element in bulletinBody:
            aCollection.bulletin.append(element)
        return self.stripCollection(aCollection)


    def buildImmediateCollectionFromReport(self,bulletin):
        """ buildImmediateCollectionFromReport(bulletin)

            This method constructs a collection bulletin based on the given
            bulletin.  The collection bulletin will come complete with the 
            the appropriate BBB values.  
            The new collection bulletin is then returned to the caller
        """
        #-----------------------------------------------------------------------------------------
        # Create a collection bulletin which is initially just a copy of the report bulletin
        #-----------------------------------------------------------------------------------------
        newCollectionBulletin = bulletin

        #-----------------------------------------------------------------------------------------
        # Here, we need to update or create the report's BBB value with that of the collection, 
        # but we're taking care to set a report's BBB to 'CCX' instead of 'CCX1'
        #-----------------------------------------------------------------------------------------
        newCollectionBulletin.setReportBBB(newCollectionBulletin.getCollectionB1() + \
                                           newCollectionBulletin.getCollectionB2() + \
                                           newCollectionBulletin.getCollectionB3())

        #-----------------------------------------------------------------------------------------
        # Change the minutes field to '00'. I.e. 'SACN94 CWAO 080319' becomes 'SACN94 CWAO 080300'
        #-----------------------------------------------------------------------------------------
        newCollectionBulletin.setBulletinMinutesField('00')

        #-----------------------------------------------------------------------------------------
        # Set the new collection's directory path (where it is in the collection sub-dir)
        #-----------------------------------------------------------------------------------------
        newCollectionBulletin.setCollectionPath(CollectionUtils.calculateBBBDirName(bulletin))
        return newCollectionBulletin


    def stripCollection(self, aCollection):
        """ stripCollection() -> :BulletinCollection

            This method removes newlines from the collection's bulletin
            list.    
        """
        while (aCollection.bulletin.count('')):
            aCollection.bulletin.remove('')
        return aCollection


    
