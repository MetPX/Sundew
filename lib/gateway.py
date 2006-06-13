# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""Superclasse pour un gateway de transfert de bulletins"""
import imp, time, sys
from MultiKeysStringSorter import MultiKeysStringSorter
from DiskReader import DiskReader
from Source import Source
import PXPaths
PXPaths.normalPaths()

__version__ = '2.0'

class gatewayException(Exception):
    """Classe d'exception sp�cialis�s relatives aux gateways"""
    pass

class gateway:
    """Regroupe les traits communs d'un gateway.

       De cette classe sera sp�cialis� les receivers, senders, etc.
       Un module self.config sera accessible qui contiendra les
       �l�ments de configuration du fichier de config.

       Les m�thodes abstraites l�vent une exception pour l'instant, et
       cette classe ne devrait pas �tre utilis�e comme telle.

       Terminologie:

          - D'un lecteur l'on pourra appeler une lecture de donn�es
            (ex: disque, socket, etc...)
          - D'un �crivain on pourra lui fournir des donn�es qu'il
            pourra "�crire" (ex: disque, socket, etc...)

       Instanciation:

            Le gateway s'instancie avec un fichier de configuration
            qu'il charge et dont l'impl�mentation varie selon le type
            de gateway.

            path            String

                            - Chemin d'acc�s vers le fichier de config

            flow            - Source ou Client (Permet d'acceder toutes les options)

            logger          Objet logger

                            - Doit pouvoir �tre appel� pour �crire les
                              messages. C'est le log principal du
                              programme

       Statut:      Abstraite
       Auteur:      Louis-Philippe Th�riault
       Date:        Octobre 2004
    """
    def __init__(self, path, flow, logger):
        self.pathToConfigFile = path
        self.logger = logger
        self.flow = flow 
        self.igniter = None
        self.reader = None

        # statistics.
        self.totBytes = 0
        self.initialTime = time.time()
        self.finalTime = None



    def resetReader(self):
        self.reader = DiskReader(PXPaths.TXQ + self.flow.name,
                                 self.flow.batch,            # Number of files we read each time
                                 self.flow.validation,       # name validation
                                 self.flow.patternMatching,  # pattern matching
                                 self.flow.mtime,            # we don't check modification time
                                 True,                       # priority tree
                                 self.logger,
                                 eval(self.flow.sorter),
                                 self.flow)

    def setIgniter(self, igniter):
        self.igniter = igniter

    def loadConfig(path):
        """loadConfig(path)

           Charge la configuration, situ�e au path en particulier.
           La configuration doit �tre syntaxiquement correcte pour
           que python puisse l'interpr�ter.

           (M�thode statique)

           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """
        try:
            fic_cfg = open(path,'r')
            config = imp.load_source('config','/dev/null',fic_cfg)
            fic_cfg.close()

            return config
        except IOError:
            print "*** Erreur: Fichier de configuration inexistant, erreur fatale!"
            sys.exit(-1)

    loadConfig = staticmethod(loadConfig)

    def establishConnection(self):
        """establishConnection()

           �tablit une connection avec le lecteur et l'�crivain (v�rifie
           que les ressources sont disponibles aussi). Est appel� si la
           connection, d'un c�t� ou l'autre, tombe.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """
        raise gatewayException('M�thode non implant�e (m�thode abstraite establishConnection)')

    def read(self):
        """read() -> data

           data : Liste d'objets

           Cette m�thode retourne une liste d'objets, qui peut �tre
           ing�r�e par l'�crivain. Elle l�ve une exception si
           une erreur est d�tect�e.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre
        """
        raise gatewayException('M�thode non implant�e (m�thode abstraite read)')

    def write(self,data):
        """write(data)

           data : Liste d'objets

           Cette m�thode prends le data lu par read, et fait le tra�tement
           appropri�.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """
        raise gatewayException('M�thode non implant�e (m�thode abstraite write)')

    def run(self):
        """run()

           Boucle infinie pour le transfert de data. Une exception
           non contenue peut �tre lev�e si le lecteur et l'�crivain
           ne sont pas disponibles.

           Visibilit�:  Publique
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """
        while True:

            try:
                data = self.read()
            except gatewayException, e:
                if e.args[0] == "Le lecteur ne peut �tre acc�d�":
                # Lecture impossible, il ne devrait plus y avoir
                # de donn�es en attente
                    if len(data) > 0:
                        self.write(data)
                        data = []

                    self.establishConnection()

                    if isinstance(self.flow, Source):
                        if self.flow.type in ['am', 'wmo']:
                            self.renewBulletinManager()
                else:
                    raise

            if len(data) == 0:
            # S'il n'y a pas de nouveau data
                time.sleep(0.1)
            else:
                self.write(data)

    def shutdown(self):
        """shutdown()

           Ferme le lecteur et l'�crivain "proprement". � �tre
           red�fini.

           Visibilit�:  Publique
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """
        self.logger.info("Fermeture propre du gateway")

    def checkLooping(self, unElementDeData):
        """checkLooping() -> bool

           Permet de d�tect� que l'on re�oit du data que l'on a
           d�ja re�u.

           Retourne True si pour l'objet pass� on a du looping.

           Statut: Abstraite
        """
        raise gatewayException("M�thode non implant�e: gateway.gateway.checkLooping()")

    def reloadConfig(self):
        """reloadConfig()

           Recharge les �l�ments du fichier de config, les �l�ments
           peuvent varier selon l'implantation.

           Utilisation:

                Recharger la config lors d'un SIGHUP.

           Visibilit�:  Publique
           Auteur:      Louis-Philippe Th�riault
           Date:        D�cembre 2004
        """
        self.logger.info('Demande de rechargement de configuration... non implant�!')

    def printSpeed(self):
        elapsedTime = time.time() - self.initialTime
        speed = self.totBytes/elapsedTime
        self.totBytes = 0
        self.initialTime = time.time()
        return "Speed = %i" % int(speed)

    def tallyBytes(self,bytecount):
        self.totBytes += bytecount

    
