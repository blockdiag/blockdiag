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
import base64
from blockdiag.utils import urlutil, Box, XY
from simplesvg import *

try:
    from blockdiag.utils.PILTextFolder import PILTextFolder as TextFolder
except ImportError:
    from blockdiag.utils.TextFolder import TextFolder

feGaussianBlur = svgclass('feGaussianBlur')


class SVGImageDrawElement(object):
    self_generative_methods = ['group', 'anchor']

    def __init__(self, svg, parent=None):
        self.svg = svg

    def rgb(self, color):
        if isinstance(color, tuple):
            color = 'rgb(%d,%d,%d)' % color

        return color

    def filter(self, name):
        if name == 'blur':
            filter = "filter:url(#filter_blur)"
        elif name == 'transp-blur':
            filter = "filter:url(#filter_blur);opacity:0.7;fill-opacity:1"
        else:
            filter = None

        return filter

    def style(self, name, thick):
        if thick is None:
            thick = 1

        if name == 'dotted':
            length = 2 * thick
        elif name == 'dashed':
            length = 4 * thick
        elif name == 'none':
            length = "%d %d" % (0, 65535 * thick)
        elif re.search('^\d+(,\d+)*$', name or ""):
            l = [int(n) * thick for n in name.split(",")]
            length = " ".join(str(n) for n in l)
        else:
            length = None

        return length

    def path(self, pd, **kwargs):
        thick = kwargs.get('thick')
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')
        style = kwargs.get('style')
        filter = kwargs.get('filter')

        p = path(pd, fill=self.rgb(fill), stroke=self.rgb(outline),
                 stroke_dasharray=self.style(style, thick),
                 style=self.filter(filter))
        self.svg.addElement(p)

    def rectangle(self, box, **kwargs):
        thick = kwargs.get('thick')
        fill = kwargs.get('fill', 'none')
        outline = kwargs.get('outline')
        style = kwargs.get('style')
        filter = kwargs.get('filter')

        x = box[0]
        y = box[1]
        width = box[2] - box[0]
        height = box[3] - box[1]

        r = rect(x, y, width, height, fill=self.rgb(fill),
                 stroke=self.rgb(outline), stroke_width=thick,
                 stroke_dasharray=self.style(style, thick),
                 style=self.filter(filter))
        self.svg.addElement(r)

    def text(self, xy, string, font, **kwargs):
        fill = kwargs.get('fill')

        t = text(xy[0], xy[1], string, fill=self.rgb(fill),
                 font_family=font.generic_family, font_size=font.size,
                 font_weight=font.weight, font_style=font.style)
        self.svg.addElement(t)

    def textarea(self, box, string, font, **kwargs):
        if 'rotate' in kwargs and kwargs['rotate'] != 0:
            angle = int(kwargs['rotate']) % 360
            del kwargs['rotate']

            if angle in (90, 270):
                _box = Box(box[0], box[1],
                           box[0] + box.height, box[1] + box.width)
                if angle == 90:
                    _box = _box.shift(x=box.width)
                elif angle == 270:
                    _box = _box.shift(y=box.height)
            elif angle == 180:
                _box = Box(box[2], box[3],
                           box[2] + box.width, box[3] + box.height)
            else:
                _box = Box(box[0], box[1],
                           box[0] + box.width, box[1] + box.height)

            rotate = "rotate(%d,%d,%d)" % (angle, _box[0], _box[1])
            group = g(transform="%s" % rotate)
            self.svg.addElement(group)

            elem = SVGImageDrawElement(group, self)
            elem.textarea(_box, string, font, **kwargs)
            return

        lines = TextFolder(box, string, font, adjustBaseline=True, **kwargs)

        if kwargs.get('outline'):
            outline = kwargs.get('outline')
            self.rectangle(lines.outlinebox, fill='white', outline=outline)

        rendered = False
        for string, xy in lines.lines:
            self.text(xy, string, font, **kwargs)
            rendered = True

        if not rendered and font.size > 0:
            font.size = int(font.size * 0.8)
            self.textarea(box, string, font, **kwargs)

    def line(self, xy, **kwargs):
        fill = kwargs.get('fill')
        style = kwargs.get('style')
        thick = kwargs.get('thick')

        pd = pathdata(xy[0].x, xy[0].y)
        for pt in xy[1:]:
            pd.line(pt.x, pt.y)

        p = path(pd, fill="none", stroke=self.rgb(fill),
                 stroke_width=thick, stroke_dasharray=self.style(style, thick))
        self.svg.addElement(p)

    def arc(self, xy, start, end, **kwargs):
        thick = kwargs.get('thick')
        fill = kwargs.get('fill')
        style = kwargs.get('style')

        w = (xy[2] - xy[0]) / 2
        h = (xy[3] - xy[1]) / 2

        if start > end:
            end += 360

        from blockdiag.utils import ellipse

        coord = ellipse.coordinate(1, w, h, start, start + 1)
        point = iter(coord).next()
        pt1 = XY(xy[0] + w + round(point[0], 0),
                 xy[1] + h + round(point[1], 0))

        coord = ellipse.coordinate(1, w, h, end, end + 1)
        point = iter(coord).next()
        pt2 = XY(xy[0] + w + round(point[0], 0),
                 xy[1] + h + round(point[1], 0))

        if end - start > 180:
            largearc = 1
        else:
            largearc = 0

        pd = pathdata(pt1[0], pt1[1])
        pd.ellarc(w, h, 0, largearc, 1, pt2[0], pt2[1])
        p = path(pd, fill="none", stroke=self.rgb(fill),
                 stroke_dasharray=self.style(style, thick))
        self.svg.addElement(p)

    def ellipse(self, xy, **kwargs):
        thick = kwargs.get('thick')
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')
        style = kwargs.get('style')
        filter = kwargs.get('filter')

        w = (xy[2] - xy[0]) / 2
        h = (xy[3] - xy[1]) / 2
        pt = XY(xy[0] + w, xy[1] + h)

        e = ellipse(pt.x, pt.y, w, h, fill=self.rgb(fill),
                    stroke=self.rgb(outline),
                    stroke_dasharray=self.style(style, thick),
                    style=self.filter(filter))
        self.svg.addElement(e)

    def polygon(self, xy, **kwargs):
        thick = kwargs.get('thick')
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')
        style = kwargs.get('style')
        filter = kwargs.get('filter')

        pg = polygon(xy, fill=self.rgb(fill), stroke=self.rgb(outline),
                     stroke_dasharray=self.style(style, thick),
                     style=self.filter(filter))
        self.svg.addElement(pg)

    def loadImage(self, filename, box):
        if urlutil.isurl(filename):
            url = filename
        else:
            string = open(filename).read()
            url = "data:;base64," + base64.b64encode(string)

        x = box[0]
        y = box[1]
        w = box[2] - box[0]
        h = box[3] - box[1]

        im = image(url, x, y, w, h)
        self.svg.addElement(im)

    def anchor(self, url):
        a_node = a(url)
        a_node.add_attribute('xlink:href', url)
        self.svg.addElement(a_node)

        return SVGImageDrawElement(a_node)

    def group(self):
        group = g()
        self.svg.addElement(group)

        return SVGImageDrawElement(group)


class SVGImageDraw(SVGImageDrawElement):
    def __init__(self, filename, size, **kwargs):
        self.filename = filename
        super(SVGImageDraw, self).__init__(svg(0, 0, size[0], size[1]))
        self.svg.use_doctype = not kwargs.get('nodoctype')

        uri = 'http://www.inkscape.org/namespaces/inkscape'
        self.svg.add_attribute('xmlns:inkspace', uri)
        uri = 'http://www.w3.org/1999/xlink'
        self.svg.add_attribute('xmlns:xlink', uri)

        # inkspace's Gaussian filter
        fgb = feGaussianBlur(id='feGaussianBlur3780', stdDeviation=4.2)
        fgb.add_attribute('inkspace:collect', 'always')
        f = filter(-0.07875, -0.252, 1.1575, 1.504, id='filter_blur')
        f.add_attribute('inkspace:collect', 'always')
        f.addElement(fgb)
        d = defs(id='defs_block')
        d.addElement(f)
        self.svg.addElement(d)

        self.svg.addElement(title('blockdiag'))

    def save(self, filename, size, format):
        # Ignore format parameter; compatibility for ImageDrawEx.

        if filename:
            self.filename = filename

        if size:
            self.svg.attributes['width'] = size[0]
            self.svg.attributes['height'] = size[1]

        svg = self.svg.to_xml()

        if self.filename:
            open(self.filename, 'w').write(svg)

        return svg
