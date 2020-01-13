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

import unittest

from blockdiag.imagedraw.textfolder import splitlabel, splittext, truncate_text
from blockdiag.utils import Size

CHAR_WIDTH = 14
CHAR_HEIGHT = 10


class Metrics(object):
    def textsize(self, text):
        length = len(text)
        return Size(CHAR_WIDTH * length, CHAR_HEIGHT)


class TestTextFolder(unittest.TestCase):
    def test_splitlabel(self):
        # single line text
        text = "abc"
        self.assertEqual(['abc'], list(splitlabel(text)))

        # text include \n (as char a.k.a. \x5c)
        text = "abc\ndef"
        self.assertEqual(['abc', 'def'], list(splitlabel(text)))

        # text include \n (as mac yensign a.k.a. \xa5)
        text = "abc\xa5ndef"
        self.assertEqual(['abc', 'def'], list(splitlabel(text)))

        # text includes \n (as text)
        text = "abc\\ndef"
        self.assertEqual(['abc', 'def'], list(splitlabel(text)))

        # text includes escaped \n
        text = "abc\\\\ndef"
        self.assertEqual(['abc\\ndef'], list(splitlabel(text)))

        # text includes escaped \n (\x5c and mac yensign mixed)
        text = "abc\xa5\\ndef"
        self.assertEqual(['abc\\ndef'], list(splitlabel(text)))

        # text include \n and spaces
        text = " abc \n def "
        self.assertEqual(['abc', 'def'], list(splitlabel(text)))

        # text starts empty line
        text = " \nabc\ndef"
        self.assertEqual(['abc', 'def'], list(splitlabel(text)))

        # text starts empty line with \n (as text)
        text = " \\nabc\\ndef"
        self.assertEqual(['', 'abc', 'def'], list(splitlabel(text)))

    def test_splittext_width(self):
        metrics = Metrics()

        # just fit text
        text = "abc"
        ret = splittext(metrics, text, CHAR_WIDTH * 3)
        self.assertEqual(['abc'], ret)

        # text should be folded (once)
        text = "abcdef"
        ret = splittext(metrics, text, CHAR_WIDTH * 3)
        self.assertEqual(['abc', 'def'], ret)

        # text should be folded (twice)
        text = "abcdefghi"
        ret = splittext(metrics, text, CHAR_WIDTH * 3)
        self.assertEqual(['abc', 'def', 'ghi'], ret)

        # empty text
        text = ""
        ret = splittext(metrics, text, CHAR_WIDTH * 3)
        self.assertEqual([' '], ret)

    def test_truncate_text(self):
        metrics = Metrics()

        # truncated
        text = "abcdef"
        ret = truncate_text(metrics, text, CHAR_WIDTH * 8)
        self.assertEqual("abcd ...", ret)

        # truncated
        text = "abcdef"
        ret = truncate_text(metrics, text, CHAR_WIDTH * 5)
        self.assertEqual("a ...", ret)

        # not truncated (too short)
        text = "abcdef"
        ret = truncate_text(metrics, text, CHAR_WIDTH * 4)
        self.assertEqual("abcdef", ret)
