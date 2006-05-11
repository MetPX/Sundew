# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: CollectionScheduler.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-20
#
# Description:  The CollectionScheduler class is used to create and send scheduled 
#               collection bulletins.
#               This class is similar to the receiverAM class.
#
# Revision History: 
#   Feb. 9, 2006  KA.  Modified findDir() so that it searches for any dir containing 
#                      'min' (for on-time) and 'RR' (for lates).  This is so that
#                      on-time dirs can be found even when the validTime is changed
#                      in the collector's config file.
#               
#############################################################################################
"""
__version__ = '1.0'

import CollectionSchedulerIgniter
import bulletinManager
import gateway
import datetime
import os
import sys
import threading
import PXPaths 
import CollectionBuilder
import BulletinWriter
import time

PXPaths.normalPaths()

    
class CollectionScheduler(threading.Thread,gateway.gateway):
    """
        The CollectionScheduler class is used to send scheduled collection bulletins.  
        Scheduled collection bulletins are bulletin collections that contain the ontime
        bulletins as well as most retard bulletins.

        An instance of this class will be (has been) launched by the scheduledCollection-
        igniter for each header type (SA, SI, SM).

        Author:      National Software Development<nssib@ec.gc.ca>
        Date:        January 2006
    """
    def __init__(self, logger,collectionConfig,idType):
        
        threading.Thread.__init__(self)
        self.logger = logger
        self.collectionConfig = collectionConfig
        self.idType = idType
        
        #-----------------------------------------------------------------------------------------
        # Getting the particular config params for this idType
        #-----------------------------------------------------------------------------------------
        self.validTime = self.collectionConfig.getReportValidTimeByHeader(idType) 
        self.lateCycle = self.collectionConfig.getReportLateCycleByHeader(idType) 
        self.timeToLive = self.collectionConfig.getTimeToLiveByHeader(idType)	
        self.timeToLive = datetime.timedelta(hours = int(self.timeToLive))
        self.sentToken = self.collectionConfig.getSentCollectionToken()
        self.busyToken = self.collectionConfig.getBusyCollectionToken()

        #-----------------------------------------------------------------------------------------
        # myRootDir points to the (/apps/px/collection/<idType>) sub-dir where this collector 
        # will be operating
        #-----------------------------------------------------------------------------------------
        self.myRootDir = self.collectionConfig.getCollectionPath() + idType 

        #-----------------------------------------------------------------------------------------
        # myControlDir points to the (/apps/px/collection/control/<idType>) sub-dir where this 
        # collector's control files are stored
        #-----------------------------------------------------------------------------------------
        self.myControlDir = self.collectionConfig.getCollectionControlPath() + idType 

        #-----------------------------------------------------------------------------------------
        # Bulletin and tools to be used for creating a collection bulletin
        #-----------------------------------------------------------------------------------------
        self.collectionBuilder = CollectionBuilder.CollectionBuilder(self.logger)
        self.collection = ''
        self.collectionWriter = BulletinWriter.BulletinWriter(self.logger, self.collectionConfig)

        #-----------------------------------------------------------------------------------------
        # Instantiate a bulletinManager for us to use for collection bulletin transmission
        #-----------------------------------------------------------------------------------------
        self.unBulletinManager = bulletinManager.bulletinManager( 
                     PXPaths.RXQ + collectionConfig.source.name, self.logger, \
                     pathFichierCircuit = '/dev/null', \
                     extension = collectionConfig.source.extension, \
                     mapEnteteDelai = collectionConfig.source.mapEnteteDelai,
                     source = collectionConfig.source)

        #-----------------------------------------------------------------------------------------
        # startDatetime placeholder
        #-----------------------------------------------------------------------------------------
        self.startDateTime = ''

        
    def run(self):
        """ run()

            This method conatains the business logic required to process
            scheduled collections.  It sends any collections which need
            to be sent, cleans any old files which need to be cleaned, 
            calculate the next sleep interval, and sleep until then.
        """
        True = 'True'
        #-----------------------------------------------------------------------------------------
        # Live forever..until you're told to die!
        #-----------------------------------------------------------------------------------------
        while (True):
        
            self.logger.info("Collector: %s waking up." %self.idType)
            #self.logger.info("REMOVEME: self.validTime: %s" %self.validTime)
            #self.logger.info("REMOVEME: self.lateCycle: %s" %self.lateCycle) 
            #self.logger.info("REMOVEME: self.timeToLive: %s" %self.timeToLive) 
            #self.logger.info("REMOVEME: My pid is: %s" %os.getpid())
            #self.logger.info("REMOVEME: stop flag is: %s" %CollectionSchedulerIgniter.stopRequested)

            #-----------------------------------------------------------------------------------------
            # Check to see if we've been requested to stop and stop if necessary
            #-----------------------------------------------------------------------------------------
            self.checkStopReqeustStatus()

            #-----------------------------------------------------------------------------------------
            # Get wakeup time (now)
            #-----------------------------------------------------------------------------------------
            self.startDateTime = datetime.datetime.now()

            #-----------------------------------------------------------------------------------------
            # Send this hour's on-time collection if not already sent
            #-----------------------------------------------------------------------------------------
            self.logger.info("Collector: %s searching for on-time collections to send" %self.idType)
            self.sendThisHoursOnTimeCollections()

            #-----------------------------------------------------------------------------------------
            # Find out if we should send this cycle's collection or not
            #-----------------------------------------------------------------------------------------
            self.logger.info("Collector: %s searching for late collections to send" %self.idType)
            self.sendLateCollections()

            #-----------------------------------------------------------------------------------------
            # Cleanup old directories and files under the /apps/px/collection sub-tree
            #-----------------------------------------------------------------------------------------
            self.logger.info("Collector: %s Searching for old directories to remove" %self.idType)
            self.purgeOldDirsAndFiles()
            
            #-----------------------------------------------------------------------------------------
            # sleep until next event
            #-----------------------------------------------------------------------------------------
            self.sleepUntil(self.calculateSleepTime())
            
        
    def sendThisHoursOnTimeCollections(self):
        """ sendThisHoursOnTimeCollections() 

            Collect and send this hour's on-time collections if they have 
            not yet been sent.  Note that we won't need mutex for the on-time
            collections because i)The on-time interval has passed and 
            ii)Only one collectionSheduler child is operating on it.
        """
        #-----------------------------------------------------------------------------------------
        # Loop until all on-time collections for this type are sent
        #-----------------------------------------------------------------------------------------
        foundPath = self.findOnTimeCollection()
        
        while (foundPath):
            #-----------------------------------------------------------------------------------------
            # Build on-time collection 
            #-----------------------------------------------------------------------------------------
            self.buildCollection(foundPath)

            #-----------------------------------------------------------------------------------------
            # This is an on-time collection, change the minutes field to '00' and set the collection's
            # BBB and well as the report's BBB to ''.
            # I.e. 'SACN94 CWAO 080306' becomes 'SACN94 CWAO 080300'
            #-----------------------------------------------------------------------------------------
            self.collection.setBulletinMinutesField('00')
            self.collection.setCollectionBBB('')
            self.collection.setReportBBB('')

            #-----------------------------------------------------------------------------------------
            # Transmit on-time collection
            #-----------------------------------------------------------------------------------------
            self.transmitCollection()
            
            #-----------------------------------------------------------------------------------------
            # Mark collection as sent
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.markCollectionAsSent(self.collection.getCollectionPath())

            #-----------------------------------------------------------------------------------------
            # Look for the next unsent on-time collection
            #-----------------------------------------------------------------------------------------
            foundPath = self.findOnTimeCollection()


    def findOnTimeCollection(self):
        """ findOnTimeCollection() -> string

            This method searches for this hour's on-time collections which have not
            been sent and returns the path to the directory where the collection
            needs to be created (/apps/px/collection/SA/162000/CWAO/SACN42/7min).
            False is returned if no on-time collections are found.
        """
        #-----------------------------------------------------------------------------------------
        # Search only if the on-time period for this hour has ended
        #-----------------------------------------------------------------------------------------
        if (int(self.startDateTime.minute) >= int(self.validTime)):
            #-----------------------------------------------------------------------------------------
            # Build dir for this hour of the form "DDHH00"
            #-----------------------------------------------------------------------------------------
            thisHoursDir = self.startDateTime.strftime("%d%H") + '00' 
            
            #-----------------------------------------------------------------------------------------
            # search for any of this hour's unsent on-time collections
            #-----------------------------------------------------------------------------------------
            searchPath = os.path.join(self.myRootDir, thisHoursDir)
            foundPath = self.findDir(searchPath,'min')
            return foundPath
        

    def findDir (self,searchPath, directory):
        """ findDir(searchPath, directory) -> Boolean

            searchPath  string  The root path of the search

            directory   string  The name of the directory to 
                                look for
            
            This method returns the path of the first directory
            under the 'searchPath' sub-tree which matches 
            'directory' and does not end with _busy or _sent.
            False is returned if no match is found.
        """
        False = ''
        #print("REMOVEME: Searching for dir: %s in: %s"%(directory,searchPath)) 
        for root, dirs, files in os.walk(searchPath):
            for dir in dirs:
                if (directory in dir and not (dir.endswith(self.sentToken) or
                                              dir.endswith(self.busyToken))):
                    #print("REMOVEME: Found dir and returning: %s" %os.path.join(root,dir))
                    return os.path.join(root,dir)
        return False


    def buildCollection(self,collectionPath):
        """ buildCollection

            Given the path to a collection directory such as
            (/apps/px/collection/SA/162000/CWAO/SACN42/7min),
            this method will build a collection bulletin based
            on the reports in the given dir.
        """
        #-----------------------------------------------------------------------------------------
        # Get a list of all reports in the given on-time dir
        #-----------------------------------------------------------------------------------------
        reports = os.listdir(collectionPath)

        if(reports):
            #-----------------------------------------------------------------------------------------
            # The first bulletin will be placed in the collection with the header intact.  This
            # header will eventually become the header for the collection
            #-----------------------------------------------------------------------------------------
            self.collection = self.collectionBuilder.buildBulletinFromFile(os.path.join(collectionPath, \
                                                                                        reports.pop(0)))
            #-----------------------------------------------------------------------------------------
            # Now append the bodies of the other reports to the collection bulletin
            #-----------------------------------------------------------------------------------------
            for report in reports:
                self.collection = self.collectionBuilder.appendToCollectionFromFile(self.collection, \
                                  os.path.join(collectionPath, report))

            #-----------------------------------------------------------------------------------------
            # Set the new collection's directory path (where it is in the collection sub-dir)
            #-----------------------------------------------------------------------------------------
            self.collection.setCollectionPath(collectionPath)
    

    def transmitCollection(self):
        """ transmitOnTimeCollection()

            This method is responsible for transmitting the on-time
            collection that we've produced.
        """
        False = ''
        #-----------------------------------------------------------------------------------------
        # Using the BulletinManager class to write the collection bulletin to the db and the
        # queues of the senders
        #-----------------------------------------------------------------------------------------
        self.unBulletinManager.writeBulletinToDisk(self.collection.bulletinAsString())


    def sendLateCollections(self):
        """ sendLateCollections() 

            Collect and send late collections if they have not yet been sent.  
            Note that we need to use a mutex while we're creating collections in
            RRx directories because receiver-collectors may try to place an
            incoming report into those dirs.
        """
        #-----------------------------------------------------------------------------------------
        # Loop until all Late (RRx) collections for this type are sent
        #-----------------------------------------------------------------------------------------
        foundPath = self.findLateCollection()
       
        while (foundPath):

            #-----------------------------------------------------------------------------------------
            # Get mutex to foundPath directory 
            #-----------------------------------------------------------------------------------------
            startTime = time.time() # DL
            key = self.collectionWriter.lockDirBranch(os.path.dirname(foundPath))
            
            #-----------------------------------------------------------------------------------------
            # Build on-time collection 
            #-----------------------------------------------------------------------------------------
            self.buildCollection(foundPath)

            #-----------------------------------------------------------------------------------------
            # This is a late collection, change the minutes field to '00' and set the BBB for the
            # bulletin and the collection to the appropriate value (collection BBB is used to find
            # the collection when marking it sent).
            # I.e. 'SACN94 CWAO 080306' becomes 'SACN94 CWAO 080300 RRA'
            #-----------------------------------------------------------------------------------------
            self.collection.setBulletinMinutesField('00')
            BBB = os.path.basename(foundPath)
            self.collection.setCollectionBBB(BBB)
            self.collection.setReportBBB(BBB)

            #-----------------------------------------------------------------------------------------
            # Mark directory as _busy so as to block the receivers from adding any more bulletins
            # to this collection directory
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.createBBB_BusyCollectionDir(self.collection)

            #-----------------------------------------------------------------------------------------
            # Release mutex to foundPath directory 
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.unlockDirBranch(key)
            stopTime = time.time() # DL
            self.logger.info("Lock duration: %f seconds (%s)" % ((stopTime - startTime), foundPath)) # DL
            #-----------------------------------------------------------------------------------------
            # Transmit on-time collection
            #-----------------------------------------------------------------------------------------
            self.transmitCollection()

            #-----------------------------------------------------------------------------------------
            # Mark collection as sent
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.markCollectionAsSent(self.collection.getCollectionPath())

            #-----------------------------------------------------------------------------------------
            # Look for the next unsent on-time collection
            #-----------------------------------------------------------------------------------------
            foundPath = self.findLateCollection()


    def findLateCollection(self):
        """ findLateCollection() -> string

            This method searches for late (RRx) collections which have not been sent
            and returns the path to the directory where the collection
            needs to be created (/apps/px/collection/SA/162000/CWAO/SACN42/RRA).
            False is returned if no late collections are found.
            If the previous cycle interval puts us in the past hour, then look for
            late bulletins during last hour as well.  Otherwise, just look for lates
            in the present hour.
        """
        currentTime = datetime.datetime.now()
        False = ''
        hour = []
        #-----------------------------------------------------------------------------------------
        # Search for this hour's late collections only if it is validTime + 1 lateCycle
        #-----------------------------------------------------------------------------------------
        if (int(currentTime.minute) >= (int(self.validTime) + int(self.lateCycle))):
            hour.append(self.startDateTime.strftime("%H"))
        
        #-----------------------------------------------------------------------------------------
        # If the previous cycle interval puts us in the previous hour, then look for late bulletins 
        # during last hour as well
        #-----------------------------------------------------------------------------------------
        lateCycleTimedelta = datetime.timedelta(minutes = int(self.lateCycle))
        oneHourTimedelta = datetime.timedelta(hours = 1)
        tmpDate = self.startDateTime - lateCycleTimedelta
        if(int(self.startDateTime.hour) == int((tmpDate + oneHourTimedelta).hour)):
            hour.insert(0,tmpDate.strftime("%H"))
        
        #-----------------------------------------------------------------------------------------
        # We now have something like hour = [14,15] or hour = [14]
        # Build dir for this hour of the form "DDHHMM"
        #-----------------------------------------------------------------------------------------
        for element in hour:
           hoursDir = self.startDateTime.strftime("%d") + str(element) + '00'
           
           #-----------------------------------------------------------------------------------------
           # search for any unsent late collections
           #-----------------------------------------------------------------------------------------
           searchPath = os.path.join(self.myRootDir, hoursDir)
           foundPath = self.findDir(searchPath,'RR')
           if (foundPath):
               return foundPath
           else:
               continue
        else:
           return False
       

    def purgeOldDirsAndFiles(self):
        """ purgeOldDirsAndFiles()

            This method removes items of this type (SA, SI, SM) which have
            exceeded the time-to-live value

        """
        dirAge = self.startDateTime - self.timeToLive
        #-----------------------------------------------------------------------------------------
        # Clean myRootDir (/apps/px/collection/<idType>)
        #-----------------------------------------------------------------------------------------
        self.findAndRemoveDirOlderThan(self.myRootDir,dirAge)
                           
        #-----------------------------------------------------------------------------------------
        # Clean control dir (/apps/px/collection/control/<idType>)
        #-----------------------------------------------------------------------------------------
        self.findAndRemoveDirOlderThan(self.myControlDir,dirAge)
            

    def findAndRemoveDirOlderThan (self,searchPath, dateTimeValue):
        """ findAndRemoveDirOlderThan(searchPath, directory) -> Boolean

            searchPath      string      The root path of the search

            dateTimeValue   datetime    A datetime value used for 
                                        comparison
            
            This method searches starting from 'searchPath' and removes
            all directories which are older than dateTimeValue.
        """
        dateTimeValue = dateTimeValue.timetuple()
        for root, dirs, files in os.walk(searchPath):
            for dir in dirs:
                dirModTime = os.stat(os.path.join(root,dir))
                dirModTime = time.localtime(dirModTime.st_mtime)

                #-----------------------------------------------------------------------------------------
                # Removing dirs which are found to be older than Time To Live
                #-----------------------------------------------------------------------------------------
                if(dirModTime <= dateTimeValue):
                    self.collectionWriter.removeDirTree(os.path.join(root,dir))


    def calculateSleepTime(self):
        """ calculateSleepTime() -> Time in seconds

            This method is responsible for calculating our sleep time between
            the current session and when we should wake up next.

            Precondition: We've completed running a scheduled session and
                          now need to figuire out how long to sleep before 
                          the next wakeup.
            
        """
        currentTime = datetime.datetime.now()
        multiplier = 0 

        #-----------------------------------------------------------------------------------------
        # The proposedSleepTime for SAs is:
        # proposedSleepTime = (7min + (i * 5min)) - (present time)
        # If proposal is in the past (negative), then increment i and recalculate
        #-----------------------------------------------------------------------------------------
        proposedSleepTime = int(self.validTime) + (multiplier * int(self.lateCycle))
        proposedSleepTime = proposedSleepTime - int(currentTime.minute)

        #-----------------------------------------------------------------------------------------
        # While our proposed sleep interval is in the past, we need to increment our sleepTime
        # by one lateCycle.  Note that we don't break out of the loop if proposedSleepTime = 0.
        # This is because:
        #  -The run method runs calculateSleepInterval last, so if we're here during a wakup
        #   interval, then it must be because we've already done everything and are looping 
        #   because the wakeup minute has not yet passed.
        #  -Also note that we're assuming that a particular run will not take us
        #   from one interval right into another (i.e. duration is smaller than one lateCycle.
        #-----------------------------------------------------------------------------------------
        while (proposedSleepTime <= 0):
            multiplier = multiplier + 1
            proposedSleepTime = int(self.validTime) + (multiplier * int(self.lateCycle))
            proposedSleepTime = proposedSleepTime - int(currentTime.minute)

        else:
            
            #self.logger.info("REMOVEME: startTime was: %s"%self.startDateTime)
            #self.logger.info("REMOVEME: currentTime: %s"%currentTime)
           
            #-----------------------------------------------------------------------------------------
            # Return sleep Time in seconds
            #-----------------------------------------------------------------------------------------
            return proposedSleepTime * 60

    
    def sleepUntil(self,secondsToldToSleep):
        """ sleepUntil()

            This method receives the number of seconds to sleep
            and is responsible for sleeping that time while 
            checking every once in a while to see if a stop has
            been requested.
        """
        #-----------------------------------------------------------------------------------------
        # This is how ofter we check to see if a stop has been requested
        #-----------------------------------------------------------------------------------------
        stopReqestCheckInterval = 2

        self.logger.info("Collector: %s sleeping for: %s seconds" %(self.idType,secondsToldToSleep))
        #self.logger.info("REMOVEME: stopReqestCheckInterval: %s seconds"%stopReqestCheckInterval)

        #-----------------------------------------------------------------------------------------
        # Don't sleep more than what's required
        #-----------------------------------------------------------------------------------------
        secondsToSleep = min(secondsToldToSleep,stopReqestCheckInterval)

        while (secondsToSleep> 0):
            
            #-----------------------------------------------------------------------------------------
            # Check to see if we've been requested to stop and stop if necessary
            #-----------------------------------------------------------------------------------------
            self.checkStopReqeustStatus()

            #-----------------------------------------------------------------------------------------
            # Sleeping the minimum
            #-----------------------------------------------------------------------------------------
            time.sleep(secondsToSleep)

            #-----------------------------------------------------------------------------------------
            # recalc seconds to sleep
            #-----------------------------------------------------------------------------------------
            secondsToldToSleep = secondsToldToSleep - secondsToSleep
            secondsToSleep = min(secondsToldToSleep,stopReqestCheckInterval)

            
    def checkStopReqeustStatus(self):
        """ checkStopReqeustStatus()

            This method checks to see if the parent has asked us to stop.
            If so, cleanup and exit.
        """
        #-----------------------------------------------------------------------------------------
        # Stop if necessary
        #-----------------------------------------------------------------------------------------
        if(CollectionSchedulerIgniter.stopRequested):
            self.cleanupAndExit()


    def cleanupAndExit(self):
        """ cleanupAndExit()

            This mehod makes sure that we release the semaphore and
            perform other cleanup taks and terminates this thread.
        """
        self.logger.info("Collector thread: %s exiting." %self.idType)

        #-----------------------------------------------------------------------------------------
        # can exit here without performing any particular semaphore cleanup tasks
        #-----------------------------------------------------------------------------------------
        sys.exit()



