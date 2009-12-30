#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""
Python source code - replace this with a description of the code and write the code below this text.
"""

__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

import sys
import bamboo
import time
from subprocess import PIPE, Popen
import urllib

class DataCollector(object):
    def get(self):
        return ""

class IPCollector(DataCollector):
    def __init__(self, cmd = "ifconfig"):
        self.cmd = cmd
        self.ignore = ["lo0", "vnic0", "vnic1"]
        self.host = "host"

    def get(self):
        output = Popen([self.cmd], stdout=PIPE).communicate()[0]
        results = []
        key = ""
        for line in output.split("\n"):
            if line == "":
                continue
            if line[0] != " " and line[0] != "\t":
                key = line.split(":")[0]
            elif key not in self.ignore:
                vals = line.strip().split()
                if vals[0] == "inet":
                    results += [ key + " inet " + vals[1]  ]

        if len(results) > 0:
            ext = urllib.urlopen("http://getip.dyndns.org/").read()
            ext =  ext.split(":")[1].strip()
            ext = ext[: ext.find("<") ]
            results += [ "external inet " + ext ]
        output = Popen([self.host, ext], stdout=PIPE).communicate()[0].split()
        results += [ "external name " + output[-1] ]
        return "\n".join(results) + "\n"


def timestamp():
    return time.strftime("%Y%m%d-%H%M")


def main(args):
    dht = bamboo.OpenDHT()
    bfs = bamboo.BambooFS("arwen-recovery", dht)

    bfs.addFile("/ip/" + timestamp(), IPCollector().get() )
    #print bfs.queryFiles()
    return 0

if __name__ == "__main__":
    #print IPCollector().get()
    sys.exit( main( sys.argv ) )

