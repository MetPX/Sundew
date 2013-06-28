"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: SortableString.py
#
# Author: Daniel Lemay
#
# Date: 2005-02-01
#
# Description:
#
#############################################################################################

"""

import os.path

class SortableString:
    # Structure des strings:
    # testfileXXXX_PRI
    # SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E.C.M.N.H.K.X.S.D.O.Q.::20050201200339

    def __init__(self, string):
        self.data = string
        self.basename = os.path.basename(string)
        self.priority = None
        self.timestamp = None
        self.concatenatedKeys = None
        self._getKeys()

    def _getKeys(self):
        parts = self.basename.split(":")
        self.priority = parts[4].split(".")[0]
        if self.priority not in ['0', '1', '2', '3', '4', '5']:
            self.priority = ''
        self.timestamp = parts[6]
        self.concatenatedKeys = self.priority + self.timestamp

if __name__ == '__main__':

    #ss = SortableString("toto99_2")
    ss = SortableString("/apps/pds/SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339")
    print ss.data
    print ss.basename
    print ss.priority
    print ss.timestamp
    print ss.concatenatedKeys
