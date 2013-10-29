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

import os, sys, logging, logging.handlers, fnmatch, stat,time

def funcToMethod(func, clas, method_name=None):
    setattr(clas, method_name or func.__name__, func)
   
def exception(self, message):
    self.log(logging.EXCEPTION, message)

def veryverbose(self, message):
    self.log(logging.VERYVERBOSE, message)

def veryveryverbose(self, message):
    self.log(logging.VERYVERYVERBOSE, message)

class Logger:

    def __init__(self, logname, log_level, loggername, bytes=False):
       
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
        if bytes:
            hdlr = logging.handlers.RotatingFileHandler(logname, "a", bytes, 3)  # Max bytes, 3 rotations
        else:
            hdlr = logging.handlers.TimedRotatingFileHandler(logname, when='midnight', interval=1, backupCount=5) 
        hdlr.setFormatter(fmt)

        self.logger = logging.getLogger(loggername)
        self.logger.setLevel(eval("logging." + log_level))                     # Set logging level
        self.logger.addHandler(hdlr)

        self.logmon = LoggerMonitor(self.logger)
        #print logging.getLevelName(5)
        #print logging.getLevelName(3)

    def getLogger(self):
        return self.logmon 

    def setBackupCount(self, backupCount=5):
	self.logger.handlers[0].backupCount=backupCount



#############################################################################################
#
# Michel Grenier Fev 2012
#
# LoggerMonitor classes
# interlace Logging and monitoring together
# monitor captures some events and logs them.
# When ingesting,delivering or when errors occur
# a loggerMonitor module is called
#
#############################################################################################

class LoggerMonitor:
    def __init__(self, logger):
        self.flow        = None
        self.logger      = logger
        self.tbegin      = 0

        self.setLevel   = logger.setLevel
        self.debug      = logger.debug
        self.info       = logger.info
        self.warning    = logger.warning
        self.error      = logger.error
        self.exception  = logger.exception
        self.critical   = logger.critical
   
        self.exception        = logger.exception
        self.veryverbose      = logger.veryverbose
        self.veryveryverbose  = logger.veryveryverbose

    def start_timer(self):
        self.tbegin = time.time()

    def delivered(self,infostr,ifile=None,fsiz=None):

        if ifile == None :
           self.info(infostr)
           return

        tend  = time.time()

        lstat = os.stat(ifile)
        ftim  = lstat[stat.ST_MTIME]

        if fsiz == None : 
           fsiz = lstat[stat.ST_SIZE]

        speed = 0.0
        dtim  = tend - self.tbegin
        if dtim > 0.0 : speed = fsiz/dtim

        latency = tend - ftim

        self.info("%s (lat=%f,speed=%f)" % (infostr,latency,speed) )


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
