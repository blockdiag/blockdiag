# -*- coding: utf-8 -*-

import re
import os
import sys
import unittest
import tempfile
from utils import stderr_wrapper
from nose.tools import raises
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


class TestRstDirectives(unittest.TestCase):
    def teardown():
        if 'blockdiag' in docutils._directives:
            del _directives['blockdiag']

    def test_rst_directives_setup(self):
        directives.setup()

        self.assertTrue('blockdiag' in docutils._directives)
        self.assertEqual(directives.BlockdiagDirective,
                         docutils._directives['blockdiag'])
        self.assertEqual('PNG', directives.format)
        self.assertEqual(False, directives.antialias)
        self.assertEqual(None, directives.fontpath)

    def test_rst_directives_setup_with_args(self):
        directives.setup(format='SVG', antialias=True, fontpath='/dev/null')

        self.assertTrue('blockdiag' in docutils._directives)
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
        self.assertEqual(type(doctree[0]), nodes.system_message)

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
        self.assertEqual(type(doctree[0]), nodes.system_message)

    # FIXME
    #@setup_directive_base
    #def test_rst_directives_base_with_filename(self):
    #    text = ".. blockdiag:: diagrams/node_attributes.diag"
    #    doctree = publish_doctree(text)
    #    self.assertEqual(type(doctree[0]), nodes.system_message)

    @stderr_wrapper
    @setup_directive_base
    def test_rst_directives_base_with_block_and_filename(self):
        text = ".. blockdiag:: diagrams/node_attributes.diag\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(type(doctree[0]), nodes.system_message)

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
        self.assertEqual(type(doctree[0]), nodes.image)
        self.assertFalse('alt' in doctree[0]) 
        self.assertEqual(0, doctree[0]['uri'].index(path))
        self.assertFalse('target' in doctree[0]) 

    @use_tmpdir
    def test_rst_directives_with_block_alt(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(type(doctree[0]), nodes.image)
        self.assertEqual('hello world', doctree[0]['alt'])
        self.assertEqual(0, doctree[0]['uri'].index(path))
        self.assertFalse('target' in doctree[0]) 

    @raises(RuntimeError)
    @use_tmpdir
    def test_rst_directives_with_block_fontpath1(self, path):
        directives.setup(format='SVG', fontpath=['dummy.ttf'], outputdir=path)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)

    @raises(RuntimeError)
    @use_tmpdir
    def test_rst_directives_with_block_fontpath2(self, path):
        directives.setup(format='SVG', fontpath='dummy.ttf', outputdir=path)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)

    @use_tmpdir
    def test_rst_directives_with_block_maxwidth(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :maxwidth: 100\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(type(doctree[0]), nodes.image)
        self.assertFalse('alt' in doctree[0]) 
        self.assertEqual(0, doctree[0]['uri'].index(path))
        self.assertFalse(0, doctree[0]['target'].index(path)) 
