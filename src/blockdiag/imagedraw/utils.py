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

import math
import unicodedata


def is_zenkaku(char):
    u"""Detect given character is Japanese ZENKAKU character

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
    return len([x for x in string if is_zenkaku(x)])


def hankaku_len(string):
    u"""Count non Japanese ZENKAKU characters from string

        >>> hankaku_len(u"abc")
        3
        >>> hankaku_len(u"あいう")
        0
        >>> hankaku_len(u"あいc")
        1
    """
    return len([x for x in string if not is_zenkaku(x)])


def string_width(string):
    u"""Measure rendering width of string.
        Count ZENKAKU-character as 2-point and non ZENKAKU-character as 1-point

        >>> string_width(u"abc")
        3
        >>> string_width(u"あいう")
        6
        >>> string_width(u"あいc")
        5
    """
    widthmap = {'Na': 1, 'N': 1, 'H': 1, 'W': 2, 'F': 2, 'A': 2}
    return sum(widthmap[unicodedata.east_asian_width(c)] for c in string)


def textsize(string, font):
    u"""Measure rendering size (width and height) of line.
        Returned size will not be exactly as rendered text size,
        Because this method does not use fonts to measure size.

        >>> from blockdiag.utils.fontmap import FontInfo
        >>> box = [0, 0, 100, 50]
        >>> font = FontInfo('serif', None, 11)
        >>> textsize(u"abc", font)
        (19, 11)
        >>> textsize(u"あいう", font)
        (33, 11)
        >>> textsize(u"あいc", font)
        (29, 11)
        >>> font = FontInfo('serif', None, 24)
        >>> textsize(u"abc", font)
        (40, 24)
        >>> font = FontInfo('serif', None, 18)
        >>> textsize(u"あいう", font)
        (54, 18)
    """
    width = (zenkaku_len(string) * font.size +
             hankaku_len(string) * font.size * 0.55)

    return (int(math.ceil(width)), font.size)
