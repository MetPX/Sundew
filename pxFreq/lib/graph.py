#!/usr/bin/python

"""
    graph.py
    
    Certaines methodes ont ete inspire du site web : http://www.python.org/doc/essays/graphs/
    
    Auteur : David Nantel
    Date : 7 Dec 2007

"""

import re,os
from node import node

# def trouverGraph(nom,graphList):
#     gr = None
#     for g in graphList:
#         if(g.name == nom):
#             gr = g
#             break
#     return gr

class graph:
    """
        Classe graph
        
        Implemente sous forme de dictionnaire, le graph contient des noeuds et a chaque noeud
        est associe une liste de liens vers d'autre noeuds.
        
        Nous pouvon donc:
            Ajouter des noeuds
            Enlever des noeuds
            Ajouter des liens
            Enlever des liens
            Trouver tous les chemins possible entre deux noeuds
            Afficher le graph sous une forme d'arboresence
            Trouver s'il existe un cycle entre deux noeud
            
    """
    def __init__(self,rootNode):
        self.root = rootNode
        self.nodesList = [self.root]
            
    def addNode(self,theNode):
        if(not self.searchNode(theNode)):
            self.nodesList.append(theNode)
            return theNode
        else:
            return self.searchNode(theNode)
            
    def removeNode(self,theNode):
        if(theNode in self.nodesList):
            #Parcourir tous les noeuds pour enlever tous liens avec ce noeud
            for inode in self.nodesList:
                if(theNode in inode.nextNodes):
                    inode.removeNext(theNode)
            
            #Enlever le noeud
            self.nodesList.remove(node)
            
    def searchNode(self,theNode):
        for inode in self.nodesList:
            if(theNode.direction == inode.direction and
                theNode.name == inode.name and
                theNode.cluster == inode.cluster):
                return inode
        return None
        
    def addLink(self,node1,node2):
        if(node1 in self.nodesList and node2 not in node1.nextNodes):
            node1.addNext(node2)
            
    def removeLink(self,node1,node2):
        if(node1 in self.nodesList and node2 in node1.nextNodes):
            node1.removeNext(node2)
        
    def findAllPaths(self, startNode, endNode, path=[]):
        path = path + [startNode]
        
        if(startNode == endNode):
            return [path]
        
        if(startNode not in self.nodesList):
            return []
        
        paths = []
        for inode in startNode.nextNodes:
            if inode not in path:
                newpaths = self.findAllPaths(inode, endNode, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths
                
    def tree(self,root=None,pred="   "):
        if(not root):
            root = self.root
            
        retour = str(root)+"\n"
        
        if(len(root.nextNodes) != 0):
            space = pred + "|-- "
            nodes = root.nextNodes
            i = 1
            while(i < len(nodes)):
                if(root.direction == "to_" and self.isLoop(root,nodes[i-1])):
                    #retour += space + nodes[i-1] + "*\n"
                    pass
                else:
                    retour += space + self.tree(nodes[i-1],pred+"|   ")
                i += 1
            space = pred + "`-- "
            if(root.direction == "to_" and self.isLoop(root,nodes[len(nodes)-1])):
                #retour += space + nodes[len(nodes)-1] + "*\n"
                pass
            else:
                retour += space + self.tree(nodes[len(nodes)-1],pred+"    ")
                
        return retour

    def isLoop(self,node1,node2,start=None):
        if(not start):
            start = self.root
        
        paths = self.findAllPaths(start,node1)
        clustersVisited = []
        for path in paths:
            for inode in path:
                if(inode.cluster not in clustersVisited):
                    clustersVisited.append(inode.cluster)
        if(node2.cluster in clustersVisited):
            return True
        else:
            return False
        
    