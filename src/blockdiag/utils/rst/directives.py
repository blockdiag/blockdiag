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
from docutils.statemachine import ViewList
from blockdiag import parser
from blockdiag.command import detectfont
from blockdiag.builder import ScreenNodeBuilder
from blockdiag.drawer import DiagramDraw
from blockdiag.utils.collections import namedtuple


format = 'PNG'
antialias = False
fontpath = None
outputdir = None


def relfn2path(env, filename):
    if filename.startswith('/') or filename.startswith(os.sep):
        relfn = filename[1:]
    else:
        path = env.doc2path(env.docname, base=None)
        relfn = os.path.join(os.path.dirname(path), filename)

    return relfn, os.path.join(env.srcdir, relfn)


def cmp_node_number(a, b):
    try:
        n1 = int(a[0])
    except (TypeError, ValueError):
        n1 = 65535

    try:
        n2 = int(b[0])
    except (TypeError, ValueError):
        n2 = 65535

    return cmp(n1, n2)


class blockdiag(nodes.General, nodes.Element):
    pass


class BlockdiagDirectiveBase(rst.Directive):
    """ Directive to insert arbitrary dot markup. """
    name = "blockdiag"
    node_class = blockdiag

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
                msg = ('%s directive cannot have both content and '
                       'a filename argument' % self.name)
                return [document.reporter.warning(msg, line=self.lineno)]

            try:
                filename = self.source_filename(self.arguments[0])
                fp = codecs.open(filename, 'r', 'utf-8')
                try:
                    dotcode = fp.read()
                finally:
                    fp.close()
            except (IOError, OSError):
                msg = 'External %s file %r not found or reading it failed' % \
                      (self.name, filename)
                return [document.reporter.warning(msg, line=self.lineno)]
        else:
            dotcode = '\n'.join(self.content).strip()
            if not dotcode:
                msg = 'Ignoring "%s" directive without content.' % self.name
                return [self.state_machine.reporter.warning(msg,
                                                            line=self.lineno)]

        node = self.node_class()
        node['code'] = dotcode
        node['alt'] = self.options.get('alt')
        node['options'] = {}
        if 'maxwidth' in self.options:
            node['options']['maxwidth'] = self.options['maxwidth']
        if 'desctable' in self.options:
            node['options']['desctable'] = self.options['desctable']

        return [node]

    def source_filename(self, filename):
        if hasattr(self.state.document.settings, 'env'):
            env = self.state.document.settings.env
            rel_filename, filename = relfn2path(env, self.arguments[0])
            env.note_dependency(rel_filename)

        return filename


class BlockdiagDirective(BlockdiagDirectiveBase):
    def run(self):
        results = super(BlockdiagDirective, self).run()

        node = results[0]
        if not isinstance(node, self.node_class):
            return results

        diagram = self.node2diagram(node)

        if 'desctable' in node['options']:
            del node['options']['desctable']
            results.append(self.description_table(diagram))

        results[0] = self.node2image(node, diagram)

        return results

    def node2diagram(self, node):
        tree = parser.parse_string(node['code'])
        return ScreenNodeBuilder.build(tree)

    def node2image(self, node, diagram):
        filename = self.image_filename(node)
        fontpath = self.detectfont()
        drawer = DiagramDraw(format, diagram, filename,
                             font=fontpath, antialias=antialias)

        if not os.path.isfile(filename):
            drawer.draw()
            drawer.save()

        size = drawer.pagesize()
        options = node['options']
        if 'maxwidth' in options and options['maxwidth'] < size[0]:
            ratio = float(options['maxwidth']) / size[0]
            thumb_size = (options['maxwidth'], size[1] * ratio)

            thumb_filename = self.image_filename(node, prefix='_thumb')
            if not os.path.isfile(thumb_filename):
                drawer.filename = thumb_filename
                drawer.draw()
                drawer.save(thumb_size)

            image = nodes.image(uri=thumb_filename, target=filename)
        else:
            image = nodes.image(uri=filename)

        if node['alt']:
            image['alt'] = node['alt']

        return image

    def detectfont(self):
        Options = namedtuple('Options', 'font')
        if isinstance(fontpath, (list, tuple)):
            options = Options(fontpath)
        elif isinstance(fontpath, (str, unicode)):
            options = Options([fontpath])
        else:
            options = Options([])

        return detectfont(options)

    def image_filename(self, node, prefix='', ext='png'):
        try:
            from hashlib import sha1 as sha
        except ImportError:
            from sha import sha

        options = dict(node['options'])
        options.update(font=fontpath, antialias=antialias)
        hashseed = node['code'].encode('utf-8') + str(options)
        hashed = sha(hashseed).hexdigest()

        filename = "%s%s-%s.%s" % (self.name, prefix, hashed, format.lower())
        if outputdir:
            filename = os.path.join(outputdir, filename)

        return filename

    def description_table(self, diagram):
        nodes = diagram.traverse_nodes
        klass = diagram._DiagramNode

        widths = [25] + [50] * (len(klass.desctable) - 1)
        headers = [klass.attrname[n] for n in klass.desctable]

        descriptions = [n.to_desctable() for n in nodes()  if n.drawable]
        descriptions.sort(cmp_node_number)

        for i in range(len(headers) - 2, -1, -1):
            if [desc[i] for desc in descriptions  if desc[i]]:
                pass
            else:
                widths.pop(i)
                headers.pop(i)
                for desc in descriptions:
                    desc.pop(i)

        return self._description_table(descriptions, widths, headers)

    def _description_table(self, descriptions, widths, headers):
        # generate table-root
        tgroup = nodes.tgroup(cols=len(widths))
        for width in widths:
            tgroup += nodes.colspec(colwidth=width)
        table = nodes.table()
        table += tgroup

        # generate table-header
        thead = nodes.thead()
        row = nodes.row()
        for header in headers:
            entry = nodes.entry()
            entry += nodes.paragraph(text=header)
            row += entry
        thead += row
        tgroup += thead

        # generate table-body
        tbody = nodes.tbody()
        for desc in descriptions:
            row = nodes.row()
            for attr in desc:
                entry = nodes.entry()
                self.state.nested_parse(ViewList([attr], source=attr),
                                        0, entry)
                row += entry
            tbody += row
        tgroup += tbody

        return table


def setup(**kwargs):
    global format, antialias, fontpath, outputdir
    format = kwargs.get('format', 'PNG')
    antialias = kwargs.get('antialias', False)
    fontpath = kwargs.get('fontpath', None)
    outputdir = kwargs.get('outputdir', None)

    rst.directives.register_directive("blockdiag", BlockdiagDirective)
