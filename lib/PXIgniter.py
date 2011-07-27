"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PXIgniter.py
#
# Author: Daniel Lemay
#
# Date: 2005-03-02
#
# Description: Use to start, stop, restart, reload and obtain status informations
#              about receivers and senders.
#
#############################################################################################

"""
import sys, os, time, commands, signal
from Igniter import Igniter
from Client import Client

class PXIgniter(Igniter):
   
   def __init__(self, direction, flowName, cmd, lockPath, logger=None):
      Igniter.__init__(self, cmd, lockPath) # Parent constructor
      self.direction = direction            # A string in ['sender', 'receiver']
      self.flowName = flowName              # Client or Source's name
      self.logger = logger                  # Logger object
      self.type = None                      # wmo, am, etc. (string)
      self.flow = None                      # Client or Source object
      self.gateway = None                   # Gateway object
      self.reloadMode = False               # Indicate if we are in reload mode or not

      eval("self." + cmd)()                 # Execute the command directly

   def setGateway(self, gateway):
      self.gateway = gateway
      #print "Gateway is: " + repr(gateway)

   def setFlow(self, flow):
      self.flow = flow
      self.type = self.flow.type
      #print "Flow is: " + repr(flow)
        
   def printComment(self, commentID):
      if commentID == 'Already start':
         print "WARNING: The %s %s is already started with PID %d, use stop or restart!" % (self.direction, self.flowName, self.lockpid)
      elif commentID == 'Locked but not running':
         print "INFO: The %s %s was locked, but not running! The lock has been unlinked!" % (self.direction, self.flowName)
      elif commentID == 'No lock':
         print "No lock on the %s %s. Are you sure it was started?" % (self.direction, self.flowName)
      elif commentID == 'Restarted successfully':
         print "%s %s has been restarted successfully!" % (self.direction.capitalize(), self.flowName)
      elif commentID == 'Status, started':
         print "%s %s is running with PID %d" % (self.direction.capitalize(), self.flowName, self.lockpid)
      elif commentID == 'Status, not running':
         print "* %s %s is not running" % (self.direction, self.flowName)
      elif commentID == 'Status, locked':
         print "** %s %s is locked (PID %d) but not running" % (self.direction, self.flowName, self.lockpid)

   def start(self):
      
      Igniter.start(self)

      # Signals assignment
      signal.signal(signal.SIGTERM, self._shutdown)
      signal.signal(signal.SIGINT, self._shutdown)
      signal.signal(signal.SIGHUP, self._reload)
      self.logger.info("%s %s has been started" % (self.direction.capitalize(), self.flowName))

   def stop(self):
      # If it is locked ...
      if self.isLocked():
         # ... and running
         if not commands.getstatusoutput('ps -p ' + str(self.lockpid))[0]:
            os.unlink(self.lock)
            os.kill(self.lockpid, signal.SIGTERM)
            # if a sender is responsive to sigterm... after .5 sec force sigkill 
            if self.direction == 'sender' :
               time.sleep(0.5)
               if not commands.getstatusoutput('ps -p ' + str(self.lockpid))[0]:
                  self.logger.info("%s %s (sigkill) has been stopped" % (self.direction.capitalize(), self.flowName))
                  os.kill(self.lockpid, signal.SIGKILL)

         # ... and not running
         else:
            self.printComment('Locked but not running')
            os.unlink(self.lock)

      # If it is unlocked 
      else:
         self.printComment('No lock')
         sys.exit()
      
      # Bye bye if stop is called directly
      if not self.comingFromRestart:
         sys.exit() 

   def _shutdown(self, sig, stack):
      """
      Do the real work here.
      """
      #print "shutdown() has been called"
      self.logger.info("%s %s (type: %s) has been stopped" % (self.direction.capitalize(), self.flowName, self.type))
      os.kill(self.lockpid, signal.SIGKILL)

   def _reload(self, sig, stack):
      """
      Do the real work here. Depends of type of sender/receiver
      """
      if self.gateway is None:
         # Because we don't have a gateway object, it means that we can only reread the configuration
         # file of the source/client, not particular files like Circuit and Stations, because
         # they haven't been read at this time anyway.

         # If we are there, it is because we don't have a gateway object, if means that we are 
         # waiting for a connection, the easiest way to reread the configuration file of 
         # the sources/clients AND the value of the variables in the configuration file of this
         # particular source/client is by restarting it!

         #self.logger.info("ppid=%s, pid=%s, pgid=%s, sid=%s, cterm=%s" % (os.getppid(), os.getpid(), os.getpgrp(), os.getsid(os.getpid()), os.ctermid()))
         #output = commands.getoutput('ls -alrt /proc/%s/fd' % os.getpid())
         #self.logger.info(output)

         if os.fork() == 0:
            for fd in range(3,10):
                try:
                    os.close(fd)
                except OSError:
                    pass
            
            import PXPaths
            PXPaths.normalPaths()

            appName = 'px' + self.direction.capitalize()

            os.execl(PXPaths.BIN + appName, appName, self.flowName, 'restart')
         else:
            pass
      else:
         #print self.gateway
         if self.direction == 'sender':
            self.reloadMode = True

         elif self.direction == 'filter':
            self.reloadMode = True

         elif self.direction == 'receiver':
            if self.type == 'am':
               # FIXME: Should be put in amReceiver code
               # We assign the defaults, reread configuration file for the source 
               # and reread all configuration file for the clients (all this in __init__)
               self.flow.__init__(self.flow.name, self.flow.logger)

               self.gateway.unBulletinManager.extension = self.flow.extension
               self.gateway.unBulletinManager.addSMHeader = self.flow.addSMHeader
               #print self.flow
               #print "ext: %s" % (self.flow.extension)
               #print "addSM: %s" % (self.flow.addSMHeader)
               # Reset all the clients + sourlients names to which px can link (independantly of the routing table)
               self.gateway.unBulletinManager.drp.pxLinkables = self.flow.ingestor.allNames 
               # Reparse the ROUTING_TABLE
               self.gateway.unBulletinManager.drp.reparse()
               self.gateway.unBulletinManager.reloadMapEntetes(self.gateway.pathFichierStations)
               self.logger.info("%s has been reloaded" % self.direction.capitalize())
            if self.type == 'wmo':
               # FIXME: Should be put in wmoReceiver code
               # We assign the defaults, reread configuration file for the source 
               # and reread all configuration file for the clients (all this in __init__)
               self.flow.__init__(self.flow.name, self.flow.logger)

               self.gateway.unBulletinManager.extension = self.flow.extension
               # Reset all the clients + sourlients names to which px can link (independantly of the routing table)
               self.gateway.unBulletinManager.drp.pxLinkables = self.flow.ingestor.allNames 
               # Reparse the ROUTING_TABLE
               self.gateway.unBulletinManager.drp.reparse()
               self.logger.info("%s has been reloaded" % self.direction.capitalize())

            if self.type == 'collector' :
               self.reloadMode = True

            if self.type == 'single-file' or self.type == 'bulletin-file':
               self.reloadMode = True

            if self.type == 'pull-bulletin' or self.type == 'pull-file':
               self.reloadMode = True

         elif self.direction == 'transceiver':
            if self.type == 'aftn':
                #if os.fork() == 0:
                #    self.restart()
                #    self.logger.info("%s %s has been reloaded by restarting it" % (self.direction.capitalize(), self.flow.name))
                #else:
                #    pass
               # FIXME: Should be put in TransceiverAFTN code
               # We assign the defaults, reread configuration file for the sourlient 
               # and reread all configuration file for the clients (all this in __init__)
               self.flow.__init__(self.flow.name, self.flow.logger)
               self.gateway.mm.reloadMode = True 
               self.gateway.mm.__init__(self.flow.logger, self.flow, True)

               #self.gateway.mm.bullManager.extension = self.flow.extension
               # Reset all the clients + sourlients names to which px can link (independantly of the routing table)
               #self.gateway.mm.bullManager.drp.pxLinkables = self.flow.ingestor.allNames 
               #self.gateway.mm.drp = self.gateway.mm.bullManager.drp
               # Reparse the ROUTING_TABLE
               #self.gateway.unBulletinManager.drp.reparse()
               self.logger.info("%s has been reloaded" % self.direction.capitalize())
                
      
   def reload(self):
      """
      If the process is locked (presence of a .lock file) and running (ps), send a SIGHUP
      signal to it. The function _reload will be called because SIGHUP signal is assigned 
      to it.
      """
      # Verify user is not root
      if os.getuid() == 0:
         print "FATAL: Do not reload as root. It will be a mess."
         sys.exit(2)
         
      if Igniter.isLocked(self) and not commands.getstatusoutput('ps -p ' + str(self.lockpid))[0]:
         # SIGHUP is sent to initiate the reload
         os.kill(self.lockpid, signal.SIGHUP) 
      else:
         print "No process to reload for %s (%s %s)!" % (self.flowName, self.direction, self.type)

      # In any case, we exit!!
      sys.exit(2)

if __name__ == "__main__":

   pass
