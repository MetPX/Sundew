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
## Description : 
##
##
##############################################################################

import os, commands, pwd, sys, PXPaths, cpickleWrapper

PXPaths.normalPaths()


class PickleVersionChecker :

    def __init__( self ):
        """
            Constructor.
        """
        
        self.currentFileList = {}
        self.savedFileList   = {}
        
        
    def getCurrentFileList( self ):
        """
            Returns the checksum of files currently found on the disk.
        """    
        
        status, md5Output = commands.getstatusoutput( "md5sum `find %s -name '*_??'` " % PXPaths.PICKLES )
        
        
        if status == 0:
        
            for line in md5Output.splitlines():
                sum,file = line.split()      
                self.currentFileList[file] = sum
            
            #print self.currentFileList     
    
        return  self.currentFileList       
            
        
        
    def getSavedList( self ):
        """
            Returns the checksum of the files when we last used them.
        """
        
        try :
            self.savedFileList = cpickleWrapper.load( PXPaths.STATS + "FILE_VERSIONS" )
        
        except: # if file does not exist
            self.savedFileList = {}
        
        return self.savedFileList
        
        
                    
    def isDifferentFile( self, file, user = "pds5pds6" ):
        """
        
        """
        
        isDifferent = True  
        
        #if user did not update both list we try and do it for him....
        if self.currentFileList == {}:
            self.getCurrentFileList()
    
        if self.savedFileList == {}:
            self.getSavedList()
    
        try:
        
            if self.savedFileList[user][file] == self.currentFileList[file] :
                isDifferent = False         
            
        except:#key doesnt exist on one of the lists
            pass
        
        
        return isDifferent
            
    
    
    def updateFileInList( self, file, user ) :
        """
        """ 

        if file in self.currentFileList.keys(): 
            self.savedFileList[user] = {}
            self.savedFileList[user][file] = self.currentFileList[file]
        
    
    
    def saveList( self ):   
        """
            Saves list. Will include modification made in updateFileInlist method 
        
        """
    
        cpickleWrapper.save( object = self.savedFileList, filename = PXPaths.STATS + "FILE_VERSIONS" )

 
           
def main():
    """
    
    """
    
    vc  = PickleVersionChecker()
    vc.getCurrentFileList()
    vc.getSavedList()
    vc.updateFileInList( file = "/apps/px/stats/pickles/pds5/20060831/rx/lvs1-dev_15" , user = "pds5pds6" ) 
    
    print vc.savedFileList["pds5pds6"]["/apps/px/stats/pickles/pds5/20060831/rx/lvs1-dev_15"]
    
    
    
if __name__ == "__main__" :
    main()


 