# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

# MG python3 compatible

class CollectionEntry:
    """A class to hold all info about a bulletin entry in a collection.
    Author: Michel Grenier
    Date:   May 2006
    """

    def __init__(self):

        self.path      = None
        self.data      = None

        self.bulletin  = None
        self.header    = None
        self.type      = None
        self.BBB       = None
        self.station   = None

        self.dictkey   = None
        self.statekey  = None

        self.sourceidx = -1

        self.period    = -1  # 0 means primary... 1,2... cycle period

    def print_debug(self):

        print(" \n " )
        print(" CollectionEntry " )
        print(" \n " )
        print(" path      = %s " % self.path     )
        print(" data      = %s " % self.data     )
        print(" \n " )
        print(" bulletin  = %s " % self.bulletin )
        print(" header    = %s " % self.header   )
        print(" type      = %s " % self.type     )
        print(" BBB       = %s " % self.BBB      )
        print(" station   = %s " % self.station  )
        print(" \n " )
        print(" dictkey   = %s " % self.dictkey  )
        print(" statekey  = %s " % self.statekey )
        print(" \n " )
        print(" sourceidx = %s " % self.statekey )
        print(" \n " )
        print(" period    = %s " % self.period   )
        print(" \n " )
        print(" delay    = %s " % self.bulletin.delay )

if __name__ == '__main__':
 pass
