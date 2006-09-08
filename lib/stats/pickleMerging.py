#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

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


import cpickleWrapper
from   ClientStatsPickler   import *
import FileStatsCollector
from   FileStatsCollector   import _FileStatsEntry, FileStatsCollector
from   PickleVersionChecker import *

  
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



def fillWithEmptyEntries( nbEmptyEntries, entries ):
    """
        Append certain number of empty entries to the entry list. 
    
    """    
    
    for i in range( nbEmptyEntries ):
        entries.append( _FileStatsEntry() )       
    
    return entries



def mergePicklesFromDifferentHours( logger = None , startTime = "2006-07-31 13:00:00", endTime = "2006-07-31 19:00:00", client = "satnet", machine = "pdsPM", fileType = "tx" ):
    """
        This method merges entire hourly pickles files. 
        
        This does not support merging part of the data of pickles yet.   
    
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
                 
            tempCollection = cpickleWrapper.load( pickle )
            entries.extend( tempCollection.fileEntries )
            
        else:
            
            emptyEntries = fillWithEmptyEntries( nbEmptyEntries = 60, entries = [] )
            entries.extend( emptyEntries )
     
            
    statsCollection = FileStatsCollector(  startTime = startTime , endTime = endTime, interval = MyDateLib.MINUTE, totalWidth = width, fileEntries = entries )
    
#     statsCollection = statsCollection.setMinMaxMeanMedians( startingBucket = 0 , finishingBucket = statsCollection.nbEntries )      
    
#     statsCollection.logger = None
#     cpickleWrapper.save( object = statsCollection, filename = "/apps/px/stats/mergedData") 
#     #print "statsCollection.nbEntries %s" %statsCollection.nbEntries
    
    return statsCollection        




def mergePicklesFromSameHour( logger = None , pickleNames = None, mergedPickleName = "", clientName = "" , combinedMachineName = "", currentTime = "", fileType = "tx" ):
    """
            This methods receives a list of filenames referring to /apps/px/lib/o 
            pickled FileStatsEntries.
            
            Saves pickles since they might be reused somewhere else...
            
            Pre condition :Pickle should be of the same timespan and bucket width.
                        If not exception will be raised and program terminated.  
            
                        
            Note : Should test if it would be somewhat faster not to recalculate everything 
            and just go with proportions 
            
    
    """
    
    
    if logger != None : 
        logger.debug( "Call to mergePickles received." )
              
    entryList = []
    
    
    for pickle in pickleNames:#for every pickle we eneed to merge
        
        if os.path.isfile( pickle ):
            
            entryList.append( cpickleWrapper.load( pickle ) )
                        
        else:#Use empty entry if there is no existing pickle of that name
            
            endTime = MyDateLib.getIsoFromEpoch( MyDateLib.getSecondsSinceEpoch( currentTime ) + MyDateLib.HOUR ) 
            entryList.append( FileStatsCollector( startTime = currentTime, endTime = endTime  ) )         
            
            if logger != None :
                logger.warning( "Pickle named %s did not exist. Empty entry was used instead." %pickle )    
    
    
    #start off with a carbon copy of first pickle in list.
    newFSC = FileStatsCollector( files = entryList[0].files , statsTypes =  entryList[0].statsTypes, startTime = entryList[0].startTime, endTime = entryList[0].endTime, interval=entryList[0].interval, totalWidth = entryList[0].totalWidth, firstFilledEntry = entryList[0].firstFilledEntry, lastFilledEntry = entryList[0].lastFilledEntry, maxLatency = entryList[0].maxLatency, fileEntries = entryList[0].fileEntries )
    
     
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
                    
                    #print entryList[i].fileEntries[j].values.dictionary[type][k]        
                    newFSC.fileEntries[j].values.rows = newFSC.fileEntries[j].values.rows + 1

        
        newFSC = newFSC.setMinMaxMeanMedians( productType = "", startingBucket = 0 , finishingBucket = newFSC.nbEntries )
             
           
    else:#Did not merge pickles named. Pickle list was not valid."
        
        if logger != None :
            logger.warning( "Did not merge pickles named : %s. Pickle list was not valid." %pickleNames )
            logger.warning( "Filled with empty entries instead." %pickleNames )
            
        newFSC.fileEntries = fillWithEmptyEntries( nbEmptyEntries = 60 , entries = [] )    
    
    
    #prevents us from having ro remerge file later on.    
    temp = newFSC.logger
    del newFSC.logger
    cpickleWrapper.save( newFSC, mergedPickleName )
    newFSC.logger = temp
    
    return newFSC
        


def createNonMergedPicklesList( currentTime, machines, fileType, client ):
    """
        Create a list of all pickles names concerning different machines for a certain hour.
    """    
    
    pickleList = []
    
    for machine in machines:
        pickleList.append( ClientStatsPickler.buildThisHoursFileName(  client = client, currentTime = currentTime, fileType = fileType, machine = machine ) )
    
    return pickleList



def createMergedPicklesList( startTime, endTime, client, fileType, machines, seperators ):
    """
        
        Pre-condition : Machines must be an array containing the list of machines to use. 
                        If only one machine is to be used still use an array containing a single item. 
    
    """   
    
    pickleList = [] 
    combinedMachineName = ""
    
    for machine in machines:
        combinedMachineName = combinedMachineName + machine     
    
    
    for seperator in seperators:
        pickleList.append( ClientStatsPickler.buildThisHoursFileName(  client = client, currentTime = seperator, fileType = fileType, machine = combinedMachineName ) )

        
    return pickleList
    
    
        
def mergePicklesFromDifferentMachines( logger = None , startTime = "2006-07-31 13:00:00", endTime = "2006-07-31 19:00:00", client = "satnet", fileType = "tx", machines = [] ):
    """
        This method allows user to merge pickles coming from numerous machines
        covering as many hours as wanted, into a single FileStatsCollector entry.
        
        Very usefull when creating graphics on a central server with pickle files coming from 
        remote locations.
        
    """ 
    
    
    vc  = PickleVersionChecker()
    vc.getCurrentFileList()
    vc.getSavedList()
    
         
    combinedMachineName = ""
    
    for machine in machines:
        combinedMachineName = combinedMachineName + machine
        
   
    width = MyDateLib.getSecondsSinceEpoch( endTime ) - MyDateLib.getSecondsSinceEpoch( startTime )
    startTime = MyDateLib.getIsoWithRoundedHours( startTime )
    
    seperators = [startTime]
    seperators.extend( MyDateLib.getSeparatorsWithStartTime( startTime = startTime , width=width, interval=60*MINUTE )[:-1])
    
    
    mergedPickleNames = createMergedPicklesList(  startTime = startTime, endTime = endTime, machines = machines, fileType = fileType, client = client, seperators = seperators ) #Resulting list of the merger.
    
    
    for i in range( len( mergedPickleNames ) ) : #for every merger needed
            
            needToMergeSameHoursPickle = False 
            pickleNames = createNonMergedPicklesList( currentTime = seperators[i], machines = machines, fileType = fileType, client = client )
            
            for pickle in pickleNames : #Verify every pickle implicated in merger.
                
                if vc.isDifferentFile( file = pickle, user = combinedMachineName ) == True : # if for some reason pickel has changed since last time
                    needToMergeSameHoursPickle = True 
                    break 
            
            if needToMergeSameHoursPickle == True :#First time or one element has changed   
                 
                mergePicklesFromSameHour( logger = None , pickleNames = pickleNames , clientName = client, combinedMachineName = combinedMachineName, currentTime = seperators[i], mergedPickleName = mergedPickleNames[i], fileType = fileType  )
                
                for pickle in pickleNames :
                    vc.updateFileInList( file = pickle, user = combinedMachineName )
            
                vc.saveList()
                
                        
    # Once all machines have merges the necessary pickles we merge all pickles 
    # into a single file stats entry. 
    newFSC = mergePicklesFromDifferentHours( logger = None , startTime = startTime, endTime = endTime, client = client, machine = combinedMachineName,fileType = fileType  )
   
    return newFSC


    
def main():
    """
        Small test case. Tests if everything works plus gives an idea on proper usage.
    """



if __name__ == "__main__":
    main()





