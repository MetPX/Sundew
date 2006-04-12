"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: CollectionSchedulerIgniter.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2006-01-09
#
# Description:  The nature of scheduled collections of different types (and with different
#               generation times) begs for the use of multi-threading.  This module is therefore
#               responsible for launching a separate thread for each collectible type (SA, SI,
#               SM) to carry out scheduled collection.
#
# Revision History: 
#               
#############################################################################################
"""
__version__ = '1.0'

import sys, os, os.path, string, commands, re, signal, fnmatch
sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')

from Logger import Logger
import CollectionConfigParser
import CollectionScheduler
import time
import PXIgniter

#-----------------------------------------------------------------------------------------
# Global vars
#-----------------------------------------------------------------------------------------
False = ''
True = 'True'
stopRequested = False

class CollectionSchedulerIgniter(object):
    """The CollectionSchedulerIgniter class

           This class needs to be able to understand the basic Px
           start, stop, and reload commands.  It's role is to 
           launch and manage the threads used to carry out collections
           of each bulletin type (SA, SI, SM).

           Author:      National Software Development<nssib@ec.gc.ca>
           Date:        January 2006
    """
    

    def __init__(self, source, logger):
        self.logger = logger   # Logger object
        self.source = source
        self.True = 'True'
        self.False = ''
        self.children = []

        #-----------------------------------------------------------------------------------------
        # Create the config parser and get a list of our children
        #-----------------------------------------------------------------------------------------
        self.collectionConfig = CollectionConfigParser.CollectionConfigParser(self.logger,self.source)
        self.listOfChildren = self.collectionConfig.getListOfTypes()

        #-----------------------------------------------------------------------------------------
        # Recording old handler for SIGTERM and intercepting it to listen for the 'stop' command
        #-----------------------------------------------------------------------------------------
        self.oldHandler = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, self._stopRequested)



    def _stopRequested(self, sig, stack):
        """ _stopRequested()

            This method will signal to the children that they need to terminate
            themselves because a 'stop' has been issued.  This method will then
            re-instate the previous handler and send SIGTERM back.  This will
            allow whatever actions are dependent on the signal to continue to 
            happen.
        """
        global stopRequested

        #-----------------------------------------------------------------------------------------
        # Code to indicate a 'stop' to the children and wait for them to terminate
        #-----------------------------------------------------------------------------------------
        stopRequested = True
        for child in self.children:
            child.join()

        #-----------------------------------------------------------------------------------------
        # Re-instate the original handler and re-propagate the signal.  This will cause
        # the PXIgniter kill this process with a SIGKILL
        #-----------------------------------------------------------------------------------------
        signal.signal(signal.SIGTERM,self.oldHandler)
        os.kill(os.getpid(), signal.SIGTERM)
        sys.exit()

    def run(self):
        """ run(self)
            start a CollectionScheduler for each of the report types (SA, SI, SM)
        """
        True = 'True'
        #print"CollSchedIgniter up and running. My pid is: ",os.getpid()
        for childType in (self.listOfChildren):
            #-----------------------------------------------------------------------------------------
            # Launching a child thread for each collection type
            #-----------------------------------------------------------------------------------------
            newThread = CollectionScheduler.CollectionScheduler(self.logger,self.collectionConfig, childType)
            newThread.start()
            self.children.append(newThread)

        #-----------------------------------------------------------------------------------------
        # newThread.join() won't work, so Sleep Forever and wait to catch stop requests
        #-----------------------------------------------------------------------------------------
        while (True):
            time.sleep(86400)


if __name__ == '__main__':
    pass
