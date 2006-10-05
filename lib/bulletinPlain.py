# -*- coding: iso-8859-1 -*-
#MetPX Copyright (C) 2004-2006  Environment Canada
#MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#named COPYING in the root of the source directory tree.
#Auteur: 
#    2004/11 -- Louis-Philippe Thériault

"""Concrete bulletin class"""

import bulletin

__version__ = '2.0'

class bulletinPlain(bulletin.bulletin):
    __doc__ = bulletin.bulletin.__doc__ + \
    """
    minimal bulletin implementation.

    Detail: doSpecificProcessing does nothing.

    Purpose:
            to create bulletins whose contents
            will not be modified.
    """

    def doSpecificProcessing(self):
        """do nothing.
        """
        return
