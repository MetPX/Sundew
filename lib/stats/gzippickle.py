"""
Origial author is Bill McNeill <billmcn@speakeasy.net>
His code was taken from the following source :
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/189972


Modified by Nicholas Lemay to make it faster by using cPickle instead of Pickle.  

Original header was :

Generic object pickler and compressor

This module saves and reloads compressed representations of generic Python
objects to and from the disk.

"""

__author__ = "Bill McNeill <billmcn@speakeasy.net>"
__version__ = "1.0"



import pickle
import gzip
import cPickle


def save(object, filename, protocol = 0):
        """Saves a compressed object to disk
        """
        file = gzip.GzipFile(filename, 'wb')
        file.write(cPickle.dumps(object, -1))
        file.close()

        
def load(filename):
        """Loads a compressed object from disk
        """
        file = gzip.GzipFile(filename, 'rb')
        buffer = ""
        while 1:
                data = file.read()
                if data == "":
                        break
                buffer += data
        object = cPickle.loads(buffer)
        file.close()
        return object


