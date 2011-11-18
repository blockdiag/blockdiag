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
import os
import sys
import copy
import codecs
from ordereddict import OrderedDict
from ConfigParser import SafeConfigParser
from blockdiag.utils.collections import namedtuple


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

    def duplicate(self):
        return copy.copy(self)


class FontMap(object):
    fontsize = 11
    default_fontfamily = 'sansserif'

    def __init__(self, filename=None):
        self.fonts = {}
        self.aliases = {}

        if filename:
            self._parse_config(filename)
        self.set_default_font(None)

    def set_default_fontfamily(self, fontfamily):
        self.default_fontfamily = fontfamily
        self.set_default_font(None)

    def _parse_config(self, conffile):
        config = SafeConfigParser(dict_type=OrderedDict)
        if hasattr(conffile, 'read'):
            config.readfp(conffile)
        elif os.path.isfile(conffile):
            fd = codecs.open(conffile, 'r', 'utf-8')
            config.readfp(fd)
        else:
            msg = "fontmap file is not found: %s" % conffile
            raise RuntimeError(msg)

        if config.has_section('fontmap'):
            for name, path in config.items('fontmap'):
                self.append_font(name, path)

        if config.has_section('fontalias'):
            for name, family in config.items('fontalias'):
                self.aliases[name] = family

    def set_default_font(self, path):
        if path is None and self.find() is not None:
            return

        self.append_font(self.default_fontfamily, path)

    def append_font(self, fontfamily, path):
        if path is None or os.path.isfile(path):
            font = FontInfo(fontfamily, path, self.fontsize)
            self.fonts[font.familyname] = font
        else:
            msg = 'fontfile `%s` is not found: %s' % (fontfamily, path)
            sys.stderr.write("WARNING: %s\n" % msg)

    def _regulate_familyname(self, name):
        return FontInfo(name, None, 11).familyname

    def find(self, element=None):
        fontfamily = getattr(element, 'fontfamily', None) or \
                       self.default_fontfamily
        fontfamily = self.aliases.get(fontfamily, fontfamily)
        fontsize = getattr(element, 'fontsize', None) or self.fontsize

        name = self._regulate_familyname(fontfamily)
        if name in self.fonts:
            font = self.fonts[name].duplicate()
            font.size = fontsize
        elif element is not None:
            msg = "Unknown fontfamily: %s" % fontfamily
            sys.stderr.write("WARNING: %s\n" % msg)
            elem = namedtuple('Font', 'fontsize')(fontsize)
            font = self.find(elem)
        else:
            font = None

        return font
