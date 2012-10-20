# -*- coding: utf-8 -*-

import os
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

    def test_setup(self):
        directives.setup()
        options = directives.directive_options

        self.assertIn('blockdiag', docutils._directives)
        self.assertEqual(directives.BlockdiagDirective,
                         docutils._directives['blockdiag'])
        self.assertEqual('PNG', options['format'])
        self.assertEqual(False, options['antialias'])
        self.assertEqual(None, options['fontpath'])
        self.assertEqual(False, options['nodoctype'])
        self.assertEqual(False, options['noviewbox'])
        self.assertEqual(False, options['inline_svg'])
        self.assertEqual(False, options['ignore_pil'])

    def test_setup_with_args(self):
        directives.setup(format='SVG', antialias=True, fontpath='/dev/null',
                         nodoctype=True, noviewbox=True, inline_svg=True,
                         ignore_pil=True)
        options = directives.directive_options

        self.assertIn('blockdiag', docutils._directives)
        self.assertEqual(directives.BlockdiagDirective,
                         docutils._directives['blockdiag'])
        self.assertEqual('SVG', options['format'])
        self.assertEqual(True, options['antialias'])
        self.assertEqual('/dev/null', options['fontpath'])
        self.assertEqual(True, options['nodoctype'])
        self.assertEqual(True, options['noviewbox'])
        self.assertEqual(True, options['inline_svg'])
        self.assertEqual(True, options['ignore_pil'])

    @stderr_wrapper
    @setup_directive_base
    def test_base_noargs(self):
        text = ".. blockdiag::"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @setup_directive_base
    def test_base_with_block(self):
        text = ".. blockdiag::\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(directives.blockdiag, type(doctree[0]))
        self.assertEqual('{ A -> B }', doctree[0]['code'])
        self.assertEqual(None, doctree[0]['alt'])
        self.assertEqual({}, doctree[0]['options'])

    @stderr_wrapper
    @setup_directive_base
    def test_base_with_emptyblock(self):
        text = ".. blockdiag::\n\n   \n"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @setup_directive_base
    def test_base_with_filename(self):
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
    def test_base_with_filename_not_exists(self):
        text = ".. blockdiag:: unknown.diag"
        doctree = publish_doctree(text)
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @stderr_wrapper
    @setup_directive_base
    def test_base_with_block_and_filename(self):
        text = ".. blockdiag:: unknown.diag\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.system_message, type(doctree[0]))

    @setup_directive_base
    def test_base_with_options(self):
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
    def test_block(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertFalse('alt' in doctree[0])
        self.assertEqual(0, doctree[0]['uri'].index(path))
        self.assertFalse('target' in doctree[0])

    @use_tmpdir
    def test_block_alt(self, path):
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
    def test_block_fontpath1(self, path):
        directives.setup(format='SVG', fontpath=['dummy.ttf'],
                         outputdir=path)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        publish_doctree(text)

    @use_tmpdir
    @assertRaises(RuntimeError)
    def test_block_fontpath2(self, path):
        directives.setup(format='SVG', fontpath='dummy.ttf',
                         outputdir=path)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        publish_doctree(text)

    @use_tmpdir
    def test_caption(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :caption: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.figure, type(doctree[0]))
        self.assertEqual(2, len(doctree[0]))
        self.assertEqual(nodes.image, type(doctree[0][0]))
        self.assertEqual(nodes.caption, type(doctree[0][1]))
        self.assertEqual(1, len(doctree[0][1]))
        self.assertEqual(nodes.Text, type(doctree[0][1][0]))
        self.assertEqual('hello world', doctree[0][1][0])

    @use_tmpdir
    def test_block_maxwidth(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :maxwidth: 100\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertFalse('alt' in doctree[0])
        self.assertEqual(0, doctree[0]['uri'].index(path))
        self.assertFalse(0, doctree[0]['target'].index(path))

    @use_tmpdir
    def test_block_nodoctype_false(self, path):
        directives.setup(format='SVG', outputdir=path, nodoctype=False)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        svg = open(doctree[0]['uri']).read()
        self.assertEqual("<?xml version='1.0' encoding='UTF-8'?>\n"
                         "<!DOCTYPE ", svg[:49])

    @use_tmpdir
    def test_block_nodoctype_true(self, path):
        directives.setup(format='SVG', outputdir=path, nodoctype=True)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[-1]))
        svg = open(doctree[0]['uri']).read()
        self.assertNotEqual("<?xml version='1.0' encoding='UTF-8'?>\n"
                            "<!DOCTYPE ", svg[:49])

    @use_tmpdir
    def test_block_noviewbox_false(self, path):
        directives.setup(format='SVG', outputdir=path, noviewbox=False)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        svg = open(doctree[0]['uri']).read()
        self.assertRegexpMatches(svg, '<svg viewBox="0 0 \d+ \d+" ')

    @use_tmpdir
    def test_block_noviewbox_true(self, path):
        directives.setup(format='SVG', outputdir=path, noviewbox=True)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        svg = open(doctree[0]['uri']).read()
        self.assertRegexpMatches(svg, '<svg height="\d+" width="\d+" ')

    @use_tmpdir
    def test_block_inline_svg_false(self, path):
        directives.setup(format='SVG', outputdir=path, inline_svg=False)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertEqual(1, len(os.listdir(path)))

    @use_tmpdir
    def test_block_inline_svg_true(self, path):
        directives.setup(format='SVG', outputdir=path, inline_svg=True)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.raw, type(doctree[0]))
        self.assertEqual('html', doctree[0]['format'])
        self.assertEqual(nodes.Text, type(doctree[0][0]))
        self.assertEqual("<?xml version='1.0' encoding='UTF-8'?>\n"
                         "<!DOCTYPE ", doctree[0][0][:49])
        self.assertEqual(0, len(os.listdir(path)))

    @use_tmpdir
    def test_block_inline_svg_true_but_nonsvg_format(self, path):
        directives.setup(format='PNG', outputdir=path, inline_svg=True)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))

    @use_tmpdir
    def test_block_ignore_pil_false(self, path):
        directives.setup(format='SVG', outputdir=path, ignore_pil=False)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))

    @use_tmpdir
    def test_block_ignore_pil_true(self, path):
        directives.setup(format='SVG', outputdir=path, ignore_pil=True)
        text = ".. blockdiag::\n   :alt: hello world\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))

    @use_tmpdir
    def test_desctable_without_description(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))

    @use_tmpdir
    def test_desctable_without_description(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n   { A -> B }"
        doctree = publish_doctree(text)
        self.assertEqual(1, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))

    @use_tmpdir
    def test_desctable(self, path):
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
    def test_desctable_using_node_group(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n   { A -> B; group { A } }"
        text = ".. blockdiag::\n   :desctable:\n\n" + \
               "   { A [description = foo]; B [description = bar]; " + \
               "     group { A } }"
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
        self.assertEqual(1, len(tbody[0][1]))
        self.assertEqual('foo', tbody[0][1][0][0])

        self.assertEqual(2, len(tbody[1]))
        self.assertEqual(1, len(tbody[1][0]))
        self.assertEqual(1, len(tbody[1][0][0]))
        self.assertEqual('B', tbody[1][0][0][0])
        self.assertEqual(1, len(tbody[1][1]))
        self.assertEqual('bar', tbody[1][1][0][0])

    @use_tmpdir
    def test_desctable_with_rest_markups(self, path):
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
    def test_desctable_with_numbered(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n" + \
               "   { A [numbered = 2]; B [numbered = 1]; }"
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
        self.assertEqual(25, doctree[1][0][0]['colwidth'])
        self.assertEqual(50, doctree[1][0][1]['colwidth'])

        # thead
        thead = doctree[1][0][2]
        self.assertEqual(2, len(thead[0]))
        self.assertEqual('No', thead[0][0][0][0])
        self.assertEqual('Name', thead[0][1][0][0])

        # tbody
        tbody = doctree[1][0][3]
        self.assertEqual(2, len(tbody))
        self.assertEqual('1', tbody[0][0][0][0])
        self.assertEqual('B', tbody[0][1][0][0])
        self.assertEqual('2', tbody[1][0][0][0])
        self.assertEqual('A', tbody[1][1][0][0])

    @use_tmpdir
    def test_desctable_with_numbered_and_description(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n" + \
               "   { A [description = foo, numbered = 2]; " + \
               "     B [description = bar, numbered = 1]; }"
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
        self.assertEqual(1, len(tbody[0][2]))
        self.assertEqual('bar', tbody[0][2][0][0])
        self.assertEqual('2', tbody[1][0][0][0])
        self.assertEqual('A', tbody[1][1][0][0])
        self.assertEqual('foo', tbody[1][2][0][0])

    @use_tmpdir
    def test_desctable_for_edges(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n" + \
               "   { A -> B [description = \"foo\"]; " + \
               "     C -> D [description = \"bar\"]; " + \
               "     C [label = \"label_C\"]; " + \
               "     D [label = \"label_D\"]; }"
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
        self.assertEqual(25, doctree[1][0][0]['colwidth'])
        self.assertEqual(50, doctree[1][0][1]['colwidth'])

        # thead
        thead = doctree[1][0][2]
        self.assertEqual(2, len(thead[0]))
        self.assertEqual('Name', thead[0][0][0][0])
        self.assertEqual('Description', thead[0][1][0][0])

        # tbody
        tbody = doctree[1][0][3]
        self.assertEqual(2, len(tbody))
        self.assertEqual('A -> B', tbody[0][0][0][0])
        self.assertEqual(1, len(tbody[0][1][0]))
        self.assertEqual(nodes.Text, type(tbody[0][1][0][0]))
        self.assertEqual('foo', str(tbody[0][1][0][0]))
        self.assertEqual('label_C -> label_D', tbody[1][0][0][0])
        self.assertEqual(1, len(tbody[1][1][0]))
        self.assertEqual(nodes.Text, type(tbody[1][1][0][0]))
        self.assertEqual('bar', str(tbody[1][1][0][0]))

    @use_tmpdir
    def test_desctable_for_nodes_and_edges(self, path):
        directives.setup(format='SVG', outputdir=path)
        text = ".. blockdiag::\n   :desctable:\n\n" + \
               "   { A -> B [description = \"foo\"]; " + \
               "     C -> D [description = \"bar\"]; " + \
               "     C [label = \"label_C\", description = foo]; " + \
               "     D [label = \"label_D\"]; }"
        doctree = publish_doctree(text)
        self.assertEqual(3, len(doctree))
        self.assertEqual(nodes.image, type(doctree[0]))
        self.assertEqual(nodes.table, type(doctree[1]))
        self.assertEqual(nodes.table, type(doctree[2]))

        # tgroup
        self.assertEqual(4, len(doctree[2][0]))
        self.assertEqual(nodes.colspec, type(doctree[2][0][0]))
        self.assertEqual(nodes.colspec, type(doctree[2][0][1]))
        self.assertEqual(nodes.thead, type(doctree[2][0][2]))
        self.assertEqual(nodes.tbody, type(doctree[2][0][3]))

        # colspec
        self.assertEqual(25, doctree[2][0][0]['colwidth'])
        self.assertEqual(50, doctree[2][0][1]['colwidth'])

        # thead
        thead = doctree[2][0][2]
        self.assertEqual(2, len(thead[0]))
        self.assertEqual('Name', thead[0][0][0][0])
        self.assertEqual('Description', thead[0][1][0][0])

        # tbody
        tbody = doctree[2][0][3]
        self.assertEqual(2, len(tbody))
        self.assertEqual('A -> B', tbody[0][0][0][0])
        self.assertEqual(1, len(tbody[0][1][0]))
        self.assertEqual(nodes.Text, type(tbody[0][1][0][0]))
        self.assertEqual('foo', str(tbody[0][1][0][0]))
        self.assertEqual('label_C -> label_D', tbody[1][0][0][0])
        self.assertEqual(1, len(tbody[1][1][0]))
        self.assertEqual(nodes.Text, type(tbody[1][1][0][0]))
        self.assertEqual('bar', str(tbody[1][1][0][0]))
