#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##############################################################################
##
##
## Name   : pickleMerging.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 06-07-2006 
##
##
## Description : Used to merge pickles. 
##
##               Very usefull for same day pickles treating the same client
##               on different machines.  
##
##               Also usefull for merging pickles form different hours.
##
##
##############################################################################
"""
import os,sys

sys.path.insert(1, sys.path[0] + '/../../')

from   pxStats.lib.CpickleWrapper       import CpickleWrapper
from   pxStats.lib.ClientStatsPickler   import ClientStatsPickler
from   pxStats.lib.FileStatsCollector   import _FileStatsEntry, FileStatsCollector
from   pxStats.lib.PickleVersionChecker import PickleVersionChecker

class PickleMerging: 
     
    def entryListIsValid( entryList ):
        """
            Returns whether or not an entry list of pickles contains 
            a list of pickles that can be merged. 
             
        """
         
        isValid = True    
         
        if entryList != [] :
            
            i = 0 
            startTime  = entryList[0].startTime
            totalWidth = entryList[0].totalWidth
            interval   = entryList[0].interval    
            statsTypes = entryList[0].statsTypes  
            
            while i < len(entryList) and isValid == True  :  
                
                if startTime != entryList[i].startTime or totalWidth != entryList[i].totalWidth or interval != entryList[i].interval :
                    isValid = False 
                
                else:
                    
                    for type in statsTypes:
                        if type not in entryList[i].statsTypes:
                            isValid = False 
                i = i + 1                      
    
        
        else:
            isValid = False         
        
        return isValid 
    
    
    entryListIsValid = staticmethod( entryListIsValid )
    
    
    
    def fillWithEmptyEntries( nbEmptyEntries, entries ):
        """
            Append certain number of empty entries to the entry list. 
        
        """    
        
        for i in range( nbEmptyEntries ):
            entries.append( _FileStatsEntry() )       
        
        return entries
    
    fillWithEmptyEntries = staticmethod( fillWithEmptyEntries  )
    
    
    
    def mergePicklesFromDifferentHours( logger = None , startTime = "2006-07-31 13:00:00", endTime = "2006-07-31 19:00:00", client = "satnet", machine = "pdsPM", fileType = "tx" ):
        """
            This method merges entire hourly pickles files. 
            
            This does not support merging part of the data of pickles.   
        
        """
        
        if logger != None :
            logger.debug( "Call to mergeHourlyPickles received." )
        
        pickles = []
        entries = []
        width = MyDateLib.getSecondsSinceEpoch( endTime ) - MyDateLib.getSecondsSinceEpoch( startTime )
        startTime = MyDateLib.getIsoWithRoundedHours( startTime )
        
        seperators = [startTime]
        seperators.extend( MyDateLib.getSeparatorsWithStartTime( startTime = startTime , width=width, interval=60*MINUTE )[:-1])
            
        for seperator in seperators :
            pickles.append( ClientStatsPickler.buildThisHoursFileName(  client = client, offset = 0, currentTime = seperator, machine = machine, fileType = fileType ) )        
        
        
        for pickle in pickles : 
            
            if os.path.isfile( pickle ) :
                     
                tempCollection = CpickleWrapper.load( pickle )
                if tempCollection != None :
                    entries.extend( tempCollection.fileEntries )
                else:
                    
                    sys.exit()
            else:
                            
                emptyEntries = fillWithEmptyEntries( nbEmptyEntries = 60, entries = [] )
                entries.extend( emptyEntries )
         
                
        statsCollection = FileStatsCollector(  startTime = startTime , endTime = endTime, interval = MyDateLib.MINUTE, totalWidth = width, fileEntries = entries, logger = logger )
           
        
        return statsCollection        
    
    
    mergePicklesFromDifferentHours = staticmethod( mergePicklesFromDifferentHours )
    
    
    
    def mergePicklesFromSameHour( logger = None , pickleNames = None, mergedPickleName = "", clientName = "" , combinedMachineName = "", currentTime = "", fileType = "tx" ):
        """
            This methods receives a list of filenames referring to pickled FileStatsEntries.
            
            After the merger pickles get saved since they might be reused somewhere else.
            
            Pre condition : Pickle should be of the same timespan and bucket width.
                            If not no merging will occur.  
            
        """
        
        
        if logger != None : 
            logger.debug( "Call to mergePickles received." )
                  
        entryList = []
        
        
        for pickle in pickleNames:#for every pickle we eneed to merge
            
            if os.path.isfile( pickle ):
                
                entryList.append( CpickleWrapper.load( pickle ) )
                            
            else:#Use empty entry if there is no existing pickle of that name
                
                endTime = MyDateLib.getIsoFromEpoch( MyDateLib.getSecondsSinceEpoch( currentTime ) + MyDateLib.HOUR ) 
                entryList.append( FileStatsCollector( startTime = currentTime, endTime = endTime,logger =logger  ) )         
                
                if logger != None :
                    logger.warning( "Pickle named %s did not exist. Empty entry was used instead." %pickle )    
        
        
        #start off with a carbon copy of first pickle in list.
        newFSC = FileStatsCollector( files = entryList[0].files , statsTypes =  entryList[0].statsTypes, startTime = entryList[0].startTime, endTime = entryList[0].endTime, interval=entryList[0].interval, totalWidth = entryList[0].totalWidth, firstFilledEntry = entryList[0].firstFilledEntry, lastFilledEntry = entryList[0].lastFilledEntry, maxLatency = entryList[0].maxLatency, fileEntries = entryList[0].fileEntries,logger = logger )
        
         
        if entryListIsValid( entryList ) == True :
            
            for i in range ( 1 , len( entryList ) ): #add other entries 
                
                for file in entryList[i].files :
                    if file not in newFSC.files :
                        newFSC.files.append( file ) 
                
                for j in range( len( newFSC.fileEntries ) ) : # add all entries
                        
                
                    for k in range( entryList[i].fileEntries[j].values.rows ):#Add all new value for each entry
                        
                        newFSC.fileEntries[j].values.productTypes.append( entryList[i].fileEntries[j].values.productTypes[k] ) 
                        
                        newFSC.fileEntries[j].files.append( entryList[i].fileEntries[j].files[k] ) 
                        newFSC.fileEntries[j].times.append( entryList[i].fileEntries[j].times[k] )          
                                            
                        if entryList[i].fileEntries[j].values.productTypes[k] != "[ERROR]" :
                            newFSC.fileEntries[ j ].nbFiles = newFSC.fileEntries[ j ].nbFiles + 1
                        
                        for type in newFSC.statsTypes :
                             
                            newFSC.fileEntries[j].values.dictionary[type].append( entryList[i].fileEntries[j].values.dictionary[type][k] ) 
                                               
                        newFSC.fileEntries[j].values.rows = newFSC.fileEntries[j].values.rows + 1
    
            
            newFSC = newFSC.setMinMaxMeanMedians( startingBucket = 0 , finishingBucket = newFSC.nbEntries -1 )
                 
               
        else:#Did not merge pickles named. Pickle list was not valid."
            
            if logger != None :
                logger.warning( "Did not merge pickles named : %s. Pickle list was not valid." %pickleNames )
                logger.warning( "Filled with empty entries instead." %pickleNames )
                
            newFSC.fileEntries = fillWithEmptyEntries( nbEmptyEntries = 60 , entries = [] )    
        
        
        #prevents us from having ro remerge file later on.    
        temp = newFSC.logger
        del newFSC.logger
        CpickleWrapper.save( newFSC, mergedPickleName )
        
        newFSC.logger = temp
        
        return newFSC
            
    
    mergePicklesFromSameHour = staticmethod( mergePicklesFromSameHour )
    
    
    
    def createNonMergedPicklesList( currentTime, machines, fileType, clients ):
        """
            Create a list of all pickles names concerning different machines for a certain hour.
        """    
        
        pickleList = []
        
        for machine in machines:
            for client in clients: 
                pickleList.append( ClientStatsPickler.buildThisHoursFileName(  client = client, currentTime = currentTime, fileType = fileType, machine = machine ) )
        
           
        
        return pickleList
    
    createNonMergedPicklesList = staticmethod( createNonMergedPicklesList )
    
    
    
    def createMergedPicklesList( startTime, endTime, clients, groupName, fileType, machines, seperators ):
        """
            
            Pre-condition : Machines must be an array containing the list of machines to use. 
                            If only one machine is to be used still use an array containing a single item. 
        
        """   
       
        pickleList = [] 
        combinedMachineName = ""
        combinedClientName  = ""
        
        for machine in machines:
            combinedMachineName = combinedMachineName + machine     
        
           
        if groupName == "":        
            for client in clients: 
                groupName = groupName + client
            
        for seperator in seperators:
            pickleList.append( ClientStatsPickler.buildThisHoursFileName(  client = groupName, currentTime = seperator, fileType = fileType, machine = combinedMachineName ) )
    
     
        return pickleList
        
    createMergedPicklesList = staticmethod( createMergedPicklesList )    
            
            
            
    def mergePicklesFromDifferentSources( logger = None , startTime = "2006-07-31 13:00:00", endTime = "2006-07-31 19:00:00", clients = ["satnet"], fileType = "tx", machines = [], groupName = "" ):
        """
            This method allows user to merge pickles coming from numerous machines
            covering as many hours as wanted, into a single FileStatsCollector entry.
            
            Very usefull when creating graphics on a central server with pickle files coming from 
            remote locations.
            
        """          
             
        combinedMachineName = ""
        combinedClientName  = ""
        
        for machine in machines:
            combinedMachineName = combinedMachineName + machine
        for client in clients: 
            combinedClientName = combinedClientName + client
        
        if groupName !="":
            clientsForVersionManagement = groupName 
        else:
            clientsForVersionManagement = clients
        
        vc  = PickleVersionChecker()    
           
        vc.getClientsCurrentFileList( clients )    
            
        vc.getSavedList( user = combinedMachineName, clients = clientsForVersionManagement )           
       
        width = MyDateLib.getSecondsSinceEpoch( endTime ) - MyDateLib.getSecondsSinceEpoch( startTime )
        startTime = MyDateLib.getIsoWithRoundedHours( startTime )
        
        seperators = [startTime]
        seperators.extend( MyDateLib.getSeparatorsWithStartTime( startTime = startTime , width=width, interval=60*MINUTE )[:-1])
            
        mergedPickleNames = createMergedPicklesList(  startTime = startTime, endTime = endTime, machines = machines, fileType = fileType, clients = clients, groupName = groupName, seperators = seperators ) #Resulting list of the merger.
            
       
        for i in range( len( mergedPickleNames ) ) : #for every merger needed
                
                needToMergeSameHoursPickle = False 
                pickleNames = createNonMergedPicklesList( currentTime = seperators[i], machines = machines, fileType = fileType, clients = clients )
                
                if not os.path.isfile( mergedPickleNames[i] ):                
                    needToMergeSameHoursPickle = True 
                else:    
                    
                    for pickle in pickleNames : #Verify every pickle implicated in merger.
                        # if for some reason pickle has changed since last time                    
                        if vc.isDifferentFile( file = pickle, user = combinedMachineName, clients = clientsForVersionManagement ) == True : 
                               
                            needToMergeSameHoursPickle = True 
                            break
                            
                
                if needToMergeSameHoursPickle == True :#First time or one element has changed   
                    
                    mergePicklesFromSameHour( logger = logger , pickleNames = pickleNames , clientName = combinedClientName, combinedMachineName = combinedMachineName, currentTime = seperators[i], mergedPickleName = mergedPickleNames[i], fileType = fileType  )
                    
                    
                    for pickle in pickleNames :
                        print pickle
                        vc.updateFileInList( file = pickle )                                               
                    
                    vc.saveList( user = combinedMachineName, clients = clientsForVersionManagement )
                    
                    
                            
        # Once all machines have merges the necessary pickles we merge all pickles 
        # into a single file stats entry. 
        if groupName !="":
            nameToUseForMerger = groupName 
        else:
            nameToUseForMerger = ""
            for client in clients:
                nameToUseForMerger = nameToUseForMerger + client
        
        newFSC = mergePicklesFromDifferentHours( logger = logger , startTime = startTime, endTime = endTime, client = nameToUseForMerger, machine = combinedMachineName,fileType = fileType  )
       
        return newFSC
    
    mergePicklesFromDifferentSources = staticmethod( mergePicklesFromDifferentSources )
        
        
        
    def main():
        """
            Small test case. Tests if everything works plus gives an idea on proper usage.
        """
    
    
    
    if __name__ == "__main__":
        main()
    
    
    
    
    
