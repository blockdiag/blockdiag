# -*- coding: utf-8 -*-

import re
import os
import sys
import tempfile
import unittest2
from utils import stderr_wrapper, assertRaises
from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import directives as docutils
from blockdiag.utils.rst import directives


def setup_directive_base(func):
    def _(self):
        klass = directives.BlockdiagDirectiveBase
        docutils.register_directive('blockdiag', klass)
        func(self)

    _.__name__ = func.__name__
    return _


def use_tmpdir(func):
    def _(self):
        try:
            tmpdir = tempfile.mkdtemp()
            func(self, tmpdir)
        finally:
            for file in os.listdir(tmpdir):
                os.unlink(tmpdir + "/" + file)
            os.rmdir(tmpdir)

    _.__name__ = func.__name__
    return _


class TestRstDirectives(unittest2.TestCase):
    def tearDown(self):
        if 'blockdiag' in docutils._directives:
            del docutils._directives['blockdiag']

    def test_rst_directives_setup(self):
        directives.setup()

        self.assertIn('blockdiag', docutils._directives)
        self.assertEqual(directives.BlockdiagDirective,
                         docutils._directives['blockdiag'])
        self.assertEqual('PNG', directives.format)
        self.assertEqual(False, directives.antialias)
        self.assertEqual(None, directives.fontpath)

    def test_rst_directives_setup_with_args(self):
        directives.setup(format='SVG', antialias=True, fontpath='/dev/null')

        self.assertIn('blockdiag', docutils._directives)
        self.assertEqual(directives.BlockdiagDirective,
                         docutils._directives['blockdiag'])
        self.assertEqual('SVG', directives.format)
        self.assertEqual(True, directives.antialias)
        self.assertEqual('/dev/null', directives.fontpath)

    @stderr_wrapper
    @setup_directive_base
    def test_rst_directives_base_noargs(self):
        text = ".. blockdiag::"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @setup_directive_base
    def test_rst_directives_base_with_block(self):
        text = ".. blockdiag::\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(directives.blockdiag, type(doctree[0]))
        self.assertEqual('{ A -> B }', doctree[0]['code'])
        self.assertEqual(None, doctree[0]['alt'])
        self.assertEqual({}, doctree[0]['options'])

    @stderr_wrapper
    @setup_directive_base
    def test_rst_directives_base_with_emptyblock(self):
        text = ".. blockdiag::\n\n   \n"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @setup_directive_base
    def test_rst_directives_base_with_filename(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'diagrams/node_attribute.diag')
        text = ".. blockdiag:: %s" % filename
        doctree = publish_doctree(text)

        self.assertEqual(1, len(doctree))
        self.assertEqual(directives.blockdiag, type(doctree[0]))
        self.assertEqual(open(filename).read(), doctree[0]['code'])
        self.assertEqual(None, doctree[0]['alt'])
        self.assertEqual({}, doctree[0]['options'])

    @stderr_wrapper
    @setup_directive_base
    def test_rst_directives_base_with_filename_not_exists(self):
        text = ".. blockdiag:: unknown.diag"
        doctree = publish_doctree(text)
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @stderr_wrapper
    @setup_directive_base
    def test_rst_directives_base_with_block_and_filename(self):
        text = ".. blockdiag:: unknown.diag\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @setup_directive_base
    def test_rst_directives_base_with_options(self):
        text = ".. blockdiag::\n   :alt: hello world\n   :desctable:\n" + \
               "   :maxwidth: 100\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(directives.blockdiag, type(doctree[0]))
        self.assertEqual('{ A -> B }', doctree[0]['code'])
        self.assertEqual('hello world', doctree[0]['alt'])
        self.assertEqual(None, doctree[0]['options']['desctable'])
        self.assertEqual(100, doctree[0]['options']['maxwidth'])

    @use_tmpdir
    def test_rst_directives_with_block(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertFalse('alt' in doctree[0])
        self.assertEqual(0, doctree[0]['uri'].index(path))
        self.assertFalse('target' in doctree[0])

    @use_tmpdir
    def test_rst_directives_with_block_alt(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertEqual('hello world', doctree[0]['alt'])
        self.assertEqual(0, doctree[0]['uri'].index(path))
        self.assertFalse('target' in doctree[0])

    @use_tmpdir
    @assertRaises(RuntimeError)
    def test_rst_directives_with_block_fontpath1(self, path):
        directives.setup(format='SVG', fontpath=['dummy.ttf'],
                         outputdir=path)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)

    @use_tmpdir
    @assertRaises(RuntimeError)
    def test_rst_directives_with_block_fontpath2(self, path):
        directives.setup(format='SVG', fontpath='dummy.ttf',
                         outputdir=path)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)

    @use_tmpdir
    def test_rst_directives_with_block_maxwidth(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :maxwidth: 100\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertFalse('alt' in doctree[0])
        self.assertEqual(0, doctree[0]['uri'].index(path))
        self.assertFalse(0, doctree[0]['target'].index(path))

    @use_tmpdir
    def test_rst_directives_with_block_desctable(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(2, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertEqual(nodes.table, type(doctree[1]))

        self.assertEqual(1, len(doctree[1]))
        self.assertEqual(nodes.tgroup, type(doctree[1][0]))

        # tgroup
        self.assertEqual(4, len(doctree[1][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][1]))
        self.assertEqual(nodes.thead, type(doctree[1][0][2]))
        self.assertEqual(nodes.tbody, type(doctree[1][0][3]))

        # colspec
        self.assertEqual(0, len(doctree[1][0][0]))
        self.assertEqual(50, doctree[1][0][0]['colwidth'])

        self.assertEqual(0, len(doctree[1][0][1]))
        self.assertEqual(50, doctree[1][0][1]['colwidth'])

        # thead
        thead = doctree[1][0][2]
        self.assertEqual(1, len(thead))
        self.assertEqual(2, len(thead[0]))

        self.assertEqual(1, len(thead[0][0]))
        self.assertEqual(1, len(thead[0][0][0]))
        self.assertEqual('Name', thead[0][0][0][0])

        self.assertEqual(1, len(thead[0][1]))
        self.assertEqual(1, len(thead[0][1][0]))
        self.assertEqual('Description', thead[0][1][0][0])

        # tbody
        tbody = doctree[1][0][3]
        self.assertEqual(2, len(tbody))

        self.assertEqual(2, len(tbody[0]))
        self.assertEqual(1, len(tbody[0][0]))
        self.assertEqual(1, len(tbody[0][0][0]))
        self.assertEqual('A', tbody[0][0][0][0])
        self.assertEqual(0, len(tbody[0][1]))

        self.assertEqual(2, len(tbody[1]))
        self.assertEqual(1, len(tbody[1][0]))
        self.assertEqual(1, len(tbody[1][0][0]))
        self.assertEqual('B', tbody[1][0][0][0])
        self.assertEqual(0, len(tbody[1][1]))

    @use_tmpdir
    def test_rst_directives_with_block_desctable_using_node_group(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n   { A -> B; group { A } }"
        doctree = publish_doctree(text)
        self.assertEqual(2, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertEqual(nodes.table, type(doctree[1]))

        self.assertEqual(1, len(doctree[1]))
        self.assertEqual(nodes.tgroup, type(doctree[1][0]))

        # tgroup
        self.assertEqual(4, len(doctree[1][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][1]))
        self.assertEqual(nodes.thead, type(doctree[1][0][2]))
        self.assertEqual(nodes.tbody, type(doctree[1][0][3]))

        # colspec
        self.assertEqual(0, len(doctree[1][0][0]))
        self.assertEqual(50, doctree[1][0][0]['colwidth'])

        self.assertEqual(0, len(doctree[1][0][1]))
        self.assertEqual(50, doctree[1][0][1]['colwidth'])

        # thead
        thead = doctree[1][0][2]
        self.assertEqual(1, len(thead))
        self.assertEqual(2, len(thead[0]))

        self.assertEqual(1, len(thead[0][0]))
        self.assertEqual(1, len(thead[0][0][0]))
        self.assertEqual('Name', thead[0][0][0][0])

        self.assertEqual(1, len(thead[0][1]))
        self.assertEqual(1, len(thead[0][1][0]))
        self.assertEqual('Description', thead[0][1][0][0])

        # tbody
        tbody = doctree[1][0][3]
        self.assertEqual(2, len(tbody))

        self.assertEqual(2, len(tbody[0]))
        self.assertEqual(1, len(tbody[0][0]))
        self.assertEqual(1, len(tbody[0][0][0]))
        self.assertEqual('A', tbody[0][0][0][0])
        self.assertEqual(0, len(tbody[0][1]))

        self.assertEqual(2, len(tbody[1]))
        self.assertEqual(1, len(tbody[1][0]))
        self.assertEqual(1, len(tbody[1][0][0]))
        self.assertEqual('B', tbody[1][0][0][0])
        self.assertEqual(0, len(tbody[1][1]))

    @use_tmpdir
    def test_rst_directives_with_block_desctable_with_description(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n" + \
               "   { A [description = foo]; B [description = bar]; }"
        doctree = publish_doctree(text)
        self.assertEqual(2, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertEqual(nodes.table, type(doctree[1]))

        # tgroup
        self.assertEqual(4, len(doctree[1][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][1]))
        self.assertEqual(nodes.thead, type(doctree[1][0][2]))
        self.assertEqual(nodes.tbody, type(doctree[1][0][3]))

        # colspec
        self.assertEqual(50, doctree[1][0][0]['colwidth'])
        self.assertEqual(50, doctree[1][0][1]['colwidth'])

        # thead
        thead = doctree[1][0][2]
        self.assertEqual(2, len(thead[0]))
        self.assertEqual('Name', thead[0][0][0][0])
        self.assertEqual('Description', thead[0][1][0][0])

        # tbody
        tbody = doctree[1][0][3]
        self.assertEqual(2, len(tbody))
        self.assertEqual('A', tbody[0][0][0][0])
        self.assertEqual('foo', tbody[0][1][0][0])
        self.assertEqual('B', tbody[1][0][0][0])
        self.assertEqual('bar', tbody[1][1][0][0])

    @use_tmpdir
    def test_rst_directives_with_block_desctable_with_rest_markups(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n" + \
               "   { A [description = \"foo *bar* **baz**\"]; " + \
               "     B [description = \"**foo** *bar* baz\"]; }"
        doctree = publish_doctree(text)
        self.assertEqual(2, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertEqual(nodes.table, type(doctree[1]))

        # tgroup
        self.assertEqual(4, len(doctree[1][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][1]))
        self.assertEqual(nodes.thead, type(doctree[1][0][2]))
        self.assertEqual(nodes.tbody, type(doctree[1][0][3]))

        # colspec
        self.assertEqual(50, doctree[1][0][0]['colwidth'])
        self.assertEqual(50, doctree[1][0][1]['colwidth'])

        # thead
        thead = doctree[1][0][2]
        self.assertEqual(2, len(thead[0]))
        self.assertEqual('Name', thead[0][0][0][0])
        self.assertEqual('Description', thead[0][1][0][0])

        # tbody
        tbody = doctree[1][0][3]
        self.assertEqual(2, len(tbody))
        self.assertEqual('A', tbody[0][0][0][0])
        self.assertEqual(4, len(tbody[0][1][0]))
        self.assertEqual(nodes.Text, type(tbody[0][1][0][0]))
        self.assertEqual('foo ', str(tbody[0][1][0][0]))
        self.assertEqual(nodes.emphasis, type(tbody[0][1][0][1]))
        self.assertEqual(nodes.Text, type(tbody[0][1][0][1][0]))
        self.assertEqual('bar', tbody[0][1][0][1][0])
        self.assertEqual(nodes.Text, type(tbody[0][1][0][2]))
        self.assertEqual(' ', str(tbody[0][1][0][2]))
        self.assertEqual(nodes.strong, type(tbody[0][1][0][3]))
        self.assertEqual(nodes.Text, type(tbody[0][1][0][3][0]))
        self.assertEqual('baz', str(tbody[0][1][0][3][0]))

        self.assertEqual('B', tbody[1][0][0][0])
        self.assertEqual(4, len(tbody[1][1][0]))
        print tbody[1][1][0]
        self.assertEqual(nodes.strong, type(tbody[1][1][0][0]))
        self.assertEqual(nodes.Text, type(tbody[1][1][0][0][0]))
        self.assertEqual('foo', str(tbody[1][1][0][0][0]))
        self.assertEqual(nodes.Text, type(tbody[1][1][0][1]))
        self.assertEqual(' ', str(tbody[1][1][0][1]))
        self.assertEqual(nodes.emphasis, type(tbody[1][1][0][2]))
        self.assertEqual(nodes.Text, type(tbody[1][1][0][2][0]))
        self.assertEqual('bar', str(tbody[1][1][0][2][0]))
        self.assertEqual(nodes.Text, type(tbody[1][1][0][3]))
        self.assertEqual(' baz', str(tbody[1][1][0][3]))

    @use_tmpdir
    def test_rst_directives_with_block_desctable_with_numbered(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n" + \
               "   { A [numbered = 2]; B [numbered = 1]; }"
        doctree = publish_doctree(text)
        self.assertEqual(2, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertEqual(nodes.table, type(doctree[1]))

        # tgroup
        self.assertEqual(5, len(doctree[1][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][0]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][1]))
        self.assertEqual(nodes.colspec, type(doctree[1][0][2]))
        self.assertEqual(nodes.thead, type(doctree[1][0][3]))
        self.assertEqual(nodes.tbody, type(doctree[1][0][4]))

        # colspec
        self.assertEqual(25, doctree[1][0][0]['colwidth'])
        self.assertEqual(50, doctree[1][0][1]['colwidth'])
        self.assertEqual(50, doctree[1][0][2]['colwidth'])

        # thead
        thead = doctree[1][0][3]
        self.assertEqual(3, len(thead[0]))
        self.assertEqual('No', thead[0][0][0][0])
        self.assertEqual('Name', thead[0][1][0][0])
        self.assertEqual('Description', thead[0][2][0][0])

        # tbody
        tbody = doctree[1][0][4]
        self.assertEqual(2, len(tbody))
        self.assertEqual('1', tbody[0][0][0][0])
        self.assertEqual('B', tbody[0][1][0][0])
        self.assertEqual(0, len(tbody[0][2]))
        self.assertEqual('2', tbody[1][0][0][0])
        self.assertEqual('A', tbody[1][1][0][0])
        self.assertEqual(0, len(tbody[1][2]))
