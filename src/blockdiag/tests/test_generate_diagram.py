# -*- coding: utf-8 -*-

import os
import sys
import re
import tempfile
import blockdiag.command
from blockdiag.elements import *


def extra_case(func):
    filename = "VL-PGothic-Regular.ttf"
    testdir = os.path.dirname(__file__)
    pathname = "%s/truetype/%s" % (testdir, filename)

    if os.path.exists(pathname):
        func.__test__ = True
    else:
        func.__test__ = False

    return func


def __build_diagram(filename, format, *args):
    testdir = os.path.dirname(__file__)
    diagpath = "%s/diagrams/%s" % (testdir, filename)

    fontfile = "VL-PGothic-Regular.ttf"
    fontpath = "%s/truetype/%s" % (testdir, fontfile)

    try:
        argv = sys.argv
        tmpdir = tempfile.mkdtemp()
        tmpfile = tempfile.mkstemp(dir=tmpdir)
        os.close(tmpfile[0])

        sys.argv = ['blockdiag.py', '-T', format, '-f', fontpath,
                    '-o', tmpfile[1], diagpath]
        if args:
            sys.argv += args

        blockdiag.command.main()
    finally:
        sys.argv = argv
        for file in os.listdir(tmpdir):
            os.unlink(tmpdir + "/" + file)
        os.rmdir(tmpdir)


def diagram_files():
    testdir = os.path.dirname(__file__)
    pathname = "%s/diagrams/" % testdir

    skipped = ['errors',
               'white.gif']

    return [d for d in os.listdir(pathname) if d not in skipped]


@extra_case
def test_generator():
    formats = ['svg', 'png']
    try:
        import reportlab.pdfgen.canvas
        formats.append('pdf')
    except ImportError:
        sys.stderr.write("Skip testing about pdf exporting.\n")
        pass

    for diagram in diagram_files():
        for format in formats:
            yield __build_diagram, diagram, format

            if re.search('separate', diagram):
                yield __build_diagram, diagram, format, '--separate'

            if format == 'png':
                yield __build_diagram, diagram, format, '--antialias'
