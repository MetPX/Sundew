# -*- coding: iso-8859-1 -*-
"""A class to process BUFR messages."""

import array, time
import string, traceback, sys

__version__ = '1.0'

class Bufr:
    """This class is a very basic BUFR processing.

    end()    returns where the BUFR message ends
    start()  returns where the BUFR message starts
    length() the length according to the bufr's header.
    validate() make sure the messages looks ok...

    Auteur: Michel Grenier
    Date:   Mars   2006
    """

    def __init__(self,stringBulletin):
        self.bulletin = stringBulletin

        self.set(stringBulletin)

    def set(self,stringBulletin):
        self.bulletin = stringBulletin

        self.begin = -1
        self.last  = -1
        self.len   = -1
        self.valid = True

        self.validate()

    def end(self):
        """check that the end is ok and return its position
        """

        e = self.begin + self.len - 1;

        if self.bulletin[e-4:e] != "7777" :
           self.valid = False
           return -1

        self.last = e

        return e

    def length(self):
        """return the length of the BUFR message
        """

        if not self.valid :
           return -1

        b = self.begin

        a = array.array('B',self.bulletin[b+4:b+7])

        l  = 0;
        l += l * 256 + int(a[0])
        l += l * 256 + int(a[1])
        l += l * 256 + int(a[2])

        if l > len(self.bulletin[b:]) :
           self.valid = False
           return -1

        self.len = l

        return l

    def start(self):
        """return the position where the BUFR message starts 
        """

        self.begin = self.bulletin.find('BUFR')

        if self.begin == -1 : self.valid = False

        return self.begin

    def validate(self):
        """Verifie que tout semble correct avec le BUFR
        """

        if self.bulletin == None : return False

        self.start()
        self.length()
        self.end()

        return self.valid

import sys, os, os.path, time, stat

if __name__=="__main__":
   pass
