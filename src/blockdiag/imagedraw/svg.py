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
from blockdiag.imagedraw import base as _base, textfolder
from blockdiag.imagedraw.simplesvg import *
from blockdiag.imagedraw.utils import cached
from blockdiag.utils import urlutil, Box, XY

feGaussianBlur = svgclass('feGaussianBlur')


def rgb(color):
    if isinstance(color, tuple):
        color = 'rgb(%d,%d,%d)' % color

    return color


def style(name):
    if name == 'blur':
        value = "filter:url(#filter_blur)"
    elif name == 'transp-blur':
        value = "filter:url(#filter_blur);opacity:0.7;fill-opacity:1"
    else:
        value = None

    return value


def dasharray(pattern, thick):
    if thick is None:
        thick = 1

    if pattern == 'dotted':
        value = 2 * thick
    elif pattern == 'dashed':
        value = 4 * thick
    elif pattern == 'none':
        value = "%d %d" % (0, 65535 * thick)
    elif re.search('^\d+(,\d+)*$', pattern or ""):
        l = [int(n) * thick for n in pattern.split(",")]
        value = " ".join(str(n) for n in l)
    else:
        value = None

    return value


def drawing_params(kwargs):
    params = {}

    if 'style' in kwargs:
        params['stroke_dasharray'] = dasharray(kwargs.get('style'),
                                               kwargs.get('thick'))

    if 'filter' in kwargs:
        params['style'] = style(kwargs.get('filter'))

    return params


class SVGImageDrawElement(_base.ImageDraw):
    self_generative_methods = ['group', 'anchor']
    supported_path = True

    def __init__(self, svg, parent=None):
        self.svg = svg
        if parent and parent.ignore_pil:
            self.ignore_pil = True
        else:
            self.ignore_pil = False

    def path(self, pd, **kwargs):
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')

        p = path(pd, fill=rgb(fill), stroke=rgb(outline),
                 **drawing_params(kwargs))
        self.svg.addElement(p)

    def rectangle(self, box, **kwargs):
        thick = kwargs.get('thick')
        fill = kwargs.get('fill', 'none')
        outline = kwargs.get('outline')

        x = box[0]
        y = box[1]
        width = box[2] - box[0]
        height = box[3] - box[1]

        r = rect(x, y, width, height, fill=rgb(fill),
                 stroke=rgb(outline), stroke_width=thick,
                 **drawing_params(kwargs))
        self.svg.addElement(r)

    def textsize(self, string, font, maxwidth=None, **kwargs):
        if maxwidth is None:
            maxwidth = 65535

        box = Box(0, 0, maxwidth, 65535)
        textbox = textfolder.get(self, box, string, font,
                                 adjustBaseline=True, **kwargs)
        return textbox.outlinebox.size

    @cached
    def textlinesize(self, string, font, **kwargs):
        if kwargs.get('ignore_pil', self.ignore_pil):
            from blockdiag.imagedraw.utils import textsize
            return textsize(string, font)
        else:
            if not hasattr(self, '_pil_drawer'):
                from blockdiag.imagedraw import png
                self._pil_drawer = png.ImageDrawEx(None)

            return self._pil_drawer.textlinesize(string, font)

    def text(self, xy, string, font, **kwargs):
        fill = kwargs.get('fill')

        t = text(xy[0], xy[1], string, fill=rgb(fill),
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

        lines = textfolder.get(self, box, string, font,
                               adjustBaseline=True, **kwargs)

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
        thick = kwargs.get('thick')

        pd = pathdata(xy[0].x, xy[0].y)
        for pt in xy[1:]:
            pd.line(pt.x, pt.y)

        p = path(pd, fill="none", stroke=rgb(fill),
                 stroke_width=thick, **drawing_params(kwargs))
        self.svg.addElement(p)

    def arc(self, xy, start, end, **kwargs):
        thick = kwargs.get('thick')
        fill = kwargs.get('fill')

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
        p = path(pd, fill="none", stroke=rgb(fill),
                 **drawing_params(kwargs))
        self.svg.addElement(p)

    def ellipse(self, xy, **kwargs):
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')

        w = (xy[2] - xy[0]) / 2
        h = (xy[3] - xy[1]) / 2
        pt = XY(xy[0] + w, xy[1] + h)

        e = ellipse(pt.x, pt.y, w, h, fill=rgb(fill),
                    stroke=rgb(outline),
                    **drawing_params(kwargs))
        self.svg.addElement(e)

    def polygon(self, xy, **kwargs):
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')

        pg = polygon(xy, fill=rgb(fill), stroke=rgb(outline),
                     **drawing_params(kwargs))
        self.svg.addElement(pg)

    def image(self, box, url):
        if not urlutil.isurl(url):
            string = open(url, 'rb').read()
            url = "data:;base64," + base64.b64encode(string)

        im = image(url, box.x1, box.y1, box.width, box.height)
        self.svg.addElement(im)

    def anchor(self, url):
        a_node = a(url)
        a_node.add_attribute('xlink:href', url)
        self.svg.addElement(a_node)

        return SVGImageDrawElement(a_node, self)

    def group(self):
        group = g()
        self.svg.addElement(group)

        return SVGImageDrawElement(group, self)


class SVGImageDraw(SVGImageDrawElement):
    def __init__(self, filename, **kwargs):
        super(SVGImageDraw, self).__init__(None)

        self.filename = filename
        self.options = kwargs
        self.ignore_pil = kwargs.get('ignore_pil')
        self.set_canvas_size((0, 0))

    def set_canvas_size(self, size):
        self.svg = svg(0, 0, size[0], size[1], **self.options)
        uri = 'http://www.inkscape.org/namespaces/inkscape'
        self.svg.add_attribute('xmlns:inkspace', uri)
        uri = 'http://www.w3.org/1999/xlink'
        self.svg.add_attribute('xmlns:xlink', uri)

        # inkspace's Gaussian filter
        if self.options.get('style') != 'blur':
            fgb = feGaussianBlur(id='feGaussianBlur3780', stdDeviation=4.2)
            fgb.add_attribute('inkspace:collect', 'always')
            f = filter(-0.07875, -0.252, 1.1575, 1.504, id='filter_blur')
            f.add_attribute('inkspace:collect', 'always')
            f.addElement(fgb)
            d = defs(id='defs_block')
            d.addElement(f)
            self.svg.addElement(d)

        self.svg.addElement(title('blockdiag'))
        self.svg.addElement(desc(self.options.get('code')))

    def save(self, filename, size, _format):
        # Ignore format parameter; compatibility for ImageDrawEx.

        if filename:
            self.filename = filename

        if size:
            self.svg.attributes['width'] = size[0]
            self.svg.attributes['height'] = size[1]

        image = self.svg.to_xml()

        if self.filename:
            open(self.filename, 'w').write(image)

        return image


def setup(self):
    from blockdiag.imagedraw import install_imagedrawer
    install_imagedrawer('svg', SVGImageDraw)
