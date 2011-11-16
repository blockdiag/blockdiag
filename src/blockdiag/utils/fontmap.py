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


class FontInfo(object):
    def __init__(self, family, path, size):
        self.path = path
        self.size = int(size)

        family = self._parse(family)
        self.name = family[0]
        self.generic_family = family[1]
        self.weight = family[2]
        self.style = family[3]

    @property
    def familyname(self):
        if self.name:
            name = self.name + "-"
        else:
            name = ''

        if self.weight == 'bold':
            return "%s%s-%s" % (name, self.generic_family, self.weight)
        else:
            return "%s%s-%s" % (name, self.generic_family, self.style)

    def _parse(self, familyname):
        pattern = '^(?:(.*)-)?' + \
                  '(serif|sansserif|monospace|fantasy|cursive)' + \
                  '(?:-(normal|bold|italic|oblique))?$'

        match = re.search(pattern, familyname or '')
        if match is None:
            msg = 'Unknown font family: %s' % familyname
            raise AttributeError(msg)

        name = match.group(1) or ''
        generic_family = match.group(2)
        style = match.group(3) or ''

        if style == 'bold':
            weight = 'bold'
            style = 'normal'
        elif style in ('italic', 'oblique'):
            weight = 'normal'
            style = style
        else:
            weight = 'normal'
            style = 'normal'

        return [name, generic_family, weight, style]
