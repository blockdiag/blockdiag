# -*- coding: utf-8 -*-

import os
import sys
import unittest
from nose.tools import raises
from blockdiag.utils.fontmap import FontInfo


class TestUtilsFontmap(unittest.TestCase):
    def test_fontinfo_new(self):
        FontInfo("serif", None, 11)
        FontInfo("sansserif", None, 11)
        FontInfo("monospace", None, 11)
        FontInfo("cursive", None, 11)
        FontInfo("fantasy", None, 11)

        FontInfo("serif-bold", None, 11)
        FontInfo("sansserif-italic", None, 11)
        FontInfo("monospace-oblique", None, 11)
        FontInfo("my-cursive", None, 11)
        FontInfo("-fantasy", None, 11)

    @raises(AttributeError)
    def test_fontinfo_invalid_familyname1(self):
        FontInfo("unknown", None, 11)

    @raises(AttributeError)
    def test_fontinfo_invalid_familyname2(self):
        FontInfo("sansserif-", None, 11)

    @raises(AttributeError)
    def test_fontinfo_invalid_familyname3(self):
        FontInfo("monospace-unkown", None, 11)

    @raises(AttributeError)
    def test_fontinfo_invalid_familyname4(self):
        FontInfo("cursive-bold-bold", None, 11)

    @raises(AttributeError)
    def test_fontinfo_invalid_familyname4(self):
        FontInfo("SERIF", None, 11)

    @raises(TypeError)
    def test_fontinfo_invalid_fontsize1(self):
        FontInfo("serif", None, None)

    @raises(ValueError)
    def test_fontinfo_invalid_fontsize2(self):
        FontInfo("serif", None, '')

    def test_fontinfo_parse(self):
        font = FontInfo("serif", None, 11)
        self.assertEqual('', font.name)
        self.assertEqual('serif', font.generic_family)
        self.assertEqual('normal', font.weight)
        self.assertEqual('normal', font.style)

        font = FontInfo("sansserif-bold", None, 11)
        self.assertEqual('', font.name)
        self.assertEqual('sansserif', font.generic_family)
        self.assertEqual('bold', font.weight)
        self.assertEqual('normal', font.style)

        font = FontInfo("monospace-italic", None, 11)
        self.assertEqual('', font.name)
        self.assertEqual('monospace', font.generic_family)
        self.assertEqual('normal', font.weight)
        self.assertEqual('italic', font.style)

        font = FontInfo("my-cursive-oblique", None, 11)
        self.assertEqual('my', font.name)
        self.assertEqual('cursive', font.generic_family)
        self.assertEqual('normal', font.weight)
        self.assertEqual('oblique', font.style)

        font = FontInfo("my-fantasy-bold", None, 11)
        self.assertEqual('my', font.name)
        self.assertEqual('fantasy', font.generic_family)
        self.assertEqual('bold', font.weight)
        self.assertEqual('normal', font.style)

        font = FontInfo("serif-serif", None, 11)
        self.assertEqual('serif', font.name)
        self.assertEqual('serif', font.generic_family)
        self.assertEqual('normal', font.weight)
        self.assertEqual('normal', font.style)

    def test_fontinfo_familyname(self):
        font = FontInfo("serif", None, 11)
        self.assertEqual('serif-normal', font.familyname)

        font = FontInfo("sansserif-bold", None, 11)
        self.assertEqual('sansserif-bold', font.familyname)

        font = FontInfo("monospace-italic", None, 11)
        self.assertEqual('monospace-italic', font.familyname)

        font = FontInfo("my-cursive-oblique", None, 11)
        self.assertEqual('my-cursive-oblique', font.familyname)

        font = FontInfo("my-fantasy-bold", None, 11)
        self.assertEqual('my-fantasy-bold', font.familyname)

        font = FontInfo("serif-serif", None, 11)
        self.assertEqual('serif-serif-normal', font.familyname)

        font = FontInfo("-serif", None, 11)
        self.assertEqual('serif-normal', font.familyname)
