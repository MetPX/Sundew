"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Client.py
#
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#          Michel Grenier (directory path with patterns)
#                         (directory path mkdir if doesn't exist)
#                         (maxLength for segmentation when needed)
#
# Date: 2005-01-10 (Initial version by PS)
#       2005-08-21 (OO version by DL)
#       2005-11-01 (Path stuff by MG)
#
# Description:
#
#############################################################################################

"""
import sys, os, re, time, fnmatch
import PXPaths
from URLParser import URLParser
from Logger import Logger
#from Flow import Flow

PXPaths.normalPaths()              # Access to PX paths

class Client(object):

    def __init__(self, name='toto', logger=None) :

        #Flow.__init__(self, name, 'sender', type, batch) # Parent constructor

        # General Attributes
        self.name = name                          # Client's name
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'tx_' + name + '.log', 'INFO', 'TX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger
        self.logger.info("Initialisation of client %s" % self.name)
        self.debug = False                        # If we want sections with debug code to be executed
        self.host = 'localhost'                   # Remote host address (or ip) where to send files
        self.type = 'single-file'                 # Must be in ['single-file', 'bulletin-file', 'file', 'am', 'wmo', 'amis']
        self.protocol = None                      # First thing in the url: ftp, file, am, wmo, amis
        self.batch = 100                          # Number of files that will be read in each pass
        self.timeout = 10                         # Time we wait between each tentative to connect
        self.maxLength = 0                        # max Length of a message... limit use for segmentation, 0 means unused

        self.validation = True                    # Validation of the filename (prio + date)

        self.purge = None                         # Purge instructions (ex: 7H,4+:10H,3)
        self.purgeAliases = {}                    # Purge Aliases
        #self.purgeAliases['TEST'] = '8H,4+:18H,3' # Purge priority 4,5 older than 10 hours and priority 3 older than 18 hours

        self.purgeInst = []                       # Purge instructions parsed 

        self.patternMatching = True               # Verification of the accept and reject mask of the client before sending a file
        self.nodups = True                        # Check if the file has already been sent (md5sum present in the cache)
        self.mtime = 0                            # Integer indicating the number of seconds a file must not have
                                                  # been touched before being picked

        self.sorter = 'MultiKeysStringSorter'     # Class (or object) used to sort
        self.masks = []                           # All the masks (accept and reject)
        self.masks_deprecated = []                # All the masks (imask and emask)
        self.url = None
        self.collection = None                    # Client do not participate in the collection effort

        # Socket Attributes
        self.port = None                    # Port number
        self.keepAlive = True               # TCP SO_KEEPALIVE on (True) or off(False)

        # Am destination thread Attributes
        self.am_dest_thread = None                # assign a destination thread number to a specific bulletin header

        # Files Attributes
        self.user = None                    # User name used to connect
        self.passwd = None                  # Password 
        self.ssh_keyfile = None             # ssh private key file for sftp protocol
        self.ftp_mode = 'passive'           # Default is 'passive', can be set to 'active'
        self.dir_mkdir = False              # Verification and creation of directory inside ftp...
        self.dir_pattern = False            # Verification of patterns in destination directory

        self.chmod = 666                    # when the file is delevered chmod it to this value
        self.timeout_send = 0               # Timeout in sec. to consider a send to hang ( 0 means inactive )
        self.lock = '.tmp'                  # file send with extension .tmp for lock
                                            # if lock == "umask" than use umask 777 to put files

        self.destfn_script = None           # a script to rename the file for client
        self.execfile      = None

        self.dx_script     = None           # a script to convert the file for client
        self.fx_script     = None           # a script to convert the file for client
        self.execfile2     = None
        self.execfile3     = None

        self.send_script   = None           # a script to send a list of files
        self.execfile4     = None

        # All defaults for a source were set earlier in this class
        # But some of them may have been overwritten in the px.conf file
        # Load the px.conf stuff related to the source

        pxconf_Path = PXPaths.ETC + 'px.conf'
        if os.path.isfile(pxconf_Path) : self.readConfigFile( pxconf_Path, '.', 'WHATFN' )

        # read in the config

        self.readConfig()

        if self.execfile != None :
           try    : execfile(PXPaths.SCRIPTS + self.execfile )
           except : self.logger.error("Problem with destfn_script %s" % self.execfile)

        if self.execfile2 != None :
           try    : execfile(PXPaths.SCRIPTS + self.execfile2 )
           except : self.logger.error("Problem with fx_script %s" % self.execfile2)

        if self.execfile3 != None :
           try    : execfile(PXPaths.SCRIPTS + self.execfile3 )
           except : self.logger.error("Problem with dx_script %s" % self.execfile3)

        if self.execfile4 != None :
           try    : execfile(PXPaths.SCRIPTS + self.execfile4 )
           except : self.logger.error("Problem with send_script %s" % self.execfile4)

        #self.printInfos(self)

    def parsePurgeInstructions(self, line):
        # '10H,4+:18H,3'
        MINUTE = 60
        HOUR = 60 * MINUTE

        newInst = []

        instructions = line.strip().split(':')
        for instruction in instructions:
            hours, pri = instruction.strip().split(',')    
            hours.strip(), pri.strip()
            sec = int(hours[:-1]) * HOUR
            if pri[-1] == '+':
                pri = range(int(pri[:-1]), 6)
            elif int(pri) in [1,2,3,4,5]:
                pri = [int(pri)]
            newInst.append((sec,pri))

        self.purgeInst = newInst

    def readConfig(self):
        currentDir = '.'                # Current directory
        currentFileOption = 'WHATFN'    # Under what filename the file will be sent (WHATFN, NONE, etc., See PDS)
        fileName = PXPaths.TX_CONF +  self.name + '.conf'
        #print filePath
        self.readConfigFile(fileName,currentDir,currentFileOption)

    def readConfigFile(self,filePath,currentDir,currentFileOption):
        
        def isTrue(s):
            if  s == 'True' or s == 'true' or s == 'yes' or s == 'on' or \
                s == 'Yes' or s == 'YES' or s == 'TRUE' or s == 'ON' or \
                s == '1' or  s == 'On' :
                return True
            else:
                return False

        def stringToOctal(string):
            if len(string) != 3:
                return 0644
            else:
                return int(string[0])*64 + int(string[1])*8 + int(string[2])

        try:
            config = open(filePath, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value))
            return 

        for line in config.readlines():
            words = line.split()
            if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)):
                try:
                    if   words[0] == 'accept':
                         cmask       = re.compile(words[1])
                         cFileOption = currentFileOption
                         if len(words) > 2: cFileOption = words[2]
                         self.masks.append((words[1], currentDir, cFileOption, cmask, True))
                    elif words[0] == 'reject':
                         cmask = re.compile(words[1])
                         self.masks.append((words[1], currentDir, currentFileOption, cmask, False))

                    elif words[0] == 'imask': self.masks_deprecated.append((words[1], currentDir, currentFileOption))  
                    elif words[0] == 'emask': self.masks_deprecated.append((words[1],))

                    elif words[0] == 'directory': currentDir = words[1]
                    elif words[0] == 'filename': currentFileOption = words[1]
                    elif words[0] == 'include':
                        fileName = PXPaths.TX_CONF + words[1]
                        self.readConfigFile(fileName,currentDir,currentFileOption)
                    elif words[0] == 'destination':
                        self.url = words[1]
                        urlParser = URLParser(words[1])
                        (self.protocol, currentDir, self.user, self.passwd, self.host, self.port) =  urlParser.parse()
                        if len(words) > 2:
                            currentFileOption = words[2]
                    elif words[0] == 'validation': self.validation =  isTrue(words[1])
                    elif words[0] == 'purgeAlias':
                        self.purgeAliases[words[1]] = words[2]
                    elif words[0] == 'purge':
                        try:
                            self.purge = self.purgeAliases[words[1]]
                            self.parsePurgeInstructions(self.purgeAliases[words[1]])
                        except:
                            self.purge = words[1]
                            self.parsePurgeInstructions(words[1])

                    elif words[0] == 'noduplicates': self.nodups =  isTrue(words[1])
                    elif words[0] == 'patternMatching': self.patternMatching =  isTrue(words[1])
                    elif words[0] == 'keepAlive': self.keepAlive =  isTrue(words[1])
                    elif words[0] == 'mtime': self.mtime = int(words[1])
                    elif words[0] == 'sorter': self.sorter = words[1]
                    elif words[0] == 'type': self.type = words[1]
                    elif words[0] == 'protocol': self.protocol = words[1]
                    elif words[0] == 'maxLength': self.maxLength = int(words[1])
                    elif words[0] == 'host': self.host = words[1]
                    elif words[0] == 'port': self.port = int(words[1])
                    elif words[0] == 'user': self.user = words[1]
                    elif words[0] == 'password': self.passwd = words[1]
                    elif words[0] == 'ssh_keyfile': self.ssh_keyfile = words[1]
                    elif words[0] == 'batch': self.batch = int(words[1])
                    elif words[0] == 'debug' and isTrue(words[1]): self.debug = True
                    elif words[0] == 'timeout': self.timeout = int(words[1])
                    elif words[0] == 'chmod': self.chmod = int(words[1])
                    elif words[0] == 'timeout_send': self.timeout_send = int(words[1])
                    elif words[0] == 'lock': self.lock = words[1]
                    elif words[0] == 'ftp_mode': self.ftp_mode = words[1]
                    elif words[0] == 'dir_pattern': self.dir_pattern =  isTrue(words[1])
                    elif words[0] == 'dir_mkdir': self.dir_mkdir =  isTrue(words[1])
                    elif words[0] == 'destfn_script': self.execfile = words[1]
                    elif words[0] == 'fx_script': self.execfile2 = words[1]
                    elif words[0] == 'dx_script': self.execfile3 = words[1]
                    elif words[0] == 'send_script': self.execfile4 = words[1]

                    elif words[0] == 'am_dest_thread':
                         if self.am_dest_thread == None : self.am_dest_thread = {}
                         self.am_dest_thread[words[1]] = int(words[2])

                except:
                    self.logger.error("Problem with this line (%s) in configuration file of client %s" % (words, self.name))

        if not self.validation:
            self.sorter = 'None'    # Must be a string because eval will be subsequently applied to this

        config.close()
    
        #self.logger.debug("Configuration file of client %s has been read" % (self.name))

    def run_destfn_script(self, filename): 
        if self.destfn_script == None : return filename
        return self.destfn_script(filename)

    def run_dx_script(self, data, logger): 
        if self.dx_script == None : return data
        return self.dx_script(data, logger)

    def run_fx_script(self, filename, logger): 
        if self.fx_script == None : return filename
        return self.fx_script(filename, logger)

    def _getMatchingMask(self, filename): 

        # check for deprecated use
        if len(self.masks_deprecated) > 0 :
           for mask in self.masks_deprecated:
               if fnmatch.fnmatch(filename, mask[0]):
                  try:
                          if mask[2]:
                             return mask
                  except:
                          return None

        # new regexp mask usage
        for mask in self.masks:
            if mask[3].match(filename) :
               if mask[4] : return mask
               return None

        return None

    def getDestInfos(self, filename):
        """
        WHATFN         -- First part (':') of filename 
        HEADFN         -- Use first 2 fields of filename
        NONE           -- Use the entire filename
        TIME or TIME:  -- TIME stamp appended
        DESTFN=fname   -- Change the filename to fname

        ex: mask[2] = 'NONE:TIME'
        """
        mask = self._getMatchingMask(filename)
        if mask:
            timeSuffix   = ''
            satnet       = ''
            parts        = filename.split(':')
            firstPart    = parts[0]
            destFileName = filename
            for spec in mask[2].split(':'):
                if spec == 'WHATFN':
                    destFileName =  firstPart
                elif spec == 'HEADFN':
                    headParts = firstPart.split('_')
                    if len(headParts) >= 2:
                        destFileName = headParts[0] + '_' + headParts[1] 
                    else:
                        destFileName = headParts[0] 
                elif spec == 'SENDER':
                    if len(parts[4]) == 1 : sender = parts[6]
                    else                  : sender = parts[5]
                    if sender[:6] == 'SENDER' : 
                       destFileName = sender.split('=')[1] 
                elif spec == 'NONE':
                    # PDS behavior no time extension when NONE... remove it
                    # extra trailing : removed if present SENDER too
                    last = -1
                    maybe = parts[-2]
                    if maybe[:6] == 'SENDER' : last = -2
                    destFileName = ':'.join(parts[:last])
                    if destFileName[-1] == ':' : destFileName = destFileName[:-1]
                elif spec == 'NONESENDER':
                    # PDS behavior no time extension when NONE... remove it
                    # extra trailing : removed if present
                    destFileName = ':'.join(parts[:-1])
                    if destFileName[-1] == ':' : destFileName = destFileName[:-1]
                elif re.compile('SATNET=.*').match(spec):
                    satnet = ':' + spec
                elif re.compile('DESTFN=.*').match(spec):
                    destFileName = spec[7:]
                elif re.compile('DESTFNSCRIPT=.*').match(spec):
                     old_destfn_script = self.destfn_script
                     old_destFileName  = destFileName
                     script = PXPaths.SCRIPTS + spec[13:]
                     try    :
                              execfile(script)
                              destFileName = self.destfn_script(filename)
                     except : self.logger.error("Problem with filename DESTFNSCRIPT=%s" % script)
                     self.destfn_script = old_destfn_script
                     if destFileName == None : destFileName = old_destFileName
                elif spec == 'TIME':
                    timeSuffix = ':' + time.strftime("%Y%m%d%H%M%S", time.gmtime())
                    # check for PX or PDS behavior ... if file already had a time extension keep his...
                    if parts[-1][0] == '2' : timeSuffix = ':' + parts[-1]
                else:
                    self.logger.error("Don't understand this DESTFN parameter: %s" % spec)
                    return (None, None) 
            return (destFileName + satnet + timeSuffix, mask[1])
        else:
            return (None, None) 

    def printInfos(self, client):
        print("==========================================================================")
        print("Name: %s " % client.name)
        print("Host: %s" % client.host)
        print("Type: %s" % client.type)
        print("Protocol: %s" % client.protocol)
        print("Batch: %s" %  client.batch)
        print("Max length: %i" % client.maxLength)
        print("Mtime: %i" % client.mtime)
        print("Timeout: %s" % client.timeout)
        print("Sorter: %s" % client.sorter)
        print("URL: %s" % client.url)
        print("Port: %s" % client.port)
        print("User: %s" % client.user)
        print("Passwd: %s" % client.passwd)
        print("ssh_keyfile: %s" % client.ssh_keyfile)
        print("Chmod: %s" % client.chmod)
        print("TCP SO_KEEPALIVE: %s" % client.keepAlive)
        print("Timeout_send: %i" % client.timeout_send)
        print("Lock: %s" % client.lock)
        print("FTP Mode: %s" % client.ftp_mode)
        print("DIR Pattern: %s" % client.dir_pattern)
        print("DIR Mkdir  : %s" % client.dir_mkdir)
        print("Validation: %s" % client.validation)
        print("Purge Aliases: %s" % client.purgeAliases)
        print("Purge: %s" % client.purge)
        print("purgeInst: %s" % client.purgeInst)
        print("Pattern Matching: %s" % client.patternMatching)
        print("No duplicates: %s" % client.nodups)
        print("am_dest_thread: %s" % client.am_dest_thread)

        print("******************************************")
        print("*       Client Masks                     *")
        print("******************************************")

        for mask in self.masks:
            if mask[4] :
               print(" accept %s" % mask[0] )
            else :
               print(" reject %s" % mask[0] )

        print("******************************************")
        print("*       Client Masks                     *")
        print("******************************************")

        for mask in self.masks_deprecated:
            print(" deprecated %s =" % mask[0] )
        print("==========================================================================")

if __name__ == '__main__':

    """
    client =  Client('wxo-b1')
    client.readConfig()
    client.printInfos(client)
    print client.getDestInfos('AWCNALO:TUTU:TITI:TOTO:MIMI:Directi')
    print client.getDestInfos('FPCN_DAN_MAN_lkdslfk:TUTU:TITI:TOTO:MIMI:Directi')
    print client.getDestInfos('WLCN_MAN_lkdslfk:TUTU:TITI:TOTO:MIMI:Direct')
    print client.getDestInfos('SMALLO:TUTU:TITI:TOTO:MIMI:Direct')
    print client.getDestInfos('WTCNALLO:TUTU:TITI:TOTO:MIMI:Direct')

    """
    for filename in os.listdir(PXPaths.TX_CONF):
        print filename
        if filename[-5:] != '.conf': 
            continue
        else:
            client = Client(filename[0:-5])
            client.readConfig()
            client.printInfos(client)

