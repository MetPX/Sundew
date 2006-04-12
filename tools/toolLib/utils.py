"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

###############################################
#
# Divers outils utiles pour Python
#
# Par: Louis-Philippe Theriault
#      Stagiaire, CMC
#
###############################################
import sys
import os
import commands
import time
import imp

def sendmail(to, msg, subject='(Aucun sujet)',header='',footer=''):
	"""Envoie un mail en utilisant la commande sendmail.
	   Les arguments doivent etre des strings."""
	
	# Init du sendmail
	SENDMAILPATH = '/usr/sbin/sendmail'
	sendmail = os.popen("%s -t" % SENDMAILPATH, "w")
	sendmail.write("To: " + to + "\n")
	sendmail.write("Subject: "+ subject + "\n")
	sendmail.write("\n")
	
	sendmail.write(header)
	
	sendmail.write(msg)
	
	sendmail.write(footer)

	sendmail.close()
 
def lireFicTexte(path):
	"""Retourne une liste contenant toutes les lignes d'un fichier texte,
	   qui est ouvert en ecriture, puis ferme le fichier.
	   
	   Le fichier doit etre suffisament petit pour entrer completement
	   dans le buffer."""
	if os.access(path,os.R_OK):
		f = open(path,'r')
		lignes = f.readlines()
		f.close
		return lignes
	else:
		raise IOError

def parseTextBracket(lignes):
	"""Prends en entree une liste contenant les lignes d'un texte.
	
	   Retourne une liste contenant des listes des lignes, le delimiteur
	   est '{' et '}'"""
	set = []
	   
	for l in lignes:
		if '#' not in l:
			if '{' in l:
				subset = list()
			elif '}' in l:
				set.append(subset)

			subset.append(l)

	return set	

def getMapFicOuv(listeFichiers, pathPrefixe="", maxFic=10, mode=os.O_RDONLY):
	"""Prends une liste de string qui pointent sur des fichiers,
	   qui seront ouvert et retournes dans un map.Le nombre maximum
	   de fichiers ouverts en meme temps est defini par maxFic.

	   Les modes permis sont:
		O_RDONLY
		O_WRONLY
		O_RDWR
		O_NDELAY
		O_NONBLOCK
		O_APPEND
		O_DSYNC
		O_RSYNC
		O_SYNC
		O_NOCTTY
		O_CREAT
		O_EXCL
		O_TRUNC

	   

	   cles:

	   'path'
	   'fileDesc'
	   'nom'

	   Le pathPrefixe sera ajoute au debut du nom du fichier s'il
	   est fourni.
	"""
	if pathPrefixe != "" and pathPrefixe[:-1] != '/':
		pathPrefixe = pathPrefixe + '/'	

	mapFile = {}
	nb_fichiers_ouv = 0

	while len(listeFichiers) > 0 and nb_fichiers_ouv < maxFic:
		nomFichier = listeFichiers.pop(0)

		try:
			mapFile[nomFichier] = {}
			mapFile[nomFichier]['fileDesc'] = os.open(pathPrefixe + nomFichier, mode)
			mapFile[nomFichier]['path'] = pathPrefixe
			mapFile[nomFichier]['nom'] = nomFichier
			nb_fichiers_ouv = nb_fichiers_ouv + 1
		except OSError:
			# C'etait un repertoire
			del(mapFile[nomFichier])

	return mapFile

def testAccess(listeTests):
	"""Leve une exception Exception('uDef',<parametre>) si le parametre est introuvable.

	   Les elements de la liste sont des fichiers/repertoires de tuples avec comme premier
	   arguments le path, et comme 2e l'acces a tester, selon ce qui est fourni avec le
	   module os.

	   os.X_OK	# Execution
	   os.R_OK	# Lecture
	   os.W_OK	# Ecriture
	   os.F_OK	# Existence"""

	for couple in listeTests:
		if couple[0] != None and not os.access(couple[0],couple[1]):
			raise Exception('uDef',couple[0])

def writeLog(filePointer,msg,sync=False,prefixeLogOn=True):
	"""Ecrit le message (suivi d'un retour de ligne dans le fichier.

	   Le fichier doit avoir ete ouvert avec os.open. Sync force
	   une ecriture physique, utile si un message critique"""
	if prefixeLogOn:
		os.write(filePointer,prefixeLog() + msg + '\n')
	else:
		os.write(filePointer,msg + '\n')

	if sync:
		os.fsync(filePointer)

def prefixeLog():
	"""Retourne l'heure du systeme avec le nom de la machine.

	   A etre insere avant le message du log."""
	return time.strftime('%x - %X') + ' (' + os.uname()[1].split('.')[0] + ') : '

def initLog(pathLog,pathOldLog='',intro=''):
	"""Copie le log present sur le disque (s'il y a lieu) vers une copie,
	   ou vers un vieu log.

	   Retourne un pointeur vers le nouveau log (ouvert par <os>)."""

	if os.access(pathLog,os.F_OK):
		if pathOldLog != '':
			os.rename(pathLog,pathOldLog)
		else:
			os.rename(pathLog,pathLog + '.oldLog')

	commands.getoutput('touch ' + pathLog)
	log = os.open(pathLog, os.O_WRONLY)
	
	if intro != '':
		os.write(log,intro)
	else:
		os.write(log,prefixeLog() + "Debut du programme...\n")

	return log

def normalizePath(path):
	"""Retourne path avec un '/' s'il est manquant"""
	if path != '' and path[-1] != '/':
		path = path + '/'

	return path

def stripFileList(fileList,pathPrefix='',sizeMax=1024):
	"""Prends une liste de string pointant sur des fichiers,
	   et retourne une liste avec l'addition des grosseurs des fichiers
	   retournes inferieures a sizeMax."""
	pathPrefix = normalizePath(pathPrefix)
	fileListRet = []
	curSize = 0

	for fichier in fileList:
		curSize = curSize + os.stat(pathPrefix + fichier)[6]
		if curSize >= sizeMax:
			break

		fileListRet.append(fichier)

	if len(fileList) > 0 and len(fileListRet) == 0:
		fileListRet = fileList[1]

	return fileListRet

def listSubstract( list1 , list2 ):
	"""Effectue une operation de soustraction sur 2 listes.

	   ex: [2,3,4] - [3,4,5] = [2,5]"""
	list1copie = list1
	list2copie = list2

	for elem in list2copie:
		try:
			pos = list1copie.index(elem)
		
			list1copie.pop(pos)
		except:
			pass

	return list1copie

def loadPythonConfigFile(pathCfg=sys.argv[min(1,len(sys.argv)-1)]):
        """Lecture du fichier de configuration du programme"""
        if len(sys.argv) >= 2:

                try:
                        fic_cfg = open(pathCfg,'r')
                        config = imp.load_source('config','/dev/null',fic_cfg)
                        fic_cfg.close()
                        return config
                except IOError:
                        print "*** Erreur: Fichier de configuration inexistant, erreur fatale!"
                        sys.exit(-1)
        else:
                print "*** Erreur: Aucun fichier de config en entree, erreur fatale !\n" + \
                      "            Le chemin du fichier doit etre le chemin complet"
                sys.exit(-1)

