import os,re,string,sys

# ---------------------------------------------------
# read in the ACCEPT/REJECT MASK
# ---------------------------------------------------

KMASKS = []
KFLAGS = []
CMASKS = []

f=open("fromPds.conf",'rb')
data=f.readlines()
f.close()

for l in data :
    l = l.strip()
    if len(l) == 0 : continue
    if l[0] == '#' : continue
    parts = l.split(' ')
    if parts[0] == 'accept' :
       KMASKS.append( parts[1] )
       CMASKS.append(re.compile(parts[1]))
       KFLAGS.append(True)
    if parts[0] == 'reject' :
       KMASKS.append( parts[1] )
       CMASKS.append(re.compile(parts[1]))
       KFLAGS.append(False)

# ---------------------------------------------------
# read in the ROUTING
# ---------------------------------------------------

f=open("pdsRouting.conf",'rb')
data2=f.readlines()
f.close()

ROUT={}
for l in data2:
    l2 = l.strip()
    if len(l2) == 0 : continue
    if l2[0] == '#' : continue
    parts = l2.split(' ')
    if len(parts) != 4 :
       print("BAD LINE %s" % l )
       continue
    if parts[1] in ROUT :
       print("duplicated %s" % parts[1])
    lst = parts[2].split(',')
    lst.sort()
    str = ','.join(lst)
    ROUT[parts[1]] = str

# ---------------------------------------------------
# get key
# ---------------------------------------------------


def getRouteKey(filename):
    """
    Given an ingest name, return a route key based on the imask given
    """
    # check against the masks

    for pos,cmask in enumerate(CMASKS):

        # not matching
        if not cmask.match(filename) : continue

        # match a reject
	if not KFLAGS[pos] : return False,False

        # match an accept
	kmask = KMASKS[pos]
        parts = re.findall( kmask, filename )
        if len(parts) == 2 and parts[1] == '' : parts.pop(1)
        if len(parts) != 1 : continue
        key = parts[0]
        if isinstance(parts[0],tuple) : key = '_'.join(parts[0])
        return key,kmask

    # no key
    return filename,'DEFAULT'

# ---------------------------------------------------
# read in the log
# ---------------------------------------------------

f=open(sys.argv[1],'rb')
data=f.readlines()
f.close()

t=len(data)

accept   = None
clients  = []
filename = None
key      = None

for l in data :

    parts = l.split()

    filename   = parts[0]
    clients    = parts[1]
    lst = clients.split(',')
    lst.sort()
    clients = ','.join(lst)
    key,accept = getRouteKey(filename)

    # rejected
    if key == False : 
      print("Rejected %s" % filename )
      continue

    # new file to ingest

    if key != None :

       if key in ROUT and clients == ROUT[key] : continue

       if not key in ROUT :
          print("missing key %s %s" % (key,clients) )
          continue

       lst_read = clients.split(',')

       rout = ROUT[key]
       rout = rout.replace(',topds','')
       lst_rout = rout.split(',')

       lst_diff = []

       for pos,cli in enumerate(lst_read):
           if pos >= len(lst_rout):
              lst_diff.append(cli)
              break

           if cli[:10] == 'conversion' and lst_rout[pos][:4] == 'cvt_' : continue
           if cli[:4] == 'cvt_'        and lst_rout[pos][:4] == 'cvt_' : continue

           if cli != lst_rout[pos] :
              lst_diff.append(cli)
              break

       if len(lst_diff) != 0 :
           print("DIFFER %s (READ) %s (ROUTING) %s" % (key,clients,ROUT[key]) )

    else :
      print("Filename %s " % filename )
