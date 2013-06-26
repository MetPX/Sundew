"""
#############################################################################################
# Name: RetransConfig.py
#
# Author: Daniel Lemay
#
# Date: 2008-03-11
#
# Description: pxRetrans config. reader
#
#############################################################################################
"""
import os, sys, os.path, re, time, pwd
import pxRetransLanguage
import PXPaths

langSel = {
'fra': pxRetransLanguage.french,
'eng': pxRetransLanguage.english,
}

class RetransConfig(object):
    def __init__(self):
        PXPaths.normalPaths()
        self.debug = 0
        self.lang = pxRetransLanguage.french

        # masterConfPath is a directory where configuration files for all clusters can be found.
        # With 2 cluster named cluster1 and cluster2, the config. files will be under:
        # "masterConfPath"/cluster1/etc/
        # "masterConfPath"/cluster2/etc/

        # When we have in fact no cluster (a single machine), the cluster name will be "." and we
        # we thus have "masterConfPath"/./etc/

        # This "scheme" works well when px is installled under a root directory (ex: /apps/px/)
        # It works less well under a Debian installation (where the all the config. files are under
        # /etc/px (not /etc/px/etc).
       
        # When installed with a debian package, a symbolic link will be created:
        # ln -s /etc/px $HOME/etc   ($HOME of the px user)
        try:
            self.masterConfPath = pwd.getpwnam('px')[5] # Master Configuration root path (1 machine, debian way)
        except:
            self.masterConfPath = '/apps/px'

        self.clusters = ['.']             # 1 machine only (no "real" clusters)
        #self.clusters = ['px', 'pxatx', 'pds']

        self.feEnvVar = 'PX_FRONTEND'
        self.sfeEnvVar = 'PX_SIMILI_FRONTEND'

        # Use to execute command (pxRetrans, .localRetrans) on the backend
        # via ssh command run on the frontend
        self.fePrivKey = ''   # Use to connect as beUser from fe to be
        self.beUser = 'px'    # Use to ssh from the frontend to the backend

        # Use to scp results from the backend to the frontend
        self.bePrivKey = ''
        self.feUser = 'px'        # On the backend, results (listing) will be sent to this frontend user
        self.feTempDir = '/tmp'   # On the backend, results (listing) will be sent to this directory

        self.waitTimeForLogEntry = 2 # Time we wait in seconds for obtaining the log line indicating a successful transfert

        self.readConfig(PXPaths.ETC + "px.conf")
        
    def readConfig(self, filename):
        from generalLib import isTrue

        try: 
            file = open(filename, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            if self.debug:
                print("Type: %s, Value: %s" % (type, value))
                print("File (%s) is not present") % filename
            return

        for line in file.readlines():
            words = line.split()
            if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)):
                try:
                    if words[0] == 'lang': self.lang = langSel.get(words[1], pxRetransLanguage.english)
                    elif words[0] == 'masterConfPath': self.masterConfPath = words[1]
                    elif words[0] == 'clusters': self.clusters = words[1].split(',')
                    elif words[0] == 'frontEndEnvVar': self.feEnvVar = words[1]
                    elif words[0] == 'similiFrontEndEnvVar': self.sfeEnvVar = words[1]

                    elif words[0] == 'frontEndPrivKey': 
                        if words[1] == "None":
                            self.fePrivKey = None
                        else:
                            self.fePrivKey = words[1]
                    elif words[0] == 'backEndUser': self.beUser = words[1]

                    elif words[0] == 'backEndPrivKey': 
                        if words[1] == "None":
                            self.bePrivKey = None
                        else:
                            self.bePrivKey = words[1]
                    elif words[0] == 'frontEndUser': self.feUser = words[1]
                    elif words[0] == 'frontEndTempDir': self.feTempDir = words[1]

                    elif words[0] == 'waitTimeForLogEntry': self.waitTimeForLogEntry = int(words[1])

                except:
                    (type, value, tb) = sys.exc_info()
                    print("Problem (%s, %s) with this line (%s) in configuration file of px.conf (pxRetrans section)" % (type, value, words))

    def printInfos(self):
        print("%s" % (80*"#"))
        #print('lang: %s' % self.lang)

        print('masterConfPath: %s' % self.masterConfPath) 
        print('clusters: %s' % self.clusters)

        print('feEnvVar: %s' % self.feEnvVar)
        print('sfeEnvVar: %s' % self.sfeEnvVar)

        print('fePrivKey: %s' % self.fePrivKey) 
        print('beUser: %s' % self.beUser)

        print('bePrivKey: %s' % self.bePrivKey) 
        print('feUser: %s' % self.feUser)
        print('feTempDir: %s' % self.feTempDir) 

        print('waitTimeForLogEntry: %s' % self.waitTimeForLogEntry)

        print("%s" % (80*"#"))

if __name__ == '__main__':
    config = RetransConfig()
    config.printInfos()
