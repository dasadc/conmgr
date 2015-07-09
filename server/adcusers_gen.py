#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

from adcusers_in import USERS
from adcconfig import SALT
from hashlib import sha256
import os, stat
#import sys, codecs
#sys.stdout = codecs.lookup('utf_8')[-1](sys.stdout)

filename="adcusers.py"

u = """# -*- coding: utf-8 -*-
# DO NO EDIT THIS FILE.
# This file is created by %s

USERS = [
""" % __file__

for t in USERS:
    str = SALT + t[0] + t[1]
    h = sha256(str).hexdigest()
    u +="    [ '%s', '%s', u'%s', %4d, %4d ],\n" % (t[0],h,t[2],t[3],t[4])
u += "]\n"
#print u

with open(filename, "w") as f:
    f.write(u.encode('utf-8'))
os.chmod(filename, stat.S_IRUSR|stat.S_IWUSR)
