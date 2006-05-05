"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Igniter.py
#
# Author: Daniel Lemay
#
# Date: 2005-02-25
#
# Description: Use to start, stop, restart and obtain status of any python program 
# 
# For an example of how this can be used, check the code example below
#
#   !/usr/bin/env python
#   import sys, Igniter
#
#   lockPath = '/apps/px/'
#
#   if len(sys.argv) != 2:
#       print "Usage: testIgnit.py {start | stop | status}"
#       sys.exit(2)
#   else: cmd = sys.argv[1]
#
#   if cmd in ['start', 'stop', 'status']:
#       igniter = Igniter.Igniter(cmd, lockPath)
#       eval("igniter." + cmd)()
#   else:
#       print "Wrong command!"
#       print "Usage: testIgnit.py {start | stop | status}"
#       sys.exit(2)
#   while True:
#       #real code goes here
#       pass
# 
#############################################################################################

"""
import sys, os, os.path, commands, signal

class Igniter:
   
   LOCK_NAME = ".lock"

   def __init__(self, cmd, lockPath):
      """
      This method could be "extended" for particular need in a subclass
      """
      self.cmd = cmd                                        # In ['start', 'stop', 'restart', 'status'] 
      self.pid = os.getpid()                                # Process ID
      self.lockpid = None                                   # Process ID in the .lock file
      self.lockPath = lockPath                              # Path where the lock file (.lock) is.
      self.lock = self.lockPath + "/" + Igniter.LOCK_NAME   # Full name of the lock file
      self.progName = sys.argv[0]                           # Program's name
      self.comingFromRestart = False

   def printComment(self, commentID):
      """
      Used to print status informations. This method can be overloaded in a 
      subclass if necessary
      """
      if commentID == 'Already start':
         print "WARNING: %s is already started with PID %d, use stop or restart!" % (self.progName, self.lockpid)
      elif commentID == 'Locked but not running':
         print "INFO: The program %s was locked, but not running! The lock has been unlinked!" % (self.progName)
      elif commentID == 'No lock':
         print "No lock on the program %s. Are you sure it was started?" % (self.progName)
      elif commentID == 'Restarted successfully':
         print "Program %s has been restarted successfully!" % (self.progName)
      elif commentID == 'Status, started':
         print "Program %s is running with PID %d" % (self.progName, self.lockpid)
      elif commentID == 'Status, not running':
         print "Program %s is not running" % (self.progName)
      elif commentID == 'Status, locked':
         print "Program %s is locked (PID %d) but not running" % (self.progName, self.lockpid)
     
   def start(self):
      """
      This method should be "extended" in a subclass if you want 
      to assign signals
      """
      if self.comingFromRestart:
         self.comingFromRestart = False

      """
      # Verify user is not root
      if os.getuid() == 0:
         print "FATAL: Do not start as root. It will be a mess!"
         sys.exit(2)
      """
      
      # If it is locked ... 
      if self.isLocked(): 
         # ... and running, exit!!
         if not commands.getstatusoutput('ps -p ' + str(self.lockpid))[0]:
            self.printComment('Already start')
            sys.exit(2)
         # ... and not running, delete the lock.
         else:
            self.printComment('Locked but not running')
            os.unlink(self.lock)
      
      if os.fork() == 0:
         # Not locked or locked but not running
         # we create the lock 
         self.makeLock()
      else:
         sys.exit()

   def stop(self):
      # If it is locked ...
      if self.isLocked():
         # ... and running
         if not commands.getstatusoutput('ps -p ' + str(self.lockpid))[0]:
            os.unlink(self.lock)
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

   def restart(self):
      self.comingFromRestart = True
      self.stop()
      self.start()
      #self.printComment('Restarted successfully') 

   def status(self):
      # If it is locked ... 
      if self.isLocked(): 
         # ... and running
         if not commands.getstatusoutput('ps -p ' + str(self.lockpid))[0]:
            self.printComment('Status, started')
         # ... and not running, delete the lock.
         else:
            self.printComment('Status, locked')
      # If it is unlocked 
      else:
         self.printComment('Status, not running')
      sys.exit()

   def isLocked(self):
      if os.path.exists(self.lock):
         lockFile = open(self.lock, 'r')
         try: 
            self.lockpid = int(lockFile.read())
         except:
	    self.printComment('lockfile corrupt, removing')
            os.unlink(self.lock)
	    self.lockpid = False
         lockFile.close()
         return self.lockpid
      else:
         return False

   def makeLock(self):
      if not os.path.exists(self.lockPath):
         os.makedirs(self.lockPath, 01775)
      self.pid = os.getpid()    
      lockFile = open(self.lock, 'w')
      lockFile.write(repr(self.pid))
      self.lockpid = self.pid
      lockFile.close()
