# -*- coding: utf-8 -*-

import os
import sys
import re
import tempfile
from blockdiag.tests.utils import stderr_wrapper
from blockdiag.tests.utils import with_pil, with_pdf

import blockdiag
import blockdiag.command


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


@stderr_wrapper
def __build_diagram(filename, _format, additional_args):
    testdir = os.path.dirname(__file__)
    diagpath = "%s/diagrams/%s" % (testdir, filename)
    fontpath = get_fontpath()

    try:
        tmpdir = tempfile.mkdtemp()
        tmpfile = tempfile.mkstemp(dir=tmpdir)
        os.close(tmpfile[0])

        args = ['-T', _format, '-o', tmpfile[1], diagpath]
        if additional_args:
            if isinstance(additional_args[0], (list, tuple)):
                args += additional_args[0]
            else:
                args += additional_args
        if os.path.exists(fontpath):
            args += ['-f', fontpath]

        blockdiag.command.main(args)

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
def not_exist_font_config_option_test():
    from blockdiag.utils.bootstrap import detectfont
    fontpath = get_fontpath()
    args = ['-f', '/font_is_not_exist', '-f', fontpath, 'input.diag']
    options = blockdiag.command.BlockdiagOptions(blockdiag).parse(args)
    detectfont(options)


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

        args = ['-T', 'SVG', '-o', tmpfile[1], diagpath]
        if os.path.exists(fontpath):
            args += ['-f', fontpath]

        blockdiag.command.main(args)

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
