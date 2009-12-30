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
import os

def main(args):
    dht = bamboo.OpenDHT()
    bfs = bamboo.BambooFS("arwen-recovery", dht)
    files = bfs.queryFiles()
    for file in files:
        fname = os.path.join("tmp", file[1:])
        data = bfs.getFile(file)
        #print "%s" % data
        print fname
        dir = os.path.dirname(fname)
        if not os.path.exists(dir):
            os.makedirs(dir)
        open(fname, "w").write(data)

    return 0

if __name__ == "__main__":
    #print IPCollector().get()
    sys.exit( main( sys.argv ) )

