#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import base64
from utils.XY import XY
from SVGdraw import *

try:
    from utils.PILTextFolder import PILTextFolder as TextFolder
except ImportError:
    from utils.TextFolder import TextFolder


class filter(SVGelement):
    def __init__(self, inkspace_collect=None, **args):
        SVGelement.__init__(self, 'filter', **args)
        if inkspace_collect != None:
            self.attributes['inkspace:collect'] = inkspace_collect


class feGaussianBlur(SVGelement):
    def __init__(self, inkspace_collect=None, **args):
        SVGelement.__init__(self, 'feGaussianBlur', **args)
        if inkspace_collect != None:
            self.attributes['inkspace:collect'] = inkspace_collect


class SVGImageDrawElement:
    def __init__(self, svg):
        self.svg = svg

    def rgb(self, color):
        if isinstance(color, tuple):
            color = 'rgb(%d,%d,%d)' % color

        return color

    def rectangle(self, box, **kwargs):
        thick = kwargs.get('width', 1)
        fill = kwargs.get('fill', 'none')
        outline = kwargs.get('outline')
        style = kwargs.get('style')
        filter = kwargs.get('filter')

        if style == 'dotted':
            length = 2
        elif style == 'dashed':
            length = 4
        else:
            length = None

        if filter == 'blur':
            filter = "filter:url(#filter_blur)"
        elif filter == 'transp-blur':
            filter = "filter:url(#filter_blur);opacity:0.7;fill-opacity:1"
        else:
            filter = None

        x = box[0]
        y = box[1]
        width = box[2] - box[0]
        height = box[3] - box[1]

        r = rect(x, y, width, height, fill=self.rgb(fill),
                 stroke=self.rgb(outline), stroke_width=thick,
                 stroke_dasharray=length, style=filter)
        self.svg.addElement(r)

    def label(self, box, string, **kwargs):
        lines = TextFolder(box, string, adjustBaseline=True, **kwargs)

        self.rectangle(lines.outlineBox(), fill='white', outline='black')
        self.textarea(box, string, **kwargs)

    def text(self, xy, string, **kwargs):
        fill = kwargs.get('fill')
        fontname = kwargs.get('font')
        fontsize = kwargs.get('fontsize')

        t = text(xy[0], xy[1], string, fontsize, fontname, fill=self.rgb(fill))
        self.svg.addElement(t)

    def textarea(self, box, string, **kwargs):
        lines = TextFolder(box, string, adjustBaseline=True, **kwargs)
        for string, xy in lines.each_line():
            self.text(xy, string, **kwargs)

    def line(self, xy, **kwargs):
        fill = kwargs.get('fill')
        style = kwargs.get('style')

        if style == 'dotted':
            length = 2
        elif style == 'dashed':
            length = 4
        else:
            length = None

        pd = pathdata(xy[0].x, xy[0].y)
        for pt in xy[1:]:
            pd.line(pt.x, pt.y)

        p = path(pd, fill="none", stroke=self.rgb(fill),
                 stroke_dasharray=length)
        self.svg.addElement(p)

    def arc(self, xy, start, end, **kwargs):
        fill = kwargs.get('fill')
        style = kwargs.get('style')

        if style == 'dotted':
            length = 2
        elif style == 'dashed':
            length = 4
        else:
            length = None

        w = (xy[2] - xy[0]) / 2
        h = (xy[3] - xy[1]) / 2
        pt1 = XY(xy[0], xy[1] + w)
        pt2 = XY(xy[2], xy[3] - w)

        pd = pathdata(pt1.x, pt1.y)
        pd.ellarc(w, h, 0, 0, 1, pt2.x, pt2.y)
        p = path(pd, fill="none", stroke=self.rgb(fill),
                 stroke_dasharray=length)
        self.svg.addElement(p)

    def ellipse(self, xy, **kwargs):
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')

        w = (xy[2] - xy[0]) / 2
        h = (xy[3] - xy[1]) / 2
        pt = XY(xy[0] + w, xy[1] + h)

        e = ellipse(pt.x, pt.y, w, h, fill=self.rgb(fill),
                    stroke=self.rgb(outline))
        self.svg.addElement(e)

    def polygon(self, xy, **kwargs):
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')

        points = [[p[0], p[1]] for p in xy]
        pg = polygon(points, fill=self.rgb(fill), stroke=self.rgb(outline))
        self.svg.addElement(pg)

    def loadImage(self, filename, box):
        string = open(filename).read()
        url = "data:;base64," + base64.b64encode(string)

        x = box[0]
        y = box[1]
        w = box[2] - box[0]
        h = box[3] - box[1]

        im = image(url, x, y, w, h)
        self.svg.addElement(im)

    def link(self, href):
        a = link(href)
        self.svg.addElement(a)

        return SVGImageDrawElement(a)


class SVGImageDraw(SVGImageDrawElement):
    def __init__(self, size):
        self.drawing = drawing()
        self.svg = svg((0, 0, size[0], size[1]))

        uri = 'http://www.inkscape.org/namespaces/inkscape'
        self.svg.namespaces['inkspace'] = uri
        uri = 'http://www.w3.org/1999/xlink'
        self.svg.namespaces['xlink'] = uri

        # inkspace's Gaussian filter
        fgb = feGaussianBlur(id='feGaussianBlur3780', stdDeviation=4.2,
                             inkspace_collect='always')
        f = filter(id='filter_blur', inkspace_collect='always',
                   x=-0.07875, y=-0.252, width=1.1575, height=1.504)
        f.addElement(fgb)
        d = defs(id='defs_block')
        d.addElement(f)
        self.svg.addElement(d)

        self.svg.addElement(title('blockdiag'))

    def save(self, filename, size, format):
        # Ignore size and format parameter; compatibility for ImageDrawEx.

        self.drawing.setSVG(self.svg)
        return self.drawing.toXml(filename)
