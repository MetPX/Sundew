#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

import sys, string, random, shutil

#original = "SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339"
#original = "WACN34_CWUL_220101_32182:ncp1:CWUL:WA:1:Direct:20050322010209"
original = "SMCN39_CWAO_071200_71978_50953:ncp1:CWAO:SM:3:Direct:20050607123429"
#root = "/apps/px/txq/dummyAMIS/"
#root = "/apps/px/rxq/yap/"
#root = "/apps/px/txq/wmoDan/1/"
#root = "/apps/px/txq/echo/"
root = "/apps/px/txq/echo/1/2005050510/"
numFiles = sys.argv[1]
priority = range(1,2)
timestamp = 20050201174200

for num in range(int(numFiles)):
    timestamp = timestamp + 1
    shutil.copy("/apps/px/" + original, root + "SMCN39_CWAO_071200_71978_50953:ncp1:CWAO:SA:" + 
                 str(random.choice(priority)) + ".A.I.E::" + str(timestamp))

