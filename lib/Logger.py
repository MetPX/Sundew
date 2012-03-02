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

    def setFlow(self,flow):
        self.logmon.monitor.flow = flow
        

#############################################################################################
#
# Michel Grenier Fev 2012
#
# Monitor and LoggerMonitor classes
# interlace Logging and monitoring together
# monitor captures logging events creating a file
# showing the immediate state of the process
#
#############################################################################################

# all the calls from a logger are supported and
# passed to the logger... some arguments for monitoring purposes
# are added when the module is envoked. The module will catch
# and remove the extra arguments... passing regular args to the logger call


class Monitor:

    def __init__(self, logger):
        self.logger = logger
        self.flow   = None

    def process(self, msg, kwargs):
        return msg, kwargs

    def debug(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        self.logger.critical(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        self.logger.log(level, msg, *args, **kwargs)

class LoggerMonitor:
    def __init__(self, logger):
        self.logger   = logger
        self.monitor  = Monitor(logger)

        self.debug    = logger.debug
        self.info     = logger.info
        self.warning  = logger.warning
        self.error    = logger.error
        self.critical = logger.critical
        self.log      = logger.log

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

# d1,d2,d3,d4,tbegin = os.times()
#
# d1,d2,d3,d4,tend   = os.times()
#
# tspan = tend - tbegin
# if tspan >= 1.0 : 
#    tspan  = tspan * 1024.0
#    tspeed = nbBytes/tspan
#    self.logger.debug("Speed %f Kb/s" % tspeed)

# if  not time.time() - os.stat(file)[ST_MTIME] > self.mtime:
# nbBytes = os.stat(file)[stat.ST_SIZE] 
#ST_MODE  = 0
#ST_INO   = 1
#ST_DEV   = 2
#ST_NLINK = 3
#ST_UID   = 4
#ST_GID   = 5
#ST_SIZE  = 6
#ST_ATIME = 7
#ST_MTIME = 8
#ST_CTIME = 9
