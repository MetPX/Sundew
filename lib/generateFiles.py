"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

import sys, string, random

#root = "/apps/pds/tools/ColumboNCCS/testfiles1/"
#root = "/home/ib/dads/dan/progProj/pds-nccs/bulletins/tata/"
#root = "/apps/px/txq/dummy/"
root = '/apps/px/bulletins/2/'
numFiles = sys.argv[1]
size = sys.argv[2]
letters = list(string.letters)
letters.remove('U')
priority = range(1,6)
timestamp = 20050201174200

for num in range(int(numFiles)):
    timestamp = timestamp + 1
    output = open(root + "SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:" + str(random.choice(priority)) + ".A.I.E.C.M.N.H.K.X.S.D.O.Q.::" + str(timestamp), 'w')
    randomString = "".join(map(lambda x: random.choice(letters), range(0, int(size))))
    output.write(randomString)
    output.close()

"""
root = "/home/ib/dads/dan/progProj/pds-nccs/bulletins/titi/"
for num in range(int(numFiles)):
    timestamp = timestamp + 1
    output = open(root + "SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA::" + str(random.choice(priority)) + ".A.I.E.C.M.N.H.K.X.S.D.O.Q.:" + str(timestamp), 'w')
    randomString = "".join(map(lambda x: random.choice(letters), range(0, int(size))))
    output.write(randomString)
    output.close()

root = "/home/ib/dads/dan/progProj/pds-nccs/bulletins/toto/"
for num in range(int(numFiles)):
    timestamp = timestamp + 1
    output = open(root + "SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA::" + str(random.choice(priority)) + ".A.I.E.C.M.N.H.K.X.S.D.O.Q.:" + str(timestamp), 'w')
    randomString = "".join(map(lambda x: random.choice(letters), range(0, int(size))))
    output.write(randomString)
    output.close()
"""
