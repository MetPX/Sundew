"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: Logger.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-28
#
#############################################################################################

import sys, logging, logging.handlers, fnmatch

def funcToMethod(func, clas, method_name=None):
   setattr(clas, method_name or func.__name__, func)
   
def exception(self, message):
   self.log(logging.EXCEPTION, message)

def veryverbose(self, message):
   self.log(logging.VERYVERBOSE, message)

def veryveryverbose(self, message):
   self.log(logging.VERYVERYVERBOSE, message)

class Logger:

   def __init__(self, logname, log_level, loggername):
       
      # Standard error is redirected in the log
      # FIXME: Potential problem when rotating occurs
      if not fnmatch.fnmatch(logname, '*.log.notb'):
        sys.stderr = open(logname, 'a')

      # Custom levels
      logging.addLevelName(45, 'EXCEPTION')
      logging.EXCEPTION = 45
      funcToMethod(exception, logging.Logger)

      logging.addLevelName(5, 'VERYVERBOSE')
      logging.VERYVERBOSE = 5
      funcToMethod(veryverbose, logging.Logger)

      logging.addLevelName(3, 'VERYVERYVERBOSE')
      logging.VERYVERYVERBOSE = 3
      funcToMethod(veryveryverbose, logging.Logger)

      #fmt = logging.Formatter("%(levelname)-8s %(asctime)s %(name)s %(message)s")
      #fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s","%x %X")
      fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
      #hdlr = logging.handlers.RotatingFileHandler(logname, "a", 1000000, 3)  # Max 100000 bytes, 3 rotations
      hdlr = logging.handlers.TimedRotatingFileHandler(logname, when='midnight', interval=1, backupCount=5) 
      hdlr.setFormatter(fmt)

      self.logger = logging.getLogger(loggername)
      self.logger.setLevel(eval("logging." + log_level))                     # Set logging level
      self.logger.addHandler(hdlr)

      #print logging.getLevelName(5)
      #print logging.getLevelName(3)

   def getLogger(self):
      return self.logger 

if (__name__ == "__main__"):
   """
   Note: There is a bug with logger.exception("This is an exception") => A None entry is added in the log???
   """
   
   bad = "This is BAD!"

   logger = Logger("/apps/px/toto.log", "VERYVERYVERBOSE", "CMISX")
   logger = logger.getLogger()

   """
   logger.debug("Ceci est un debug")
   logger.info("Ceci est un info")
   logger.warning("Ceci est un warning!")
   logger.error("Ceci est un error!")
   logger.critical("Ceci est un critical!")
   """

   #logger.log(5, "Ceci est veryverbose")
   #logger.log(logging.DEBUG, "Ceci est un debug")

   logger.exception("Ceci est exception")
   logger.veryverbose("Ceci est veryverbose")
   logger.veryveryverbose("Ceci est veryveryverbose")

   """
   try:
      raise bad

   except bad:   
      print "Bad exception has been raised"
      logger.exception("Ceci est un exception!")
   """
