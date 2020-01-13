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

import io
import os
import tempfile
import unittest

import blockdiag
from blockdiag.command import BlockdiagOptions
from blockdiag.tests.utils import with_pdf
from blockdiag.utils.bootstrap import detectfont


class TestBootParams(unittest.TestCase):
    def setUp(self):
        self.parser = BlockdiagOptions(blockdiag)

    def test_type_option_svg(self):
        options = self.parser.parse(['-Tsvg', 'input.diag'])
        self.assertEqual(options.output, 'input.svg')

        options = self.parser.parse(['-TSVG', 'input.diag'])
        self.assertEqual(options.output, 'input.svg')

        options = self.parser.parse(['-TSvg', 'input.diag'])
        self.assertEqual(options.output, 'input.svg')

        options = self.parser.parse(['-TSvg', 'input.test.diag'])
        self.assertEqual(options.output, 'input.test.svg')

    def test_type_option_png(self):
        options = self.parser.parse(['-Tpng', 'input.diag'])
        self.assertEqual(options.output, 'input.png')

    @with_pdf
    def test_type_option_pdf(self):
        options = self.parser.parse(['-Tpdf', 'input.diag'])
        self.assertEqual(options.output, 'input.pdf')

    def test_invalid_type_option(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['-Tsvgz', 'input.diag'])

    def test_separate_option_svg(self):
        self.parser.parse(['-Tsvg', '--separate', 'input.diag'])

    def test_separate_option_png(self):
        self.parser.parse(['-Tpng', '--separate', 'input.diag'])

    @with_pdf
    def test_separate_option_pdf(self):
        self.parser.parse(['-Tpdf', '--separate', 'input.diag'])

    def test_svg_nodoctype_option(self):
        self.parser.parse(['-Tsvg', '--nodoctype', 'input.diag'])

    def test_png_nodoctype_option(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['-Tpng', '--nodoctype', 'input.diag'])

    def test_pdf_nodoctype_option(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['-Tpdf', '--nodoctype', 'input.diag'])

    def test_svg_notransparency_option(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['-Tsvg', '--no-transparency', 'input.diag'])

    def test_png_notransparency_option(self):
        self.parser.parse(['-Tpng', '--no-transparency', 'input.diag'])

    def test_pdf_notransparency_option(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['-Tpdf', '--no-transparency', 'input.diag'])

    def test_config_option(self):
        try:
            tmp = tempfile.mkstemp()
            self.parser.parse(['-c', tmp[1], 'input.diag'])
        finally:
            os.close(tmp[0])
            os.unlink(tmp[1])

    def test_config_option_with_bom(self):
        try:
            tmp = tempfile.mkstemp()
            fp = io.open(tmp[0], 'wt', encoding='utf-8-sig')
            fp.write("[blockdiag]\n")
            fp.close()

            self.parser.parse(['-c', tmp[1], 'input.diag'])
        finally:
            os.unlink(tmp[1])

    def test_invalid_config_option(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['-c', '/unknown_config_file', 'input.diag'])

    def test_invalid_dir_config_option(self):
        try:
            tmp = tempfile.mkdtemp()

            with self.assertRaises(RuntimeError):
                self.parser.parse(['-c', tmp, 'input.diag'])
        finally:
            os.rmdir(tmp)

    def test_config_option_fontpath(self):
        try:
            tmp = tempfile.mkstemp()
            config = "[blockdiag]\nfontpath = /path/to/font\n"
            io.open(tmp[0], 'wt', encoding='utf-8-sig').write(config)

            options = self.parser.parse(['-c', tmp[1], 'input.diag'])
            self.assertEqual(options.font, ['/path/to/font'])
        finally:
            os.unlink(tmp[1])

    def test_exist_font_config_option(self):
        try:
            fd, path = tempfile.mkstemp()
            os.close(fd)

            options = self.parser.parse(['-f', path, 'input.diag'])
            self.assertEqual(options.font, [path])
            fontpath = detectfont(options)
            self.assertEqual(fontpath, path)
        finally:
            os.unlink(path)

    def test_not_exist_font_config_option(self):
        with self.assertRaises(RuntimeError):
            args = ['-f', '/font_is_not_exist', 'input.diag']
            options = self.parser.parse(args)
            detectfont(options)

    def test_not_exist_font_config_option2(self):
        with self.assertRaises(RuntimeError):
            args = ['-f', '/font_is_not_exist',
                    '-f', '/font_is_not_exist2', 'input.diag']
            options = self.parser.parse(args)
            detectfont(options)

    def test_no_size_option(self):
        options = self.parser.parse(['input.diag'])
        self.assertEqual(None, options.size)

    def test_size_option(self):
        options = self.parser.parse(['--size', '480x360', 'input.diag'])
        self.assertEqual([480, 360], options.size)

    def test_invalid_size_option1(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['--size', '480-360', 'input.diag'])

    def test_invalid_size_option2(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['--size', '480', 'input.diag'])

    def test_invalid_size_option3(self):
        with self.assertRaises(RuntimeError):
            self.parser.parse(['--size', 'foobar', 'input.diag'])

    def test_not_exist_fontmap_config(self):
        with self.assertRaises(RuntimeError):
            args = ['--fontmap', '/fontmap_is_not_exist', 'input.diag']
            options = self.parser.parse(args)
            fontpath = detectfont(options)
            self.assertTrue(fontpath)

    def test_unknown_image_driver(self):
        from blockdiag.drawer import DiagramDraw
        from blockdiag.elements import Diagram

        with self.assertRaises(RuntimeError):
            DiagramDraw('unknown', Diagram())
