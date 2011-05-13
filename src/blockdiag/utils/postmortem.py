# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
