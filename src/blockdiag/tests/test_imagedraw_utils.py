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

from blockdiag.imagedraw.utils import (hankaku_len, is_zenkaku, string_width,
                                       textsize, zenkaku_len)


class TestUtils(unittest.TestCase):
    def test_is_zenkaku(self):
        # A
        self.assertEqual(False, is_zenkaku("A"))
        # あ
        self.assertEqual(True, is_zenkaku("\u3042"))

    def test_zenkaku_len(self):
        # abc
        self.assertEqual(0, zenkaku_len("abc"))
        # あいう
        self.assertEqual(3, zenkaku_len("\u3042\u3044\u3046"))
        # あいc
        self.assertEqual(2, zenkaku_len("\u3042\u3044c"))

    def test_hankaku_len(self):
        # abc
        self.assertEqual(3, hankaku_len("abc"))
        # あいう
        self.assertEqual(0, hankaku_len("\u3042\u3044\u3046"))
        # あいc
        self.assertEqual(1, hankaku_len("\u3042\u3044c"))

    def test_string_width(self):
        # abc
        self.assertEqual(3, string_width("abc"))
        # あいう
        self.assertEqual(6, string_width("\u3042\u3044\u3046"))
        # あいc
        self.assertEqual(5, string_width("\u3042\u3044c"))

    def test_test_textsize(self):
        from blockdiag.utils.fontmap import FontInfo
        font = FontInfo('serif', None, 11)

        # abc
        self.assertEqual((19, 11), textsize("abc", font))
        # あいう
        self.assertEqual((33, 11), textsize("\u3042\u3044\u3046", font))
        # あいc
        self.assertEqual((29, 11), textsize("\u3042\u3044c", font))

        # abc
        font = FontInfo('serif', None, 24)
        self.assertEqual((40, 24), textsize("abc", font))

        # あいう
        font = FontInfo('serif', None, 18)
        self.assertEqual((54, 18), textsize("\u3042\u3044\u3046", font))
