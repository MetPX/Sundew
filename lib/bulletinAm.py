# -*- coding: iso-8859-1 -*-
# MetPX Copyright (C) 2004-2006  Environment Canada
# MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
# named COPYING in the root of the source directory tree.
#
# Author:
# 2004 - Louis-Phillippe Thériault.
#

"""Derived classs for AM protocol bulletins """

import time
import struct
import string
import curses
import curses.ascii
import bulletin

__version__ = '2.0'

class bulletinAm(bulletin.bulletin):
    __doc__ = bulletin.bulletin.__doc__ + \
    """
    Concrete Implementation of a bulletin class.

    Implantation pour un usage concret de la classe bulletin

            * information to pass to the constructor

            mapEntetes              dict (default=None)

                                    - a mapping of headers to stations.
                                      to build the key, take the first two
                                      letters of the header (ie. CA, RA )
                                      and concatenate the station. ie.
                                      CACYUL.  The value is what to add to 
                                      the header to complete it. 
                                      for an SP received from CZPC:
                                       TH["SPCZPC"] = "CN52 CWAO "
                                      
                                    - if None, leave header alone.

            SMHeaderFormat          bool (default=False)

                                    - If true, add "AAXX jjhhmm4\\n"
                                      to the second line of the bulletin. 

    """


    def __init__(self,stringBulletin,logger,lineSeparator='\n',mapEntetes=None,SMHeaderFormat=False):
        bulletin.bulletin.__init__(self,stringBulletin,logger,lineSeparator='\n')
        self.mapEntetes = mapEntetes
        self.SMHeaderFormat = SMHeaderFormat

    def doSpecificProcessing(self):
        __doc__ = bulletin.bulletin.doSpecificProcessing.__doc__ + \
        """AM specific processing.

        """
        self.replaceChar('\r','')

        unBulletin = self.bulletin

        if len(self.getHeader().split()) < 1:
        # If the first line is empty, bad bulletin, do nothing.
            bulletin.bulletin.verifyHeader(self)
            return

        # If the bulletin needs a new header and/or modification.
        if self.mapEntetes != None and len(self.getHeader().split()[0]) == 2:
            # Si le premier token est 2 lettres de long

            uneEnteteDeBulletin = None

            premierMot = self.getType()

            station = self.getStation()

            # Fetch de l'entête
            if station != None:
                # Construction de la cle
                if premierMot != "SP":
                    uneCle = premierMot + station
                else:
                    uneCle = "SA" + station

                # Fetch de l'entete a inserer
                # FIXME: default should be configurable in px.conf
                if premierMot in ["CA","MA","RA"]:
                    uneEnteteDeBulletin = "CN00 CWAO "
                else:
                    try:
                        uneEnteteDeBulletin = self.mapEntetes[uneCle]
                    except KeyError:
                    # L'entête n'a pu être trouvée
                        uneEnteteDeBulletin = None

            # build header
            if station != None and uneEnteteDeBulletin != None:
                if len(unBulletin[0].split()) == 1:
                    if premierMot == "CA" :
                       uneEnteteDeBulletin = premierMot + uneEnteteDeBulletin + self.getCaFormattedTime()
                    else:
                       uneEnteteDeBulletin = premierMot + uneEnteteDeBulletin + self.getFormattedSystemTime()
                elif len(unBulletin[0].split()) == 2:
                    uneEnteteDeBulletin = premierMot + uneEnteteDeBulletin + unBulletin[0].split()[1]
                else:
                    uneEnteteDeBulletin = premierMot + uneEnteteDeBulletin + unBulletin[0].split()[1] + ' ' + unBulletin[0].split()[2]

                # Apply the header to the bulletin.
                self.setHeader(uneEnteteDeBulletin)

                # Insert AAXX jjhhmm4 if needed (for SM/SI.)
                if self.SMHeaderFormat and self.getType() in ["SM","SI"]:
                    self.bulletin.insert(1, "AAXX " + self.getHeader().split()[2][0:4] + "4")

            if station == None or uneEnteteDeBulletin == None:
                if station == None:
                    self.setError("station missing from either configuration or bulletin")

                    self.logger.warning("station not found")
                    self.logger.warning("Bulletin:\n"+self.getBulletin())

                # Header not found in station configuration file, error.
                elif uneEnteteDeBulletin == None:
                    self.setError("header not found in stations configuration file")

                    self.logger.warning("Station <" + station + "> not found for prefix <" + premierMot + ">")
                    self.logger.warning("Bulletin:\n"+self.getBulletin())

        if self.getType() in ['UG','UK','US'] and self.bulletin[1] == '':
            self.bulletin.remove('')

        if self.bulletin[0][0] == '\x01':
            self.replaceChar('\x01','')
            self.replaceChar('\x03\x04','')

        if self.bulletin[0][:6] in ['RACN00']:
            self.replaceChar('\x02','')
            self.replaceChar('\x03','')
            self.replaceChar('\x04','')

        if self.bulletin[0][:4] in ['SACN']:
            self.replaceChar('\x0e','')
            self.replaceChar('\x0f','')


        bulletin.bulletin.verifyHeader(self)

    def getCaFormattedTime(self):
        """getFormattedSystemTime() -> heure

           heure:       String

           Return a string with the local system time.
           ddhhmm : day of month/hour(0-23h)/minutes

           Purpose:

               Generate the time stamp for a bulletin header.
        """

        try :
              year  = time.strftime("%Y",time.localtime())
              jul   = time.strftime("%j",time.localtime())
              hhmm  = 'x'

              yjul  = int(jul)-1
              yjul  = "%s"%yjul

              line  = self.bulletin[2]
              tok   = line.split(',')

              # this covers most common cases...
              # when it doesn't work use current date !
              # as the default was before

              case = 9
              if    tok[0] == year :
                                     case = 0
              elif  tok[1] == year :
                                     case = 1
              elif  tok[2] == year :
                 if tok[3] == jul  : case = 2
                 if tok[3] == yjul and jul != '1' : case = 2

              if case > 2 and jul == '1' :
                 yyear  = int(year)-1
                 yyear  = "%s"%yyear
                 if    tok[0] == yyear :
                                        case = 0
                 elif  tok[1] == yyear :
                                        case = 1
                 elif  tok[2] == yyear :
                    if tok[3] == '365' or tok[3] == '366' : case = 2

              if case <= 2 :
                 year = tok[case]
                 jul  = string.zfill( tok[case+1], 3 )
                 hhmm = string.zfill( tok[case+2], 4 )

              # FIX ME
              # if year not present, the jul day is "mostly" the second tok in 3rd line
              # this may not always be the case...
              else :
                 jul  = string.zfill( tok[1], 3 )
                 hhmm = string.zfill( tok[2], 4 )

              #self.logger.debug(" year jul hhmm = %s %s %s " % (year,jul,hhmm) )
              arrivalStr = year + jul + hhmm
              timeStruct = time.strptime(arrivalStr, '%Y%j%H%M')
              ddHHMM = time.strftime("%d%H%M",timeStruct)
        except :
              self.logger.warning("Was not able to get time from bulletin...took current time")
              ddHHMM = time.strftime("%d%H%M",time.localtime())

        return ddHHMM

    def getFormattedSystemTime(self):
        """getFormattedSystemTime() -> heure

           heure:       String

           Return a string with the local system time.
           ddhhmm : day of month/hour(0-23h)/minutes

           Purpose:

               Generate the time stamp for a bulletin header.
        """
        return time.strftime("%d%H%M",time.localtime())

    def verifyHeader(self):
        __doc__ = bulletin.bulletin.verifyHeader.__doc__ + \
        """
           Override to prevent header verification during instantiation.
        """
        return
