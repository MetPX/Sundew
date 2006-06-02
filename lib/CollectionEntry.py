# -*- coding: iso-8859-1 -*-
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

class CollectionEntry:
    """A class to hold all info about a bulletin entry in a collection.
    Author: Michel Grenier
    Date:   May 2006
    """

    def __init__(self):

        self.path     = None
        self.data     = None
        self.bulletin = None
        self.index    = -1

        self.header   = None
        self.BBB      = None
        self.station  = None
        self.dictkey  = None

        self.period   = -1  # 0 means primary... 1,2... cycle period

        self.statekey = None

    def print_debug(self):

        print(" \n CollectionEntry \n "         )
        print(" path     = %s " % self.path     )
        print(" data     = %s " % self.data     )
        print(" bulletin = %s " % self.bulletin )
        print(" index    = %d " % self.index    )

        print(" header   = %s " % self.header   )
        print(" BBB      = %s " % self.BBB      )
        print(" station  = %s " % self.station  )
        print(" dictkey  = %s " % self.dictkey  )

        print(" period   = %s " % self.period   )

        print(" statekey = %s " % self.statekey )

        print(" delay    = %s " % self.bulletin.delay )

if __name__ == '__main__':
 pass
