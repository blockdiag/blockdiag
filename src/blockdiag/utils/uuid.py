# -*- coding: utf-8 -*-

try:
    from uuid import uuid1 as uuid
except ImportError:
    from random import random as uuid


def generate():
    return str(uuid())
