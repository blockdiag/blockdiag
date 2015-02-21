# -*- coding: utf-8 -*-

import sys
from blockdiag.utils import Size, unquote

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestUtils(unittest.TestCase):
    def test_size_resize(self):
        size = Size(10, 20)

        resized = size.resize(width=50, height=50)
        self.assertEqual((50, 50), resized)

        resized = size.resize(width=50)
        self.assertEqual((50, 100), resized)

        resized = size.resize(height=50)
        self.assertEqual((25, 50), resized)

        resized = size.resize(scale=50)
        self.assertEqual((5, 10), resized)

        resized = size.resize(width=50, scale=50)
        self.assertEqual((25, 50), resized)

        resized = size.resize(height=50, scale=50)
        self.assertEqual((12.5, 25), resized)

        resized = size.resize(width=50, height=50, scale=50)
        self.assertEqual((25, 25), resized)

    def test_size_to_integer_point(self):
        size = Size(1.5, 2.5)

        self.assertEqual((1, 2), size.to_integer_point())

    def test_unquote(self):
        self.assertEqual('test', unquote('"test"'))
        self.assertEqual('test', unquote("'test'"))
        self.assertEqual("'half quoted", unquote("'half quoted"))
        self.assertEqual('"half quoted', unquote('"half quoted'))
