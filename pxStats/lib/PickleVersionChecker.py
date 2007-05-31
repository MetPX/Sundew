"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

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
"""


import os, commands, pwd, sys, glob
sys.path.insert(1, sys.path[0] + '/../../')


from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.CpickleWrapper import CpickleWrapper


class PickleVersionChecker :

    def __init__( self ):
        """
            Constructor. Contains two current and saved lists.
        """
        
        self.currentClientFileList = {} # Current file list found for a client on disk.
        self.savedFileList         = {} # The one that was previously recorded
        
        
    def getClientsCurrentFileList( self, clients ):
        """
            Client list is used here since we need to find all the pickles that will be used in a merger.
            Thus unlike all other methods we dont refer here to the combined name but rather to a list of
            individual machine names. 
            
            Returns the checksum of all pickle files currently found on the disk.
            
        """  
        
        
        fileNames = []
        
        for client in clients : 
            filePattern = StatsPaths.STATSPICKLES + client + "/*/*"  #_??
            folderNames = glob.glob( filePattern )
                        
            
            for folder in folderNames:
                if os.path.isdir( folder ):                    
                    filePattern = folder + "/" + "*_??"
                    fileNames.extend( glob.glob( filePattern ) )       
                    
    
            for fileName in fileNames :
                self.currentClientFileList[fileName] = os.path.getmtime( fileName )            
   
                
        return  self.currentClientFileList       
            
        
        
    def getSavedList( self, user, clients ):
        """
            Returns the checksum of the files contained in the saved list.
        
        """
        
        self.savedFileList         = {}
        directory = StatsPaths.STATSDATA + "fileAcessVersions/"              
                
        combinedName = ""
        for client in clients:
            combinedName = combinedName + client
        
        fileName  = user + "_" + combinedName             
            
        try :
            
            self.savedFileList = CpickleWrapper.load( directory + fileName )
            
            if savedFileList == None :
                self.savedFileList = {}
                
        except: # if file does not exist
            pass
        
        
        return self.savedFileList
        
        
                    
    def isDifferentFile( self, user ,clients, file):
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
            self.getClientsCurrentFileList( clients )
    
        if self.savedFileList == {}:
            self.getSavedList( user, clients )

           
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
            
    
    def saveList( self, user, clients ):   
        """
            Saves list. Will include modification made in updateFileInlist method 
        
        """
        
        directory = StatsPaths.STATSETC + "fileAcessVersions/"
         
        
        combinedName = ""
        for client in clients:
            combinedName = combinedName + client
        
        fileName  = user + "_" + combinedName
        
        if not os.path.isdir( directory ):
            os.makedirs( directory, mode=0777 )
            #create directory
        
        CpickleWrapper.save( object = self.savedFileList, filename = directory + fileName )

 
           
def main():
    """
        small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    vc  = PickleVersionChecker()
    vc.currentClientFileList( "bob")
    vc.getSavedList()
#     vc.updateFileInList( file = "/apps/px/stats/pickles/client/20060831/rx/machine_15" , user = "someUser" ) 
#     
#     print vc.savedFileList["someUser"]["/apps/px/stats/pickles/client/20060831/rx/machine_15"]
    
    
    
if __name__ == "__main__" :
    main()


 