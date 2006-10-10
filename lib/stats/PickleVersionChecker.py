"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##############################################################################
##
##
## Name   : pickleVersionChecker.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 06-07-2006 
##
##
## Description : This file contains all the needed methods needed to compare 
##               the current checksum of a pickle file to the previously saved
##               checksum of the file.           
##
##               Note : The user parameter is used in some methods. This concept                
##                      has been implemented as to differentiate the different
##                      parties wich manipulate said file. This had to be done 
##                      since different users can use the file at different 
##                      points in time and thus a file shoudl be considered modified 
##                      for a certain user might not be for another and vice-versa.
##
## 
##
##############################################################################

import os, commands, pwd, sys, PXPaths, cpickleWrapper,glob

PXPaths.normalPaths()


class PickleVersionChecker :

    def __init__( self ):
        """
            Constructor. Contains two current and saved lists.
        """
        
        self.currentClientFileList = {} # Current file list found for a client on disk.
        self.savedFileList         = {} # The one that was previously recorded
        
        
    def getClientsCurrentFileList( self, client ):
        """
            Client list is used here since we need to find all the pickles that will be used in a merger.
            Thus unlike all other methos we dont refer here to the combined name but rather to a list of
            individual machine names. 
            
            Returns the checksum of all pickle files currently found on the disk.
            
        """  

        filePattern = PXPaths.PICKLES + client + "/*/*"  #_??
        folderNames = glob.glob( filePattern )
        
        
        fileNames = []
        for folder in folderNames:
            if os.path.isdir( folder ):                    
                filePattern = folder + "/" + "*_??"
                fileNames.extend( glob.glob( filePattern ) )       
                

        for fileName in fileNames :
            self.currentClientFileList[fileName] = os.path.getmtime( fileName )            
   
        return  self.currentClientFileList       
            
        
        
    def getSavedList( self, user, client ):
        """
            Returns the checksum of the files contained in the saved list.
        
        """
        
        directory = PXPaths.STATS + "file_versions/"
        fileName  = user + "_" + client 
        
        try :
            self.savedFileList = cpickleWrapper.load( directory + fileName )
            if self.savedFileList == None :
                self.savedFileList = {}
        except: # if file does not exist
            self.savedFileList = {}
        
        return self.savedFileList
        
        
                    
    def isDifferentFile( self, user ,client, file,):
        """
            
            Goal : Returns whether or not the file is different than 
                   the one previously recorded.
            
            File   : File to verify
            Client : Client to wich the file is related(used to narrow down searchs)
            User   : Name of the client, person, etc.. wich has a relation with the 
                     file.  
             
        """
        
        isDifferent = True  
        
        #if user did not update both list we try and do it for him....
        if self.currentClientFileList == {}:
            self.getClientsCurrentFileList( client )
    
        if self.savedFileList == {}:
            self.getSavedList( user, client )
        
        try:
            if self.savedFileList[file] == self.currentClientFileList[file] :
                isDifferent = False         
            
        except:#key doesnt exist on one of the lists
            pass
        
        
        return isDifferent
            
    
    
    def updateFileInList( self, file ) :
        """
            File : Name of the file 
            User : Person for whom a relation with the file exists. 
            Puts current checksum value  
            
        """ 
        
        if self.savedFileList == None :
            self.savedFileList = {}  
        
        try :
            self.savedFileList[file] = self.currentClientFileList[file]
        except:
            self.savedFileList[file] = 0
            
    
    def saveList( self, user, client ):   
        """
            Saves list. Will include modification made in updateFileInlist method 
        
        """
        
        directory = PXPaths.STATS + "file_versions/"
        fileName  = user + "_" + client 
        
        if not os.path.isdir( directory ):
            os.makedirs( directory, mode=0777 )
            #create directory
        
        cpickleWrapper.save( object = self.savedFileList, filename = directory + fileName )

 
           
def main():
    """
        small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    vc  = PickleVersionChecker()
    vc.currentClientFileList( "bob")
    vc.getSavedList()
#     vc.updateFileInList( file = "/apps/px/stats/pickles/pds5/20060831/rx/lvs1-dev_15" , user = "pds5pds6" ) 
#     
#     print vc.savedFileList["pds5pds6"]["/apps/px/stats/pickles/pds5/20060831/rx/lvs1-dev_15"]
    
    
    
if __name__ == "__main__" :
    main()


 