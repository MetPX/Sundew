# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""Gestion des bulletins "WMO" """

import bulletinManager, bulletinWmo, os, string

__version__ = '2.0'

class bulletinManagerWmo(bulletinManager.bulletinManager):
    __doc__ = bulletinManager.bulletinManager.__doc__ + \
    """### Ajout de bulletinManagerWmo ###

       Spécialisation et implantation du bulletinManager.

       Pour l'instant, un bulletinManagerWmo est pratiquement
       la même chose que le bulletinManager.

       Auteur:      Louis-Philippe Thériault
       Date:        Octobre 2004
    """

    def __init__(self,pathTemp,logger,pathSource=None, \
                    pathDest=None,maxCompteur=99999,lineSeparator='\n',extension=':', \
                    pathFichierCircuit=None,mapEnteteDelai=None, source=None):

        bulletinManager.bulletinManager.__init__(self,pathTemp,logger, \
                                        pathSource,pathDest,maxCompteur,lineSeparator,extension,pathFichierCircuit,mapEnteteDelai, source)

    def _bulletinManager__generateBulletin(self,rawBulletin):
        __doc__ = bulletinManager.bulletinManager._bulletinManager__generateBulletin.__doc__ + \
        """### Ajout de bulletinManagerWmo ###

           Overriding ici pour passer les bons arguments au bulletinWmo

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return bulletinWmo.bulletinWmo(rawBulletin,self.logger,self.lineSeparator)
