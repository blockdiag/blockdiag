#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from utils.XY import XY
from SVGdraw import *
from utils.TextFolder import TextFolder


class SVGImageDraw:
    def __init__(self):
        self.drawing = drawing()
        self.svg = None

    def resetCanvas(self, size):
        self.svg = svg((0, 0, size[0], size[1]))
        self.svg.addElement(title('blockdiag'))

    def rgb(self, color):
        if isinstance(color, tuple):
            color = 'rgb(%d,%d,%d)' % color

        return color

    def save(self, filename):
        self.drawing.setSVG(self.svg)
        self.drawing.toXml(filename)

    def rectangle(self, box, **kwargs):
        thick = kwargs.get('width', 1)
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')
        style = kwargs.get('style')

        if style == 'dotted':
            len = 2
        elif style == 'dashed':
            len = 4
        else:
            len = None

        x = box[0]
        y = box[1]
        width = box[2] - box[0]
        height = box[3] - box[1]

        r = rect(x, y, width, height, fill=self.rgb(fill),
                 stroke=self.rgb(outline), stroke_width=thick,
                 stroke_dasharray=len)
        self.svg.addElement(r)

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
            len = 2
        elif style == 'dashed':
            len = 4
        else:
            len = None

        pd = pathdata(xy[0].x, xy[0].y)
        for pt in xy[1:]:
            pd.line(pt.x, pt.y)

        p = path(pd, fill="none", stroke=self.rgb(fill), stroke_dasharray=len)
        self.svg.addElement(p)

    def arc(self, xy, start, end, **kwargs):
        fill = kwargs.get('fill')

        w = (xy[2] - xy[0]) / 2
        h = (xy[3] - xy[1]) / 2
        pt1 = XY(xy[0], xy[1] + w)
        pt2 = XY(xy[2], xy[3] - w)

        pd = pathdata(pt1.x, pt1.y)
        pd.ellarc(w, h, 0, 0, 1, pt2.x, pt2.y)
        p = path(pd, fill="none", stroke=self.rgb(fill))
        self.svg.addElement(p)

    def polygon(self, xy, **kwargs):
        fill = kwargs.get('fill')
        outline = kwargs.get('outline')

        points = [[p[0], p[1]] for p in xy]
        pg = polygon(points, fill=self.rgb(fill), stroke=self.rgb(outline))
        self.svg.addElement(pg)

    def loadImage(self, filename, box):
        msg = "WARNING: blockdiag does not support " \
              "background image for SVG Image.\n"
        sys.stderr.write(msg)
