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
from optparse import OptionParser
from blockdiag.utils.config import ConfigParser
from blockdiag.utils.fontmap import parse_fontpath, FontMap


class Application(object):
    module = None

    def run(self):
        try:
            self.parse_options()
            self.create_fontmap()

            parsed = self.parse_diagram()
            return self.build_diagram(parsed)
        except SystemExit, e:
            return e
        except UnicodeEncodeError, e:
            msg = "ERROR: UnicodeEncodeError caught " + \
                  "(check your font settings)\n"
            sys.stderr.write(msg)
            return -1
        except Exception, e:
            sys.stderr.write("ERROR: %s\n" % e)
            return -1

    def parse_options(self):
        self.options = Options(self.module).parse()

    def create_fontmap(self):
        self.fontmap = create_fontmap(self.options)

    def parse_diagram(self):
        if self.options.input == '-':
            import codecs
            stream = codecs.getreader('utf-8')(sys.stdin)
            tree = self.module.parser.parse_string(stream.read())
        else:
            tree = self.module.parser.parse_file(self.options.input)

        return tree

    def build_diagram(self, tree):
        DiagramDraw = self.module.drawer.DiagramDraw

        diagram = self.module.builder.ScreenNodeBuilder.build(tree)

        drawer = DiagramDraw(self.options.type, diagram,
                             self.options.output, fontmap=self.fontmap,
                             antialias=self.options.antialias,
                             nodoctype=self.options.nodoctype,
                             transparency=self.options.transparency)
        drawer.draw()
        drawer.save()

        return 0


class Options(object):
    def __init__(self, module):
        self.module = module
        self.build_parser()

    def parse(self):
        self.options, self.args = self.parser.parse_args()
        self.validate()
        self.read_configfile()

        return self.options

    def build_parser(self):
        version = "%%prog %s" % self.module.__version__
        usage = "usage: %prog [options] infile"
        self.parser = p = OptionParser(usage=usage, version=version)
        p.add_option('-a', '--antialias', action='store_true',
                     help='Pass diagram image to anti-alias filter')
        p.add_option('-c', '--config',
                     help='read configurations from FILE', metavar='FILE')
        p.add_option('-o', dest='output',
                     help='write diagram to FILE', metavar='FILE')
        p.add_option('-f', '--font', default=[], action='append',
                     help='use FONT to draw diagram', metavar='FONT')
        p.add_option('--fontmap',
                     help='use FONTMAP file to draw diagram', metavar='FONT')
        p.add_option('--no-transparency', dest='transparency',
                     default=True, action='store_false',
                     help='do not make transparent background of diagram ' +\
                          '(PNG only)')
        p.add_option('-T', dest='type', default='PNG',
                     help='Output diagram as TYPE format')
        p.add_option('--nodoctype', action='store_true',
                     help='Do not output doctype definition tags (SVG only)')

        return p

    def validate(self):
        if len(self.args) == 0:
            self.parser.print_help()
            sys.exit(0)

        self.options.input = self.args.pop(0)
        if self.options.output:
            pass
        elif self.options.output == '-':
            self.options.output = 'output.' + self.options.type.lower()
        else:
            ext = '.%s' % self.options.type.lower()
            self.options.output = re.sub('\..*?$', ext, self.options.input)

        self.options.type = self.options.type.upper()
        if not self.options.type in ('SVG', 'PNG', 'PDF'):
            msg = "unknown format: %s" % self.options.type
            raise RuntimeError(msg)

        if self.options.type == 'PDF':
            try:
                import reportlab.pdfgen.canvas
            except ImportError:
                msg = "could not output PDF format; Install reportlab."
                raise RuntimeError(msg)

        if self.options.nodoctype and self.options.type != 'SVG':
            msg = "--nodoctype option work in SVG images."
            raise RuntimeError(msg)

        if self.options.transparency is False and self.options.type != 'PNG':
            msg = "--no-transparency option work in PNG images."
            raise RuntimeError(msg)

        if self.options.config and not os.path.isfile(self.options.config):
            msg = "config file is not found: %s" % self.options.config
            raise RuntimeError(msg)

        if self.options.fontmap and not os.path.isfile(self.options.fontmap):
            msg = "fontmap file is not found: %s" % self.options.fontmap
            raise RuntimeError(msg)

    def read_configfile(self):
        if self.options.config:
            configpath = self.options.config
        elif os.environ.get('HOME'):
            configpath = '%s/.blockdiagrc' % os.environ.get('HOME')
        elif os.environ.get('USERPROFILE'):
            configpath = '%s/.blockdiagrc' % os.environ.get('USERPROFILE')
        else:
            configpath = ''

        appname = self.module.__name__
        if os.path.isfile(configpath):
            config = ConfigParser()
            config.read(configpath)

            if config.has_option(appname, 'fontpath'):
                fontpath = config.get(appname, 'fontpath')
                self.options.font.append(fontpath)

            if config.has_option(appname, 'fontmap'):
                if self.options.fontmap is None:
                    self.options.fontmap = config.get(appname, 'fontmap')

            if self.options.fontmap is None:
                self.options.fontmap = configpath


def detectfont(options):
    fonts = ['c:/windows/fonts/VL-Gothic-Regular.ttf',  # for Windows
             'c:/windows/fonts/msgothic.ttf',  # for Windows
             'c:/windows/fonts/msgoth04.ttc',  # for Windows
             '/usr/share/fonts/truetype/ipafont/ipagp.ttf',  # for Debian
             '/usr/local/share/font-ipa/ipagp.otf',  # for FreeBSD
             '/Library/Fonts/Hiragino Sans GB W3.otf',  # for MacOS
             '/System/Library/Fonts/AppleGothic.ttf']  # for MacOS

    fontpath = None
    if options.font:
        for path in options.font:
            _path, index = parse_fontpath(path)
            if os.path.isfile(_path):
                fontpath = path
                break
        else:
            msg = 'fontfile is not found: %s' % options.font
            raise RuntimeError(msg)

    if fontpath is None:
        for path in fonts:
            _path, index = parse_fontpath(path)
            if os.path.isfile(_path):
                fontpath = path
                break

    return fontpath


def create_fontmap(options):
    fontmap = FontMap(options.fontmap)
    if fontmap.find().path is None or options.font:
        fontpath = detectfont(options)
        fontmap.set_default_font(fontpath)

    return fontmap
