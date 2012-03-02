#!/usr/bin/python2

import sys

pds_file = '.etc/'+sys.argv[1]+'.conf'

f = open(pds_file, 'r')
data = f.read()
f.close()

lines=data.split('\n')

for l in lines :
    if len(l) > 0 and l[0] == '#' : print l

print "# STATUS:         Operational"
print "#"
print "# DESCRIPTION:    "
print "#"
print "# SOURCE:         "
print "#"
print "# DESTINATION:    "
print "#"
print ""
print "type single-file"
print ""
print "# connection info"
print ""
print "protocol    ftp"
print "host        " + sys.argv[2]
print "user        " + sys.argv[3]
print "password    " + sys.argv[4]
print "ftp_mode    active"
print ""
print "# no filename validation (pds format)"
print ""
print "validation  False"
print ""
print "# delivery method"
print ""
print "lock  umask"
print "chmod 775"
print "batch 100"
print ""
print "#---------------------------------------------------------------"
print "host         " + "YOUR.TEST.MACHINE.HERE"
print "user         " + "YOUR.TEST.USER"
print "password     " + "YOUR.TEST.PASSWORD"
print "dir_mkdir    " + "true"
print "noduplicates " + "false"
print "#---------------------------------------------------------------"
print ""
print "# what,how and where to put data "
print ""

lst_filename=" "
lst_directory=" "
lst_machine=" "

for l in lines :
    l = l.strip()
    if len(l) == 0 :
       print ""
       continue

    if l[0] == '#' :
       print l
       continue

    parts=l.split()

    if parts[0] == 'emask' :
       msk = parts[1].replace('*','.*')
       msk = msk.replace('+','\+')
       if msk[-1] != '*' : msk = msk + '.*'
       print("reject %s" % msk )
       print ""
       continue

    if parts[0] == 'imask' :
       machine  = parts[2]
       if machine != lst_machine :
          print ""
          print("# *********** MACHINE %s" % machine )
          print ""
          lst_machine = machine

       filename = parts[3]
       #if filename[:12] == "DESTFNSCRIPT" :
       #   script=filename.split('=')[1]
       #   filename="NONE"
       #   print ""
       #   print("destfn_script %s" % script )
       #   print ""

       if len(parts) < 5 :
          directory = "/"
       else :
          if parts[4][0] == '/' :
             directory = '/' + parts[4]
          else :
             directory = parts[4]

       if filename != lst_filename or directory != lst_directory :
          print ""
          print("filename %s" % filename)
          print("directory %s" % directory)
          dir = directory

       lst_filename  = filename 
       lst_directory = directory

       msk=parts[1].replace('*','.*')
       msk = msk.replace('+','\+')
       if msk[-1] != '*' : msk = msk + '.*'
       print("accept %s" % msk )
       continue

    print "# ????? " + l
