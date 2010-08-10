"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: CacheManager.py
#
# Author: Daniel Lemay
#
# Date: 2005-06-30
#
# Description: U
#
#############################################################################################

import md5, time, os
"""
import sys, time, os

if sys.version[:3] >= '2.6' :
        import hashlib
        from hashlib import md5
        md5new = md5
else :
        import md5
        md5new = md5.new

class CacheManager(object):

    MINUTE = 60                     # Number of seconds in a minute
    HOUR = 60 * MINUTE              # Number of seconds in an hour 

    def __init__(self, maxEntries, timeout = 3 * HOUR):
        self.cache = {}
        self.maxEntries = maxEntries
        self.timeout = timeout

    def add(self, key):
        #print "Was new"
        if len(self.cache) < self.maxEntries:
            self.cache[key] = [time.time(), 1]
            return

        #print "Was full, try timeoutClear"
        self.timeoutClear( self.timeout )
        if len(self.cache) < self.maxEntries:
            self.cache[key] = [time.time(), 1]
            return

        # at this point Daniel was sorting in time all entries
        # deleting the oldest and adding the new one...
        # BUT when maxEntries was reached and timeout was not
        # until some entries timed out this was a lot of processing
        # and was slowing down very busy senders...
        # MG (I decided to flush half of the cache when it happens)

        #print "still full, clean half or more of cache"
        temp = [(item[1][0], item[0]) for item in self.cache.items()]
        temp.sort()            
        half_timeout = time.time() - temp[self.maxEntries/2][0]
        self.timeoutClear( half_timeout )
        #print "add new"
        #print len(self.cache)
        self.cache[key] = [time.time(), 1]

    def find(self, object, keyType='standard'):
        #Create the key according to key type:
        if keyType == 'standard': 
            key = object
        elif keyType == 'md5':
            key = md5new(object).hexdigest()

        if key in self.cache:
            self.cache[key][0] = time.time()
            self.cache[key][1] += 1
            #print "Was cached"
            return self.cache[key]
        else:
            self.add(key)
            return None

    # MG test without adding... 
    # can test for presence and add whenever convenient

    def has(self, object, keyType='standard'):
        #Create the key according to key type:
        if keyType == 'standard': 
            key = object
        elif keyType == 'md5':
            key = md5new(object).hexdigest()

        if key in self.cache: return True

        return False

    # MG get md5 from file...

    def get_md5_from_file(self, path ):

        m  = md5new()
        sz = os.stat(path)[6]

        # one meg or less buffer read

        f=open(path,'r')

        data = f.read(1048576)
        while len(data) :
              m.update(data)
              data = f.read(1048576)

        f.close()

        key = m.hexdigest()

        return key

    def clear(self):
        self.cache = {}

    def timeoutClear(self, timeout ):
        # Remove all the elements that are older than oldest acceptable time
        #print self.getStats()
        oldestAcceptableTime = time.time() - timeout
        for item  in self.cache.items():
            if item[1][0] < oldestAcceptableTime:
                del self.cache[item[0]]

    def getStats(self):

        compteurs = {}

        for item in self.cache.items():
            if item[1][1] in compteurs:
                compteurs[item[1][1]] += 1
            else:
                compteurs[item[1][1]] = 1
        
        total = 0.0
        cached = 0.0

        for (key, value) in compteurs.items():
            cached += (key-1) * value
            total += key * value

        #percentage = "%2.2f %% of the last %i requests were cached (implied %i files were deleted)" % (cached/total * 100,  total, cached)

        return (compteurs, cached, total)

if __name__ == '__main__':
  
    manager = CacheManager(maxEntries=3, timeout=5 * 3600)

    cacheMD5 = manager.get_md5_from_file(sys.argv[1])
    print cacheMD5

    manager.find('toto')
    manager.find('tutu')
    time.sleep(6)
    #print manager.cache

    if     manager.has('toto') : print(" HAS toto")
    if not manager.has('titi') : print(" NO  titi")
    manager.find('titi')
    manager.find('toto')
    print manager.cache
    manager.find('mimi')
    print manager.cache
    print manager.getStats()
