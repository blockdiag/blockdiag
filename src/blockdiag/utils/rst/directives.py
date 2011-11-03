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
import codecs
from docutils import nodes
from docutils.parsers import rst
from blockdiag import diagparser
from blockdiag.command import detectfont
from blockdiag.builder import ScreenNodeBuilder
from blockdiag.DiagramDraw import DiagramDraw
from blockdiag.utils.collections import namedtuple


format = 'PNG'
antialias = False
fontpath = None


def relfn2path(env, filename):
    if filename.startswith('/') or filename.startswith(os.sep):
        relfn = filename[1:]
    else:
        path = env.doct2path(env.docname, base=None)
        relfn = os.path.join(os.path.dirname(path), filename)

    return relfn, os.path.join(env.srtdir, relfn)


def cmp_node_number(a, b):
    try:
        n1 = int(a[0])
    except TypeError:
        n1 = 65535

    try:
        n2 = int(a[0])
    except TypeError:
        n2 = 65535

    return cmp(n1, n2)


class blockdiag(nodes.General, nodes.Element):
    pass


class BlockdiagDirectiveBase(rst.Directive):
    """ Directive to insert arbitrary dot markup. """
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'alt': rst.directives.unchanged,
        'desctable': rst.directives.flag,
        'maxwidth': rst.directives.nonnegative_int,
    }

    def run(self):
        if self.arguments:
            document = self.state.document
            if self.content:
                return [document.reporter.warning(
                    'blockdiag directive cannot have both content and '
                    'a filename argument', line=self.lineno)]

            env = self.state.document.settings.env
            rel_filename, filename = relfn2path(env, self.arguments[0])
            env.note_dependency(rel_filename)
            try:
                fp = codecs.open(filename, 'r', 'utf-8')
                try:
                    dotcode = fp.read()
                finally:
                    fp.close()
            except (IOError, OSError):
                return [document.reporter.warning(
                    'External blockdiag file %r not found or reading '
                    'it failed' % filename, line=self.lineno)]
        else:
            dotcode = '\n'.join(self.content)
            if not dotcode.strip():
                return [self.state_machine.reporter.warning(
                    'Ignoring "blockdiag" directive without content.',
                    line=self.lineno)]

        node = blockdiag()
        node['code'] = dotcode
        node['alt'] = self.options['alt']
        node['options'] = {}
        if 'maxwidth' in self.options:
            node['options']['maxwidth'] = self.options['maxwidth']
        if 'desctable' in self.options:
            node['options']['desctable'] = self.options['desctable']

        return [node]


class BlockdiagDirective(BlockdiagDirectiveBase):
    def run(self):
        results = super(BlockdiagDirective, self).run()

        node = results[0]
        tree = diagparser.parse_string(node['code'])
        diagram = ScreenNodeBuilder.build(tree)

        if 'desctable' in node['options']:
            del node['options']['desctable']
            results.append(self.description_table(diagram))

        filename = self._filename(node)
        if not os.path.isfile(filename):
            # FIXME: maxwidth parameter is ignored
            fontpath = self.detectfont()
            drawer = DiagramDraw(format, diagram, filename,
                                 font=fontpath, antialias=antialias)
            drawer.draw()
            drawer.save()

        if 'alt' in node:
            results[0] = nodes.image(uri=filename, alt=node['alt'])
        else:
            results[0] = nodes.image(uri=filename)

        return results

    def detectfont(self):
        Options = namedtuple('Options', 'font')
        if isinstance(fontpath, (list, tuple)):
            options = Options(fontpath)
        elif isinstance(fontpath, (str, unicode)):
            options = Options([fontpath])
        else:
            options = Options([])

        return detectfont(options)

    def _filename(self, node, ext='png'):
        try:
            from hashlib import sha1 as sha
        except ImportError:
            from sha import sha

        options = dict(node['options'])
        options.update(font=fontpath, antialias=antialias)
        hashed = node['code'].encode('utf-8') + str(options)
        return "blockdiag-%s.%s" % (sha(hashed).hexdigest(), format.lower())

    def description_table(self, diagram):
        descriptions = []
        for n in diagram.traverse_nodes():
            if hasattr(n, 'description') and n.description:
                label = n.label or n.id
                descriptions.append((n.numbered, label, n.description))
        descriptions.sort(cmp_node_number)

        if any(desc[0] for desc in descriptions):
            widths = [20, 40, 40]
            labels = ['No', 'Name', 'Description']
        else:
            widths = [50, 50]
            descriptions = [desc[1:] for desc in descriptions]
            labels = ['Name', 'Description']

        return self._description_table(descriptions, widths, labels)

    def _description_table(self, descriptions, widths, labels):
        # generate table-root
        tgroup = nodes.tgroup(cols=len(widths))
        for width in widths:
            tgroup += nodes.colspec(colwidth=width)
        table = nodes.table()
        table += tgroup

        # generate table-header
        thead = nodes.thead()
        row = nodes.row()
        for label in labels:
            entry = nodes.entry()
            entry += nodes.paragraph(text=label)
            row += entry
        thead += row
        tgroup += thead

        # generate table-body
        tbody = nodes.tbody()
        for desc in descriptions:
            row = nodes.row()
            for attr in desc:
                entry = nodes.entry()
                entry += nodes.paragraph(text=attr)
                row += entry
            tbody += row
        tgroup += tbody

        return table


def setup(**kwargs):
    global format, antialias, fontpath
    format = kwargs.get('format', 'PNG')
    antialias = kwargs.get('antialias', False)
    fontpath = kwargs.get('fontpath', None)

    rst.directives.register_directive("blockdiag", BlockdiagDirective)
