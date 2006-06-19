"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: AlarmFTP.py
#
# Authors: 
#          Michel Grenier (from a web inspiration)
#
#############################################################################################

"""
import  signal,socket


class FtpTimeoutException(Exception):
    """Classe d'exception sp�cialis�s au ftp timeout"""
    pass

class AlarmFTP:
      def __init__(self, message ):
          self.state   = False
          self.message = message
      def sigalarm(self, n, f):
          raise FtpTimeoutException(self.message)
      def alarm(self, time):
          self.state = True
          signal.signal(signal.SIGALRM, self.sigalarm)
          signal.alarm(time)
      def cancel(self):
          signal.alarm(0)
          self.state = False
