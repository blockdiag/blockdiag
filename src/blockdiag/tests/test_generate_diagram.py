# -*- coding: utf-8 -*-

import os
import re
import sys
from nose.tools import nottest
import blockdiag
import blockdiag.command
from blockdiag.tests.utils import capture_stderr, TemporaryDirectory
from blockdiag.tests.utils import supported_pil, supported_pdf

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


TESTDIR = os.path.dirname(__file__)
FONTPATH = os.path.join(TESTDIR, 'VLGothic', 'VL-Gothic-Regular.ttf')


def get_fontpath(testdir):
    return os.path.join(testdir, 'VLGothic', 'VL-Gothic-Regular.ttf')


def get_diagram_files(testdir):
    diagramsdir = os.path.join(testdir, 'diagrams')

    skipped = ['README', 'debian-logo-256color-palettealpha.png',
               'errors', 'white.gif']
    for file in os.listdir(diagramsdir):
        if file in skipped:
            pass
        else:
            yield os.path.join(diagramsdir, file)


def test_generate():
    mainfunc = blockdiag.command.main
    basepath = os.path.dirname(__file__)
    files = get_diagram_files(basepath)
    options = []

    for testcase in testcase_generator(basepath, mainfunc, files, options):
        yield testcase


def test_generate_with_separate():
    mainfunc = blockdiag.command.main
    basepath = os.path.dirname(__file__)
    files = get_diagram_files(basepath)
    filtered = (f for f in files if re.search('separate', f))
    options = ['--separate']

    for testcase in testcase_generator(basepath, mainfunc, filtered, options):
        yield testcase


@nottest
def testcase_generator(basepath, mainfunc, files, options):
    fontpath = get_fontpath(basepath)
    options = options + ['-f', fontpath]

    for source in files:
        yield generate, mainfunc, 'svg', source, options

        if not supported_pil():
            yield unittest.skip("Pillow is not available")(generate)
            yield unittest.skip("Pillow is not available")(generate)
        elif os.environ.get('ALL_TESTS') is None:
            message = "Skipped by default. To enable it, specify $ALL_TESTS=1"
            yield unittest.skip(message)(generate)
            yield unittest.skip(message)(generate)
        else:
            yield generate, mainfunc, 'png', source, options
            yield generate, mainfunc, 'png', source, options + ['--antialias']

        if not supported_pdf():
            yield unittest.skip("reportlab is not available")(generate)
        elif os.environ.get('ALL_TESTS') is None:
            message = "Skipped by default. To enable it, specify $ALL_TESTS=1"
            yield unittest.skip(message)(generate)
        else:
            yield generate, mainfunc, 'pdf', source, options


@capture_stderr
def generate(mainfunc, filetype, source, options):
    try:
        tmpdir = TemporaryDirectory()
        fd, tmpfile = tmpdir.mkstemp()
        os.close(fd)

        mainfunc(['--debug', '-T', filetype, '-o', tmpfile, source] +
                 list(options))
    finally:
        tmpdir.clean()


def not_exist_font_config_option_test():
    args = ['-f', '/font_is_not_exist', '-f', FONTPATH, 'input.diag']
    options = blockdiag.command.BlockdiagOptions(blockdiag).parse(args)

    from blockdiag.utils.bootstrap import detectfont
    detectfont(options)


def stdin_test():
    testdir = os.path.dirname(__file__)
    diagpath = os.path.join(testdir, 'diagrams', 'single_edge.diag')

    try:
        stdin = sys.stdin
        sys.stdin = open(diagpath, 'r')

        tmpdir = TemporaryDirectory()
        fd, tmpfile = tmpdir.mkstemp()
        os.close(fd)

        args = ['-T', 'SVG', '-o', tmpfile, '-']
        ret = blockdiag.command.main(args)
        assert ret == 0
    finally:
        sys.stdin = stdin
        tmpdir.clean()


@capture_stderr
def ghostscript_not_found_test():
    testdir = os.path.dirname(__file__)
    diagpath = os.path.join(testdir, 'diagrams', 'background_url_image.diag')

    try:
        old_path = os.environ['PATH']
        os.environ['PATH'] = ''
        tmpdir = TemporaryDirectory()
        fd, tmpfile = tmpdir.mkstemp()
        os.close(fd)

        args = ['-T', 'SVG', '-o', tmpfile, diagpath]
        ret = blockdiag.command.main(args)
        assert 'Could not convert image:' in sys.stderr.getvalue()
        assert ret == 0
    finally:
        tmpdir.clean()
        os.environ['PATH'] = old_path


@capture_stderr
def svg_includes_source_code_tag_test():
    from xml.etree import ElementTree

    testdir = os.path.dirname(__file__)
    diagpath = os.path.join(testdir, 'diagrams', 'single_edge.diag')

    try:
        tmpdir = TemporaryDirectory()
        fd, tmpfile = tmpdir.mkstemp()
        os.close(fd)

        args = ['-T', 'SVG', '-o', tmpfile, diagpath]
        blockdiag.command.main(args)

        # compare embeded source code
        source_code = open(diagpath).read()
        tree = ElementTree.parse(tmpfile)
        desc = tree.find('{http://www.w3.org/2000/svg}desc')

        # strip spaces
        source_code = re.sub('\s+', ' ', source_code)
        embeded = re.sub('\s+', ' ', desc.text)
        assert source_code == embeded
    finally:
        tmpdir.clean()
