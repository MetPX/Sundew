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
    """Classe d'exception spécialisés relatives aux gateways"""
    pass

class gateway:
    """Regroupe les traits communs d'un gateway.

       De cette classe sera spécialisé les receivers, senders, etc.
       Un module self.config sera accessible qui contiendra les
       éléments de configuration du fichier de config.

       Les méthodes abstraites lèvent une exception pour l'instant, et
       cette classe ne devrait pas être utilisée comme telle.

       Terminologie:

          - D'un lecteur l'on pourra appeler une lecture de données
            (ex: disque, socket, etc...)
          - D'un écrivain on pourra lui fournir des données qu'il
            pourra "écrire" (ex: disque, socket, etc...)

       Instanciation:

            Le gateway s'instancie avec un fichier de configuration
            qu'il charge et dont l'implémentation varie selon le type
            de gateway.

            path            String

                            - Chemin d'accès vers le fichier de config

            flow            - Source ou Client (Permet d'acceder toutes les options)

            logger          Objet logger

                            - Doit pouvoir être appelé pour écrire les
                              messages. C'est le log principal du
                              programme

       Statut:      Abstraite
       Auteur:      Louis-Philippe Thériault
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

           Charge la configuration, située au path en particulier.
           La configuration doit être syntaxiquement correcte pour
           que python puisse l'interpréter.

           (Méthode statique)

           Auteur:      Louis-Philippe Thériault
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

           Établit une connection avec le lecteur et l'écrivain (vérifie
           que les ressources sont disponibles aussi). Est appelé si la
           connection, d'un côté ou l'autre, tombe.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        raise gatewayException('Méthode non implantée (méthode abstraite establishConnection)')

    def read(self):
        """read() -> data

           data : Liste d'objets

           Cette méthode retourne une liste d'objets, qui peut être
           ingérée par l'écrivain. Elle lève une exception si
           une erreur est détectée.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre
        """
        raise gatewayException('Méthode non implantée (méthode abstraite read)')

    def write(self,data):
        """write(data)

           data : Liste d'objets

           Cette méthode prends le data lu par read, et fait le traîtement
           approprié.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        raise gatewayException('Méthode non implantée (méthode abstraite write)')

    def run(self):
        """run()

           Boucle infinie pour le transfert de data. Une exception
           non contenue peut être levée si le lecteur et l'écrivain
           ne sont pas disponibles.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        while True:

            try:
                data = self.read()
            except gatewayException, e:
                if e.args[0] == "Le lecteur ne peut être accédé":
                # Lecture impossible, il ne devrait plus y avoir
                # de données en attente
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

           Ferme le lecteur et l'écrivain "proprement". À être
           redéfini.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        self.logger.info("Fermeture propre du gateway")

    def checkLooping(self, unElementDeData):
        """checkLooping() -> bool

           Permet de détecté que l'on reçoit du data que l'on a
           déja reçu.

           Retourne True si pour l'objet passé on a du looping.

           Statut: Abstraite
        """
        raise gatewayException("Méthode non implantée: gateway.gateway.checkLooping()")

    def reloadConfig(self):
        """reloadConfig()

           Recharge les éléments du fichier de config, les éléments
           peuvent varier selon l'implantation.

           Utilisation:

                Recharger la config lors d'un SIGHUP.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Décembre 2004
        """
        self.logger.info('Demande de rechargement de configuration... non implanté!')

    def printSpeed(self):
        elapsedTime = time.time() - self.initialTime
        speed = self.totBytes/elapsedTime
        self.totBytes = 0
        self.initialTime = time.time()
        return "Speed = %i" % int(speed)

    def tallyBytes(self,bytecount):
        self.totBytes += bytecount

    
