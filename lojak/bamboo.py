#!/usr/bin/env python
import sys
import hashlib
import optparse
from xmlrpclib import *


default_server = "http://openlookup.appspot.com/"
default_ttl = 3600
#60*60*24*7
MAX_SIZE = 1024
CLIENT_STR = "BAMBOOLIB.py"
SEP = "\0"
SECRET = "oink"

#        res = {0:"Success", 1:"Capacity", 2:"Again"}
class DHTExceptionCapacity(Exception): pass
class DHTExceptionAgain(Exception): pass
DHT_EXCEPT = [ 0, DHTExceptionCapacity, DHTExceptionAgain ]

class SHAKey(object):
    def __init__(self, s = None, digest = None):
        if digest is not None:
            self.digest = digest
        else:
            self.digest = hashlib.sha1(s).digest()

    def __repr__(self):
        return "<SHAKey: 0x%s>" % self.digest

    def Binary(self):
        return Binary(self.digest)


class BambooFS(object):
    def __init__(self, root_id, dht):
        self.root_id = root_id
        self.dht = dht
        self.root_node = self.root_id + SEP + "/"
        self.queryFiles()
        self.secret = "oink"

    def queryFiles(self):
        datas, pm = self.dht.get(self.root_node)
        #map(lambda x: assert( x[:3] ==)
        data = reduce(lambda x,y: x+y,  map(lambda x: x[3:].split(SEP), datas),
                list())
        self.files =  dict([ (data[d], ( data[d+1], int(data[d+2])))
            for d in range(0, len(data), 3) ])
        return self.files

    def addFile(self, name, data):
        #if name in self.files:
        #    raise "File exists"
        secret = self.genSecret(name)
        self.files[name] =  hashlib.sha1(data).digest()
        size = len(data)
        file_prefix = self.root_id + SEP + name + SEP
        for i in range(0, len(data), 1024):
            bkey = file_prefix + str(i / 1024)
            self.dht.put(bkey, data[i:i+1024], secret)
        self.dht.put(self.root_node,
                "BFS" + name + SEP + name + "0" + SEP + str(size),
                secret)

    def getFile(self, name):
        size = self.files[name][1]
        file_prefix = self.root_id + SEP + name + SEP
        data = ""
        for i in range(0, size, 1024):
            block, pm =  self.dht.get(file_prefix + str(i/1024))
            data += block[0]
        return data

    def rmFile(self, name):
        secret = self.genSecret(name)
        size = self.files[name][1]
        file_prefix = self.root_id + SEP + name + SEP
        data = ""
        for i in range(0, size, 1024):
            bkey = file_prefix + str(i/1024)
            blocks, pm =  self.dht.get(bkey)
            for block in blocks:
                self.dht.rm(bkey, block[0], secret)
        return data

    def genSecret(self, name):
        return hashlib.sha1(self.root_id + name + self.secret).hexdigest()



class Block(object):
    def __init__(self, data):
        pass

class OpenDHT(object):
    def __init__(self, server = default_server):
        self.server  = server
        self.pxy = ServerProxy(server)
        self.keys = []

    def get(self, key, maxvals = 10, pm = None):
        if pm == None:
            pm      = Binary("")
        if not isinstance(key, SHAKey):
            key = SHAKey(key)
        vals, pm = self.pxy.get(key.Binary(), maxvals, pm, CLIENT_STR)
        return [ v.data for v in vals], pm

    def get_details(self, key, maxvals = 10, pm = None):
        if pm == None:
            pm      = Binary("")
        if not isinstance(key, SHAKey):
            key = SHAKey(key)
        vals, pm = self.pxy.get_details(key.Binary(), maxvals, pm, "get.py")
        return [ (v[0].data, v[1], v[2], v[3].data) for v in vals], pm

    def put(self, key, val, secret = None, ttl = default_ttl):
        k = key
        val = Binary(val)
        ttl = int(ttl);
        if not isinstance(key, SHAKey):
            key = SHAKey(key)
        if secret:
            self.keys += [ (key, secret, SHAKey(val.data), ttl) ]
            if not isinstance(secret, SHAKey):
                shash = SHAKey(secret)
            else:
                shash = secret
            ret = self.pxy.put_removable(key.Binary() ,val, "SHA",
                    shash.Binary(), ttl, CLIENT_STR)
        else:
            ret = self.pxy.put(key.Binary(), val, ttl, CLIENT_STR)
        if ret != 0:
            raise DHT_EXCEPT[ret]
        return ret

    def rm(self, key, value, secret, ttl = default_ttl):
        ttl = int(ttl)
        if not isinstance(key, SHAKey):
            key = SHAKey(key)
        if not isinstance(value, SHAKey):
            vh = SHAKey(value)
        else:
            vh = value
        secret = Binary(secret)
        ret = self.pxy.rm(key.Binary(), vh.Binary(), "SHA", secret, ttl,
                CLIENT_STR)
        return ret

    def clear_all(self):
        for key, secret, valhash, ttl in self.keys:
            self.rm(key, valhash, SECRET, ttl)
        self.keys = []

if __name__ == "__main__":
    dht = OpenDHT()
    #dht.put("colors", "red", "oink")
    #print dht.get("colors")[0]
    #dht.put("colors", "green", "oink")
    #print dht.get("colors")[0]
    #dht.put("colors", "blue", "oink")
    #print dht.get("colors")[0]
    #dht.clear_all()
    #print dht.get("colors")[0]
    try:
        bfs = BambooFS("arwen-recovery", dht)
        print bfs.queryFiles()
        data = open("out.jpg").read()
        print hashlib.sha1(data).hexdigest()
        bfs.addFile("/a", data)
        print bfs.queryFiles()
        data2 =  bfs.getFile("/a")
        open("out2.jpg", "w").write(data)
        #print data2
        print hashlib.sha1(data2).hexdigest()
    except Exception, e:
        print "Exception thrown",e
        pass
    dht.clear_all()
