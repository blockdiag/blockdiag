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
import math
import unicodedata
from blockdiag.utils import Box, XY
from blockdiag.utils.fontmap import FontInfo


def is_zenkaku(char):
    u"""
    Detect given character is Japanese ZENKAKU character

    >>> is_zenkaku(u"A")
    False
    >>> is_zenkaku(u"あ")
    True
    """
    char_width = unicodedata.east_asian_width(char)
    return char_width in u"WFA"


def zenkaku_len(string):
    u"""
    Count Japanese ZENKAKU characters from string

    >>> zenkaku_len(u"abc")
    0
    >>> zenkaku_len(u"あいう")
    3
    >>> zenkaku_len(u"あいc")
    2
    """
    return len([x for x in string  if is_zenkaku(x)])


def hankaku_len(string):
    u"""
    Count non Japanese ZENKAKU characters from string

    >>> hankaku_len(u"abc")
    3
    >>> hankaku_len(u"あいう")
    0
    >>> hankaku_len(u"あいc")
    1
    """
    return len([x for x in string  if not is_zenkaku(x)])


def string_width(string):
    u"""
    Measure rendering width of string.
    Count ZENKAKU-character as 2-point and non ZENKAKU-character as 1-point

    >>> string_width(u"abc")
    3
    >>> string_width(u"あいう")
    6
    >>> string_width(u"あいc")
    5
    """
    width = 0
    for c in string:
        char_width = unicodedata.east_asian_width(c)
        if char_width in u"WFA":
            width += 2
        else:
            width += 1

    return width


class TextFolder(object):
    def __init__(self, box, string, font, **kwargs):
        self.box = box
        self.string = string
        self.font = font
        self.scale = 1
        self.scale = 1
        self.halign = kwargs.get('halign', 'center')
        self.valign = kwargs.get('valign', 'center')
        self.padding = kwargs.get('padding', 8)
        self.line_spacing = kwargs.get('line_spacing', 2)

        if kwargs.get('adjustBaseline'):
            self.adjustBaseline = True
        else:
            self.adjustBaseline = False

        self._result = self._lines()

    def textsize(self, string):
        u"""
        Measure rendering size (width and height) of line.
        Returned size will not be exactly as rendered text size,
        Because this method does not use fonts to measure size.

        >>> box = [0, 0, 100, 50]
        >>> _font = FontInfo('serif', None, 11)
        >>> TextFolder(box, "", _font).textsize(u"abc")
        (19, 11)
        >>> TextFolder(box, "", _font).textsize(u"あいう")
        (33, 11)
        >>> TextFolder(box, "", _font).textsize(u"あいc")
        (29, 11)
        >>> font = FontInfo('serif', None, 24)
        >>> TextFolder(box, "", font).textsize(u"abc")
        (40, 24)
        >>> font = FontInfo('serif', None, 18)
        >>> TextFolder(box, "", font).textsize(u"あいう")
        (54, 18)
        """
        width = zenkaku_len(string) * self.font.size + \
                hankaku_len(string) * self.font.size * 0.55
        return (int(math.ceil(width)), self.font.size)

    def height(self):
        u"""
        Measure rendering height of text.

        If texts is heighter than bounding box,
        jut out lines will be cut off.

        >>> box = [0, 0, 100, 50]
        >>> _font = FontInfo('serif', None, 11)
        >>> TextFolder(box, u"abc", _font).height()
        11
        >>> TextFolder(box, u"abc\\ndef", _font).height()
        24
        >>> TextFolder(box, u"abc\\n\\ndef", _font).height()
        37
        >>> TextFolder(box, u"abc\\ndef\\nghi\\njkl", _font).height()
        50
        >>> TextFolder(box, u"abc\\ndef\\nghi\\njkl\\nmno", _font).height()
        50
        >>> font = FontInfo('serif', None, 24)
        >>> TextFolder(box, u"abc", font).height()
        24
        >>> TextFolder(box, u"abc\\ndef", _font, line_spacing=8).height()
        30
        >>> font = FontInfo('serif', None, 15)
        >>> TextFolder(box, u"abc\\ndef", font, line_spacing=8).height()
        38
        """
        height = 0
        for string in self._result:
            height += self.textsize(string)[1]

        if len(self._result) > 1:
            height += (len(self._result) - 1) * self.line_spacing

        return height

    @property
    def lines(self):
        size = XY(self.box[2] - self.box[0], self.box[3] - self.box[1])

        if self.valign == 'top':
            height = self.line_spacing
        elif self.valign == 'bottom':
            height = size.y - self.height() - self.line_spacing
        else:
            height = int(math.ceil((size.y - self.height()) / 2.0))
        base_xy = XY(self.box[0], self.box[1])

        for string in self._result:
            textsize = self.textsize(string)

            halign = size.x - textsize[0] * self.scale
            if self.halign == 'left':
                x = self.padding
            elif self.halign == 'right':
                x = halign - self.padding
            else:
                x = int(math.ceil(halign / 2.0))

            if self.adjustBaseline:
                height += textsize[1]
            draw_xy = XY(base_xy.x + x, base_xy.y + height)

            yield string, draw_xy

            if self.adjustBaseline:
                height += self.line_spacing
            else:
                height += textsize[1] + self.line_spacing

    @property
    def outlinebox(self):
        corners = []
        for string, xy in self.lines:
            textsize = self.textsize(string)
            width = textsize[0] * self.scale
            height = textsize[1] * self.scale

            if self.adjustBaseline:
                xy = XY(xy.x, xy.y - textsize[1])

            corners.append(xy)
            corners.append(XY(xy.x + width, xy.y + height))

        if corners:
            box = Box(min(p.x for p in corners) - self.padding,
                      min(p.y for p in corners) - self.line_spacing,
                      max(p.x for p in corners) + self.padding,
                      max(p.y for p in corners) + self.line_spacing)
        else:
            box = [self.box[0], self.box[1], self.box[0], self.box[1]]

        return box

    def _splitlines(self):
        u"""
        Split text to lines as generator.
        Every line will be stripped.
        If text includes characters "\n", treat as line separator.

        >>> box = [0, 0, 100, 50]
        >>> ft = FontInfo('serif', None, 11)
        >>> [l for l in TextFolder(box, u"abc", ft)._splitlines()]
        [u'abc']
        >>> [l for l in TextFolder(box, u"abc\\ndef", ft)._splitlines()]
        [u'abc', u'def']
        >>> [l for l in TextFolder(box, u"abc\\\\ndef", ft)._splitlines()]
        [u'abc', u'def']
        >>> [l for l in TextFolder(box, u" abc \\n def ", ft)._splitlines()]
        [u'abc', u'def']
        >>> [l for l in TextFolder(box, u" \\nabc\\\\ndef", ft)._splitlines()]
        [u'abc', u'def']
        >>> [l for l in TextFolder(box, u" \\\\nab \\\\ncd", ft)._splitlines()]
        [u'', u'ab', u'cd']
        >>> [l for l in TextFolder(box, u"abc\\\\\\\\ndef", ft)._splitlines()]
        [u'abc\\\\ndef']
        >>> [l for l in TextFolder(box, u"abc\xa5\\\\ndef", ft)._splitlines()]
        [u'abc\\\\ndef']
        """
        string = re.sub('^\s*(.*?)\s*$', '\\1', self.string)
        string = re.sub('(?:\xa5|\\\\){2}', '\x00', string)
        string = re.sub('(?:\xa5|\\\\)n', '\n', string)
        for line in string.splitlines():
            yield re.sub('\x00', '\\\\', line).strip()

    def _lines(self):
        lines = []
        size = (self.box[2] - self.box[0], self.box[3] - self.box[1])

        height = 0
        truncated = 0
        for line in self._splitlines():
            while True:
                string = line.strip()
                for i in range(0, len(string)):
                    length = len(string) - i
                    metrics = self.textsize(string[0:length])

                    if metrics[0] <= size[0]:
                        break
                else:
                    length = 0
                    metrics = self.textsize(u" ")

                if size[1] < height + metrics[1]:
                    truncated = 1
                    break

                lines.append(string[0:length])
                height += metrics[1] + self.line_spacing

                line = string[length:]
                if line == "":
                    break

        # truncate last line.
        if len(lines) == 0:
            pass
        elif truncated:
            string = lines.pop()
            for i in range(0, len(string)):
                if i == 0:
                    truncated = string + ' ...'
                else:
                    truncated = string[0:-i] + ' ...'

                metrics = self.textsize(truncated)
                if metrics[0] <= size[0]:
                    lines.append(truncated)
                    break

        return lines
