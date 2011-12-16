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


def parse_option(appname, version, option_parser=None):
    if option_parser is None:
        option_parser = build_option_parser(appname, version)

    options, args = option_parser.parse_args()

    if len(args) == 0:
        p.print_help()
        sys.exit(0)

    options.input = args.pop(0)
    if options.output:
        pass
    elif options.output == '-':
        options.output = 'output.' + options.type.lower()
    else:
        ext = '.%s' % options.type.lower()
        options.output = re.sub('\..*?$', ext, options.input)

    options.type = options.type.upper()
    if not options.type in ('SVG', 'PNG', 'PDF'):
        msg = "unknown format: %s" % options.type
        raise RuntimeError(msg)

    if options.type == 'PDF':
        try:
            import reportlab.pdfgen.canvas
        except ImportError:
            msg = "could not output PDF format; Install reportlab."
            raise RuntimeError(msg)

    if options.nodoctype and options.type != 'SVG':
        msg = "--nodoctype option work in SVG images."
        raise RuntimeError(msg)

    if options.config and not os.path.isfile(options.config):
        msg = "config file is not found: %s" % options.config
        raise RuntimeError(msg)

    if options.fontmap and not os.path.isfile(options.fontmap):
        msg = "fontmap file is not found: %s" % options.fontmap
        raise RuntimeError(msg)

    parse_config(appname, options)

    return options, args


def build_option_parser(appname, version):
    version = "%%prog %s" % version
    usage = "usage: %prog [options] infile"
    p = OptionParser(usage=usage, version=version)
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
    p.add_option('-T', dest='type', default='PNG',
                 help='Output diagram as TYPE format')
    p.add_option('--nodoctype', action='store_true',
                 help='Do not output doctype definition tags (SVG only)')

    return p


def parse_config(appname, options):
    if options.config:
        configpath = options.config
    elif os.environ.get('HOME'):
        configpath = '%s/.blockdiagrc' % os.environ.get('HOME')
    elif os.environ.get('USERPROFILE'):
        configpath = '%s/.blockdiagrc' % os.environ.get('USERPROFILE')
    else:
        configpath = ''

    if os.path.isfile(configpath):
        config = ConfigParser()
        config.read(configpath)

        if config.has_option(appname, 'fontpath'):
            fontpath = config.get(appname, 'fontpath')
            options.font.append(fontpath)

        if config.has_option(appname, 'fontmap'):
            if options.fontmap is None:
                fontmap = config.get(appname, 'fontmap')

        if options.fontmap is None:
            options.fontmap = configpath


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
