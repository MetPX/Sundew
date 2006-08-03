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
## Description : Used to merge a list of pickles. Very usefull for same day 
##               pickles treating the same client on different machines.  
##
##
##############################################################################


import cpickleWrapper
from   ClientStatsPickler import *
import FileStatsCollector
from   FileStatsCollector import _FileStatsEntry,FileStatsCollector


  
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



def mergeHourlyPickles( logger = None , startTime = "2006-07-31 13:00:00", endTime = "2006-07-31 19:00:00", client = "satnet" ):
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
        pickles.append( ClientStatsPickler.buildThisHoursFileName(  client = client, offset = 0, currentTime = seperator ) )        
    
    
    for pickle in pickles : 
        print "####pickle : %s" %pickle
        
        if os.path.isfile( pickle ) :
            tempCollection = cpickleWrapper.load( pickle )
            entries.extend( tempCollection.fileEntries )
        else:
            emptyEntries = fillWithEmptyEntries( nbEmptyEntries = 60, entries = [] )
            entries.extend( emptyEntries )
     
            
    statsCollection = FileStatsCollector( statsTypes = types, startTime = startTime , endTime = endTime, interval = MyDateLib.MINUTE, totalWidth = width, fileEntries = entries )
    
    
    return statsCollection        



def mergePickles( logger = None , pickleNames = None, pickledTimes = None, clientName = ""  ):
    """
            This methods receives a list of filenames referring to 
            pickled FileStatsEntries.
            
            
            Pre condition :Pickle should be of the same timespan and bucket width.
                        If not exception will be raised and program terminated.  
            
            Note : Should test if it would be somewhat faster not to recalculate everything 
            and just go with proportions 
    """
    if logger != None : 
        logger.debug( "Call to mergePickles received." )
              
    entryList = []
    
    for pickle in pickleNames:
        
        entryList.append( cpickleWrapper.load( pickle ) )
    
    
    if entryListIsValid( entryList ) == True :
        
        #start off with a carbon copy of entryList[0]
        newFSC = FileStatsCollector( files = entryList[0].files , statsTypes =  entryList[0].statsTypes, startTime = entryList[0].startTime, endTime = entryList[0].endTime, interval=entryList[0].interval, totalWidth = entryList[0].totalWidth, firstFilledEntry = entryList[0].firstFilledEntry, lastFilledEntry = entryList[0].lastFilledEntry, maxLatency = entryList[0].maxLatency, fileEntries = entryList[0].fileEntries )
        
        
        for i in range (1 , len(entryList) ): #add other entries 
            
            for file in entryList[i].files :
                if file not in newFSC.files :
                    newFSC.files.append( file ) 
            
            for j in range( len(newFSC.fileEntries ) ) : 
                    
            
                for k in range( entryList[i].fileEntries[j].values.rows ):#Add all new value
                    
                    newFSC.fileEntries[j].values.productTypes.append( entryList[i].fileEntries[j].values.productTypes[k] ) 
                    
                    newFSC.fileEntries[j].files.append( entryList[i].fileEntries[j].files[k] ) 
                    newFSC.fileEntries[j].times.append( entryList[i].fileEntries[j].times[k] )          
                                        
                    if entryList[i].fileEntries[j].values.productTypes[k] != "[ERROR]" :
                        newFSC.fileEntries[ j ].nbFiles = newFSC.fileEntries[ j ].nbFiles + 1
                    
                    for type in newFSC.statsTypes :
                        newFSC.fileEntries[j].values.dictionary[type].append( entryList[i].fileEntries[j].values.dictionary[type][k] ) 
                        
                    newFSC.fileEntries[j].values.rows = newFSC.fileEntries[j].values.rows + 1

        
        newFSC = newFSC.setMinMaxMeanMedians( startingBucket = 0 , finishingBucket = newFSC.nbEntries )
    
    else:
    
        logger.warning( "Did not merge pickles named : %s. Pickle list was not valid." %pickleNames )
        logger.warning( "Filled with empty entries instead." %pickleNames )
        newFSC.fileEntries = fillWithEmptyEntries( nbEmptyEntries, [] )
    
    
    return newFSC
        

    
    

def main():
    """
        Small test case. Tests if everything works plus gives an idea on proper usage.
    """
   
    #for this example to work these pickels need to exist. 
    fsc = mergeHourlyPickles( client = "satnet", startTime = "2006-07-19 01:00:00", endTime = "2006-07-19 04:00:00" )
    
    
    
    #join a pickle with itself to make it easier to see if data was merged or not. 
    #use pickleUpdater.py to create some hourly pickles to use this test
#     pickleNames = [ PXPaths.PICKLES + "tx/amis/2006081/03", PXPaths.PICKLES + "tx/amis/2006081/03" ]
#     pickledTimes = [PXPaths.PICKLES + "PICKLED-TIMES"]
#     pickle = PXPaths.PICKLES + "mergedpickle/amismerged"
#     
#     newFSC = mergePickles( pickleNames=pickleNames, pickledTimes=pickledTimes  )
#     cpickleWrapper.save ( object = newFSC, filename = pickle )     

    
if __name__ == "__main__":
    main()





