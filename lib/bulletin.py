# -*- coding: iso-8859-1 -*-
"""Définition de la classe principale pour les bulletins."""

import time
import string, traceback, sys
from   Bufr import Bufr
from   Grib import Grib

__version__ = '2.0'

class bulletinException(Exception):
    """Classe d'exception spécialisés relatives aux bulletins"""
    pass

class bulletin:
    """Classe abstraite regroupant tout les traits communs des bulletins
    quels que soient les protocoles utilisés. Les méthodes
    qui ne retournent qu'une exception doivent êtres redéfinies
    dans les sous-classes (il s'agit de méthodes abstraites).

    Le bulletin est représenté à l'interne comme une liste de strings,
    découpés par l'attribut lineSeparator.

    Vérifie l'entête du bulletin lors de l'instanciation. Pour sauter
    cette vérification dans une des classes spécialisées, overrider
    la méthode par une méthode vide.

            * Paramètres à passer au constructeur

            stringBulletin          String

                                    - Le bulletin lui-même en String

            logger                  Objet log

                                    - Log principal pour les bulletins

            finalLineSeparator      String

                                    - Séparateur utilisé comme fin de ligne
                                      lors de l'appel du get

            lineSeparator           String

                                    - Marqueur utilise pour separer les lignes
                                      du bulletin source

            * Attributs (usage interne seulement)

            errorBulletin           tuple (default=None)

                                    - Est modifié une fois que le
                                      traîtement spécifique est
                                      effectué.
                                    - Si une erreur est détectée,
                                      errorBulletin[0] est le message
                                      relatif à l'erreur
                                    - errorBulletin[1:] est laissé
                                      libre pour la spécialisation
                                      de la classe

            bulletin                liste de strings [str]

                                    - Lors d'un getBulletin, le
                                      bulletin est fusionné avec
                                      lineSeparator comme caractère
                                      d'union

    Statut: Abstraite
    Auteur: Louis-Philippe Thériault
    Date:   Octobre 2004
    Modifications: Decembre 2004, Louis-Philippe et Pierre
    Modifications: May      2006, Michel Grenier... time tools + modules in alpha order
    """

    def __init__(self,stringBulletin,logger,lineSeparator='\n',finalLineSeparator='\n'):
        self.logger = logger
        self.errorBulletin = None
        self.lineSeparator = lineSeparator
        self.finalLineSeparator = finalLineSeparator
        self.bulletin = self.splitlinesBulletin(stringBulletin.lstrip(lineSeparator))
        self.dataType = None

        # time stuff
        self.arrival     = None
        self.emission    = None
        self.delay       = None
        self.age         = None

        self.ep_arrival  = -1
        self.ep_emission = -1

        # Normalization du header ici (enlever les espaces au début et a la fin)
        self.setHeader(self.getHeader().strip())

        # Vérification du header du bulletin
        # pour ne pas l'effectuer, simplement overrider la méthode
        # dans la classe spécialisée, par une méthode qui ne fait rien
        self.verifyHeader()

        self.logger.veryverbose("newBulletin: %s" % stringBulletin)
    def compute_Age(self, ep_now=None ):
        """compute_Age() -

           Compute the age of the bulletin
           the age is given by  age = now-emission 
           were age, now and emission are integer, epocal in second

           Visibility:  Publique
           Author:      Michel Grenier
           Date:        May 2006
        """

        if ep_now == None : ep_now = time.mktime(time.gmtime())
        self.age = ep_now - self.ep_emission

    def compute_Delay(self):
        """compute_Delay() -

           Compute attribut delay which corresponds to  arrival-emission
           delay is an integer in seconds

           Visibility:  Private
           Author:      Michel Grenier
           Date:        May 2006
        """

        self.delay = self.ep_arrival - self.ep_emission

    def compute_Emission(self):
        """compute_Emission() -

           compute emission of bulletin
           emission is a character string of the form YYYYMMDDhhmmss
           ep_emission is its epocal correspondant

           Visibility:  Private
           Author:      Michel Grenier
           Date:        May 2006
        """

        if self.arrival == None : return

        arrival          = self.arrival
        header           = self.getHeader().split()
        YYGGGg           = header[2]
        self.emission    = arrival[0:6] + YYGGGg + "00"
        timeStruct       = time.strptime(self.emission, '%Y%m%d%H%M%S')
        self.ep_emission = time.mktime(timeStruct)

        # if the arrival day is the same as the one in header... we are done
        # if not go backward in time until the emission day is reached

        if YYGGGg[:2] == arrival[6:8] : return

        day    = arrival[6:8]
        ep_day = self.ep_arrival

        while day != YYGGGg[:2] :
              ep_day     = ep_day - 24 * 60 * 60
              day        = time.strftime('%d',time.gmtime(ep_day))

        self.ep_emission = ep_day
        self.emission    = time.strftime('%Y%m%d%H%M%S',time.gmtime(ep_day))

    def doSpecificProcessing(self):
        """doSpecificProcessing()

           Modifie le bulletin s'il y a lieu, selon le traîtement désiré.

           Utilisation:

                Inclure les modifications à effectuer sur le bulletin, qui
                sont propres au type de bulletin en question.

           Statut:      Abstraite
           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        raise bulletinException('Méthode non implantée (méthode abstraite doSpecificProcessing)')

    def getAge(self, ep_now=None ):
        """getAge() -> (TypeErreur)

           Return the age of the bulletin

           Visitility:  Publique
           Author:      Michel Grenier
           Date:        May 2006
        """

        self.computeAge(ep_now)
        return self.age

    def getBBB(self):
        """getBBB() -> (TypeErreur)

           Return None if BBB not present or in error.
           Otherwise return the bulletin's BBB

           Visitilité:  Publique
           Auteur:      Michel Grenier
           Date:        May 2006
        """

        header = self.getHeader().split()
        if len(header) != 4 : return None

        BBB = header[3]

        if len(BBB) != 3 :
           self.setError('Entete non conforme BBB incorrect')
           return None

        if BBB[0] != 'A' and BBB[0] != 'C' and BBB[0] != 'R' :
           self.setError('Entete non conforme BBB incorrect')
           return None

        if BBB[1] < 'A' or BBB[1] > 'Z' or BBB[2] < 'A' or BBB[2] > 'Z' :
           self.setError('Entete non conforme BBB incorrect')
           return None

        return BBB

    def getBulletin(self,includeError=False,useFinalLineSeparator=True):
        """getBulletin([includeError]) -> bulletin

           bulletin     : String

           includeError:        Bool
                                - Si est à True, inclut l'erreur dans le corps du bulletin

           useFinalLineSeparator:       Bool
                                - Si est a True, utilise le finalLineSeparator

           Retourne le bulletin en texte

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
           Modifications: Decembre 2004, Louis-Philippe et Pierre
        """
        if useFinalLineSeparator:
            marqueur = self.finalLineSeparator
        else:
            marqueur = self.lineSeparator

        if self.errorBulletin == None:
            return string.join(self.bulletin,marqueur)
        else:
            if includeError:
                return ("### " + self.errorBulletin[0] + marqueur + "PROBLEM BULLETIN" + marqueur) + string.join(self.bulletin,marqueur)
            else:
                return string.join(self.bulletin,marqueur)

    def getDataType(self):
        """getDataType() -> dataType

           dataType:    String élément de ('BI','AN')
                        - Type de la portion de données du bulletin

           Visitilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        if self.dataType != None:
            return self.dataType

        for ligne in self.bulletin:
            if ligne.lstrip()[:4] == 'BUFR' or ligne.lstrip()[:4] == 'GRIB':
                # Il faut que le BUFR/GRIB soit au début d'une ligne
                self.dataType = 'BI'
                break

        # Si le bulletin n'est pas binaire, il est alphanumérique
        if self.dataType == None: self.dataType = 'AN'

        return self.dataType

    def getError(self):
        """getError() -> (TypeErreur)

           Retourne None si aucune erreur détectée dans le bulletin,
           sinon un tuple avec comme premier élément la description
           de l'erreur. Les autres champs sont laissés libres

           Visitilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return self.errorBulletin

    def getHeader(self):
        """getHeader() -> header

           header       : String

           Retourne l'entête (première ligne) du bulletin

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return self.bulletin[0]

    def getLength(self):
        """getLength() -> longueur

           longueur     : int

           Retourne la longueur du bulletin avec le lineSeparator

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return len(self.getBulletin())

    def getLogger(self):
        """getLogger() -> objet_logger

           Retourne l'attribut logger du bulletin

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Novembre 2004
        """
        return self.logger

    def getOrigin(self):
        """getOrigin() -> origine

           origine      : String

           Retourne l'origine (2e champ de l'entête) du bulletin (CWAO,etc...)

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return self.getHeader().split(' ')[1]

    def getStation(self):
        """getStation() -> station

           station      : String

           Retourne la station associée au bulletin,
           retourne None si elle est introuvable.

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """


        #print(" ********************* BULLETIN GET STATION APPELE ")

        station = None
        try:
            premiereLignePleine = ""
            deuxiemeLignePleine = ""
            bulletin = self.bulletin

            # Cas special, il faut aller chercher la prochaine ligne pleine
            i = 0
            for ligne in bulletin[1:]:
                i += 1
                premiereLignePleine = ligne
                if len(premiereLignePleine) > 1:
                   if len(bulletin) > i+1 : deuxiemeLignePleine = bulletin[i+1]
                   break

            #print " ********************* header = ", bulletin[0][0:7]
            # Embranchement selon les differents types de bulletins
            if bulletin[0][0:2] == "SA":
                if bulletin[1].split()[0] in ["METAR","LWIS"]:
                    station = premiereLignePleine.split()[1]
                else:
                    station = premiereLignePleine.split()[0]

            elif bulletin[0][0:2] == "SP":
                station = premiereLignePleine.split()[1]

            elif bulletin[0][0:2] in ["SI","SM"]:
                station = premiereLignePleine.split()[0]
                if station == "AAXX" :
                   if deuxiemeLignePleine != "" :
                      station = deuxiemeLignePleine.split()[0]
                   else :
                      station = None

            elif bulletin[0][0:6] in ["SRCN40","SXCN40","SRMT60"]:
                station = premiereLignePleine.split()[0]

            elif bulletin[0][0:2] in ["FC","FT"]:
                if premiereLignePleine.split()[1] == "AMD":
                    station = premiereLignePleine.split()[2]
                else:
                    station = premiereLignePleine.split()[1]

            elif bulletin[0][0:2] in ["UE","UG","UK","UL","UQ","US"]:
                station = premiereLignePleine.split()[2]

            elif bulletin[0][0:2] in ["RA","MA","CA"]:
                station = premiereLignePleine.split()[0].split('/')[0]

        except Exception:
            station = None

        if station != None :
           while len(station) > 1 and station[0] == '?' :
                 station = station[1:]
           if station[0] != '?' :
              station = station.split('?')[0]
              if station[-1] == '=' : station = station[:-1]
           else :
              station = None

        self.station = station

        return station

    def getType(self):
        """getType() -> type

           type         : String

           Retourne le type (2 premieres lettres de l'entête) du bulletin (SA,FT,etc...)

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return self.getHeader()[:2]

    def replaceChar(self,oldchars,newchars):
        """replaceChar(oldchars,newchars)

           oldchars,newchars    : String

           Remplace oldchars par newchars dans le bulletin. Ne touche pas à la portion Data
           des GRIB/BUFR

           Utilisation:

                Pour des remplacements dans doSpecifiProcessing.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Novembre 2004
        """
        for i in range(len(self.bulletin)):
            if self.bulletin[i].lstrip()[:4] != 'GRIB' and self.bulletin[i].lstrip()[:4] != 'BUFR':
               self.bulletin[i] = self.bulletin[i].replace(oldchars,newchars)

    def setArrivalEp(self,ep_arrival):
        """setArrivalEp(ep_arrival)

           Assign arrival attribut of bulletin
           ep_arrival is an integer expressing time in epocal seconds

           Visibility:  Public
           Author:      Michel Grenier
           Date:        Mai 2006
        """ 

        self.ep_arrival = ep_arrival
        self.arrival    = time.strftime('%Y%m%d%H%M%S',time.gmtime(ep_arrival))

        self.compute_Emission()
        self.compute_Delay()
        self.compute_Age()

    def setArrivalStr(self,arrivalStr):
        """setArrivalStr(arrivalStr)

           Assign arrival attribut of bulletin
           arrivalStr is a character string of the form YYYYMMDDhhmmss

           Visibility:  Public
           Author:      Michel Grenier
           Date:        Mai 2006
        """

        self.arrival    = arrivalStr
        timeStruct      = time.strptime(arrivalStr[:14], '%Y%m%d%H%M%S')
        self.ep_arrival = time.mktime(timeStruct)

        self.compute_Emission()
        self.compute_Delay()
        self.compute_Age()

    def setError(self,msg):
        """setError(msg)

           msg: String
                - Message relatif à l'erreur

           Flag le bulletin comme erroné. L'utilisation du message est propre
           au type de bulletin.

           Visitilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        if self.errorBulletin == None:
            self.errorBulletin = [msg]

    def setHeader(self,header):
        """setHeader(header)

           header       : String

           Assigne l'entête du bulletin

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        self.bulletin[0] = header

        self.logger.debug("Nouvelle entête du bulletin: %s",header)

    def setLogger(self,logger):
        """setLogger(logger)

           Assigne l'attribut logger du bulletin

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Novembre 2004
        """
        self.logger = logger

    def splitlinesBulletin(self,stringBulletin):
        """splitlinesBulletin(stringBulletin) -> listeLignes

           stringBulletin       : String
           listeLignes          : Liste

           Retourne la liste de lignes des bulletins. Ne pas utiliser .splitlines()
           (de string) car il y a possibilité d'un bulletin en binaire.

           Les bulletins binaires (jusqu'à présent) commencent par GRIB/BUFR et
           se terminent par 7777 (la portion binaire).

           Utilisation:

                Pour découpage initial du bulletin, ou si l'on insère un self.linseparator
                dans le bulletin, pour le redécouper (faire un getBulletin() puis le redécouper).

           Nb.: Les bulletins GRIB/BUFR sont normalisés en enlevant tout data après le '7777'
                (délimiteur de fin de portion de data) en en ajoutant un lineSeparator.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Novembre 2004
        """
        try:
            estBinaire = False

            # On détermine si le bulletin est binaire
            for ligne in stringBulletin.splitlines():
                if ligne.lstrip()[:4] == 'BUFR' or ligne.lstrip()[:4] == 'GRIB':
                    # Il faut que le BUFR/GRIB soit au début d'une ligne
                    estBinaire = True
                    break

            if estBinaire:
                if stringBulletin.find('GRIB') != -1:
                # Type de bulletin GRIB, découpage spécifique
                # TODO check if grib is valid  grib.valid  and if not react 

                    grib = Grib(stringBulletin)

                    b = stringBulletin[:grib.begin].split(self.lineSeparator)

                    # Si le dernier token est un '', c'est qu'il y avait
                    # un \n à la fin, et on enlève puisque entre 2 éléments de la liste,
                    # on insère un \n
                    if b[-1] == '':
                        b.pop(-1)

                    b = b + [stringBulletin[grib.begin:grib.last]] + ['']

                    return b

                elif stringBulletin.find('BUFR') != -1:
                # Type de bulletin BUFR, découpage spécifique
                # TODO check if bufr is valid  bufr.valid  and if not react 

                    bufr = Bufr(stringBulletin)

                    b = stringBulletin[:bufr.begin].split(self.lineSeparator)

                    # Si le dernier token est un '', c'est qu'il y avait
                    # un \n à la fin, et on enlève puisque entre 2 éléments de la liste,
                    # on insère un \n
                    if b[-1] == '':
                        b.pop(-1)

                    b = b + [stringBulletin[bufr.begin:bufr.last]] + ['']

                    return b
            else:
                # Le bulletin n'est pas binaire
                return stringBulletin.split(self.lineSeparator)
        except Exception, e:
            self.logger.exception('Erreur lors du decoupage du bulletin:\n'+''.join(traceback.format_exception(Exception,e,sys.exc_traceback)))
            self.setError('Erreur lors du découpage de lignes')
            return stringBulletin.split(self.lineSeparator)

    def verifyHeader(self):
        """verifyHeader()

           Vérifie l'entête du bulletin et le flag en erreur s'il y a erreur.

           Utilisation:

                Est appelé à l'instance, masquer pour ne pas faire l'appel.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Novembre 2004
        """
        header = self.getHeader()

        # remove duplicate spaces
        tokens = header.split()
        header = ' '.join(tokens)
        self.setHeader(header)

        if header=='':
            self.setError('Entete vide')
            return

        # Changement qui doit être fait avant de vérifier l'entête,
        # le tandem enlève le 'z' ou 'Z' à la fin de l'entête
        # s'il y a lieu.
        if header[-1]  in ['z','Z']:
            header = header[:-1]
            self.setHeader(header)

        tokens = header.split()

        if len(tokens) < 3:
            self.setError('Entete non conforme (moins de 3 champs)')
            return

        if len(tokens[2]) > 6: # On enleve les ['z', 'Z'] ou ['utc', 'UTC'] s'ils sont presents dans le groupe JJHHMM
            tokens[2] = tokens[2][0:5]
            self.logger.info("Entete corrigee: le groupe JJHHMM a ete tronque (plus de 6 caracteres)")
            self.setHeader(' '.join(tokens))
            tokens = self.getHeader().split()

        if not tokens[0].isalnum() or len(tokens[0]) not in [4,5,6] or \
           not tokens[1].isalnum() or len(tokens[1]) not in [4,5,6] or \
           not tokens[2].isdigit() or len(tokens[2]) != 6 or \
           not (0 <= int(tokens[2][:2]) <= 31) or not(00 <= int(tokens[2][2:4]) <= 23) or \
           not(00 <= int(tokens[2][4:]) <= 59):

            self.setError('Entete non conforme (format des 3 premiers champs incorrects)')
            return

        if len(tokens) == 3:
            return

        if not tokens[3].isalpha() or len(tokens[3]) != 3 or tokens[3][0] not in ['C','A','R','P']:
            #self.setError('Entete non conforme (champ BBB incorrect')
            self.logger.info("Entete corrigee: 4ieme champ (et les suivants) enleve du header") 
            parts = self.getHeader().split()
            del parts[3:]
            self.setHeader(' '.join(parts))
            return

        if len(tokens) == 5 and \
                (not tokens[4].isalpha() or len(tokens[4]) != 3 or tokens[4][0] not in ['C','A','R','P']):

            #self.setError('Entete non conforme4 (champ BBB no2 incorrect')
            self.logger.info("Entete corrigee: 5ieme champ (et les suivants) enleve du header")
            parts = self.getHeader().split()
            del parts[4:]
            self.setHeader(' '.join(parts))
            return

        if len(tokens) > 5:

            #self.setError('Entete non conforme (plus de 5 champs')
            self.logger.info("Entete corrigee: 6ieme champ (et les suivants) enleve du header")
            parts = self.getHeader().split()
            del parts[5:]
            self.setHeader(' '.join(parts))
            return

if __name__ == '__main__':
 pass
