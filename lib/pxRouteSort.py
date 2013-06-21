#!/usr/bin/python

"""
    pxRouteSort

    Description:
        pxRouteSort est un outil tres simple qui permet de trier les clients et les alias dans le fichier
        de configuration de la table de routage (pxRouting.conf)
    
        Un test de verification est egalement effectue pour s'assurer que le fichier de sortie n'est pas
        modifie autre que le tri.
        
    Auteur: David Nantel
    Date: 9 Octobre 2007
    Version: 1.0

    MG python3 compatible
"""

import sys, os
from optparse import OptionParser
#from sets import *

def commandLineParser():
    """
        Gestion des options lors de l'appel du script
        Retour: (parser, options, args)
    """
    version = os.path.basename(sys.argv[0])+" 1.0"
    usage = "pxRouteSort.py ficEntree ficSortie"
    description = "Tri du fichier de configuration de la table de routage (pxRouting.conf)."
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
                      
    (options, args) = parser.parse_args()
    
    if(options.version):
        print(version)
        sys.exit()
            
    if(len(args) != 2):
        parser.error("Erreur d'argument.")
        
    return (parser, options, args)

def ouvrirFichier(nomFic,mode):
    """
        Ouverture d'un fichier avec le mode specifie.
        
        Entree: le chemin du fichier a ouvrir et le mode d'ouverture
        Retour: Objet de type fichier
        Exception: Le fichier n'a pu etre ouvert
    """
    try:
        fic = open(nomFic, mode)
    except IOError:
        parser.error("Impossible d'ouvrir %s\n" % (nomFic))
        
    return fic

def sortirFichierTableRoutageMAJ(listeLignes, fic):
    """
        Ecriture de la table de routage mise a jour dans un fichier.
        Entree: Liste de ligne correspondant a la table de routage
    """
    
    ficOut = ouvrirFichier(fic,"w")
    for ligne in listeLignes:
        ficOut.write(ligne)
    ficOut.close()

def sortTableRoutage(tableRoutage):
    """
        Fonction effectuant le tri de la table de routage ligne par ligne.
        Entree : La table de routage de depart
        Sortie : La table de routage triee
    """
    
    tableRoutageSortie = []
    
    for ligne in tableRoutage:
        if(ligne[0:3] == "key" or ligne[0:11] == "clientAlias"):
            ligne = ligne.strip().split()
            if((ligne[0] == "clientAlias" and len(ligne) == 3) or (ligne[0] == "key" and len(ligne) == 4)):
                setNoms = Set(ligne[2].strip().split(","))
                listeNoms = list(setNoms)
                listeNoms.sort()
                #Enlever les blanc (double virgule)
                while("" in listeNoms):
                    listeNoms.remove("")
                strNoms = ",".join(listeNoms)
                ligne[2] = strNoms
            
            ligne = " ".join(ligne)
            ligne = ligne + "\n"
                
            
        tableRoutageSortie.append(ligne)
    return tableRoutageSortie

def diffTableRoutage(tableRoutage1, tableRoutage2):
    """
        Fonction permettant de capter les differences entre les deux table de routage (depart et triee)
        S'il y a lieu, les erreurs seront envoye sur la sortie standard avec le format suivant:
            Erreur a la ligne ???
            NomFichier1 : NbCaractere : ligne en erreur du fichier 1
            NomFichier2 : NbCaractere : ligne en erreur du fichier 2
    """
    
    listListTuple1 = []
    listListTuple2 = []
    erreur = False
    nbCaractDiff = 0
    totalLigne = len(tableRoutage1)
    numLigne = 0
    
    while(numLigne < totalLigne):
        charCount = {}
        for char in tableRoutage1[numLigne]:
            charCount[char] = charCount.get(char, 0) + 1
        listTuple1 = []
        for cle in charCount:
            listTuple1.append((cle,charCount[cle]))
        listTuple1.sort()
        #if(len(listTuple1) > 0 and listTuple1[0][0] == "\n"):
        #    del listTuple1[0]
        #if(len(listTuple1) > 0 and listTuple1[0][0] == " "):
        #    del listTuple1[0]
        charCount = {}
        for char in tableRoutage2[numLigne]:
            charCount[char] = charCount.get(char, 0) + 1
        listTuple2 = []
        for cle in charCount:
            listTuple2.append((cle,charCount[cle]))
        listTuple2.sort()
        #if(len(listTuple2) > 0 and listTuple2[0][0] == "\n"):
        #    del listTuple2[0]
        #if(len(listTuple2) > 0 and listTuple2[0][0] == " "):
        #    del listTuple2[0]
            
        if(listTuple1 != listTuple2):
            nbCaract1 = 0
            for t in listTuple1:
                nbCaract1 += t[1]
            nbCaract2 = 0
            for t in listTuple2:
                nbCaract2 += t[1]
            print("ERREUR a la ligne", numLigne+1)
            print(ficEntree,":",nbCaract1,":",tableRoutage1[numLigne],)
            print(ficSortie,":",nbCaract2,":",tableRoutage2[numLigne],)
            print("")
            nbCaractDiff += (nbCaract1 - nbCaract2) 
            erreur = True
    
        numLigne += 1
    if not erreur:
        if(options.verbose): print("Test complete avec succes.")
    else:
        print("Le test de difference a echoue.")
        print(nbCaractDiff, "caractere(s) de difference entre les deux fichiers")
    
if __name__ == "__main__":
    
    parser,options,args = commandLineParser()
    
    ficEntree = args[0]
    ficSortie = args[1]
    
    #Sorting
    if(options.verbose): print("Tri du fichier de la table de routage", ficEntree)
    tableRoutage1 = ouvrirFichier(ficEntree,"r")
    sortirFichierTableRoutageMAJ(sortTableRoutage(tableRoutage1),ficSortie)
    if(options.verbose): print("Sortie du fichier trie:", ficSortie)
    
    
    #Testing
    if(options.verbose): print("Test de difference entre", ficEntree, "et", ficSortie )
    tableRoutage1 = ouvrirFichier(ficEntree,"r")
    tableRoutage2 = ouvrirFichier(ficSortie,"r")
    table1 = tableRoutage1.readlines()
    table2 = tableRoutage2.readlines()
    tableRoutage1.close()
    tableRoutage2.close()
    diffTableRoutage(table1,table2)
