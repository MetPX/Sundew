#!/usr/bin/python

"""
    pxRoute

    Description:
        Mise a jour de la table de routage pour un client ou pour un alias

    Documentation: doc_pxRoute.txt
        
    Auteur: David Nantel
    Mise a jour: 18 Dec. 2007
    Version: 1.4
"""

from pxRouteLanguage import Language

import sys, re, os, shutil, dircache
from time import strftime,ctime
from optparse import OptionParser,OptionGroup
from sets import *

##########################################################
# Fonctions et methodes pour la gestion du script
##########################################################

def commandLineParser():
    """
        Gestion des options lors de l'appel du script
        
        Retour: (parser, options, args)
    """
    version = os.path.basename(sys.argv[0])+" 1.4 - David Nantel - 18 Dec. 2007"
    parser = OptionParser(usage=lang.usage, description=lang.description, add_help_option=False)
    
    groupeFichiers = OptionGroup(parser, lang.groupeFichiersTitre, lang.groupeFichiersDescription)
                                
    groupeModes = OptionGroup(parser, lang.groupeModesTitre, lang.groupeModesDescription)
    
    parser.add_option("--version",
                      action="store_true",dest="version", default=False,
                      help=lang.optVersionHelp)
    
    parser.add_option("-h", "--help",
                      action="help",
                      help=lang.optHelpHelp)
                      
    parser.add_option("-u", "--undo",
                      action="store_true",dest="undo",default=False,
                      help=lang.optUndoHelp)
                      
    groupeFichiers.add_option("-r", "--routing",
                      action="store", dest="routage", default="pxRouting.conf",
                      help=lang.optRoutingHelp)
                      
    groupeFichiers.add_option("-b", "--bulletins",
                      action="store", dest="bulletins",
                      help=lang.optBulletinsHelp)
    
    groupeModes.add_option("-m", "--mode", #Cette option est obligatoire
                      action="store", dest="mode",
                      choices=[lang.choixModeAppend,lang.choixModeRemove,lang.choixModeRenew,lang.choixModeFind],
                      help=lang.optModeHelp)                      
                                        
    parser.add_option("-f", "--force",
                      action="store_true", dest="force", default=False,
                      help=lang.optForceHelp)
    
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help=lang.optQuietHelp)
                      
    parser.add_option("-i", "--invert",
                      action="store_true", dest="invert", default=False,
                      help=lang.optInvertHelp)
                      
    parser.add_option("-t", "--test",
                      action="store_true", dest="test", default=False,
                      help=lang.optTestHelp)
                      
    parser.add_option_group(groupeModes)
    parser.add_option_group(groupeFichiers)
    
    (options, args) = parser.parse_args()
    
    
    #Test des options et arguments entrees pour etre sur qu'il n'y ai pas d'incoherence    
    if(options.version):
        print version
        sys.exit()
            
    
    if len(args) != 1 and options.undo == False:
        parser.error(lang.argsError)
    elif options.undo == True and len(args) != 0:
        parser.error(lang.argsErrorUndo)
    
    if(not(options.mode) and not(options.undo)):
        parser.error(lang.modeError)
    
    if(not(options.undo) and (options.mode == lang.choixModeAppend or options.mode == lang.choixModeRenew)):
        if(not(options.bulletins)):
            parser.error(lang.optBulletinsMissing)
            
    if(not(options.undo) and options.mode == lang.choixModeFind and options.bulletins):
        parser.error(lang.optBulletinsProhibited)
        
    if(options.invert and not options.bulletins):
        parser.error(lang.optInvertError)
    
    return (parser, options, args)

def afficher(st=""):
    """
        Affichage si dans le mode 'verbose': l'option '-v' (par defaut).
        L'option '-q' (quiet) empeche cette affichage de ce produire.
        
        Entree: Texte a afficher
    """
    if(options.verbose): print st

def demanderChoix():
    """
        Affiche la question (Oui/Non) et demande la reponse au clavier
        Les reponses acceptees sont : o, n, oui et non (la case n'est pas sensible)
        
        Retour: Vrai si la reponse et positive (o,oui)
    """
    choix = ""
    while choix != 'OUI' and choix != 'NON' and choix !='O' and choix !='N' and choix != 'YES' and choix != 'Y' and choix != 'NO':
        print "(%s/%s)" %(lang.yes,lang.no),
        choix = raw_input()
        choix = choix.upper()
    
    if(choix == "OUI" or choix == "YES" or choix == "O" or choix == "Y"):
        return True
    else:
        return False

##########################################################
# Fonctions et methodes pour la gestion de fichiers
##########################################################

def backup(nomFic):
    """
        Sauvegarde du fichier (si existant) dans les repertoires correspondant a la date et a l'heure courante
        
        Entree: chemin et nom du fichier a sauvegarder
    """
    global execTime,execDate
    
    if(os.path.exists(".output/")):
        if(not os.path.exists(".output/"+execDate)):
            os.mkdir(".output/"+execDate)
    else:
        os.mkdir(".output")
        os.mkdir(".output/"+execDate)
        
    #Creation du repertoire de backup
    if(not os.path.exists(".output/"+execDate+"/"+execTime)):
        os.mkdir(".output/"+execDate+"/"+execTime)
    
    #transfert du fichier dans le backup
    if(nomFic == options.routage):
        #Copy
        shutil.copy(options.routage,".output/"+execDate+"/"+execTime+"/")
        #afficher(lang.backup + ": " + nomFic + " -> output/"+execDate+"/"+execTime+"/")
        
    elif(os.path.exists(nomFic)):
        #move
        shutil.move(nomFic, ".output/"+execDate+"/"+execTime+"/")
        #afficher(lang.backup + ": " + nomFic + " -> output/"+execDate+"/"+execTime+"/")
    
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
        parser.error(fileOpenError + "%s\n" % (nomFic))
        
    return fic

    
def sortirFichierTableRoutageMAJ(listeLignes):
    """
        Ecriture de la table de routage mise a jour dans un fichier.
        
        Entree: Liste de ligne correspondant a la table de routage
    """
    #Backup du fichier de routage
    shutil.copy(options.routage, options.routage+".bak")
    
    ficSortie = ouvrirFichier(options.routage,"w")
    for ligne in listeLignes:
        ficSortie.write(ligne)
    ficSortie.close()
    afficher(lang.output + ": " + options.routage)
    
def annulerModiffication():
    """
        Annule la derniere modification effectuer avec le script pxRoute
    """
    afficher(lang.recovery)
    if(os.path.exists(options.routage + ".bak")):
        afficher(lang.lastModification + ctime(os.path.getmtime(options.routage + ".bak")))
        shutil.move(options.routage+".bak", options.routage)
    else:
        print lang.undoError
    
##########################################################
# Fonctions et methodes pour la manipulation de donnees
##########################################################

def extraireInfoTableRoutage(listeLignes):
    """
        Extraction de l'information utile du fichier de la table de routage.
        
        Entree: liste contenant les lignes du fichier de la table de routage
        Retour: Dictionnaire -> cle=Alias et def=liste de clients/alias
                Dictionnaire -> cle=Bulletin et def=liste de clients/alias
    """
    dictAlias = {}      #Dictionnaire : cle=Alias et def=liste de clients/alias
    dictBulletins = {}  #Dictionnaire : cle=Bulletin et def=liste de clients/alias
    for ligne in listeLignes:
        ligne = ligne.strip().split()
        if(len(ligne)>0 and (ligne[0] == "clientAlias" or ligne[0] == "key")):
            if(ligne[0] == 'key'):
                # Ajouter ce bulletin a la liste
                if(len(ligne) == 3):
                    #Pas de client = Reserved
                    dictBulletins[ligne[1]+" (Reserved)"] = []
                else:
                    dictBulletins[ligne[1]] = ligne[2].strip().split(",")
            elif(ligne[0] == 'clientAlias'):
                # Ajouter cette alias a la liste
                if(len(ligne) == 2):
                    #Pas de client
                    dictAlias[ligne[1]] = []
                else:
                    dictAlias[ligne[1]] = ligne[2].strip().split(",")
    return (dictBulletins,dictAlias)
                
def extraireClientsEtAlias(dictBulletins,dictAlias):
    """
        Extraction des noms de clients et des noms d'alias
        
        Entree: dictionnaire des bulletins:liste de clients/alias
                dictionnaire des alias:liste de clients/alias 
        Retour: Liste des client actifs et des alias actifs
    """
    listeAlias = dictAlias.keys()
    listeClient = []
    for alias in dictAlias.keys():
        for abonne in dictAlias[alias]:
            if(abonne not in listeAlias and abonne not in listeClient):
                listeClient.append(abonne)
    for bulletin in dictBulletins.keys():
        for abonne in dictBulletins[bulletin]:
            if(abonne not in listeAlias and abonne not in listeClient):
                listeClient.append(abonne)
                
    return (listeClient, listeAlias)

def trouverGroupes(nom,dictAlias):
    """
        Recherche des groupes auxquels le client/alias est abonnes
        Les sous-groupes doivent etres trouver egalement
        
        Entree: le nom du client/alias et le dictionnaire alias:liste de clients/alias
        Retour: Liste des groupes que le client/alias est abonnes
    """
    setGroupes = Set()
    for alias in dictAlias.keys():
            if(nom in dictAlias[alias]):
                setGroupes.add(alias)
                
    change = True
    while(change):
        change = False
        for clef in dictAlias.keys():
            if(len(setGroupes.intersection(dictAlias[clef]))>0):
                if(clef not in setGroupes):
                    setGroupes.add(clef)
                    change = True
                                
                                
                                
    return list(setGroupes)
            
def trouverPossibilites(st,listeBulletins):
    """
        Tente une completion de nom sur une entree comportant le caractere '*'.
        Si aucun resultat, une liste vide est retournee.
        
        Entree: le nom a completer et la liste de reference
        Retour: la liste des resultats de la completion
    """
    resultat = []
    test = st.replace('*','.*')
    p = re.compile( test+"$" )
    for entree in listeBulletins:
        if(p.match(entree)):
            resultat.append(entree)
    return resultat

def trouverNonValide(listeBulletinsOfficiels, listeBulletins):
    """
        Classification des bulletins dans 2 listes distinctes : valide et non-valide.
        Les entrees valide sont ceux qui se retrouve dans la liste de bulletins officiels.
        Les entrees non-valide sont le complement des entrees valide. Une raison de refus est associee
        a chaque entree non-valide
        
        Entree: la liste de bulletins de la table de routage et la liste de bulletins du fichier bulletins
        Retour: la liste valide et la liste non-valide
    """
    valide = []
    nonValide = []
    for ligne in listeBulletins:
        #Formater l'entree
        ligne = ligne.strip()
        if(not ligneCommentaire(ligne) and not ligneVide(ligne)):
            #faire le formatage de l'entree
            #  les retour de ligne sont supprimes
            #  et les espaces entre les mots sont remplaces par '_'
            p = re.compile(r'\n')
            q = re.compile(r'( +)')
            bull = p.sub('', ligne)
            bull = q.sub('_', bull)
        else:
            continue
                
        if (bull in listeBulletinsOfficiels):
            #Format valide et dans la liste de la table de routage
            if(bull in valide):
                #Deja dans la liste des valide alors on fait rien
                pass
            elif(re.compile(r'[a-zA-Z]{4}[0-9]{2}_CWAO[0-9]+').match(bull)):
                #interdiction sur les bulletins terminant par "_CWAOxx"
                nonValide.append((ligne,lang.forbidden+"-> _CWAOxx"))
            else:
                valide.append(bull)

        elif (bull.find('*') != -1):
            #Presence du caractere '*' representant la completion de nom
            poss = trouverPossibilites(bull,listeBulletinsOfficiels)
            possibilite = []
            for t in poss:
                if (t not in valide):
                    possibilite.append(t)
            if(len(possibilite)==0 and len(poss)!=0):
                nonValide.append((ligne,lang.double))
            elif(len(possibilite) > 0):
                #valide.extend(possibilite)
                for p in possibilite:
                    if(re.compile(r'[a-zA-Z0-9_]* \(Reserved\)').match(p)):
                        nonValide.append((p.split(" (Reserved)")[0],lang.reserved))
                    elif(p not in valide):
                        valide.append(p)
            else:
                nonValide.append((ligne,lang.noExtension))

        else:
            if(bull+" (Reserved)" in listeBulletinsOfficiels):
                nonValide.append((ligne,lang.reserved))
            #Format non valide ou pas dans la table de routage
            elif(re.compile(r'[a-zA-Z]{4}[0-9]{2}_[a-zA-Z]{4}').match(bull)):
                nonValide.append((ligne,lang.notInTable))
            else:
                nonValide.append((ligne,lang.invalidFormat))
    
    return valide, nonValide

def inverserListe(listeBulletinsOfficiels, listeValide):
    """
        Traitement pour avoir la liste des bulletins qui ne sont PAS dans la liste valide 
    """
    listInverse = []
    
    for bull in listeBulletinsOfficiels:
        if(bull not in listeValide):
            if(re.compile(r'[a-zA-Z0-9_]* \(Reserved\)').match(bull)):
                pass
            else:
                listInverse.append(bull)
                
    return listInverse
            
def trouverListeInscriptions(nom,dictBulletinsOfficiels):
    """
        Trouve une liste de bulletins auxquels le client/alias est inscrit
        
        Entree: Un nom de client/alias et un dictionnaire -> clef:bulletins reff:liste de clients/alias
        Retour: la liste des buletins que le client/alias est inscrit
    """
    listeInscriptions = []
    for bulletin in dictBulletinsOfficiels.keys():
        if(nom in dictBulletinsOfficiels[bulletin]):
            listeInscriptions.append(bulletin)
    return listeInscriptions
            
def removeSansListe(nom,tableRoutage):
    """
        Desinscrit completement un client ou un alias a tous les groupes et a tous les bulletins de la table de routage.

        Entree: nom du client/alias et la table de routage
        Retour: la table de routage modifiee
    """
    tableRoutageSortie = []
    
    #Ces varaibles sont utiliser lors d'une supression d'un alias. Il va de soit qu'il faut transferer les abonnes
    # du groupe vers les inscriptions auxquels ils etaient inscrit.
    isAlias = False
    listeDesinscription = []
    listeAlias = []
    listeAbonneAlias = []
    
    for ligne in tableRoutage:
        if(len(ligne.strip())>0 and ligne.strip()[0] != "#"):
        
            ligne = ligne.strip().split()
            if(len(ligne)>0 and ligne[0] == "clientAlias"):
                if(nom == ligne[1]):
                    isAlias = True
                    if(len(ligne)>2):
                        #Sauvegarde des clients abonnes a ce groupe
                        setNoms = Set(ligne[2].strip().split(","))
                        listeAbonneAlias.extend(list(setNoms))
                    #Le continue fait en sorte que la ligne ne sera pas reecrite dans la nouvelle table de routage, donc supression de la ligne
                    continue
                
                if(len(ligne) == 3):
                    setNoms = Set(ligne[2].strip().split(","))
                    if(nom in setNoms):
                        setNoms.discard(nom)
                        listeAlias.append(ligne[1])
                        
                    listeNoms = list(setNoms)
                    listeNoms.sort()
                    strNoms = ",".join(listeNoms)
                    ligne[2] = strNoms
                    
                
            elif(len(ligne)>0 and ligne[0] == "key"):
                
                if(len(ligne) == 4):
                    setNoms = Set(ligne[2].strip().split(","))
                    if(isAlias and nom in setNoms):
                        #Inscription des clients qui etais abonnes au groupe
                        listeNoms = list(setNoms)
                        listeNoms.extend(listeAbonneAlias)
                        setNoms = Set(listeNoms)
                    
                    if(nom in setNoms or len(Set(listeAlias).intersection(setNoms))>0):
                        setNoms.discard(nom)
                        listeDesinscription.append(ligne[1])
                    
                    listeNoms = list(setNoms)
                    listeNoms.sort()
                    strNoms = ",".join(listeNoms)
                    ligne[2] = strNoms
                    
            ligne = " ".join(ligne)
            ligne = ligne + "\n"
        tableRoutageSortie.append(ligne)
    return tableRoutageSortie, listeAlias, listeDesinscription

def removeAvecListe(nom,tableRoutage,listeRetrait):
    """
        Desinscrit un client ou un alias a tous les bulletins present dans le fichier 'bulletins'.
        
        Entree: nom du client/alias, la table de routage et la liste de bulletin a retirer
        Sortie: la table de routage modifiee, le nombre de buletins et de groupes desinscrit
                et le nombre d'inscription avant et apres les modifications
    """
    tableRoutageSortie = []
    setGroupes = Set()
    dictGroupes = {}
    listeDesinscription = []
    nbRetirer = 0
    nbTotalAvant = 0
    firstTime = True
    
    for ligne in tableRoutage:
        if(len(ligne.strip())>0 and ligne.strip()[0] != "#"):
            ligne = ligne.strip().split()
            
            if(len(ligne)>0 and ligne[0] == "clientAlias"):
                
                if(len(ligne) == 3):
                    setNoms = Set(ligne[2].strip().split(","))
                    dictGroupes[ligne[1]] = setNoms
                    if(nom in setNoms):
                        setNoms.discard(nom)
                        setGroupes.add(ligne[1])
                    
                    listeNoms = list(setNoms)
                    listeNoms.sort()
                    strNoms = ",".join(listeNoms)
                    ligne[2] = strNoms
            
            elif(len(ligne)>0 and ligne[0] == "key"):
                if(firstTime):
                    change = True
                    while(change):
                        change = False
                        for clef in dictGroupes.keys():
                            if(len(setGroupes.intersection(dictGroupes[clef]))>0):
                                if(clef not in setGroupes):
                                    setGroupes.add(clef)
                                    change = True
                    firstTime = False
                if(len(ligne) == 4):
                    setNoms = Set(ligne[2].strip().split(","))
                    if(nom in setNoms or len(setGroupes.intersection(setNoms))>0):
                        nbTotalAvant += 1
                        
                    if(ligne[1] in listeRetrait and (nom in setNoms or len(setGroupes.intersection(setNoms))>0)):
                        nbRetirer += 1
                        listeDesinscription.append(ligne[1])
                        setNoms.discard(nom)
                    elif(len(setGroupes.intersection(setNoms))>0):
                        setNoms.add(nom)
                    
                    listeNoms = list(setNoms)
                    listeNoms.sort()
                    strNoms = ",".join(listeNoms)
                    ligne[2] = strNoms
                    
            ligne = " ".join(ligne)
            ligne = ligne + "\n"
        tableRoutageSortie.append(ligne)
        
    nbTotalApres = nbTotalAvant - nbRetirer
    return tableRoutageSortie,nbTotalAvant,nbTotalApres,listeDesinscription,list(setGroupes)

def appendAvecListe(nom,tableRoutage,listeAjout):
    """
        Ajoute les inscriptions d'un client/alias aux bulletins indiques dans la liste d'ajout
        
        Entree: nom du client/alias, la table de routage et la liste de bulletin a ajouter
        Sortie: la table de routage modifiee, le nombre d'ajout effectue, le nombre total
                d'inscription avant et apres les modifications
    """
    tableRoutageSortie = []
    dictGroupes = {}
    setGroupes = Set()
    listeInscriptions = []
    nbAjouter = 0
    nbTotalAvant = 0
    firstTime = True
    
    for ligne in tableRoutage:
        if(len(ligne.strip())>0 and ligne.strip()[0] != "#"):
            ligne = ligne.strip().split()
            
            if(len(ligne)>0 and ligne[0] == "clientAlias"):
                if(len(ligne) == 3):
                    setNoms = Set(ligne[2].strip().split(","))
                    dictGroupes[ligne[1]] = setNoms
                    if(nom in setNoms):
                        setGroupes.add(ligne[1])
                    listeNoms = list(setNoms)
                    listeNoms.sort()
                    strNoms = ",".join(listeNoms)
                    ligne[2] = strNoms
                        
            elif(len(ligne)>0 and ligne[0] == "key"):
                if(firstTime):
                    change = True
                    while(change):
                        change = False
                        for clef in dictGroupes.keys():
                            if(len(setGroupes.intersection(dictGroupes[clef]))>0):
                                if(clef not in setGroupes):
                                    setGroupes.add(clef)
                                    change = True
                    firstTime = False
                if(len(ligne) == 4):
                    setNoms = Set(ligne[2].strip().split(","))
                    if(nom in setNoms or len(setGroupes.intersection(setNoms))>0):
                        nbTotalAvant += 1
                    if(ligne[1] in listeAjout):    
                        if(nom not in setNoms and len(setGroupes.intersection(setNoms))==0):
                            nbAjouter += 1
                            listeInscriptions.append(ligne[1])
                            setNoms.add(nom)
                    listeNoms = list(setNoms)
                    listeNoms.sort()
                    strNoms = ",".join(listeNoms)
                    ligne[2] = strNoms
                        
            ligne = " ".join(ligne)
            ligne = ligne + "\n"
        tableRoutageSortie.append(ligne)
        
    nbTotalApres = nbTotalAvant + nbAjouter
    return tableRoutageSortie,nbTotalAvant,nbTotalApres,listeInscriptions

def renewAvecListe(nom,tableRoutage,listeNew):
    """
        Renouvellement des inscriptions du clien/alias avec les bulletins presents dans 'listeNew'
        
        Entree: nom du client/alias, la table de routage et la liste de bulletin a renouveller
        Sortie: la table de routage modifiee, le nombre d'ajout et de retrait effectue, le nombre total
                d'inscription avant et apres les modifications
    """
    
    tableRoutageSortie = []
    setGroupes = Set()
    dictGroupes = {}
    listeAjouter = []
    listeRetirer = []
    nbTotalAvant = 0
    firstTime = True
    
    for ligne in tableRoutage:
        if(len(ligne.strip())>0 and ligne.strip()[0] != "#"):
            ligne = ligne.strip().split()
            
            if(len(ligne)>0 and ligne[0] == "clientAlias"):
                if(len(ligne) == 3):
                    setNoms = Set(ligne[2].split(','))
                    dictGroupes[ligne[1]] = setNoms
                    if(nom in setNoms):
                        setNoms.discard(nom)
                        setGroupes.add(ligne[1])
                    listeNoms = list(setNoms)
                    listeNoms.sort()
                    strNoms = ",".join(listeNoms)
                    ligne[2] = strNoms
                
            elif(len(ligne)>0 and ligne[0] == "key"):
                if(firstTime):
                    change = True
                    while(change):
                        change = False
                        for clef in dictGroupes.keys():
                            if(len(setGroupes.intersection(dictGroupes[clef]))>0):
                                if(clef not in setGroupes):
                                    setGroupes.add(clef)
                                    change = True
                    firstTime = False
                    
                if(len(ligne) == 4):
                    setNoms = Set(ligne[2].split(','))
                    if(nom in setNoms or len(setGroupes.intersection(setNoms))>0):
                        nbTotalAvant += 1
                    if(ligne[1] in listeNew):
                        if(nom not in setNoms and len(setGroupes.intersection(setNoms))==0):
                            listeAjouter.append(ligne[1])
                        setNoms.add(nom)
                    elif(nom in setNoms or len(setGroupes.intersection(setNoms))>0):
                        setNoms.discard(nom)
                        listeRetirer.append(ligne[1])
                    listeNoms = list(setNoms)
                    listeNoms.sort()
                    strNoms = ",".join(listeNoms)
                    ligne[2] = strNoms
            
            ligne = " ".join(ligne)
            ligne = ligne + "\n"
        tableRoutageSortie.append(ligne)
    nbTotalApres = nbTotalAvant - len(listeRetirer) + len(listeAjouter)
    return tableRoutageSortie,listeAjouter,listeRetirer,nbTotalAvant,nbTotalApres,list(setGroupes)
            

                
##########################################################
# Autres outils
##########################################################
        
def ligneCommentaire(ligne):
    """
        Verifie si la ligne est une ligne en commentaire (Caractere '#' en debut de ligne)
        
        Entree: une ligne de texte
        Sortie: Vrai si la ligne est un commentaire
    """
    retour = False
    ligne = ligne.strip()
    if(ligne != ""):
        if(ligne[0] == "#"):
            retour = True
    return retour

def ligneVide(ligne):
    """
        Verifie si la ligne est une ligne vide
        
        Entree: une ligne de texte
        Sortie: Vrai si la ligne est vide
    """
    retour = False
    if(ligne == ""):
        retour = True
    return retour

##########################################################
# Fonctions principales (MODES)
##########################################################

def modeAppend():
    global tableRoutage, listeValide, typeNom
    
    if(typeNom == None):
        if(options.test):
            print lang.clientNotExistTest
            print
            typeNom = "client"
        else:
            print lang.clientNotExistQuestion,
            if(demanderChoix()):
                typeNom = "client"
    if(typeNom):
        afficher(lang.modificationCalcul)
        tableRoutage,nbTotalAvant,nbTotalApres,listeInscriptions = appendAvecListe(nom,tableRoutage,listeValide)
        listeInscriptions.sort()
        
        if(options.test):
            afficher()
            print lang.testAddInscription
            if(typeNom == "alias"):
                print "ALIAS :", nom
            else:
                print "CLIENT :", nom
            print
            print lang.beforeModification + ":",nbTotalAvant,lang.bulletinsSubscription
            print
            print lang.subscription + ":", len(listeInscriptions), lang.newBulletins
            for bull in listeInscriptions:
                print bull
            print
            print lang.afterModification + ":", nbTotalApres, lang.bulletinsSubscription
            
                
        else:
            #Sauvegarde du fichier avec toutes les informations detaillees
            #backup(".output/details.txt")
            
            #Construction d'un fichier avec toutes les informations detaillees
            #ficInfo = ouvrirFichier(".output/details.txt","w")
            #ficInfo.write(lang.addSubscription + "\n\n")
            #if(typeNom == "alias"):
            #    ficInfo.write("ALIAS : " + nom + "\n")
            #else:
            #    ficInfo.write("CLIENT : " + nom + "\n")
            #    
            #ficInfo.write("\n" + lang.beforeModification + ": " + str(nbTotalAvant) + " " + lang.bulletinsSubscription + "\n")
            #ficInfo.write("\n" + lang.subscription + ": " + str(len(listeInscriptions)) + " " + lang.newBulletins + "\n")
            #for i in listeInscriptions:
            #    ficInfo.write(i + "\n")
            #ficInfo.write("\n" + lang.afterModification + ": " + str(nbTotalApres) + " " + lang.bulletinsSubscription + "\n")
            #
            #ficInfo.close()
            #afficher(lang.output + ": output/details.txt")    
            
            if(options.force):
                if(len(listeInscriptions) == 0):
                    print lang.noModificationToDo
                else:
                    #Sauvegarde du fichier de configuration de la table de routage
                    #backup(options.routage)
                    #Effectuer les changements dans le fichier de sortie
                    sortirFichierTableRoutageMAJ(tableRoutage)
            else:
                print     lang.warning
                if(typeNom == "alias"):
                    print "* ALIAS :", nom
                else:
                    print "* CLIENT :", nom
                print     "* " + lang.beforeModification + ":", nbTotalAvant, lang.bulletinsSubscription
                print     "* " + lang.subscription + ":", len(listeInscriptions), lang.newBulletins
                print     "* " + lang.afterModification + ":", nbTotalApres, lang.bulletinsSubscription
                print     "***************************************************************"
                if(len(listeInscriptions) == 0):
                    print lang.noModificationToDo
                else:
                    print lang.confirm,
                    if(demanderChoix()):
                        #Sauvegarde du fichier de configuration de la table de routage
                        #backup(options.routage)
                        #Effectuer les changements dans le fichier de sortie
                        sortirFichierTableRoutageMAJ(tableRoutage)

    else:
        parser.error(lang.nameNotClientOrAliasError)
        
def modeRemove():
    global tableRoutage, listeValide

    #Si l'option '-b' n'est pas utilise, alors on efface tout
    if(not options.bulletins):
        if(typeNom):
            afficher(lang.modificationCalcul)
            tableRoutage,listeAlias,listeDesinscription = removeSansListe(nom,tableRoutage)
            listeDesinscription.sort()
            listeAlias.sort()
            
            if(options.test):
                afficher()
                print lang.testCancelInscription
                if(typeNom == "alias"):
                    print "ALIAS :", nom
                    print
                    print lang.totalSupressAlias
                    print
                    print lang.cancellationSubscription + ":", len(listeDesinscription), "BULLETIN(S)"
                    for bull in listeDesinscription:
                        print bull
                    print
                    print lang.cancellationSubscription + ":", len(listeAlias), "ALIAS"
                    for alias in listeAlias:
                        print alias
                    print
                    print lang.individuallyRegistered
                else:
                    print "CLIENT :", nom
                    print
                    print lang.totalSupressClient
                    print
                    print lang.cancellationSubscription + ":", len(listeDesinscription), "BULLETIN(S)"
                    for bull in listeDesinscription:
                        print bull
                    print
                    print lang.cancellationSubscription + ":", len(listeAlias), "ALIAS"
                    for alias in listeAlias:
                        print alias
                        
                    
            else:
            
                #Sauvegarde du fichier avec toutes les informations detaillees
                #backup(".output/details.txt")
                
                #Construction d'un fichier avec toutes les informations detaillees
                #ficInfo = ouvrirFichier(".output/details.txt","w")
                #ficInfo.write(lang.totalSupress + "\n\n")
                #if(typeNom == "alias"):
                #    ficInfo.write("ALIAS : " + nom + "\n")
                #else:
                #    ficInfo.write("CLIENT : " + nom + "\n")
                #ficInfo.write("\n" + lang.cancellationSubscription + ": " + str(len(listeDesinscription)) + " BULLETIN(S)\n")
                #for i in listeDesinscription:
                #    ficInfo.write(i + "\n")
                #ficInfo.write("\n" + lang.cancellationSubscription + ": " + str(len(listeAlias)) + " ALIAS\n")
                #for i in listeAlias:
                #    ficInfo.write(i + "\n")
                #ficInfo.close()
                #afficher(lang.output + ": output/details.txt")
                
                if(options.force):
                    if(len(listeDesinscription) == 0):
                        print lang.noModificationToDo
                    else:
                        #Sauvegarde du fichier de configuration de la table de routage
                        #backup(options.routage)
                        #Effectuer les changements dans le fichier de sortie
                        sortirFichierTableRoutageMAJ(tableRoutage)
                else:
                    print     lang.warning
                    if(typeNom == "alias"):
                        print "* ALIAS :", nom
                        print "* " + lang.totalSupressAlias
                        print "* " + lang.cancellationSubscription + ":", len(listeDesinscription), "BULLETIN(S)"
                        print "* " + lang.cancellationSubscription + " (ALIAS):", listeAlias 
                        print "* " + lang.individuallyRegistered
                        print     "***************************************************************"
                    else:
                        print "* CLIENT :", nom
                        print "* " + lang.totalSupressClient
                        print "* " + lang.cancellationSubscription + ":", len(listeDesinscription), "BULLETIN(S)"
                        print "* " + lang.cancellationSubscription + " (ALIAS):", listeAlias
                        print     "***************************************************************"
                    if(len(listeDesinscription) == 0):
                        print lang.noModificationToDo
                    else:
                        print lang.confirm,
                        if(demanderChoix()):
                            #Sauvegarde du fichier de configuration de la table de routage
                            #backup(options.routage)
                            #Effectuer les changements dans le fichier de sortie
                            sortirFichierTableRoutageMAJ(tableRoutage)
        else:
            parser.error(lang.nameNotClientOrAliasError)

    #Si l'option '-b' est utilise, on efface seulement les entrees specifiees        
    else:
        if(typeNom):
            afficher(lang.modificationCalcul)
            tableRoutage,nbTotalAvant,nbTotalApres,listeDesinscription,listeGroupes = removeAvecListe(nom,tableRoutage,listeValide)
            listeDesinscription.sort()
            listeGroupes.sort()
            
            if(options.test):
                afficher()
                print lang.testCancelInscription
                if(typeNom == "alias"):
                    print "ALIAS :", nom
                else:
                    print "CLIENT :", nom
                print
                print lang.beforeModification + ":",nbTotalAvant,lang.bulletinsSubscription
                print
                print lang.cancellationSubscription + ":", len(listeDesinscription), "BULLETIN(S)"
                for bull in listeDesinscription:
                    print bull
                print
                print lang.cancellationSubscription + ":", len(listeGroupes), "ALIAS"
                for alias in listeGroupes:
                    print alias
                print
                print lang.afterModification + ":", nbTotalApres, lang.bulletinsSubscription
            
            else:
                #Sauvegarde du fichier avec toutes les informations detaillees
                #backup(".output/details.txt")
                
                #Construction d'un fichier avec toutes les informations detaillees
                #ficInfo = ouvrirFichier(".output/details.txt","w")
                #ficInfo.write(lang.cancelInscription + "\n\n")
                #if(typeNom == "alias"):
                #    ficInfo.write("ALIAS : " + nom + "\n")
                #else:
                #    ficInfo.write("CLIENT : " + nom + "\n")
                #ficInfo.write("\n" + lang.beforeModification + ": " + str(nbTotalAvant) + " " + lang.bulletinsSubscription + "\n")
                #ficInfo.write("\n" + lang.cancellationSubscription + ": " + str(len(listeDesinscription)) + " BULLETIN(S)\n")
                #for i in listeDesinscription:
                #    ficInfo.write(i + "\n")
                #ficInfo.write("\n" + lang.cancellationSubscription + ": " + str(len(listeGroupes)) + " ALIAS\n")
                #for i in listeGroupes:
                #    ficInfo.write(i + "\n")
                #ficInfo.write("\n" + lang.afterModification + ": " + str(nbTotalApres) + " " + lang.bulletinsSubscription + "\n")
                #ficInfo.close()
                #afficher(lang.output + ": output/details.txt")
                        
                if(options.force):
                    if(len(listeDesinscription) == 0):
                        print lang.noModificationToDo
                    else:
                        #Sauvegarde du fichier de configuration de la table de routage
                        #backup(options.routage)
                        #Effectuer les changements dans le fichier de sortie
                        sortirFichierTableRoutageMAJ(tableRoutage)
                else:
                    print lang.warning
                    if(typeNom == "alias"):
                        print "* ALIAS :", nom
                    else:
                        print "* CLIENT :", nom
                    print     "* " + lang.beforeModification + ":", nbTotalAvant, lang.bulletinsSubscription
                    print     "* " + lang.cancellationSubscription + ":", len(listeDesinscription), "BULLETIN(S)"
                    print     "* " + lang.cancellationSubscription + " (ALIAS):", listeGroupes
                    print     "* " + lang.afterModification + ":", nbTotalApres, lang.bulletinsSubscription
                    print     "***************************************************************"
                    if(len(listeDesinscription) == 0):
                        print lang.noModificationToDo
                    else:
                        print     lang.confirm,
                        if(demanderChoix()):
                            #Sauvegarde du fichier de configuration de la table de routage
                            #backup(options.routage)
                            #Effectuer les changements dans le fichier de sortie
                            sortirFichierTableRoutageMAJ(tableRoutage)
            
        else:
            parser.error(lang.nameNotClientOrAliasError)
                        
def modeRenew():
    global tableRoutage, listeValide, typeNom
    
    if(typeNom == None):
        if(options.test):
            print lang.clientNotExistTest
            print
            typeNom = "client"
        else:
            print lang.clientNotExistQuestion,
            if(demanderChoix()):
                typeNom = "client"
    if(typeNom):
        afficher(lang.modificationCalcul)
        tableRoutage,listeAjouter,listeRetirer,nbTotalAvant,nbTotalApres,listeGroupes = renewAvecListe(nom,tableRoutage,listeValide)
        listeAjouter.sort()
        listeRetirer.sort()
        
        if(options.test):
            afficher()
            print lang.testRenewInscription
            if(typeNom == "alias"):
                print "ALIAS :", nom
            else:
                print "CLIENT :", nom
            print
            print lang.beforeModification + ":",nbTotalAvant,lang.bulletinsSubscription
            print
            print lang.subscription + ":", len(listeAjouter), lang.newBulletins
            for bull in listeAjouter:
                print bull
            print
            print lang.cancellationSubscription + ":", len(listeRetirer), "BULLETIN(S)"
            for bull in listeRetirer:
                print bull
            print
            print lang.cancellationSubscription + ":", len(listeGroupes), "ALIAS"
            for alias in listeGroupes:
                print alias
            print
            print lang.afterModification + ":", nbTotalApres, lang.bulletinsSubscription
            
            
        else:
            #Sauvegarde du fichier avec toutes les informations detaillees
            #backup(".output/details.txt")
            
            #Construction d'un fichier avec toutes les informations detaillees
            
            #ficInfo = ouvrirFichier(".output/details.txt","w")
            #ficInfo.write(lang.subscriptionRenew + "\n\n")
            #if(typeNom == "alias"):
            #    ficInfo.write("ALIAS : " + nom + "\n")
            #else:
            #    ficInfo.write("CLIENT : " + nom + "\n")
            #ficInfo.write("\n" + lang.beforeModification + ": " + str(nbTotalAvant) + " " + lang.bulletinsSubscription + "\n")
            #ficInfo.write("\n" + lang.subscription + ": " + str(len(listeAjouter)) + " " + lang.newBulletins + "\n")
            #for i in listeAjouter:
            #    ficInfo.write(i + "\n")
            #ficInfo.write("\n" + lang.cancellationSubscription + ": " + str(len(listeRetirer)) + " BULLETIN(S)\n")
            #for i in listeRetirer:
            #    ficInfo.write(i + "\n")
            #ficInfo.write("\n" + lang.cancellationSubscription + ": " + str(len(listeGroupes)) + " ALIAS\n")
            #for i in listeGroupes:
            #    ficInfo.write(i + "\n")
            #ficInfo.write("\n" + lang.afterModification + ": " + str(nbTotalApres) + " " + lang.bulletinsSubscription + "\n")
            #    
            #ficInfo.close()
            #afficher(lang.output + ": output/details.txt")
            
            if(options.force):
                if(len(listeAjouter) == 0 and len(listeRetirer) == 0):
                    print lang.noModificationToDo
                else:
                    #Sauvegarde du fichier de configuration de la table de routage
                    #backup(options.routage)
                    #Effectuer les changements dans le fichier de sortie
                    sortirFichierTableRoutageMAJ(tableRoutage)
            else:
                print     lang.warning
                if(typeNom == "alias"):
                    print "* ALIAS :", nom
                else:
                    print "* CLIENT :", nom
                print     "* " + lang.beforeModification + ":", nbTotalAvant, lang.bulletinsSubscription
                print     "* " + lang.subscription + ":", len(listeAjouter), lang.newBulletins
                print     "* " + lang.cancellationSubscription + ":", len(listeRetirer), "BULLETIN(S)"
                print     "* " + lang.cancellationSubscription + " (ALIAS):", listeGroupes
                print     "* " + lang.afterModification + ":", nbTotalApres, lang.bulletinsSubscription
                print     "***************************************************************"
                if(len(listeAjouter) == 0 and len(listeRetirer) == 0):
                    print lang.noModificationToDo
                else:
                    print lang.confirm,
                    if(demanderChoix()):
                        #Sauvegarde du fichier de configuration de la table de routage
                        #backup(options.routage)
                        #Effectuer les changements dans le fichier de sortie
                        sortirFichierTableRoutageMAJ(tableRoutage)
    else:
        parser.error(lang.nameNotClientOrAliasError)

def modeFind():
    
    if(typeNom):
        #Trouver la liste des abonnements de "nom" incluant les groupes (alias)
        #pour chaque groupe inscrit, sortir les abonnement de ce groupe
        listeGroupes = trouverGroupes(nom,dictAliasOfficiels)
        listeAbonnements = []
        listeInscription = trouverListeInscriptions(nom, dictBulletinsOfficiels)
        listeAbonnements.extend(trouverListeInscriptions(nom, dictBulletinsOfficiels))
        
        for gr in listeGroupes:
            for tempo in trouverListeInscriptions(gr, dictBulletinsOfficiels):
                if(tempo not in listeAbonnements):
                    listeAbonnements.append(tempo)
        
        listeAbonnements.sort()
        
        if(typeNom == "alias"):
            listeClientInscritGroupe = dictAliasOfficiels[nom]
            listeClientInscritGroupe.sort()
            
            print "ALIAS :", nom
            
            if(len(listeGroupes)>0):
                print "\n" + lang.groupListAlias + "\n"
                for groupe in listeGroupes:
                    print groupe
                    
            print "\n" + lang.clientListAlias + "\n"
            if(len(listeClientInscritGroupe)>0):
                for client in listeClientInscritGroupe:
                    print client
            else:
                print lang.noAliasSubscriber
            
            print "\n" + lang.listBulletinsIntendForGroup + "\n"
            if(len(listeAbonnements)>0):
                for bull in listeAbonnements:
                    print bull
            else:
                print "\n" + lang.noSubscriptionFor, nom, "(", typeNom, ")"
                    
        elif(typeNom == "client"):
            print "CLIENT :", nom
            
            if(len(listeGroupes)>0):
                print "\n" + lang.groupListClient + "\n"
                for groupe in listeGroupes:
                    print groupe
            
            print "\n" + lang.listBulletinsIntendForClient + "\n"
            if(len(listeAbonnements)>0):
                for bull in listeAbonnements:
                    print bull
            else:
                print "\n" + lang.noSubscriptionFor, nom, "(", typeNom, ")"
    
    elif(nom == '?'):
        listeClients.sort()
        listeAlias.sort()
        print "\n" + lang.aliasList + "\n"
        for alias in listeAlias:
            print alias
        
        print "\n" + lang.clientList + "\n"
        for client in listeClients:
            print client
                
    elif(nom == '+'):
        listeBulletins = dictBulletinsOfficiels.keys()
        listeBulletins.sort()
        
        print "\n" + lang.allBulletinsList + "\n"
        for bull in listeBulletins:
            print bull
            
    else:
        parser.error(lang.nameNotClientOrAliasError)

##########################################################
# Corps principal du script
##########################################################
            
def main():
    global nom,typeNom
    global listeClients,listeAlias
    global dictBulletinsOfficiels, dictAliasOfficiels
    global tableRoutage, listeValide
    
    nom = args[0]
    
    #Ouverture du fichier de la table de routage
    afficher(lang.openAndRead + " " + options.routage + " ...")
    ficTableRoutage = ouvrirFichier(options.routage, "r")
    
    #Lecture du fichier de la table de routage
    tableRoutage = ficTableRoutage.readlines()
    ficTableRoutage.close()
    
    #Extraction des infos de la table de routage
    dictBulletinsOfficiels, dictAliasOfficiels = extraireInfoTableRoutage(tableRoutage)
    listeBulletinsOfficiels = dictBulletinsOfficiels.keys()
    listeClients, listeAlias = extraireClientsEtAlias(dictBulletinsOfficiels,dictAliasOfficiels)
    
    #Recherche du type (alias ou client) du "nom"
    if(nom in listeAlias):
        typeNom = "alias"
    elif(nom in listeClients):
        typeNom = "client"
    else:
        typeNom = None
    
    if(options.bulletins):
        #Ouverture du fichier bulletins
        afficher(lang.openAndRead + " " + options.bulletins + " ...")
        ficBulletins = ouvrirFichier(options.bulletins, "r")
        
        #Lecture du fichier bulletins
        listeBulletinsOptionel = ficBulletins.readlines()
        ficBulletins.close()
        
        #Recherche des entrees non valides et valides du fichier bulletins
        afficher(lang.findInvalidEntries)
        listeValide, listeNonValide = trouverNonValide(listeBulletinsOfficiels, listeBulletinsOptionel)
        
        if(options.invert):
            #Inverser la liste des bulletins valide
            afficher(lang.invertValidEntries)
            listeValide = inverserListe(listeBulletinsOfficiels, listeValide)
            
        # Mettre en ordre la liste non-valide pour regrouper les raisons de refus
        listeNonValide.sort(lambda x, y: cmp(x[1],y[1]))
        
        
        if(options.test):
            afficher()
            print len(listeValide),lang.validEntries
            for bull in listeValide:
                print bull
            print
            print len(listeNonValide),lang.invalidEntries
            for bull in listeNonValide:
                print "%-25s %s" %(bull[0],bull[1])
            print
        
        else:
            afficher(str(len(listeValide)) + " " + lang.validEntries)
            afficher(str(len(listeNonValide)) + " " + lang.invalidEntries)
        
            #backup('.output/entreesValides.txt')
            #backup('.output/entreesNonValides.txt')
        
            #if(len(listeValide)>0):
            #    #----------- Fichier de sortie -------------------------------------------------------------------
            #    ficInter = ouvrirFichier('.output/entreesValides.txt','w')
            #    ficInter.write("\n" + lang.validBuletinsList + "\n")
            #    for st in listeValide:
            #        ficInter.write(st + '\n')
            #    ficInter.close()
            #    #afficher(lang.output + ": output/entreesValides.txt")
            #    #-------------------------------------------------------------------------------------------------
            #    
            #if(len(listeNonValide)>0):
            #    #----------- Fichier de sortie -------------------------------------------------------------------
            #    ficNonValide = ouvrirFichier('.output/entreesNonValides.txt','w')
            #    ficNonValide.write("\n" + lang.nonvalidBuletinsList + "\n")
            #    for st in listeNonValide:
            #        tempo = "%-25s %s\n" %(st[0],st[1])
            #        ficNonValide.write(tempo)
            #    ficNonValide.close()
            #    #afficher(lang.output + ': output/entreesNonValides.txt')
            #    #-------------------------------------------------------------------------------------------------
        
        if(len(listeValide) == 0):
            parser.error(lang.noValidEntries)
            
    repartition = {lang.choixModeAppend: modeAppend,
                   lang.choixModeRemove: modeRemove,
                   lang.choixModeRenew: modeRenew,
                   lang.choixModeFind: modeFind }
    
    repartition[options.mode]()

if __name__ == "__main__":
    execTime = strftime("%H-%M-%S")
    execDate = strftime("%Y-%m-%d")
    
    #Test de la langue avec la variable d'environnement PXROUTE_LANGUAGE
    lang = Language()
    parser,options,args = commandLineParser()
    
    if(options.undo):
        annulerModiffication()
        sys.exit()
    
    main()
    
