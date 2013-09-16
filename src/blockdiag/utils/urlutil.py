# -*- coding: utf-8 -*-

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def isurl(url):
    o = urlparse.urlparse(url)
    accpetable = ["http", "https"]
    if o[0] in accpetable:
        return True
    else:
        return False
