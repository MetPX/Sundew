# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""Définition d'une sous-classe pour les bulletins "WMO" """

import string
import bulletin

__version__ = '2.0'

class bulletinWmo(bulletin.bulletin):
    __doc__ = bulletin.bulletin.__doc__ + \
    """### Ajout de bulletinWmo ###

    Implantation pour un usage concret de la classe bulletin.

    Pour l'instant, un bulletinWmo ne se différencie que par son
    traîtement spécifique.

    Auteur: Louis-Philippe Thériault
    Date:   Octobre 2004
    """

    def __init__(self,stringBulletin,logger,lineSeparator='\n',finalLineSeparator='\n'):
        bulletin.bulletin.__init__(self,stringBulletin,logger,lineSeparator,finalLineSeparator)

    def doSpecificProcessing(self):
        """doSpecificProcessing()

           Modifie les bulletins provenant de Washington, transmis
           par protocole Wmo, nommés "WMO"

           Visibilité:  Publique
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        if self.getDataType() == 'BI':
        # Si le bulletin est un BUFR, l'on remplace le premier set,
        # puis le dernier (apres le 7777) s'il y a lieu
            self.replaceChar('\r','')
            return

        if self.bulletin[0][:2] in ['SD','SO','WS','SR','SX','FO','WA','AC','FA','FB','FD']:
            self.replaceChar('\x1e','')

        if self.bulletin[0][:2] in ['SR','SX']:
            self.replaceChar('~',self.lineSeparator)

        if self.bulletin[0][:2] in ['UK']:
            self.replaceChar('\x01','')

        if self.bulletin[0][:4] in ['SICO']:
            self.replaceChar('\x01','')

        if self.bulletin[0][:2] in ['SO','SR']:
            self.replaceChar('\x02','')

        if self.bulletin[0][:2] in ['SX','SR','SO']:
            self.replaceChar('\x00','')

        if self.bulletin[0][:2] in ['SX']:
            self.replaceChar('\x11','')
            self.replaceChar('\x14','')
            self.replaceChar('\x19','')
            self.replaceChar('\x1f','')

        if self.bulletin[0][:2] in ['SR']:
            self.replaceChar('\b','')
            self.replaceChar('\t','')
            self.replaceChar('\x1a','')
            self.replaceChar('\x1b','')
            self.replaceChar('\x12','')

        if self.bulletin[0][:2] in ['FX']:
            self.replaceChar('\x10','')
            self.replaceChar('\xf1','')

        if self.bulletin[0][:2] in ['WW']:
            self.replaceChar('\xba','')

        if self.bulletin[0][:2] in ['US']:
            self.replaceChar('\x18','')

        if self.bulletin[0][:4] in ['SXUS','SXCN','SRCN']:
            self.replaceChar('\x7f','?')
            
        if self.bulletin[0][:4] in ['SRCN']:
            self.replaceChar('\x0e','')
            self.replaceChar('\x11','')
            self.replaceChar('\x16','')
            self.replaceChar('\x19','')
            self.replaceChar('\x1d','')
            self.replaceChar('\x1f','')

        if self.bulletin[0][:4] in ['SXVX','SRUS','SRMT']:
            self.replaceChar('\x7f','')

        self.replaceChar('\r','')

        if self.bulletin[0][:2] in ['SA','SM','SI','SO','UJ','US','FT']:
            self.replaceChar('\x03','')

        # Re-calcul du bulletin
        self.bulletin = self.splitlinesBulletin(self.getBulletin(useFinalLineSeparator=False))

        # Enlève les espaces à la fin des lignes
        for i in range(len(self.bulletin)):
            self.bulletin[i] = self.bulletin[i].rstrip()

        # Si pas de newline, on en ajoute un à la fin
        if self.bulletin[-1] != '':
            self.bulletin += ['']

        bulletin.bulletin.verifyHeader(self)
