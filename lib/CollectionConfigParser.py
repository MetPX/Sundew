# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: CollectionConfigParser.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-19
#
# Description:  This module provides access to the global collection configuration
#               parameters.
#
# Revision History: 
#               
#############################################################################################
"""
__version__ = '1.0'

from Logger import Logger
import string
import PXPaths

PXPaths.normalPaths()              # Access to PX paths

class CollectionConfigParser:
    """ CollectionConfigParser():

        This class provides access to the global collection configuration
        parameters
    """

    def __init__ (self, logger, source):
        self.logger = logger        # Logger object
        self.source = source        # The source object containing the global collection config params


    def getReportValidTimeByHeader (self, header):
        """ getReportValidTimeByHeader (self, Header) -> string

            Given the Two letter header, returns a string representing how many minutes past
            the hour a bulletin of this type is considered valid according to the global
            collection config parameters.
        """
        #-----------------------------------------------------------------------------------------
        # Find out the index of the given header in the headersToCollect list
        #-----------------------------------------------------------------------------------------
        headerIndex = self._getIndexForHeader(header)

        #-----------------------------------------------------------------------------------------
        # Now return the appropriate element in the headersValidTime list
        #-----------------------------------------------------------------------------------------
        return self.source.headersValidTime[headerIndex]


    def getReportLateCycleByHeader (self, header):
        """ getReportLateCycleByHeader (self, Header) -> string

            Given the Two letter header, returns a string representing how often (in minutes) past
            the initial valid time after the hour we need to run to collect late bulletins.
        """
        #-----------------------------------------------------------------------------------------
        # Find out the index of the given header in the headersToCollect list
        #-----------------------------------------------------------------------------------------
        headerIndex = self._getIndexForHeader(header)

        #-----------------------------------------------------------------------------------------
        # Now return the appropriate element in the headersLateCycle list
        #-----------------------------------------------------------------------------------------
        return self.source.headersLateCycle[headerIndex]


    def getTimeToLiveByHeader (self, header):
        """ getTimeToLiveByHeader (self, Header) -> string

            Given the Two letter header, returns a string representing how long (in hours) we
            need to hang on to files of this header type before purging them from the 
            /collection/<type> dir tree.
        """
        #-----------------------------------------------------------------------------------------
        # Find out the index of the given header in the headersToCollect list
        #-----------------------------------------------------------------------------------------
        headerIndex = self._getIndexForHeader(header)

        #-----------------------------------------------------------------------------------------
        # Now return the appropriate element in the headersTimeToLive list
        #-----------------------------------------------------------------------------------------
        return self.source.headersTimeToLive[headerIndex]


    def _getIndexForHeader (self, header):
        """ _getIndexForHeader (self, Header) -> index

            Given the Two letter header, returns the index of this header in the 
            headersToCollect list
        """
        #-----------------------------------------------------------------------------------------
        # Find out the index of the given header in the headersToCollect list
        #-----------------------------------------------------------------------------------------
        return self.source.headersToCollect.index(header)


    def getFutureDatedReportWindowByHeader (self, header):
        """ getFutureDatedReportWindowByHeader (self, Header) -> int

            Given the Two letter header, returns the future-dated time window for this
            header type
        """
        #-----------------------------------------------------------------------------------------
        # Find out the index of the given header in the headersToCollect list
        #-----------------------------------------------------------------------------------------
        headerIndex = self._getIndexForHeader(header)

        #-----------------------------------------------------------------------------------------
        # Now return the appropriate element in the headersValidTime list
        #-----------------------------------------------------------------------------------------
        return self.source.futureDatedReportWindow[headerIndex]


    def getCollectionPath (self):
        """ getCollectionPath (self) -> string

            Returns a string representing the location path to the collection dir
            (I.e. /apps/px/collection/)
        """
        return PXPaths.COLLECTION_DB


    def getCollectionControlPath (self):
        """ getCollectionControlPath (self) -> string

            Returns a string representing the location path to the collection 
            control dir
            (I.e. /apps/px/collection/control)
        """
        return PXPaths.COLLECTION_CONTROL


    def getSentCollectionToken (self):
        """ getSentCollectionToken (self) -> string

            Returns a string representing the sent collection
            (I.e. The '_sent' in '/apps/px/collection/SA/281400/RR_sent')
        """
        return self.source.sentCollectionToken

    def getBusyCollectionToken (self):
        """ getBusyCollectionToken (self) -> string

            Returns a string representing a collection in generation
            (I.e. The '_busy' in '/apps/px/collection/SA/281400/RR_busy')
        """
        return self.source.busyCollectionToken

    def getListOfTypes (self):
        """ getListOfTypes (self) -> list
            Return a list of two-letter types.
        """
        return self.source.headersToCollect

