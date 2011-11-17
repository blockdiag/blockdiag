# -*- coding: utf-8 -*-

import os
import sys
import tempfile
from utils import argv_wrapper
from nose.tools import raises, ok_, eq_
from blockdiag.command import parse_option, detectfont


@argv_wrapper
def type_option_test():
    sys.argv = ['', '-Tsvg', 'input.diag']
    parse_option()

    sys.argv = ['', '-TSVG', 'input.diag']
    parse_option()

    sys.argv = ['', '-TSvg', 'input.diag']
    parse_option()

    sys.argv = ['', '-Tpng', 'input.diag']
    parse_option()

    sys.argv = ['', '-Tpdf', 'input.diag']
    parse_option()


@raises(RuntimeError)
@argv_wrapper
def invalid_type_option_test():
    sys.argv = ['', '-Tsvgz', 'input.diag']
    (options, args) = parse_option()


@argv_wrapper
def separate_option_test():
    sys.argv = ['', '-Tsvg', '--separate', 'input.diag']
    (options, args) = parse_option()

    sys.argv = ['', '-Tpng', '--separate', 'input.diag']
    (options, args) = parse_option()

    sys.argv = ['', '-Tpdf', '--separate', 'input.diag']
    (options, args) = parse_option()


@argv_wrapper
def svg_nodoctype_option_test():
    sys.argv = ['', '-Tsvg', '--nodoctype', 'input.diag']
    (options, args) = parse_option()


@raises(RuntimeError)
@argv_wrapper
def png_nodoctype_option_test():
    sys.argv = ['', '-Tpng', '--nodoctype', 'input.diag']
    (options, args) = parse_option()


@raises(RuntimeError)
@argv_wrapper
def pdf_nodoctype_option_test():
    sys.argv = ['', '-Tpdf', '--nodoctype', 'input.diag']
    (options, args) = parse_option()


@argv_wrapper
def config_option_test():
    tmp = tempfile.mkstemp()
    sys.argv = ['', '-c', tmp[1], 'input.diag']
    (options, args) = parse_option()

    os.close(tmp[0])
    os.unlink(tmp[1])


@raises(RuntimeError)
@argv_wrapper
def invalid_config_option_test():
    tmp = tempfile.mkstemp()
    os.close(tmp[0])
    os.unlink(tmp[1])

    sys.argv = ['', '-c', tmp[1], 'input.diag']
    (options, args) = parse_option()


@raises(RuntimeError)
@argv_wrapper
def invalid_dir_config_option_test():
    try:
        tmp = tempfile.mkdtemp()

        sys.argv = ['', '-c', tmp, 'input.diag']
        (options, args) = parse_option()
    finally:
        os.rmdir(tmp)


@argv_wrapper
def config_option_fontpath_test():
    tmp = tempfile.mkstemp()
    os.fdopen(tmp[0], 'wt').write('[blockdiag]\nfontpath = /path/to/font\n')

    sys.argv = ['', '-c', tmp[1], 'input.diag']
    (options, args) = parse_option()
    eq_(['/path/to/font'], options.font)

    os.unlink(tmp[1])


@raises(RuntimeError)
@argv_wrapper
def not_exist_font_config_option_test():
    sys.argv = ['', '-f', '/font_is_not_exist', 'input.diag']
    (options, args) = parse_option()
    detectfont(options)


@argv_wrapper
def auto_font_detection_test():
    sys.argv = ['', 'input.diag']
    (options, args) = parse_option()
    fontpath = detectfont(options)
    ok_(fontpath)
