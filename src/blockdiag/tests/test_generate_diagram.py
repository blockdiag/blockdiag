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

import os
import re
import sys
import unittest
from xml.etree import ElementTree

import pytest

import blockdiag
import blockdiag.command
from blockdiag.tests.utils import (TemporaryDirectory, capture_stderr,
                                   supported_pdf, supported_pil)

TESTDIR = os.path.dirname(__file__)
FONTPATH = os.path.join(TESTDIR, 'VLGothic', 'VL-Gothic-Regular.ttf')


def get_fontpath(testdir):
    return os.path.join(testdir, 'VLGothic', 'VL-Gothic-Regular.ttf')


def get_diagram_files(testdir):
    diagramsdir = os.path.join(testdir, 'diagrams')

    skipped = ['README', 'debian-logo-256color-palettealpha.png',
               'errors', 'invalid.txt', 'white.gif']
    for file in os.listdir(diagramsdir):
        if file in skipped:
            pass
        else:
            yield os.path.join(diagramsdir, file)


base_path = os.path.dirname(__file__)
files = get_diagram_files(base_path)
generate_testdata = []
generate_with_separate_testdata = []
for file_source in files:
    generate_testdata.append((file_source, 'svg', []))
    generate_testdata.append((file_source, 'png', []))
    generate_testdata.append((file_source, 'png', ['--antialias']))
    generate_testdata.append((file_source, 'pdf', []))
    if re.search('separate', file_source):
        generate_with_separate_testdata.append((file_source, 'svg', ['--separate']))
        generate_with_separate_testdata.append((file_source, 'png', ['--separate']))
        generate_with_separate_testdata.append((file_source, 'png', ['--separate', '--antialias']))
        generate_with_separate_testdata.append((file_source, 'pdf', ['--separate']))


@pytest.mark.parametrize("source,file_type,options", generate_with_separate_testdata)
def test_generate_with_separate_option(source, file_type, options):
    generate(source, file_type, options)


@pytest.mark.parametrize("source,file_type,options", generate_testdata)
def test_generate_with_separate(source, file_type, options):
    generate(source, file_type, options)


@capture_stderr
def generate(source, file_type, options):
    if file_type == 'png':
        if not supported_pil():
            unittest.skip('Pillow is not available')
            return
        if os.environ.get('ALL_TESTS') is None:
            unittest.skip('Skipped by default. To enable it, specify $ALL_TESTS=1')
            return
    elif file_type == 'pdf':
        if not supported_pdf():
            unittest.skip('reportlab is not available')
            return
        if os.environ.get('ALL_TESTS') is None:
            unittest.skip('Skipped by default. To enable it, specify $ALL_TESTS=1')
            return

    tmpdir = None
    try:
        tmpdir = TemporaryDirectory()
        fd, tmp_file = tmpdir.mkstemp()
        os.close(fd)
        blockdiag.command.main(
            [
                '--debug',
                '-T',
                file_type,
                '-o', tmp_file, source
            ] + list(options)
        )
    finally:
        if tmpdir is not None:
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
        source_code = re.sub(r'\s+', ' ', source_code)
        embeded = re.sub(r'\s+', ' ', desc.text)
        assert source_code == embeded
    finally:
        tmpdir.clean()


@capture_stderr
def svg_sanitizes_url_on_error_test():
    testdir = os.path.dirname(__file__)
    diagpath = os.path.join(testdir, 'diagrams', 'background_url_local.diag')

    try:
        tmpdir = TemporaryDirectory()
        fd, tmpfile = tmpdir.mkstemp()
        os.close(fd)

        args = ['-T', 'SVG', '-o', tmpfile, diagpath]
        ret = blockdiag.command.main(args)
        tree = ElementTree.parse(tmpfile)
        images = tree.findall('{http://www.w3.org/2000/svg}image')
        valid_url, invalid_url = [image.attrib.get('{http://www.w3.org/1999/xlink}href') for image in images]

        assert valid_url
        assert not invalid_url
        assert 'unknown image type:' in sys.stderr.getvalue()
        assert ret == 0
    finally:
        tmpdir.clean()
