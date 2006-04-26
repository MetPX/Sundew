# -*- coding: UTF-8 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""        
#############################################################################################
# Name: bulletinManager.py
#
# Authors: Louis-Philippe Thériault
#         
# Date: Octobre 2004 
#       
#
# Description: Gestionnaire de bulletins
#
#
# Revision History: 
#   2005-10-01  NSD         Adding collection capability.
#
#############################################################################################
"""
import math, re, string, os, bulletinPlain, traceback, sys, time
import PXPaths

from CollectionManager import CollectionManager
import bulletinAm
import bulletinWmo

PXPaths.normalPaths()

__version__ = '2.0'

class bulletinManagerException(Exception):
    pass

class bulletinManager:
    """Manipulates bulletins as entities.  Does not modify contents.
       Bulletin Managers take care of reading bulletins from and writing them
       to disk.

       pathTemp             path
           - Required, must be on the same file system as pathSource/pathDest.

       pathSource           path
           - Directory from which bulletins are read (if necessary.)

       pathDest             path
           - Directory to which bulletins are written.
             (only needed if use_pds=true)

       mapEnteteDelai       map

            - maps bulletin headers to valid reception times.

                   the elements are tuples, 
                       -- element[0] is number of max. minutes before the hour, 
                       -- element[1] is number of max. minutes after the hour.

                       -- Set the map to None to turn off header validity checking.

                    sample: mapEnteteDelai = { 'CA':(5,20),'WO':(20,40)}

       SMHeaderFormat       Bool

            - if true, Add a line "AAXX jjhh4\\n" to SM/SI bulletins.

       ficCollection        path
        
            - Collection configuration file.
                Set to None to deactivate message collection.

       pathFichierCircuit   path
             - The routing table.  (Header2circuit.conf)
             - set to None to disable. 

       maxCompteur          Int
             - Maximum number before rollover of unique numbers in file names.


    """

    def __init__(self,
            pathTemp,
            logger,
            pathSource=None,
            pathDest=None,
            maxCompteur=99999, \
            lineSeparator='\n',
            extension=':',
            pathFichierCircuit=None,
            mapEnteteDelai=None,
            use_pds=0,
            source=None):

        self.logger = logger
        self.pathSource = self.__normalizePath(pathSource)
        self.pathDest = self.__normalizePath(pathDest)
        self.pathTemp = self.__normalizePath(pathTemp)
        self.maxCompteur = maxCompteur
        # FIXME: this should be read from a config file, haven't understood enough yet.
        self.use_pds = use_pds
        self.compteur = 0
        self.extension = extension
        self.lineSeparator = lineSeparator
        self.mapEnteteDelai = mapEnteteDelai
        self.source = source

        #map du contenu de bulletins en format brut
        #associe a leur arborescence absolue
        self.mapBulletinsBruts = {}

        # Init du map des circuits
        self.initMapCircuit(pathFichierCircuit)

        # Collection regex
        self.regex = re.compile(r'SACN|SICN|SMCN')

        #-----------------------------------------------------------------------------------------
        # Create a collection manager if collections are enabled.
        #-----------------------------------------------------------------------------------------
        if self.source.collection:
            self.collectionManager = CollectionManager(self.source.ingestor.collector, self.logger)

    def effacerFichier(self,nomFichier):
        try:
            os.remove(nomFichier)
        except:
            self.logger.error("(BulletinManager.effacerFichier(): Erreur d'effacement d'un bulletin)")
            raise

    def writeBulletinToDisk(self,unRawBulletin,compteur=True,includeError=True):
        """writeBulletinToDisk(bulletin [,compteur,includeError])

           unRawBulletin        String

                     - unRawBulletin is a string, instantiated
                       as a bulletin before it is written to disk 
                     - modifications to the contents are done via a
                       unObjetBulletin.doSpecificProcessing() call
                       before writing.

           compteur             Bool

                     - If true, include counter in file name.

           includeError         Bool

                     - If true, and the bulletin is problematic, prepend
                       the bulletin data with a diagnostic message.

        """
        
        if self.pathDest == None:
            raise bulletinManagerException("opération impossible, pathDest n'est pas fourni")

        if self.compteur > self.maxCompteur:
            self.compteur = 0

        self.compteur += 1
        
        unBulletin = self.__generateBulletin(unRawBulletin)
        unBulletin.doSpecificProcessing()

        # Vérification du temps d'arrivée
        self.verifyDelay(unBulletin)

        # Génération du nom du fichier
        nomFichier = self.getFileName(unBulletin,compteur=compteur)
        if not self.use_pds:
            nomFichier = nomFichier + ':' + time.strftime( "%Y%m%d%H%M%S", time.gmtime(time.time()) )

        tempNom = self.pathTemp + nomFichier
        try:
            unFichier = os.open( tempNom , os.O_CREAT | os.O_WRONLY )

        except (OSError,TypeError), e:
            # Le nom du fichier est invalide, génération d'un nouveau nom

            self.logger.warning("Manipulation du fichier impossible! (Ecriture avec un nom non standard)")
            self.logger.error("Exception: " + ''.join(traceback.format_exception(Exception,e,sys.exc_traceback)))

            nomFichier = self.getFileName(unBulletin,error=True,compteur=compteur)
            tempNom = self.pathTemp + nomFichier
            unFichier = os.open( tempNom, os.O_CREAT | os.O_WRONLY )
        
        os.write( unFichier , unBulletin.getBulletin(includeError=includeError) )
        os.close( unFichier )
        os.chmod(tempNom,0644)

        if self.use_pds:
            pathDest = self.getFinalPath(unBulletin)

            if not os.access(pathDest,os.F_OK):
                os.mkdir(pathDest, 0755)

            os.rename( tempNom , pathDest + nomFichier )
            self.logger.info("Ecriture du fichier <%s>",pathDest + nomFichier)
        else:
            entete = ' '.join(unBulletin.getHeader().split()[:2])

            # MG use filename for Pattern File Matching from source ...  (As Proposed by DL )
            if self.source.patternMatching:
                if not self.source.fileMatchMask(nomFichier) :
                    self.logger.warning("Bulletin file rejected because of RX mask: " + nomFichier)
                    os.unlink(tempNom)
                    return

                """
                transfo = self.source.getTransformation(nomFichier)
                if transfo:
                    newNames = Transformations.transfo(tempNom)

                    for name in newNames:
                        self.source.ingestor.ingest()
                """

            if self.mapCircuits.has_key(entete):
                clist = self.mapCircuits[entete]['routing_groups']
            else:
                clist = []

            if self.source.clientsPatternMatching:
                clist = self.source.ingestor.getMatchingClientNamesFromMasks(nomFichier, clist)

            #fet.directIngest( nomFichier, clist, tempNom, self.logger )
            self.source.ingestor.ingest(tempNom, nomFichier, clist)

            #-----------------------------------------------------------------------------------------
            # Collecting the report if collection is turned on and transmitting the collection 
            # bulletin if necessary.  Note that the collectReport(tempNom) function returns an
            # object of the class BulletinCollection and from it we extract the raw bulletin
            #-----------------------------------------------------------------------------------------
            if self.source.collection and self.regex.search(nomFichier):
                collectionBulletin = self.collectionManager.collectReport(tempNom)
                if collectionBulletin:
                    rawBull = collectionBulletin.bulletinAsString()
                    originalExtension = self.extension
                    self.extension = self.extension.replace('Direct', 'Collected')
                    self._writeBulletinToDisk(rawBull) 
                    self.extension = originalExtension
                    #-----------------------------------------------------------------------------------------
                    # At this point the collection bulletin has been ingested and queued for transmission
                    # within the _writeBulletinToDisk method above.
                    # From the viewpoint of the collection module, the collection bulletin has been sent
                    # and we now need to mark it as such in the ../collection/ temporary db.
                    #-----------------------------------------------------------------------------------------
                    self.collectionManager.markCollectionAsSent(collectionBulletin)
            os.unlink(tempNom)

    def _writeBulletinToDisk(self,unRawBulletin,compteur=True,includeError=True):
        
        if self.pathDest == None:
            raise bulletinManagerException("opération impossible, pathDest n'est pas fourni")

        if self.compteur > self.maxCompteur:
            self.compteur = 0

        self.compteur += 1

        unBulletin = self.__generateBulletin(unRawBulletin)
        unBulletin.doSpecificProcessing()

        # Vérification du temps d'arrivée
        self.verifyDelay(unBulletin)

        # Génération du nom du fichier
        nomFichier = self.getFileName(unBulletin,compteur=compteur)
        if not self.use_pds:
            nomFichier = nomFichier + ':' + time.strftime( "%Y%m%d%H%M%S", time.gmtime(time.time()) )

        tempNom = self.pathTemp + nomFichier
        try:
            unFichier = os.open( tempNom , os.O_CREAT | os.O_WRONLY )

        except (OSError,TypeError), e:
            # Le nom du fichier est invalide, génération d'un nouveau nom

            self.logger.warning("Manipulation du fichier impossible! (Ecriture avec un nom non standard)")
            self.logger.error("Exception: " + ''.join(traceback.format_exception(Exception,e,sys.exc_traceback)))

            nomFichier = self.getFileName(unBulletin,error=True,compteur=compteur)
            tempNom = self.pathTemp + nomFichier
            unFichier = os.open( tempNom, os.O_CREAT | os.O_WRONLY )

        os.write( unFichier , unBulletin.getBulletin(includeError=includeError) )
        os.close( unFichier )
        os.chmod(tempNom,0644)

        if self.use_pds:
            pathDest = self.getFinalPath(unBulletin)

            if not os.access(pathDest,os.F_OK):
                os.mkdir(pathDest, 0755)

            os.rename( tempNom , pathDest + nomFichier )
            self.logger.info("Ecriture du fichier <%s>",pathDest + nomFichier)
        else:
            entete = ' '.join(unBulletin.getHeader().split()[:2])

            # MG use filename for Pattern File Matching from source ...  (As Proposed by DL )
            if self.source.patternMatching:
                if not self.source.fileMatchMask(nomFichier) :
                    self.logger.warning("Bulletin file rejected because of RX mask: " + nomFichier)
                    os.unlink(tempNom)
                    return

                """
                transfo = self.source.getTransformation(nomFichier)
                if transfo:
                    newNames = Transformations.transfo(tempNom)

                    for name in newNames:
                        self.source.ingestor.ingest()
                """

            if self.mapCircuits.has_key(entete):
                clist = self.mapCircuits[entete]['routing_groups']
            else:
                clist = []

            if self.source.clientsPatternMatching:
                clist = self.source.ingestor.getMatchingClientNamesFromMasks(nomFichier, clist)

            #fet.directIngest( nomFichier, clist, tempNom, self.logger )
            self.source.ingestor.ingest(tempNom, nomFichier, clist)

            os.unlink(tempNom)

    def __generateBulletin(self,rawBulletin):
        """__generateBulletin(rawBulletin) -> objetBulletin

           Retourne un objetBulletin d'à partir d'un bulletin
           "brut".

        """
        return bulletinPlain.bulletinPlain(rawBulletin,self.logger,self.lineSeparator)

    def getListeNomsFichiersAbsolus(self):
        return self.mapBulletinsBruts.keys()

    def __normalizePath(self,path):
        """normalizePath(path) -> path

           Retourne un path avec un '/' à la fin
        """

        if path != None:
            if path != '' and path[-1] != '/':
                path = path + '/'

        return path

    def createWhatFn(self,bulletin,compteur=True ):
        """createWhatFn(bulletin[,compteur]) -> whatfn

           Return the first token of the filename. Build out of the
           bulletin header, the station (if defined) and a counter
           the WHATFN should looked like (if all the informations needed
           are available)

           SACN31_CWAO_121435_RRA_CYUL_045440 

           Missing info are going to be left empty
           possible outcome are :

           SACN31_CWAO_121435__CYUL_045440
           SACN31_CWAO_121435_CCA__045440


        """

        # header : 1- get header from bulletin
        #          2- must be alphanumeric
        #          3- consider an empty BBB to add an '_'

        header = bulletin.getHeader()
        if (header.replace(' ','')).isalnum() :
           parts  = header.split()
           header = header.replace(' ','_')
           if len(parts) < 4 : header = header + '_'
        else :
           header = None

        # station name :  1- bulletin header must be good
        #                 2- get station from bulletin
        #                 3- must be alphanumeric
        #                 4- station in WhatFn is conditional to some bulletin type
        #                    bulletinAm      always have the station name in the WhatFn (if found)
        #                    bulletinWmo     SRCN40 have the station name in the WhatFn (if found)
        #                    bulletin-file ? SRCN40 have the station name in the WhatFn (if found)
        #                    collector       Don't place station in the filename

        station = ''
        if header != None :
           if not (self.source.type == 'collector'):
              station = bulletin.getStation()
           if station == None       : station = ''
           if not station.isalnum() : station = ''
           if not isinstance(bulletin, bulletinAm.bulletinAm) :
	      if not (bulletin.getHeader())[:6] in ["SRCN40","SXCN40","SRMT60"] : station = ''
           
        # adding a counter to the file name insure its uniqueness

        strCompteur = ''
        if compteur :
           strCompteur = string.zfill(self.compteur, len(str(self.maxCompteur)))

        # correct header if needed

        if header == None : header = 'UNPRINTABLE_HEADER'

        # whatfn

        whatfn = header + '_' + station + '_' + strCompteur

        return whatfn


    def getFileName(self,bulletin,error=False, compteur=True ):
        """getFileName(bulletin[,error, compteur]) -> fileName

           Retourne le nom du fichier pour le bulletin. Si error
           est à True, c'est que le bulletin a tenté d'être écrit
           et qu'il y a des caractère "illégaux" dans le nom,
           un nom de fichier "safe" est retourné. Si le bulletin semble être
           correct mais que le nom du fichier ne peut être généré,
           les champs sont mis à ERROR dans l'extension.

           Si compteur est à False, le compteur n'est pas inséré
           dans le nom de fichier.

           Utilisation:

                Générer le nom du fichier pour le bulletin concerné.
        """

        # whatfn
        whatfn = self.createWhatFn(bulletin,compteur)

        if bulletin.getError() == None and not error:

        # Bulletin normal
            try:
                return  whatfn + self.getExtension(bulletin,error).replace(' ','_')

            except Exception, e:
                # Une erreur est détectée (probablement dans l'extension) et le nom est généré avec des erreurs
                # Si le compteur n'a pas été calculé, c'est que le bulletin était correct,
                # mais si on est ici dans le code, c'est qu'il y a eu une erreur.

                self.logger.warning(e)
                whatfn = self.createWhatFn(bulletin,compteur)
                return 'PROBLEM_BULLETIN_' + whatfn + self.getExtension(bulletin,error=True).replace(' ','_')

        elif bulletin.getError() != None and not error:
            self.logger.warning("Le bulletin est erronné " + bulletin.getError()[0] )
            return 'PROBLEM_BULLETIN_' + whatfn + self.getExtension(bulletin,error=True).replace(' ','_')
        else:
            self.logger.warning("L'entête n'est pas imprimable" )
            return ('PROBLEM_BULLETIN ' + 'UNPRINTABLE HEADER ' + self.getExtension(bulletin,error)).replace(' ','_')

    def getExtension(self,bulletin,error=False):
        """getExtension(bulletin) -> extension

           Retourne l'extension à donner au bulletin. Si error est à True,
           les champs 'dynamiques' sont mis à 'PROBLEM'.

           -TT:         Type du bulletin (2 premieres lettres)
           -CCCC:       Origine du bulletin (2e champ dans l'entête
           -CIRCUIT:    Liste des circuits, séparés par des points,
                        précédés de la priorité.

           Exceptions possibles:
                bulletinManagerException:       Si l'extension ne peut être générée
                                                correctement et qu'il n'y avait pas
                                                d'erreur à l'origine.

           Utilisation:

                Générer la portion extension du nom du fichier.
        """
        newExtension = self.extension

        if not error and bulletin.getError() == None:
            newExtension = newExtension.replace('-TT',bulletin.getType())\
                                       .replace('-CCCC',bulletin.getOrigin())

            if self.mapCircuits != None:
            # Si les circuits sont activés
            # NB: Lève une exception si l'entête est introuvable
                newExtension = newExtension.replace('-CIRCUIT',self.getCircuitList(bulletin))

            return newExtension
        else:
            # Une erreur est détectée dans le bulletin
            newExtension = newExtension.replace('-TT','PROBLEM')\
                                       .replace('-CCCC','PROBLEM')\
                                       .replace('-CIRCUIT','PROBLEM')

            return newExtension

    def lireFicTexte(self,pathFic):
        """
           lireFicTexte(pathFic) -> liste des lignes

           pathFic:        String
                           - Chemin d'accès vers le fichier texte

           liste des lignes:       [str]
                                   - Liste des lignes du fichier texte

        Utilisation:

                Retourner les lignes d'un fichier, utile pour lire les petites
                databases dans un fichier ou les fichiers de config.
        """
        if os.access(pathFic,os.R_OK):
            f = open(pathFic,'r')
            lignes = f.readlines()
            f.close
            return lignes
        else:
            raise IOError

    def reloadMapCircuit(self,pathHeader2circuit):
        """reloadMapCircuit(pathHeader2circuit)

           pathHeader2circuit:  String
                                - Chemin d'accès vers le fichier de circuits


           Recharge le fichier de mapCircuits.

           Utilisation:

                Rechargement lors d'un SIGHUP.
        """
        oldMapCircuits = self.mapCircuits

        try:

            self.initMapCircuit(pathHeader2circuit)

            self.logger.info("Succès du rechargement du fichier de Circuits")

        except Exception, e:

            self.mapCircuits = oldMapCircuits

            self.logger.warning("bulletinManager.reloadMapCircuit(): Échec du rechargement du fichier de Circuits")

            raise


    def initMapCircuit(self,pathHeader2circuit):
        """initMapCircuit(pathHeader2circuit)

           pathHeader2circuit:  String
                                - Chemin d'accès vers le fichier de circuits

           Charge le fichier de header2circuit et assigne un map avec comme cle
           champs:
                'routing_groups' -- list of clients to which the messages 
'                priority'       -- priority to assign to the message.

           FIXME: Peter a fixé le chemin a /apps/px/etc/header2circuit.conf
                donc le parametre choisi simplement si on s´en sert ou pas.
        """
        if pathHeader2circuit == None:
        # Si l'option est à OFF
            self.mapCircuits = None
            return

        self.mapCircuits = {}

        # Test d'existence du fichier
        try:
            pathHeader2circuit = PXPaths.ETC + 'header2client.conf'

            fic = os.open( pathHeader2circuit, os.O_RDONLY )
        except Exception:
            raise bulletinManagerException('Impossible d\'ouvrir le fichier d\'entetes ' + pathHeader2circuit + ' (fichier inaccessible)' )

        lignes = os.read(fic,os.stat(pathHeader2circuit)[6])

        #self.logger.info("Validating header2client.conf, clients:" + string.join(self.source.ingestor.clientNames))
        bogus=[]
        routable=[] # sub group of the clients, only ones for which we can route bulletins
        for ligne in lignes.splitlines():
            uneLigneSplitee = ligne.split(':')
            ahl = uneLigneSplitee[0]
            self.mapCircuits[uneLigneSplitee[0]] = {}
            try:
                self.mapCircuits[ahl] = {}
                self.mapCircuits[ahl]['entete'] = ahl
                self.mapCircuits[ahl]['routing_groups'] = ahl
                self.mapCircuits[ahl]['priority'] = uneLigneSplitee[2]
                gs=[]
                for g in uneLigneSplitee[1].split() :
                    #if g in fet.clients.keys():
                    if g in self.source.ingestor.clientNames:
                        gs = gs + [ g ]
                        if g not in routable: routable.append(g)
                    else:
                        if g not in bogus:
                            bogus = bogus + [ g ]
                            #self.logger.warning("client (%s) invalide, ignorée ", g )
                            self.logger.warning("Client '%s' is in header2client.conf but inexistant in px", g )
                self.mapCircuits[ahl]['routing_groups'] =  gs
                
            except IndexError:
                raise bulletinManagerException('Les champs ne concordent pas dans le fichier header2circuit',ligne)
        self.logger.info("From header2client.conf we learn that we can route bulletins to: %s" % routable)

    def getMapCircuits(self):
        """getMapCircuits() -> mapCircuits

           À utiliser pour que plusieurs instances utilisant la même
           map.
        """
        return self.mapCircuits

    def setMapCircuits(self,mapCircuits):
        """setMapCircuits(mapCircuits)

           À utiliser pour que plusieurs instances utilisant la même
           map.
        """
        self.mapCircuits = mapCircuits

    def getCircuitList(self,bulletin):
        """circuitRename(bulletin) -> Circuits

           bulletin:    Objet bulletin

           Circuits:    String
                        -Circuits formattés correctement pour êtres insérés dans l'extension

           Retourne la liste des circuits pour le bulletin précédés de la priorité, pour être inséré
           dans l'extension.

              Exceptions possibles:
                   bulletinManagerException:       Si l'entête ne peut être trouvée dans le
                                                   fichier de circuits
        """
        if self.mapCircuits == None:
            raise bulletinManagerException("Le mapCircuit n'est pas chargé")

        entete = ' '.join(bulletin.getHeader().split()[:2])

        if not self.mapCircuits.has_key(entete):
            bulletin.setError('Entete +' +entete+ ' non trouvée dans fichier de circuits')
            raise bulletinManagerException('Entete non trouvée dans fichier de circuits')

        # Check ici, si ce n'est pas une liste, en faire une liste
        if not type(self.mapCircuits[entete]['routing_groups']) == list:
            self.mapCircuits[entete]['routing_groups'] = [ self.mapCircuits[entete]['routing_groups'] ]

        if self.use_pds:
            return self.mapCircuits[entete]['priority'] + '.' + '.'.join(self.mapCircuits[entete]['routing_groups']) + '.'
        else:
            return self.mapCircuits[entete]['priority']

    def getFinalPath(self,bulletin):
        """getFinalPath(bulletin) -> path

           path         String
                        - Répertoire où le fichier sera écrit

           bulletin     objet bulletin
                        - Pour aller chercher l'entête du bulletin

           Utilisation:

                Pour générer le path final où le bulletin sera écrit. Génère
                le répertoire incluant la priorité.
        """
        # Si le bulletin est erronné
        if bulletin.getError() != None:
            return self.pathDest.replace('-PRIORITY','PROBLEM')

        try:
            entete = ' '.join(bulletin.getHeader().split()[:2])
        except Exception:
            self.logger.error("Entête non standard, priorité impossible à déterminer(%s)",bulletin.getHeader())
            return self.pathDest.replace('-PRIORITY','PROBLEM')

        if self.mapCircuits != None:
            # Si le circuitage est activé
            if not self.mapCircuits.has_key(entete):
                    # Entête est introuvable
                self.logger.error("Entête introuvable, priorité impossible à déterminer")
                return self.pathDest.replace('-PRIORITY','PROBLEM')

            return self.pathDest.replace('-PRIORITY',self.mapCircuits[entete]['priority'])
        else:
            return self.pathDest.replace('-PRIORITY','NONIMPLANTE')

    def getPathSource(self):
        """getPathSource() -> Path_source

           Path_source:         String
                                -Path source que contient le manager
        """
        return self.pathSource

    def verifyDelay(self,unBulletin):
        """verifyDelay(unBulletin)

           Vérifie que le bulletin est bien dans les délais (si l'option
           de délais est activée). Flag le bulletin en erreur si le delai
           n'est pas respecté.

           Ne peut vérifier le délai que si self.mapEnteteDelai n'est
           pas à None.

           Utilisation:

                Pouvoir vérifier qu'un bulletin soit dans les délais
                acceptables.
        """
        if (self.mapEnteteDelai == None):
            return

        now = time.strftime("%d%H%M",time.localtime())

        try:
            bullTime = unBulletin.getHeader().split()[2]
            header = unBulletin.getHeader()

            minimum,maximum = None,None

            for k in self.mapEnteteDelai.keys():
            # Fetch de l'intervalle valide dans le map
                if k == header[:len(k)]:
                    (minimum,maximum) = self.mapEnteteDelai[k]
                    break

            if minimum == None:
            # Si le cas n'est pas défini, considéré comme correct
                return

        except Exception:
            unBulletin.setError('Découpage d\'entête impossible')
            return

        # Détection si wrap up et correction pour le calcul
        if abs(int(now[:2]) - int(bullTime[:2])) > 10:
            if now > bullTime:
            # Si le temps présent est plus grand que le temps du bulletin
            # (donc si le bulletin est généré le mois suivant que présentement),
            # On ajoute une journée au temps présent pour faire le temps du bulletin
                bullTime = str(int(now[:2]) + 1) + bullTime[2:]
            else:
            # Contraire (...)
                now = str(int(bullTime[:2]) + 1) + now[2:]

        # Conversion en nombre de minutes
        nbMinNow = 60 * 24 * int(now[0:2]) + 60 * int(now[2:4]) + int(now[4:])
        nbMinBullTime = 60 * 24 * int(bullTime[0:2]) + 60 * int(bullTime[2:4]) + int(bullTime[4:])

        # Calcul de l'interval de validité
        if not( -1 * abs(minimum) < nbMinNow - nbMinBullTime < maximum ):
            # La différence se situe en dehors de l'intervale de validité
            self.logger.warning("Délai en dehors des limites permises bulletin: "+unBulletin.getHeader()+', heure présente '+now)
            unBulletin.setError('Bulletin en dehors du delai permis')


    def reloadCollectionManager(self):
        """ reloadCollectionManager()

            The purposed of this method is to carry out a reload of the collectionManager 
            used to create immediate collections in the case where a 'reload' command
            is issued.
        """
        self.collectionManager.__init__(self.source.ingestor.collector, self.logger)

        
