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

import io
import os
import unittest

from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import directives as docutils

from blockdiag.tests.utils import TemporaryDirectory, capture_stderr
from blockdiag.utils.rst import directives
from blockdiag.utils.rst.nodes import blockdiag as blockdiag_node


class TestRstDirectives(unittest.TestCase):
    def setUp(self):
        docutils.register_directive('blockdiag',
                                    directives.BlockdiagDirectiveBase)
        self._tmpdir = TemporaryDirectory()

    def tearDown(self):
        if 'blockdiag' in docutils._directives:
            del docutils._directives['blockdiag']

        self._tmpdir.clean()

    @capture_stderr
    def test_without_args(self):
        text = ".. blockdiag::"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    def test_block(self):
        text = (".. blockdiag::\n"
                "\n"
                "   { A -> B }")
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(blockdiag_node, type(doctree[0]))
        self.assertEqual('{ A -> B }', doctree[0]['code'])
        self.assertEqual(None, doctree[0]['alt'])
        self.assertEqual({}, doctree[0]['options'])

    @capture_stderr
    def test_emptyblock(self):
        text = ".. blockdiag::\n\n   \n"
        text = (".. blockdiag::\n"
                "\n"
                "   ")
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    def test_filename(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../diagrams/node_attribute.diag')
        text = ".. blockdiag:: %s" % filename
        doctree = publish_doctree(text)

        self.assertEqual(1, len(doctree))
        self.assertEqual(blockdiag_node, type(doctree[0]))
        self.assertEqual(io.open(filename, encoding='utf-8-sig').read(),
                         doctree[0]['code'])
        self.assertEqual(None, doctree[0]['alt'])
        self.assertEqual({}, doctree[0]['options'])

    @capture_stderr
    def test_filename_not_exists(self):
        text = ".. blockdiag:: unknown.diag"
        doctree = publish_doctree(text)
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @capture_stderr
    def test_both_block_and_filename(self):
        text = (".. blockdiag:: unknown.diag\n"
                "\n"
                "   A -> B")
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    def test_full_options(self):
        text = (".. blockdiag::\n"
                "   :alt: hello world\n"
                "   :align: center\n"
                "   :desctable:\n"
                "   :width: 200\n"
                "   :height: 100\n"
                "   :scale: 50%\n"
                "   :name: foo\n"
                "   :class: bar\n"
                "   :figwidth: 400\n"
                "   :figclass: baz\n"
                "\n"
                "   A -> B")
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(blockdiag_node, type(doctree[0]))
        self.assertEqual('A -> B', doctree[0]['code'])
        self.assertEqual('hello world', doctree[0]['alt'])
        self.assertEqual('center', doctree[0]['options']['align'])
        self.assertEqual(None, doctree[0]['options']['desctable'])
        self.assertEqual('200', doctree[0]['options']['width'])
        self.assertEqual('100', doctree[0]['options']['height'])
        self.assertEqual(50, doctree[0]['options']['scale'])
        self.assertEqual('hello world', doctree[0]['options']['alt'])
        self.assertEqual('foo', doctree[0]['options']['name'])
        self.assertEqual(['bar'], doctree[0]['options']['classes'])
        self.assertEqual('400px', doctree[0]['options']['figwidth'])
        self.assertEqual(['baz'], doctree[0]['options']['figclass'])

    @capture_stderr
    def test_maxwidth_option(self):
        text = (".. blockdiag::\n"
                "   :maxwidth: 200\n"
                "\n"
                "   A -> B")
        doctree = publish_doctree(text)
        self.assertEqual(2, len(doctree))
        self.assertEqual(blockdiag_node, type(doctree[0]))
        self.assertEqual('A -> B', doctree[0]['code'])
        self.assertEqual('200', doctree[0]['options']['width'])
        self.assertEqual(nodes.system_message, type(doctree[1]))
