#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##############################################################################
##
##
## Name   : backwardReader.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 06-07-2006 
##
##
## Description : Small utility that can be used to read text files backward. 
##
##  Has a readlineBackwards method that is similar to readline 
##  and a tail method that is similar to the tail used in linux 
## 
##############################################################################

import os,sys 

class BackwardReader:
    
    def tail( nbLines = 1, file = "", printIt = False ):
        """
            Similar to the usual tail method we use in linux, only now it is in pure python.
            
            File must exist or else program will be terminated. 
            
            nbLines : Number of lines we want to get from the end of the file.
            file    : Absolute path to the file we want to use.
            printIt : Whether or not user want to print the results of action performed here. 
            
        """
        
        if os.path.isfile( file ):
            
            offset   = -1
            lines    = []
            fileSize = os.stat( file )[6]
            
            if fileSize >=2 : 
                
                fileHandle = open( file ,"r" )
                fileHandle.seek( offset,2 )
                
                for lineNumber in range( nbLines + 1 ) :
                    
                    while abs( offset ) <=  fileSize and fileHandle.read(1) == "\n" :
                        
                        offset = offset - 1
                        if abs( offset) <=  fileSize :
                            fileHandle.seek( offset,2 )
                        else:
                            fileHandle.seek( (fileSize - ( 2*fileSize ) ), 2 )  
                                
                    
                    while abs( offset) <=  fileSize and fileHandle.read(1) != "\n" :
                        
                        offset = offset - 1
                        
                        if abs( offset) <=  fileSize :
                            fileHandle.seek( offset, 2 )
                        else:
                            fileHandle.seek( (fileSize - ( 2 * fileSize) ), 2 )    
                    
                        
                    line = fileHandle.readline()
                    
                    if line != "" : #might not be usefull
                        lines.append( line )
                    
                    if abs( offset) >  fileSize : # cant tail any more lines than the file pocess..
                        break   
                
                fileHandle.close()
            
            lines.reverse()            
            
            if printIt == True :
                for line in lines:
                    print line 
            
        else:
        
            print "Error. %s does not exist." %file 
            print "Program terminated."
            sys.exit()   
            
        return lines          
    
    tail = staticmethod(tail)    
        
    def readLineBackwards( fileHandle, offset = -1 , fileSize =0 ) :           
        """
            This method is to be used in place of readlines to read a file line by 
            line backwards. 
            
            It will prove to be much faster and much less demanding on memory when 
            using large files than reading an entire file form the top with either 
            readline or readlines.  
        
        """
    
        
        line = ""
        
        if abs( offset ) <=  fileSize :
        
            
            fileHandle.seek( offset,2 )
            
            
            while abs( offset ) <=  fileSize and fileHandle.read(1) == "\n"  :
                
                offset = offset- 1
                
                if abs( offset ) <=  fileSize :
                    fileHandle.seek( offset,2 )
                else:
                    fileHandle.seek( ( fileSize - ( 2*fileSize ) ), 2 ) 
                    
            if abs( offset ) <=  fileSize :
                fileHandle.seek( offset, 2 )
            else:
                fileHandle.seek( ( fileSize - ( 2 * fileSize ) ), 2 ) 
                    
            while abs( offset ) <=  fileSize and fileHandle.read(1) != "\n" : 
                offset = offset- 1
                
                if abs( offset ) <=  fileSize :
                    fileHandle.seek( offset,2 )
                else:
                    fileHandle.seek( (fileSize - ( 2*fileSize ) ), 2 ) 
                        
            line = fileHandle.readline()
            
                
        return line, offset        
    
    readLineBackwards = staticmethod( readLineBackwards )
    
    if __name__ == "__main__":
        
        """
            Small test case. Tests if everything works plus gives an idea on proper usage.
        """
        
        #------------------------------------------------------ print "tail tests :"
        # tail( nbLines =10, file = PXPaths.STATS + "testFiles/empty", printIt = True )
        # tail( nbLines =10, file = PXPaths.STATS + "testFiles/tx_amis.log", printIt = True )
        # tail( nbLines =10, file = PXPaths.STATS + "testFiles/onelinefile", printIt = True)
    #------------------------------------------------------------------------------ 
        #---------------------------------------- print "read lines backward test :"
        #-------------------------------- fileName = PXPaths.STATS + "testFiles/bob"
        #------------------------------------------ fileHandle = open(fileName, "r")
    #------------------------------------------------------------------------------ 
        #------------------------------------------- fileSize = os.stat(fileName)[6]
        # line,offset  = readLineBackwards( fileHandle, offset = -1, fileSize = fileSize  )
    #------------------------------------------------------------------------------ 
        #---------------------------------------------------------------- print line
    #------------------------------------------------------------------------------ 
        #--------------------------------------------------------- while line != "":
            # line,offset = readLineBackwards( fileHandle = fileHandle, offset = offset , fileSize = fileSize )
            #-------------------------------------------------------- if line != "":
                #-------------------------------------------------------- print line
    #------------------------------------------------------------------------------ 
        # tail( nbLines =10, file = PXPaths.STATS + "testFiles/nonexisting", printIt = True )
    #------------------------------------------------------------------------------ 
        #-------------------------------------------------------- fileHandle.close()
        
