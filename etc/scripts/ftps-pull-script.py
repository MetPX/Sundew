#
# MG  Pull using ftps  Janv 2014 
#

import sys, os, os.path, time, stat, string


# this pull manages the GET instruction to perform

class Puller(object):

    def __init__(self) :
        pass

    # formating a name for the grib2 file

    def pull(self, flow, logger, sleeping ):
        sys.path.insert(0, '/apps/px' )
        sys.path.insert(0, '/apps/px/etc/scripts' )
        sys.path.insert(0, '/usr/lib/px' )
        from PullFTPS import PullFTPS

        puller = PullFTPS(flow,logger,sleeping)
        files  = puller.get()
        puller.close()

        return files

puller=Puller()
self.pull_script=puller.pull
