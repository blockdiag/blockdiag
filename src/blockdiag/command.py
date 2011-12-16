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

import re
import sys
import blockdiag
import blockdiag.parser
import DiagramDraw
from builder import ScreenNodeBuilder
from blockdiag.utils import bootstrap

# for compatibility
from blockdiag.utils.bootstrap import create_fontmap, detectfont


def parse_option(appname, version):
    p = bootstrap.build_option_parser(appname, version)
    p.add_option('-s', '--separate', action='store_true',
                 help='Separate diagram images for each group (SVG only)')

    return bootstrap.parse_option(appname, version, p)


def main():
    try:
        options, args = parse_option(appname='blockdiag',
                                     version=blockdiag.__version__)

        if options.input == '-':
            import codecs
            stream = codecs.getreader('utf-8')(sys.stdin)
            tree = blockdiag.parser.parse_string(stream.read())
        else:
            tree = blockdiag.parser.parse_file(options.input)

        fontmap = create_fontmap(options)
        if options.separate:
            from builder import SeparateDiagramBuilder

            basename = re.sub('.svg$', '', options.output)
            for i, group in enumerate(SeparateDiagramBuilder.build(tree)):
                outfile = '%s_%d.svg' % (basename, i + 1)
                draw = DiagramDraw.DiagramDraw(options.type, group, outfile,
                                               fontmap=fontmap,
                                               antialias=options.antialias,
                                               nodoctype=options.nodoctype)
                draw.draw()
                draw.save()
        else:
            diagram = ScreenNodeBuilder.build(tree)

            draw = DiagramDraw.DiagramDraw(options.type, diagram,
                                           options.output, fontmap=fontmap,
                                           antialias=options.antialias,
                                           nodoctype=options.nodoctype)
            draw.draw()
            draw.save()
    except UnicodeEncodeError, e:
        msg = "ERROR: UnicodeEncodeError caught (check your font settings)\n"
        sys.stderr.write(msg)
        return -1
    except Exception, e:
        sys.stderr.write("ERROR: %s\n" % e)
        return -1
