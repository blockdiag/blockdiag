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

import re
from xml.parsers import expat
from blockdiag.utils.collections import namedtuple


class ElementTree(object):
    @classmethod
    def parse(cls, filename):
        return cls(filename)

    def __init__(self, filename):
        self.filename = filename

    def find(self, match):
        match = re.sub('{(.*?)}', '\\1 ', match)

        # extract embeded source code
        parser = expat.ParserCreate(namespace_separator=' ')
        desc = [None]

        def start_element(name, attrs):
            if name == match:
                desc[0] = []

        def end_element(name):
            if name == match:
                desc[0] = ''.join(desc[0])

        def char_data(data):
            if isinstance(desc[0], list):
                desc[0].append(data)

        parser.StartElementHandler = start_element
        parser.EndElementHandler = end_element
        parser.CharacterDataHandler = char_data
        parser.ParseFile(open(self.filename))

        Node = namedtuple('Node', 'text')
        if desc[0]:
            return Node(desc[0])
        else:
            return Node('')
