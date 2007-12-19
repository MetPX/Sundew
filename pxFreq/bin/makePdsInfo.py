#!/usr/bin/python

"""
    makePdsInfo.py
    
    Ce script lit les fichiers logs d'un cluster pour faire ressortir differentes informations:
        Les nom des produits
        Les sources associees a chaque produit
        Les clients vers qui le produit sont envoyees
        La premiere heure et date de reception du produit
        La frequence d'arrivee du produit
        
    Auteur : David Nantel
    date :   19 Dec 2007
"""

import re,os,sys
from optparse import OptionParser
from sets import *
from datetime import *

sys.path.append("/apps/px/sundew/lib/")
from Logger import Logger

def commandLineParser():
    """
        Gestion des options lors de l'appel du script
        Retour: (parser, options, args)
    """
    version = os.path.basename(sys.argv[0])+" 1.0"
    usage = "makePdsInfo.py [options] logFiles"
    description = "Creation d'une base de donnees a partir des logs de differents 'clusters'."
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
                      
    parser.add_option("-c", "--cluster",
                      action="store", dest="cluster", default=None, choices=["px","pxatx","pds","px-stage"],
                      help="Definie le cluster sur lequel travailler. Choix = [ px | pxatx | pds | px-stage ]")
                      
    (options, args) = parser.parse_args()
    
    if(options.version):
        print version
        sys.exit()
            
    if(len(args) < 1):
        parser.error("Au moins un fichier de log est necessaire.")
        
    if(options.cluster == None):
        parser.error("Choisir le 'cluster' avec l'option '-c'.")
    
    return (parser, options, args)

def afficher(st=""):
    """
        Affichage si dans le mode 'verbose': l'option '-v'.        
        Entree: Texte a afficher
    """
    if(options.verbose): print st
    
def openFile(nomFic,mode):
    """
        Ouvre un fichier selon le mode specifier.
        Retourne le fichier ouvert ou None si une erreur est survenue
    """
    try:
        fic = open(nomFic,mode)
    except:
        fic = None
        afficher("Impossible d'ouvrir le fichier: "+nomFic)
        logger.warn("Can't open file: "+nomFic)
        
    return fic

def openLogsFile():
    """
        Ouvre une serie de fichiers logs et place les fichiers ouverts dans une liste.
    """
    logsFile = []
    for ficName in args:
        #Ouverture du fichier log
        ficLog = openFile(ficName,"r")
        if(ficLog):
            logsFile.append((ficName,ficLog))
            
    return logsFile
            
def closeLogsFile(logsFile):
    """
        Ferme la serie de fichiers logs ouvert prealablement avec 'openLogsFile()'.
    """
    for fic in logsFile:
        fic.close()

def parseLine(line):
    """
        Fait le 'parsing' de la ligne avec les regex donnees
            - la ligne contient un produit alors on trouve le nom du produit ainsi que la date et l'heure de l'ingestion
            - la ligne contient une liste de clients vers lesquels le produit precedent est 'linke'
        Toutes l'informations trouvee est retournees
    """
    if(re.compile('Ingested in DB as').search(line)):
        line = line.split()
        date = line[0]
        heure = line[1]
        nameParsed = False
        nom = line[9].split("/")
        nom = nom[len(nom)-1]
        
        for regex in listeRegex:
            m = regex.match(nom)
            if(m):
                nom = "*".join(m.groups())
                nameParsed = True
                break

        return ("produit",nom,date,heure,nameParsed)
        
    else:
        m = re.compile('Queued for: ').search(line)
        if(m):
            line = line[m.end():line.find(" /n")]
            line = line.strip(" ")
            return ("clients",line.split(" "))
        
    return None
    
def updateDB(ficLog):
    """
        Lire ligne par ligne le fichier de logs et ressortir toutes l'informations
            dataBase -> {produit:[sources,clients,infoSurFrequence]}
            dataBase[produit][0] == sources
            dataBase[produit][1] == clients
            dataBase[produit][2] == {sources:([date/heure],frequence)}
    """
    global dataBase
    
    source = ficLog[0].split("/")
    source = source[len(source)-1].split(".")[0]
    source = source[3:]
    
    fic = ficLog[1]
    
    dernierProduit = None
    for line in fic:
        
        data = parseLine(line)
            
        if(data):
            if(data[0] == "produit"):
                produit,date,heure,nameParsed = data[1],data[2],data[3],data[4]
                dernierProduit = produit
                if(not nameParsed):
                    if(produit[0:16] != "PROBLEM_BULLETIN" and produit[0:16] != "FILE_FOR_COLUMBO" and produit[0:5] != "dummy"):
                        afficher("# "+produit)
                        logger.warn(options.cluster+": Regex not found for : "+produit)
                        
                    dernierProduit = None
                else:
                    if(produit in dataBase):
                        if(source in dataBase[produit][2]):
                            dataBase[produit][2][source][0].append((date,heure))
                        else:
                            dataBase[produit][2][source] = [[(date,heure)],"NA"]
                            dataBase[produit][0].add(source)
                    else:
                        dataBase[produit] = [Set([source]),Set([]),{source:[[(date,heure)],"NA"]}]
                        
            elif(data[0] == "clients"):
                for c in data[1]:
                    if(dernierProduit and c != ""):
                        dataBase[dernierProduit][1].add(c)
                dernierProduit = None
                
def parseDateAndTime(tic):
    """
        Take a tuple containing a date and a time.
        Returning a tuple containing each part of date and time.
        ex.:
            in = ('2007-10-27', '01:07:47,432')
            out= (2007, 10, 27, 01, 07, 47, 432)
    """
    
    date = tic[0]
    temps = tic[1]
    
    date = date.split("-")
    annee = int(date[0])
    mois  = int(date[1])
    jour = int(date[2])
    
    temps = temps.split(":")
    heure = int(temps[0])
    minute = int(temps[1])
    temps = temps[2].split(",")
    seconde = int(temps[0])
    mili = int(temps[1])
    
    return annee,mois,jour,heure,minute,seconde,mili

def TrouverIntervalle(delta):
    """
        Trouve et retourne la bonne frequence.
        Si aucune n'est trouvee, retourne la valeur 0
    """
    
    for intervalle in listeIntervalles:
        if(delta < (intervalle[0] + intervalle[1]) and delta > (intervalle[0] - intervalle[1])):
            return intervalle[0]
    return 0
    
def compare(x,y):
    """
        Comparaison de deux date/heure
        format de x et y : tuple("AAAA-MM-JJ","hh:mm:ss:ll")
    """
    x1 = x[0]+x[1]
    y1 = y[0]+y[1]
    if(x1<y1): return -1
    elif(x1==y1): return 0
    else: return 1
    
def trouverFrequences():
    """
        Tente de trouver la frequences de chaque produit.
    """
    global dataBase
    
    for entree in dataBase:
        for source in dataBase[entree][2]:
            
            liste = dataBase[entree][2][source][0]
            liste.sort(compare)
            
            if(len(liste) >= 4):
                pattern = {0:[]}
                firstOccurence = {0:None}
                for intervalle in listeIntervalles:
                    pattern[intervalle[0]] = []
                    firstOccurence[intervalle[0]] = None
                
                listeDelta = []
                tic = None
                for tac in liste:
                    if(tic == None):
                        #on debute ici la liste ... tac est l'element 0
                        tic = tac
                    else:
                        #ici, tic est le precedent de tac dans la liste
                        annee,mois,jour,heure,minute,seconde,mili = parseDateAndTime(tic)
                        dt1 = datetime(annee,mois,jour,heure,minute,seconde,mili*1000)
                        occ = (heure,minute,seconde)
                        annee,mois,jour,heure,minute,seconde,mili = parseDateAndTime(tac)
                        dt2 = datetime(annee,mois,jour,heure,minute,seconde,mili*1000)
                        
                        delta = dt2 - dt1
                        heures = delta.days * 24
                        minutes = delta.seconds / 60
                        heures = minutes / 60
                        minutes = minutes % 60
                        secondes = delta.seconds % 60
                        delta = secondes + 60*minutes + 60*60*heures
                        
                        #Ajouter le delta (secondes) dans la bonne intervalle
                        intervalle = TrouverIntervalle(delta)
                        pattern[intervalle].append(delta)
                        if(firstOccurence[intervalle] == None): firstOccurence[intervalle] = occ
                        
                        tic = tac
                
                #Trouver l'intervalle qui reviens le plus souvent
                nbmax = 0
                intmax = None
                for k in pattern:
                    if(len(pattern[k]) > nbmax):
                            nbmax = len(pattern[k])
                            intmax = k
    
                #Modifier la frequence dans la database
                if(intmax and intmax != 0):
                    occ = firstOccurence[intmax]
                    occ = "%02i:%02i:%02i" %(occ[0],occ[1],occ[2])
                    #                         premiere occurence de la journee, frequence
                    if(intmax == 5*60):       dataBase[entree][2][source][1] = occ + "- 00:05:00"
                    elif(intmax == 10*60):    dataBase[entree][2][source][1] = occ + "- 00:10:00"
                    elif(intmax == 15*60):    dataBase[entree][2][source][1] = occ + "- 00:15:00"
                    elif(intmax == 30*60):    dataBase[entree][2][source][1] = occ + "- 00:30:00"
                    elif(intmax == 60*60):    dataBase[entree][2][source][1] = occ + "- 01:00:00"
                    elif(intmax == 6*60*60):  dataBase[entree][2][source][1] = occ + "- 06:00:00"
                    elif(intmax == 12*60*60): dataBase[entree][2][source][1] = occ + "- 12:00:00"
                
def sparsify(d):
    """
    Improve dictionary sparsity.

    The dict.update() method makes space for non-overlapping keys.
    Giving it a dictionary with 100% overlap will build the same
    dictionary in the larger space.  The resulting dictionary will
    be no more that 1/3 full.  As a result, lookups require less
    than 1.5 probes on average.
    """

    e = d.copy()
    d.update(e)
    
def lireRegex():
    """
        Lecture du fichier de configuration des regex
        
        Retourne une liste de regex
    """
    listeRegex = []
    
    ficRegex = openFile("/apps/px/sundew/pxFreq/bin/regex.conf","r")
    
    if(ficRegex):
        for line in ficRegex:
            if(line[0] != "#" and line[0] != "\n"):
                listeRegex.append(re.compile(line[:line.find("\n")]))
        ficRegex.close()
    else:
        logger.error("Execution stop because 'regex.conf' was not found.")
        sys.exit()
        
    return listeRegex
                        
def lireIntervalles():
    """
        Lecture du fichier de configuration des intervalles pour les frequences
        
        Retourne une liste d'intervalles dans le format : tuple("hh:mm:ss","hh:mm:ss","hh:mm:ss")
                                                                   freq       marge     alarme
    """
    listeIntervalles = []
    
    ficIntervalles = openFile("/apps/px/sundew/pxFreq/bin/intervalles.conf","r")
    
    if(ficIntervalles):
        for line in ficIntervalles:
            if(line[0] != "#" and line[0] != "\n"):
                line = line.split()
                freq,marge,alarme = line[0],line[1],line[2]
                freq = freq.split(":")
                freq = int(freq[0])*60*60 + int(freq[1])*60 + int(freq[2])
                marge = marge.split(":")
                marge = int(marge[0])*60*60 + int(marge[1])*60 + int(marge[2])
                alarme = alarme.split(":")
                alarme = int(alarme[0])*60*60 + int(alarme[1])*60 + int(alarme[2])
                
                listeIntervalles.append((freq,marge,alarme))
        ficIntervalles.close()
    else:
        logger.error("Execution stop because 'intervalles.conf' was not found.")
        sys.exit()
        
    return listeIntervalles
                
if __name__ == "__main__":
    
    parser,options,args = commandLineParser()
    
    #Au moment de l'implementation, le code source du module 'Logger' avait ete modifie sur le serveur utilise afin 
    #d'enlever la posibilite d'utiliser l'option de rotation des logs par date. J'ai donc du utiliser la rotation
    #utilisant l'espace fichier (en bytes). 
    logger = Logger('/apps/px/sundew/pxFreq/log/pxFreq.log', 'INFO', "pxFreqLog", bytes=1000000) # Enable logging
    logger = logger.getLogger()
    
    logger.info("Updating data base for "+options.cluster+" cluster ...")
    
    logsFile = openLogsFile()
    
    #Lire les fichiers de configuration
    listeRegex = lireRegex()
    listeIntervalles = lireIntervalles()
    
    dataBase = {}
    #Parsing des fichiers log
    i = 1
    j = len(logsFile)
    for fic in logsFile:
        afficher("("+str(i)+"/"+str(j)+") "+"Mise a jour de la BD avec "+str(fic[0])+" ...")
        #Mise a jour de la BD
        updateDB(fic)
        i += 1
    
    #Trouver la frequence des produits
    afficher("Trouver les frequences ...")
    trouverFrequences()
    
    #Lire la DB pour en sortir un fichier texte
    afficher("Creation du fichier de sortie " + options.cluster + ".db ...")
    
    #Acceleration des acces a la BD
    sparsify(dataBase)
    
    ficSortie = openFile("/apps/px/sundew/pxFreq/data/"+options.cluster+".db","w")
    
    for entree in dataBase:
        
        sourceListe = []
        for src in dataBase[entree][0]:
            sourceListe.append(src+"="+dataBase[entree][2][src][1])    
        
        sources = str(sourceListe).replace(" ","").replace("'","")
        clients = str(list(dataBase[entree][1])).replace(" ","").replace("'","")
        
        ficSortie.write(entree + " " + sources + " " + clients + "\n")
        
    logger.info("End of updating data base for "+options.cluster+" cluster")
