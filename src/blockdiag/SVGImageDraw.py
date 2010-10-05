#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from utils.XY import XY
from SVGdraw import *
from ImageDrawEx import TextFolder


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
        x = box[0]
        y = box[1]
        width = box[2] - box[0]
        height = box[3] - box[1]

        r = rect(x, y, width, height, fill=self.rgb(fill),
                 stroke=self.rgb(outline), stroke_width=thick)
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

        p1 = xy[0]
        for p2 in xy[1:]:
            l = line(p1.x, p1.y, p2.x, p2.y, stroke=self.rgb(fill))
            self.svg.addElement(l)

            p1 = p2

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
