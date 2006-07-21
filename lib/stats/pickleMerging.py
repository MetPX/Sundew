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


import gzippickle
from   FileStatsCollector     import *


def picklesWereLastUpdatedAtTheSameTime( pickledTimes = [], clientName = ""  ):
    """
        This methods searchs all pickled times for the time of the last pickle 
        of the clientName. 
        
        Returns whether or not all pickled times had the same time or not.   
    
    """
    
    
    try :
     
        if len(pickledTimes) == 1:
            updatedAtTheSameTime = True     
        
        elif pickledTimes != []:
            
            i =0
            updatedAtTheSameTime = True
            lastUpdates = []
            
            for pickle in pickledTimes :
                times = {}
                lastCronJob = {}
                
                if os.path.isfile( pickle ):
            
                    fileHandle  = open( fileName, "r" )
                    times       = pickle.load( fileHandle )
                    lastUpdates.append( times[ clientName ] )
                    fileHandle.close()    
            
            while updatedAtTheSameTime == True and i < len(lastUpdates) :
                if lastUpdates[i] != lastupDates[0]:
                    updatedAtTheSameTime = False 
                i = i + 1               
            
        
        else:
            updatedAtTheSameTime = False 
    
    except:                 
        updatedAtTheSameTime = False 
        fileHandle.close()
    
    return updatedAtTheSameTime   



def entryListIsValid( entryList ):
    """
        returns whether or not an entry list of pickles contains 
        a list of pickles that can be merged. 
         
        #Might be incomplete...
    
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



def mergePickles( pickleNames = None, pickledTimes = None, clientName = ""  ):
    """
        This methods receives a list of filenames referring to 
        pickled FileStatsEntries.
        
        Pre condition :Pickle should be of the same timespan and bucket width.
                       If not exception will be raised and program temrinated.  
        
        
                           
    """
    z =0 
       
    entryList = []
    
    for pickle in pickleNames:
        
        entryList.append( gzippickle.load( pickle ) )
    
    if entryListIsValid( entryList ) == True and picklesWereLastUpdatedAtTheSameTime( pickledTimes, clientName ) :
        
        #start off with a carbon copy of entryList[0]
        newFSC = FileStatsCollector( files = entryList[0].files , statsTypes =  entryList[0].statsTypes, startTime = MyDateLib.getIsoFromEpoch(entryList[0].startTime), width = entryList[0].width, interval=entryList[0].interval, totalWidth = entryList[0].totalWidth, lastEntryCalculated = entryList[0].lastEntryCalculated, lastFilledEntry = entryList[0].lastFilledEntry, maxLatency = entryList[0].lastFilledEntry, fileEntries = entryList[0].fileEntries )
        
        
        for i in range (1 , len(entryList) ): #add other entries 
            
            newFSC.files.update( entryList[i].files ) 
             
            for j in range( len(newFSC.fileEntries ) ) : 
                 
                for k in range( entryList[i].fileEntries[j].values.rows ):#Add all new value
                    
                    newFSC.fileEntries[j].values.productTypes.append( entryList[i].fileEntries[j].values.productTypes[k] ) 
                    
                    newFSC.fileEntries[j].files.append( entryList[i].fileEntries[j].files[k] ) 
                    newFSC.fileEntries[j].times.append( entryList[i].fileEntries[j].times[k] )          
                                        
                    if entryList[i].fileEntries[j].values.productTypes[k] != "[ERROR]" :
                         newFSC.fileEntries[ j ].nbFiles = newFSC.fileEntries[ j
                          ].nbFiles + 1
                    
                    for type in newFSC.statsTypes :
                       # print k,type
                        newFSC.fileEntries[j].values.dictionary[type].append( entryList[i].fileEntries[j].values.dictionary[type][k] ) 
                        
                    newFSC.fileEntries[j].values.rows = newFSC.fileEntries[j].values.rows + 1
                    z = z + 1
                    print "newFSC.fileEntries[j].values.rows : %s" %newFSC.fileEntries[j].values.rows
                    print "len(newFSC.fileEntries[j].values.dictionary[type]) : %s" %len(newFSC.fileEntries[j].values.dictionary[type])        
        
        print "z = %s " %z
        print newFSC.nbEntries
        
        newFSC = newFSC.setMinMaxMeanMedians( startingBucket = 0 , finishingBucket = newFSC.nbEntries )
        
        return newFSC
        
    else:
        print "Error trying to merge pickles."
        print "Please give a valid list of pickle names."
        print "This list : %s is not valid." %pickleNames
        print "Program terminated."
        sys.exit() 
    
    

def main():
    
    pickleNames = ["/apps/px/lib/stats/PICKLES/amis2/amis2-PICKLE-2006-07-17","/apps/px/lib/stats/PICKLES/amis1/amis1-PICKLE-2006-07-17"]
    
    
    pickledTimes = ["/apps/px/lib/stats/PICKLED-TIMES"]
    pickle = "/apps/px/lib/stats/PICKLES/amis3/amis3-PICKLE-2006-07-17"
    
    newFSC = mergePickles( pickleNames=pickleNames, pickledTimes=pickledTimes  )
    gzippickle.save ( object = newFSC, filename = pickle )     

    
if __name__ == "__main__":
    main()





