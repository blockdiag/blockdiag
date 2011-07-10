# -*- coding: utf-8 -*-

import os
import sys
import tempfile
from nose.tools import raises
from blockdiag.command import parse_option, main


def replace_argv(func):
    def test():
        try:
            argv = sys.argv
            func()
        finally:
            sys.argv = argv

    return test


@replace_argv
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
@replace_argv
def invalid_type_option_test():
    sys.argv = ['', '-Tsvgz', 'input.diag']
    option = parse_option()


@replace_argv
def svg_separate_option_test():
    sys.argv = ['', '-Tsvg', '--separate', 'input.diag']
    option = parse_option()


@raises(RuntimeError)
@replace_argv
def png_separate_option_test():
    sys.argv = ['', '-Tpng', '--separate', 'input.diag']
    option = parse_option()


@raises(RuntimeError)
@replace_argv
def pdf_separate_option_test():
    sys.argv = ['', '-Tpdf', '--separate', 'input.diag']
    option = parse_option()


@replace_argv
def svg_nodoctype_option_test():
    sys.argv = ['', '-Tsvg', '--nodoctype', 'input.diag']
    option = parse_option()


@raises(RuntimeError)
@replace_argv
def png_nodoctype_option_test():
    sys.argv = ['', '-Tpng', '--nodoctype', 'input.diag']
    option = parse_option()


@raises(RuntimeError)
@replace_argv
def pdf_nodoctype_option_test():
    sys.argv = ['', '-Tpdf', '--nodoctype', 'input.diag']
    option = parse_option()


@replace_argv
def config_option_test():
    tmp = tempfile.mkstemp()
    sys.argv = ['', '-c', tmp[1], 'input.diag']
    option = parse_option()

    os.close(tmp[0])
    os.unlink(tmp[1])


@raises(RuntimeError)
@replace_argv
def invalid_config_option_test():
    tmp = tempfile.mkstemp()
    os.close(tmp[0])
    os.unlink(tmp[1])

    sys.argv = ['', '-c', tmp[1], 'input.diag']
    option = parse_option()


@raises(RuntimeError)
@replace_argv
def invalid_dir_config_option_test():
    try:
        tmp = tempfile.mkdtemp()

        sys.argv = ['', '-c', tmp, 'input.diag']
        option = parse_option()
    finally:
        os.rmdir(tmp)


@raises(RuntimeError)
@replace_argv
def not_exist_font_config_option_test():
    try:
        tmp = tempfile.mkdtemp()

        sys.argv = ['', '-f', '/font_is_not_exist', '-c', tmp, 'input.diag']
        option = parse_option()
    finally:
        os.rmdir(tmp)
