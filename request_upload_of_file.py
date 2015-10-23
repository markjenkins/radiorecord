#!/usr/bin/env python

from urllib import urlopen, urlencode
from sys import argv

urlopen(
    "http://localhost:8888/specific_file",
    data=urlencode( {"upload": argv[1]} )
)
