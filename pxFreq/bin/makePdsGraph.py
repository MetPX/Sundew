#!/usr/bin/python


"""
    makePdsGraph.py
    
    Ce programme trouve le parcour des fichiers dans le reseau. Pour ce faire, j'utilise les trois base de donnees
    construite avec le programme 'makePdsInfo' (pxFreq). Trois clusters sont donc observes pour trouver les chemins
    mais la mise en place d'autre cluster pourrait augmenter la richesse de ce programme.
    
    Author : David Nantel
    Date :   10 Dec 2007
    
"""

import sys
from optparse import OptionParser


sys.path.append("../lib/")
from graph import *


def commandLineParser():
    """
        Gestion des options lors de l'appel du script
        Retour: (parser, options, args)
    """
    version = os.path.basename(sys.argv[0])+" 1.0"
    usage = "makePdsGraph.py [options] -p produit"
    description = "Construction de graph a partir des bases de donnees des clusters."
    parser = OptionParser(usage=usage, description=description, add_help_option=False)
    
    parser.add_option("--version",
                      action="store_true",dest="version", default=False,
                      help="Affiche la version.")
    
    parser.add_option("-h", "--help",
                      action="help",
                      help="Affiche cette aide.")
                      
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Mode verbeux.")
    
    parser.add_option("-p", "--products",
                      action="store", dest="products", default=None,
                      help="Demande un nom de produit. L'utilisation du caractere '*' est possible.")
                      
    parser.add_option("-d", "--details",
                      action="store_true", dest="details", default=False,
                      help="Demande l'affichage en detail du ou des produits.")
                      
    parser.add_option("-t", "--tree",
                      action="store_true", dest="tree", default=False,
                      help="Demande l'affichage en arboressence du ou des produits.")
                      
    (options, args) = parser.parse_args()
    
    if(options.version):
        print version
        sys.exit()
            
    if(options.products == None):
        parser.error("Un nom de produit doit etre donne avec l'option '-p'.")
    
    return (parser, options, args)
    
def findProducts(products, dbFics):
    """
        Trouve toutes l'informations demandees par la regex 'products'
        Cette informations est placees dans un dictionnaire: {produit:[(sources,nomFichier,clients)]}  
    """
    
    products = products.replace("*",".*")
    c = re.compile(products)
    productsDict = {}
    for fic in dbFics:
        cluster = fic.name.split("/").pop().rstrip(".db")
        for line in fic:
            if(c.match(line)):
                product,sources,clients = parseLine(line)
                if(product not in productsDict):
                    productsDict[product] = [(sources,cluster,clients)]
                else:
                    productsDict[product].append((sources,cluster,clients))
                    
    return productsDict
            
def parseLine(line):
    """
        Decortique une ligne d'un fichier .db
        Retourne le nom du produit, une liste de sources et une liste de clients
    """
    
    line = line.split()
    product, sources, clients = line[0], line[1], line[2]
    
    #Traitement des sources
    sources = sources.lstrip("[").rstrip("]").split(",")
    for i in range(len(sources)):
        m = re.compile(r"([^=]*)=.*").match(sources[i])
        if(m):
            sources[i] = m.group(1)
        else:
            sources = []
            
    #Traitement des clients
    clients = clients.lstrip("[").rstrip("]").split(",")
    if(clients == [""]):
        clients = []
        
    return (product, sources, clients)

def readAliasConf():
    """
        Lecture du fichier de configuration des alias
    """
    
    conf = open("alias.conf","r")
    alias = {}
    
    for line in conf:
        line = line.strip()
        if(len(line) != 0):
            if(line[0] != "#"):
                line = line.split("=")
                alias[line[0]] = line[1]
            
    return alias
    
def buildGraphs(Products):
    """
        Construction d'un graph pour chaque produit. Le graph correspond aux chemins
        que prends ce produit dans le reseau.
        
        La structure du graph est toujours la meme:
            Le noeud de depart est le produit lui-meme.
            Une source est precedee du prefixe 'rx_'.
            Un client est precede du prefixe 'tx_'.
            les noeuds avec le prefixe 'to_' ne sont present que pour lier differentes parties du graph.
                Il sont par consequent transparent.
                
        Le retour de cette fonction est une liste de graphs
    """
    
    alias = readAliasConf();
    graphList = []
    for p in Products:
        product = node("",p,"")
        g = graph(product)
        
        #Pour chaque cluster
        for i in range(len(Products[p])):
            cluster = Products[p][i][1]
            
            #Pour chaque source
            for source in Products[p][i][0]:
                newSource = g.addNode(node("rx_",source,cluster))
                g.addLink(product,newSource)
                
                #Pour chaque client
                for client in Products[p][i][2]:
                    newClient = g.addNode(node("tx_",client,cluster))
                    g.addLink(newSource,newClient)
                    if(client in alias):
                        toNode = g.addNode(node("to_",alias[client],cluster))
                        g.addLink(newClient,toNode)
                        
        #Enlever les liens entre le root et un cluster interne
        listNode = []
        for n in product.nextNodes:
            listNode.append(n)
            
        for inode in listNode:
            if(inode.name in alias):
                theNode = g.searchNode(node("to_",inode.cluster,alias[inode.name]))
                if(theNode):
                    g.addLink(theNode,inode)
                    g.removeLink(product,inode)
        
                
        #Sauter par dessus les 'to_' (Ce sont des noeuds transparent)
        listNode = []
        for n in g.nodesList:
            listNode.append(n)
                
        for inode in listNode:
            listLink = []
            for l in inode.nextNodes:
                listLink.append(l)
                
            for link in listLink:
                if(link.direction == "to_"):
                    for n in link.nextNodes:
                        g.addLink(inode,n)
                    g.removeLink(inode,link)
        
        graphList.append(g)
        
    return graphList

def printDetails(Products):
    """
        Affichage detaille des produits demande
    """
    for p in Products:
        print "produit:",p
        for i in range(len(Products[p])):
            print "Sources:",Products[p][i][0]
            print "Cluster:",Products[p][i][1]
            print "Clients:",Products[p][i][2]
            print
        print
        
def printTrees(graphList):
    """
        Affichage sous la forme d'arborescence
    """
    for g in graphList:
        print g.tree()
        
if __name__ == "__main__":
    #Parsing de la ligne de commande
    parser, options, args = commandLineParser()
    
    #Ouverture des trois clusters
    pathClusters = "../data/"
    dbPx = open(pathClusters+"px.db","r")
    dbPds = open(pathClusters+"pds.db","r")
    dbPxatx = open(pathClusters+"pxatx.db","r")
    dbPxstage = open(pathClusters+"px-stage.db","r")
    
    #Trouver toutes les lignes avec le ou les produits specifie en parametre
    Products = findProducts(options.products, [dbPx, dbPds, dbPxatx, dbPxstage])
    
    dbPx.close()
    dbPds.close()
    dbPxatx.close()
    dbPxstage.close()
    
    #Affichage du detail
    if(options.details):
        printDetails(Products)
        
    #Construire le ou les graphs ( graph + noeuds + liens ) et affichage
    if(options.tree):
        graphList = buildGraphs(Products)
        printTrees(graphList)
