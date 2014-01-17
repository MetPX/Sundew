#
#  MG  RWIN BC PULL  for migration of RWIN acquisition to CMC
#      Sept 2011
#
import sys, os, os.path, time, stat, string

# this pull implements the regular WGET with user password to BC
# getting RWIN files

class Puller(object):

      def __init__(self) :
          # give 2 mins before cycle for pull time
          self.margin = 60
          # a cycle is 1200 secs = 20 mins between pulls
          self.cycle  = 1200

      def renamer(self,flow):
          now            = time.localtime()
          YYYYMMDDhhmmss = time.strftime('%Y%m%d%H%M%S',now)

          opath = "/apps/px/rxq/"+flow.name
          opath = opath + "/OB.BC.MOT.BC_GRP."
          opath = opath + YYYYMMDDhhmmss + '.cmml'

          return opath

      def pull(self, flow, logger, sleeping ):

          files = []

          # if pull is sleeping and we delete files... nothing to do
          if sleeping : return files

          # wait 2 minutes to the hour
          self.wait_next_list(logger)

          # wakeup and pull the file
          logger.info("pull %s is waking up" % flow.name )

          # build url, and get user and password

          dirget_lst = flow.pulls[0]
          directory  = dirget_lst[0]
          self.url   = flow.protocol + '://' + flow.host + directory

          try :
                 opath = self.renamer(flow)

                 data  = self.wget(self.url,flow.user,flow.passwd)

                 f = open(opath,'w')
                 f.write(data)
                 f.close()

                 files.append(opath)

                 # sleep to complete the cycle
                 time.sleep(self.margin)

                 return files

          except :
                 logger.error("PROBLEM")
                 pass

          return files

      def wait_next_cycle(self,logger) :
          now   = time.localtime()
          epoch = time.mktime(now)

          e_cycle       = int(epoch/self.cycle)
          e_next_cycle  = (e_cycle + 1) * self.cycle
          sleep_tocycle =  e_next_cycle - epoch - self.margin

          if sleep_tocycle < 0 : return
          logger.info("pull will sleep for %d sec" % sleep_tocycle )
          time.sleep(sleep_tocycle)

      def wait_next_list(self,logger) :
          listm = [10,20,40,59]

          now   = time.localtime()
          epoch = time.mktime(now)
          e_min = int(epoch/60) 
          minhr = e_min % 60 

          if minhr    < 10 :
             e_target = 10
          elif minhr  < 20 :
             e_target = 20
          elif minhr  < 40 :
             e_target = 40
          elif minhr  < 59 :
             e_target = 59

          e_next_epoch  = (e_min + e_target - minhr) * 60
          sleep_toepoch =  e_next_epoch - epoch

          if sleep_toepoch < 0 : return
          logger.info("pull will sleep for %d sec" % sleep_toepoch )
          time.sleep(sleep_toepoch)

      def wget(self,url,user=None,password=None) :
          import urllib2
      
          # the simplest, simply get the html source from URL
      
          if user == None :
             sock       = urllib2.urlopen(url)
             htmlSource = sock.read()
             return htmlSource
      
          # a little more complicated, need to authenticate
      
          # create a password manager
          # Add the username and password.
      
          password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
          password_mgr.add_password(None, url, user, password )
          handler = urllib2.HTTPBasicAuthHandler(password_mgr)
      
          # create "opener" (OpenerDirector instance)
      
          opener = urllib2.build_opener(handler)
      
          # use the opener to fetch a URL
      
          opener.open(url)
      
          # Install the opener.
          # Now all calls to urllib2.urlopen use our opener.
      
          urllib2.install_opener(opener)
      
          # now  get the html source from URL
      
          sock       = urllib2.urlopen(url)
          htmlSource = sock.read()
          return htmlSource
  
puller=Puller()
self.pull_script=puller.pull
