"""
MetPX Copyright (C) 2004-2007  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: fileLib.py
#
# Author: Daniel Lemay
#
# Date: 2007-10-11
#
# Description: Useful file related functions
#
#############################################################################################
"""
import sys, commands

def getNumLines(filename):
    try:    
        file = open(filename, 'r')
        lines = file.readlines()
        file.close()
        return len(lines)
    except:
        #(type, value, tb) = sys.exc_info()
        #print ("Type: %s, Value: %s" % (type, value))
        return -1

def getLines(filename):
    try:    
        file = open(filename, 'r')
        lines = file.readlines()
        file.close()
        return lines
    except:
        #(type, value, tb) = sys.exc_info()
        #print ("Type: %s, Value: %s" % (type, value))
        return None

def sortFilesByTime(list, searchWord):
    files = {}
    for file in list:
        #print file
        first = commands.getoutput('grep -m1 %s %s | head -n1 | cut -f1,2 -d" "' % (searchWord, file))
        if first:
            #print "debut"
            last =  commands.getoutput('grep %s %s | tail -n1 | cut -f1,2 -d" "' % (searchWord, file))
            #print "fin"
            files[file] = (first, last)

    backItems = [(item[1][1], item[0]) for item in files.items()]
    backItems.sort()
    return [tuple[1] for tuple in backItems]

    #FIXME: Pour optimiser la recherche, les fichiers qui sont en dehors des limites de recherche devraient
    #       etre elimines immediatement (faire une autre fonction pour cette tache)

def mergeFiles(files, mergeName):
    fileString = ""
    for file in files:
        fileString += file + " "
    if fileString:
        commands.getstatusoutput("cat %s | sort > %s" % mergeName)
        return mergeName
    else:
        return ""
        
