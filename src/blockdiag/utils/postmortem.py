# -*- coding: utf-8 -*-

import sys
import traceback
import pdb

__all__ = ['postmortem']


def postmortem(type, value, tb):
    if hasattr(sys, 'ps1' or not (
            sys.stderr.isatty() and sys.stdin.isatty()
            ) or issubclass(type, SyntaxError)):
        sys.__excepthook__(type, value, tb)
    else:
        traceback.print_exception(type, value, tb)
        pdb.pm()
