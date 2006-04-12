# -*- coding: UTF-8 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: BulletinCollection.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-19
#
# Description:  This module extends the PX's standard bulletin and gives us the
#               functionality needed for collection operations.
#
# Revision History: 
#   Feb. 9, 2006  KA.  Moving buildImmediateCollectionFromReport to CollectionBuilder.py
#
#############################################################################################
"""
__version__ = '1.1'

import bulletin
import string
from Logger import Logger

#-----------------------------------------------------------------------------------------
# Global attribute
#-----------------------------------------------------------------------------------------
blankValue = '   '

class BulletinCollection(bulletin.bulletin):
    """ BulletinCollection(bulletin.bulletin):

        This class extends PX's bulletin class and adds the methods we need
        in order to carry out collections.
        This class will add the following attributes to a bulletin:

            collectionBBB     string
                    -Represents the BBB field for a collection

            bulletinTimeStamp   string
                                -Timestamp for this bulletin
            

    """
    def __init__(self,stringBulletin,logger,lineSeparator='\n'):
        #-----------------------------------------------------------------------------------------
        # Class attributes
        #-----------------------------------------------------------------------------------------
        bulletin.bulletin.__init__(self,stringBulletin,logger,lineSeparator='\n')
        self.collectionBBB = blankValue   # The BBB value which we'll dertermine for the collection bulletin
        self.collectionPath = ''          # Path of this bulletin in the 'collection' sub-dir


    def getTimeStamp(self):
        """ getTimeStamp() parses the header and returns the timestamp as a string
        """
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = self.getHeader().split() 

        #-----------------------------------------------------------------------------------------
        # the timstamp is always the third token in header
        #-----------------------------------------------------------------------------------------
        timeStamp = headerTokens[2] 
        return timeStamp


    def getTimeStampWithMinsSetToZero(self):
        """ getTimeStampWithMinsSetToZero() returns the timestamp but with the minute
            field set to zero.
        """
        #-----------------------------------------------------------------------------------------
        # sets mins to zero
        #-----------------------------------------------------------------------------------------
        zeroedMinTime = self.getBulletinDaysField() + self.getBulletinHoursField() + '00'
        return zeroedMinTime


    """ The following get & set methods are here to make CollectionManager easy to read
        They do the obvious.
    """
    def getCollectionBBB(self):
        return str(self.collectionBBB).strip()

    def getCollectionB1(self):
        return self.collectionBBB[0]

    def getCollectionB2(self):
        return self.collectionBBB[1]

    def getCollectionB3(self):
        return self.collectionBBB[2]

    def setCollectionB1(self, newCollectionB):
        self.collectionBBB = "%s%s%s" % (newCollectionB, self.collectionBBB[1], self.collectionBBB[2])

    def setCollectionB2(self, newCollectionB):
        self.collectionBBB = "%s%s%s" % (self.collectionBBB[0], newCollectionB, self.collectionBBB[2])

    def setCollectionB3(self, newCollectionB):
        self.collectionBBB = "%s%s%s" % (self.collectionBBB[0], self.collectionBBB[1], newCollectionB)

    def setCollectionBBB(self,newBBB):
        if not(newBBB):
            self.colletionBBB = blankValue
        elif(len(str(newBBB)) == 3):
            self.collectionBBB = newBBB
        else:
            self.logger.error("The given BBB value: %s is invalid!" %newBBB)

    def getTwoLetterType(self):
        """ getTwoLetterType() parses the header and returns the two letter header
            (I.e 'SA' will be returned for 'SACNXX')
        """
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = self.getHeader().split() 

        #-----------------------------------------------------------------------------------------
        # the first two letters of the first element make up the two-letter header
        #-----------------------------------------------------------------------------------------
        TwoLetterType = headerTokens[0] 
        return TwoLetterType[:2]


    def getFullType(self):
        """ getFullHeaderType() parses the header and returns the type
            (I.e 'SACN51' from SACN51 CWAO 062000)
        """
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = self.getHeader().split() 
        #-----------------------------------------------------------------------------------------
        # the full type is the first element in the header
        #-----------------------------------------------------------------------------------------
        return headerTokens[0]


    def getBulletinMinutesField(self):
        """ getBulletinMinutesField() parses the header and returns the minutes field
            of the bulletin.
        """
        #-----------------------------------------------------------------------------------------
        # get the timestamp
        #-----------------------------------------------------------------------------------------
        timeStamp = self.getTimeStamp() 
        
        #-----------------------------------------------------------------------------------------
        # the minutes field is made up of the last two chars in the timestamp in DDHHMM
        #-----------------------------------------------------------------------------------------
        minutesField = timeStamp[(len(timeStamp) -2):]
        return minutesField


    def getBulletinHoursField(self):
        """ getBulletinHoursField() parses the header and returns the hours field
            of the bulletin.
        """
        #-----------------------------------------------------------------------------------------
        # get the timestamp
        #-----------------------------------------------------------------------------------------
        timeStamp = self.getTimeStamp()  

        #-----------------------------------------------------------------------------------------
        # the hours field is made up of the middle two chars in the timestamp in DDHHMM
        #-----------------------------------------------------------------------------------------
        hoursField = timeStamp[2:4]
        return hoursField


    def getBulletinDaysField(self):
        """ getBulletinDaysField() parses the header and returns the days field
            of the bulletin.
        """
        #-----------------------------------------------------------------------------------------
        # get the timestamp
        #-----------------------------------------------------------------------------------------
        timeStamp = self.getTimeStamp()  

        #-----------------------------------------------------------------------------------------
        # the hours field is made up of the first two chars in the timestamp in DDHHMM
        #-----------------------------------------------------------------------------------------
        daysField = timeStamp[:2]
        return daysField


    def getReportBBB(self):
        """ getReportBBB() -> String || False

            parses the header and returns the BBB field
            in the bulletin, or False if one does not exist.
        """
        False == ''
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = self.getHeader().split() 
        
        #-----------------------------------------------------------------------------------------
        # The header looks like "SACN58 CWAO 231334 BBB".  The BBB field is the fourth element
        #-----------------------------------------------------------------------------------------
        if (len(headerTokens) > 3):
            return headerTokens[3]
        else:
            return False


    def getReportB1(self):
        """ getReportB1() -> Char || False

            parses the header and returns the first element
            of the BBB field in the bulletin, or False if one 
            does not exist.
        """
        False == ''
        #-----------------------------------------------------------------------------------------
        # get the report's BBB field
        #-----------------------------------------------------------------------------------------
        reportBBB = self.getReportBBB()
        
        #-----------------------------------------------------------------------------------------
        # return first element
        #-----------------------------------------------------------------------------------------
        if (reportBBB):
            return reportBBB[0]
        else:
            return False


    def getReportB2(self):
        """ getReportB2() -> Char || False

            parses the header and returns the second element
            of the BBB field in the bulletin, or False if one 
            does not exist.
        """
        False == ''
        #-----------------------------------------------------------------------------------------
        # get the report's BBB field
        #-----------------------------------------------------------------------------------------
        reportBBB = self.getReportBBB()

        #-----------------------------------------------------------------------------------------
        # return second element
        #-----------------------------------------------------------------------------------------
        if (reportBBB):
            return reportBBB[1]
        else:
            return False


    def bulletinAsString(self):
        """ bulletinAsString([list]) -> string

            Converts a bulletin which is stored as a list into 
            a string.
            (I.e. ['SACN98 CWAO 291600 ','ZMJ SA 1600 AUTO8 M M M 089////M/ 3009 92MM=', '']
                  will be converted into "SACN98 CWAO 291600 
                                          ZMJ SA 1600 AUTO8 M M M 089////M/ 3009 92MM=" 

        """
        #-----------------------------------------------------------------------------------------
        # Stripping out all list related symbols
        #-----------------------------------------------------------------------------------------
        bullString = ''
        for element in self.bulletin:
            bullString = bullString+str(element)+"\n"

        return bullString.strip()


    def setReportBBB(self,BBB):
        """ setReportBBB(BBB)

            Given a BBB string, this method sets the report's BBB field to the 
            given BBB variable
        """
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = self.getHeader().split() 
        
        #-----------------------------------------------------------------------------------------
        # The header looks like "SACN58 CWAO 231334 BBB".  The BBB field is the fourth element
        #-----------------------------------------------------------------------------------------
        if (len(headerTokens) >= 3):
            newHeader = headerTokens[0]+' '+headerTokens[1]+' '+headerTokens[2]+' '+BBB
            self.setHeader(newHeader.strip())

        #print "REMOVEME: Modified the collection's bbb. New HDR is: ",self.getHeader()
        

    
    def setBulletinMinutesField(self,newValue):
        """ setBulletinMinutesField(newValue)

            This method sets the minutes in the bulletin's timestamp (located
            in the header) to the given value.
            I.e. 'SACN94 CWAO 080319' becomes 'SACN94 CWAO 080300'

            newValue    string  Represents the minutes in ddhhmm
        """
        #-----------------------------------------------------------------------------------------
        # Build the new time stamp
        #-----------------------------------------------------------------------------------------
        timeStamp = self.getTimeStamp()
        newTimeStamp = timeStamp[:-2]+ newValue

        #-----------------------------------------------------------------------------------------
        # get the header as a list
        #-----------------------------------------------------------------------------------------
        headerTokens = self.getHeader().split() 

        #-----------------------------------------------------------------------------------------
        # The header looks like "SACN58 CWAO 231334 BBB".  Replace the time stamp
        #-----------------------------------------------------------------------------------------
        if (len(headerTokens) >= 3):
            newHeader = headerTokens
            newHeader[2] = newTimeStamp
            newHeader = " ".join(newHeader)
            self.setHeader(newHeader.strip())

        #print "REMOVEME: Modified the collection's timeStamp. New HDR is: ",self.getHeader()


    def setCollectionPath(self,path):
        """ setCollectionPath(path)

            Set the path for this collection to the given path.  The path is where this
            bulletin resides in the 'colleciton' sub-dir.  
            This path may be used to mark the collection as sent.
        """
        self.collectionPath = path


    def getCollectionPath(self):
        """ getCollectionPath()

            Returns the collection's path.  The path is where this
            bulletin resides in the 'colleciton' sub-dir.  
            This path may be used to mark the collection as sent.
        """
        return self.collectionPath



