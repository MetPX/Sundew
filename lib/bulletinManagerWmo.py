# -*- coding: iso-8859-1 -*-
#
#MetPX Copyright (C) 2004-2006  Environment Canada
#MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#named COPYING in the root of the source directory tree.
#
# Auteur:
#    2004/10   Louis-Philippe Thériault
#

"""WMO socket protocol bulletin manager"""

import bulletinManager, bulletinWmo, os, string

__version__ = '2.0'

class bulletinManagerWmo(bulletinManager.bulletinManager):
    __doc__ = bulletinManager.bulletinManager.__doc__ + \
    """concrete implementation of bulletinManager for WMO
    """

    def _bulletinManager__generateBulletin(self,rawBulletin):
        __doc__ = bulletinManager.bulletinManager._bulletinManager__generateBulletin.__doc__ + \
        """ Overriding here to pass correct parameter types.
        """
        return bulletinWmo.bulletinWmo(rawBulletin,self.logger,self.lineSeparator)
