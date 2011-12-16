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
import blockdiag
import DiagramDraw
import diagparser
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
    except RuntimeError, e:
        sys.stderr.write("ERROR: %s\n" % e)
        return

    infile = args[0]
    if options.filename:
        outfile = options.filename
    elif infile == '-':
        outfile = 'output.' + options.type.lower()
    else:
        outfile = re.sub('\..*', '', infile) + '.' + options.type.lower()

    try:
        if infile == '-':
            import codecs
            stream = codecs.getreader('utf-8')(sys.stdin)
            tree = diagparser.parse_string(stream.read())
        else:
            tree = diagparser.parse_file(infile)

        fontmap = create_fontmap(options)
        if options.separate:
            from builder import SeparateDiagramBuilder

            for i, group in enumerate(SeparateDiagramBuilder.build(tree)):
                outfile2 = re.sub('.svg$', '', outfile) + ('_%d.svg' % (i + 1))
                draw = DiagramDraw.DiagramDraw(options.type, group, outfile2,
                                               fontmap=fontmap,
                                               antialias=options.antialias,
                                               nodoctype=options.nodoctype)
                draw.draw()
                draw.save()
        else:
            diagram = ScreenNodeBuilder.build(tree)

            draw = DiagramDraw.DiagramDraw(options.type, diagram, outfile,
                                           fontmap=fontmap,
                                           antialias=options.antialias,
                                           nodoctype=options.nodoctype)
            draw.draw()
            draw.save()
    except UnicodeEncodeError, e:
        msg = "ERROR: UnicodeEncodeError caught (check your font settings)\n"
        sys.stderr.write(msg)
    except Exception, e:
        sys.stderr.write("ERROR: %s\n" % e)
