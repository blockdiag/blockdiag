# -*- coding: utf-8 -*-

import os
import sys
import re
import tempfile
import blockdiag
import blockdiag.command
from utils import *
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
def __build_diagram(filename, format, args):
    testdir = os.path.dirname(__file__)
    diagpath = "%s/diagrams/%s" % (testdir, filename)
    fontpath = get_fontpath()

    try:
        tmpdir = tempfile.mkdtemp()
        tmpfile = tempfile.mkstemp(dir=tmpdir)
        os.close(tmpfile[0])

        sys.argv = ['blockdiag.py', '-T', format, '-o', tmpfile[1], diagpath]
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
        for file in os.listdir(tmpdir):
            os.unlink(tmpdir + "/" + file)
        os.rmdir(tmpdir)


def diagram_files():
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/" % testdir

    skipped = ['errors',
               'white.gif']

    return [d for d in os.listdir(pathname) if d not in skipped]


def test_generator_svg():
    args = []
    try:
        import _imagingft
        _imagingft
    except ImportError:
        args.append('--ignore-pil')

    for testcase in generator_core('svg', args):
        yield testcase


@extra_case
def test_generator_png():
    try:
        import _imagingft
        _imagingft

        for testcase in generator_core('png'):
            yield testcase
    except ImportError:
        sys.stderr.write("Skip testing about png exporting.\n")


@extra_case
def test_generator_pdf():
    try:
        import reportlab.pdfgen.canvas
        reportlab.pdfgen.canvas

        for testcase in generator_core('pdf'):
            yield testcase
    except ImportError:
        sys.stderr.write("Skip testing about pdf exporting.\n")


def generator_core(format, *args):
    for diagram in diagram_files():
        yield __build_diagram, diagram, format, args

        if re.search('separate', diagram):
            _args = list(args) + ['--separate']
            yield __build_diagram, diagram, format, _args

        if format == 'png':
            _args = list(args) + ['--antialias']
            yield __build_diagram, diagram, format, _args


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
        for file in os.listdir(tmpdir):
            os.unlink(tmpdir + "/" + file)
        os.rmdir(tmpdir)
