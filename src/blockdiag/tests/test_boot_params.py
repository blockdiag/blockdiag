# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import unittest2
from utils import argv_wrapper, assertRaises
import blockdiag
from blockdiag.command import BlockdiagOptions
from blockdiag.utils.bootstrap import detectfont


class TestBootParams(unittest2.TestCase):
    def setUp(self):
        self.parser = BlockdiagOptions(blockdiag)

    @argv_wrapper
    def test_type_option(self):
        sys.argv = ['', '-Tsvg', 'input.diag']
        self.parser.parse()

        sys.argv = ['', '-TSVG', 'input.diag']
        self.parser.parse()

        sys.argv = ['', '-TSvg', 'input.diag']
        self.parser.parse()

        sys.argv = ['', '-Tpng', 'input.diag']
        self.parser.parse()

        sys.argv = ['', '-Tpdf', 'input.diag']
        self.parser.parse()

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_invalid_type_option(self):
        sys.argv = ['', '-Tsvgz', 'input.diag']
        self.parser.parse()

    @argv_wrapper
    def test_separate_option(self):
        sys.argv = ['', '-Tsvg', '--separate', 'input.diag']
        self.parser.parse()

        sys.argv = ['', '-Tpng', '--separate', 'input.diag']
        self.parser.parse()

        sys.argv = ['', '-Tpdf', '--separate', 'input.diag']
        self.parser.parse()

    @argv_wrapper
    def test_svg_nodoctype_option(self):
        sys.argv = ['', '-Tsvg', '--nodoctype', 'input.diag']
        self.parser.parse()

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_png_nodoctype_option(self):
        sys.argv = ['', '-Tpng', '--nodoctype', 'input.diag']
        self.parser.parse()

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_pdf_nodoctype_option(self):
        sys.argv = ['', '-Tpdf', '--nodoctype', 'input.diag']
        self.parser.parse()

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_svg_notransparency_option(self):
        sys.argv = ['', '-Tsvg', '--no-transparency', 'input.diag']
        self.parser.parse()

    @argv_wrapper
    def test_png_notransparency_option(self):
        sys.argv = ['', '-Tpng', '--no-transparency', 'input.diag']
        self.parser.parse()

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_pdf_notransparency_option(self):
        sys.argv = ['', '-Tpdf', '--no-transparency', 'input.diag']
        self.parser.parse()

    @argv_wrapper
    def test_config_option(self):
        try:
            tmp = tempfile.mkstemp()
            sys.argv = ['', '-c', tmp[1], 'input.diag']
            self.parser.parse()
        finally:
            os.close(tmp[0])
            os.unlink(tmp[1])

    @argv_wrapper
    def test_config_option_with_bom(self):
        try:
            tmp = tempfile.mkstemp()
            fp = os.fdopen(tmp[0], 'wt')
            fp.write("\xEF\xBB\xBF[blockdiag]\n")
            fp.close()

            sys.argv = ['', '-c', tmp[1], 'input.diag']
            self.parser.parse()
        finally:
            os.unlink(tmp[1])

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_invalid_config_option(self):
        sys.argv = ['', '-c', '/unknown_config_file', 'input.diag']
        self.parser.parse()

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_invalid_dir_config_option(self):
        try:
            tmp = tempfile.mkdtemp()

            sys.argv = ['', '-c', tmp, 'input.diag']
            self.parser.parse()
        finally:
            os.rmdir(tmp)

    @argv_wrapper
    def test_config_option_fontpath(self):
        try:
            tmp = tempfile.mkstemp()
            config = '[blockdiag]\nfontpath = /path/to/font\n'
            os.fdopen(tmp[0], 'wt').write(config)

            sys.argv = ['', '-c', tmp[1], 'input.diag']
            options = self.parser.parse()
            self.assertEqual(options.font, ['/path/to/font'])
        finally:
            os.unlink(tmp[1])

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_not_exist_font_config_option(self):
        sys.argv = ['', '-f', '/font_is_not_exist', 'input.diag']
        options = self.parser.parse()
        detectfont(options)

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_not_exist_font_config_option2(self):
        sys.argv = ['', '-f', '/font_is_not_exist',
                    '-f', '/font_is_not_exist2', 'input.diag']
        options = self.parser.parse()
        detectfont(options)

    @argv_wrapper
    def test_auto_font_detection(self):
        sys.argv = ['', 'input.diag']
        options = self.parser.parse()
        fontpath = detectfont(options)
        self.assertTrue(fontpath)

    @assertRaises(RuntimeError)
    @argv_wrapper
    def test_not_exist_fontmap_config(self):
        sys.argv = ['', '--fontmap', '/fontmap_is_not_exist', 'input.diag']
        options = self.parser.parse()
        fontpath = detectfont(options)
        self.assertTrue(fontpath)

    @assertRaises(RuntimeError)
    def test_unknown_image_driver(self):
        from blockdiag.drawer import DiagramDraw
        from blockdiag.elements import Diagram

        DiagramDraw('unknown', Diagram())
