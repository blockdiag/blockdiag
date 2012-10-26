# -*- coding: utf-8 -*-

import os
import sys
import unittest2
from blockdiag.imagedraw.textfolder import splitlabel
from blockdiag.imagedraw.textfolder import splittext
from blockdiag.imagedraw.textfolder import truncate_text
from blockdiag.utils import Size


CHAR_WIDTH = 14
CHAR_HEIGHT = 10


class Metrics(object):
    def textsize(self, text):
        length = len(text)
        return Size(CHAR_WIDTH * length, CHAR_HEIGHT)


class TestTextFolder(unittest2.TestCase):
    def test_splitlabel(self):
        labels = splitlabel("abc")
        #self.assertIsInstance(labels, generator)

        # single line text
        text = "abc"
        self.assertItemsEqual(['abc'], splitlabel(text))

        # text include \n (as char a.k.a. \x5c)
        text = "abc\ndef"
        self.assertItemsEqual(['abc', 'def'], splitlabel(text))

        # text include \n (as mac yensign a.k.a. \xa5)
        text = "abc\xa5ndef"
        self.assertItemsEqual(['abc', 'def'], splitlabel(text))

        # text includes \n (as text)
        text = "abc\\ndef"
        self.assertItemsEqual(['abc', 'def'], splitlabel(text))

        # text includes escaped \n
        text = "abc\\\\ndef"
        self.assertItemsEqual(['abc\\ndef'], splitlabel(text))

        # text includes escaped \n (\x5c and mac yensign mixed)
        text = u"abc\xa5\\ndef"
        self.assertItemsEqual(['abc\\ndef'], splitlabel(text))

        # text include \n and spaces
        text = " abc \n def "
        self.assertItemsEqual(['abc', 'def'], splitlabel(text))

        # text starts empty line
        text = " \nabc\ndef"
        self.assertItemsEqual(['abc', 'def'], splitlabel(text))

        # text starts empty line with \n (as text)
        text = " \\nabc\\ndef"
        self.assertItemsEqual(['', 'abc', 'def'], splitlabel(text))

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
        self.assertEqual([''], ret)

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
