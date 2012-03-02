import os,sys,re

# EXTRACTING ALL FILENAMES AND THEIR CLIENTS

# ---------------------------------------------------
# read in the log
# ---------------------------------------------------

f=open(sys.argv[1],'rb')
data=f.readlines()
f.close()

n=0
t=len(data)

clients  = []
filename = None

for l in data :

    n = n + 1
    parts = l.split()

    # new file to ingest

    if parts[6] == 'Read'         :

       # all products will have its first client as "allproducts"
       if filename != None :
          if len(clients) == 0 :
             clients.append('allproducts')
          else :
             clients.sort()
             clients.insert(0,'allproducts')
          print("%s %s" % (filename,','.join(clients)) )

       filepath = parts[-1]
       filename = filepath.split('/')[-1]

       fparts   = filename.split(':')
       # :20070409000009 trailing get rid of it
       if fparts[-1][:2] == '20' and len(fparts[-1]) == 14 :
          fparts = fparts[:-1]

       # '::' trailing get rid of it
       if fparts[-1] == '' :
          fparts = fparts[:-1]

       filename = ':'.join(fparts)
       clients  = []

    if parts[6] == 'Written'      :
       filepath = parts[-1]
       client   = 'conversion_' +filepath.split('/')[1]
       if client == 'conversion_ppmtogif' : client = 'cvt_togif'
       if client == 'conversion_rawtodfx' : continue
       clients.append(client)

    if parts[6] == 'create_link:' : 
       filepath = parts[-1]
       client   = filepath.split('/')[4]
       clients.append(client)

if len(clients) == 0 :
   clients.append('allproducts')
else :
   clients.sort()
   clients.insert(0,'allproducts')

print("%s %s" % (filename,','.join(clients)) )
