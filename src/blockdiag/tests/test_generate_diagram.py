# -*- coding: utf-8 -*-

import os
import sys
import re
import tempfile
from blockdiag.tests.utils import *

import blockdiag
import blockdiag.command
from blockdiag.elements import *


def get_fontpath():
    filename = "VL-PGothic-Regular.ttf"
    testdir = os.path.dirname(__file__)
    return "%s/truetype/%s" % (testdir, filename)


def extra_case(func):
    pathname = get_fontpath()

    if os.path.exists(pathname):
        func.__test__ = True
    else:
        func.__test__ = False

    return func


@argv_wrapper
@stderr_wrapper
def __build_diagram(filename, _format, args):
    testdir = os.path.dirname(__file__)
    diagpath = "%s/diagrams/%s" % (testdir, filename)
    fontpath = get_fontpath()

    try:
        tmpdir = tempfile.mkdtemp()
        tmpfile = tempfile.mkstemp(dir=tmpdir)
        os.close(tmpfile[0])

        sys.argv = ['blockdiag.py', '-T', _format, '-o', tmpfile[1], diagpath]
        if args:
            if isinstance(args[0], (list, tuple)):
                sys.argv += args[0]
            else:
                sys.argv += args
        if os.path.exists(fontpath):
            sys.argv += ['-f', fontpath]

        blockdiag.command.main()

        if re.search('ERROR', sys.stderr.getvalue()):
            raise RuntimeError(sys.stderr.getvalue())
    finally:
        for filename in os.listdir(tmpdir):
            os.unlink(tmpdir + "/" + filename)
        os.rmdir(tmpdir)


def diagram_files():
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/" % testdir

    skipped = ['errors',
               'white.gif']

    return [d for d in os.listdir(pathname) if d not in skipped]


def test_generator_svg():
    args = []
    if not supported_pil():
        args.append('--ignore-pil')

    for testcase in generator_core('svg', args):
        yield testcase


@with_pil
@extra_case
def test_generator_png():
    for testcase in generator_core('png'):
        yield testcase


@with_pdf
@extra_case
def test_generator_pdf():
    for testcase in generator_core('pdf'):
        yield testcase


def generator_core(_format, *args):
    for diagram in diagram_files():
        yield __build_diagram, diagram, _format, args

        if re.search('separate', diagram):
            _args = list(args) + ['--separate']
            yield __build_diagram, diagram, _format, _args

        if _format == 'png':
            _args = list(args) + ['--antialias']
            yield __build_diagram, diagram, _format, _args


@extra_case
@argv_wrapper
def not_exist_font_config_option_test():
    fontpath = get_fontpath()
    sys.argv = ['', '-f', '/font_is_not_exist', '-f', fontpath, 'input.diag']
    options = blockdiag.command.BlockdiagOptions(blockdiag).parse()
    blockdiag.command.detectfont(options)


@argv_wrapper
@stderr_wrapper
def svg_includes_source_code_tag_test():
    from xml.etree import ElementTree

    testdir = os.path.dirname(__file__)
    diagpath = "%s/diagrams/single_edge.diag" % testdir
    fontpath = get_fontpath()

    try:
        tmpdir = tempfile.mkdtemp()
        tmpfile = tempfile.mkstemp(dir=tmpdir)
        os.close(tmpfile[0])

        sys.argv = ['blockdiag.py', '-T', 'SVG', '-o', tmpfile[1], diagpath]
        if os.path.exists(fontpath):
            sys.argv += ['-f', fontpath]
        if not supported_pil():
            sys.argv += ['--ignore-pil']

        blockdiag.command.main()

        if re.search('ERROR', sys.stderr.getvalue()):
            raise RuntimeError(sys.stderr.getvalue())

        # compare embeded source code
        source_code = open(diagpath).read()
        tree = ElementTree.parse(tmpfile[1])
        desc = tree.find('{http://www.w3.org/2000/svg}desc')

        # strip spaces
        source_code = re.sub('\s+', ' ', source_code)
        embeded = re.sub('\s+', ' ', desc.text)
        assert source_code == embeded
    finally:
        for filename in os.listdir(tmpdir):
            os.unlink(tmpdir + "/" + filename)
        os.rmdir(tmpdir)
