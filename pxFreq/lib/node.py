#!/usr/bin/python

class node:
    def __init__(self,nodeDirection,nodeName,nodeCluster):
        self.direction = nodeDirection
        self.name = nodeName
        self.cluster = nodeCluster
        
        self.nextNodes = []
        
    def addNext(self,node):
        if(node not in self.nextNodes):
            self.nextNodes.append(node)
        
    def removeNext(self,node):
        if(node in self.nextNodes):
            self.nextNodes.remove(node)
            
    def removeAllNext(self):
        self.nextNodes = []
        
    def __str__(self):
        if(self.cluster == ""):
            return  self.direction + self.name
        else:
            return  self.direction + self.name + " (" + self.cluster + ")"
        
    def __cmp__(self,node):
        if(self.direction == node.direction and
            self.name == node.name and
            self.cluster == node.cluster):
            return 0
        else:
            return 1