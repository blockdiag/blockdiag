# -*- coding: utf-8 -*-

import urlparse


def isurl(url):
    o = urlparse.urlparse(url)
    accpetable = ["http", "https"]
    if o.scheme in accpetable:
        return True
    else:
        return False
