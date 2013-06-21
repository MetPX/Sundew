import os, sys

# MG python3 compatible

def daemonize():
   try:
      pid = os.fork()
   except OSError as e:
      raise Exception( "fork #1 failed: %s [%d]" % (e.strerror, e.errno))

   if (pid == 0):
      os.setsid()
      try:
         pid = os.fork() 
      except OSError as e:
         raise Exception( "fork #2 failed: %s [%d]" % (e.strerror, e.errno))

      if (pid == 0):   
         os.chdir('/')
         os.umask(0)
      else:
         os._exit(0) 
   else:
      os._exit(0)  

   os.close(sys.stdin.fileno())
   os.close(sys.stdout.fileno())
   #os.close(sys.stderr.fileno())

   os.open('/dev/null', os.O_RDWR)  # stdin
   os.dup2(0, 1)                    # stdout

   return(0)

if __name__ == "__main__":
    pass
