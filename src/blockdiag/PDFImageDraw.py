#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import ImageColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import inch
from utils.XY import XY

try:
    from utils.PILTextFolder import PILTextFolder as TextFolder
except ImportError:
    from utils.TextFolder import TextFolder


class PDFImageDraw:
    def __init__(self, filename, size):
        self.canvas = canvas.Canvas(filename, bottomup=0, pagesize=size)
        #self.canvas.translate(inch, inch)

    def set_style(self, style):
        if style == 'dotted':
            self.canvas.setDash([2, 2])
        elif style == 'dashed':
            self.canvas.setDash([4, 4])
        else:
            self.canvas.setDash()

    def set_stroke_color(self, color="black"):
        if isinstance(color, str) or isinstance(color, unicode):
            rgb = ImageColor.getrgb(color)
            self.canvas.setStrokeColorRGB(*rgb)
        elif color:
            self.canvas.setStrokeColorRGB(*color)
        else:
            self.set_stroke_color()

    def set_fill_color(self, color="white"):
        if isinstance(color, str) or isinstance(color, unicode):
            rgb = ImageColor.getrgb(color)
            self.canvas.setFillColorRGB(*rgb)
        elif color:
            self.canvas.setFillColorRGB(*color)
        else:
            self.set_fill_color()

    def path(self, pd, **kwargs):
        self.set_stroke_color(kwargs.get('outline'))
        self.set_fill_color(kwargs.get('fill', 'none'))
        self.set_style(kwargs.get('style'))

        if kwargs.get('fill') == 'none':
            self.canvas.drawPath(pd, stroke=1, fill=0)
        else:
            self.canvas.drawPath(pd, stroke=1, fill=1)

    def rectangle(self, box, **kwargs):
        self.set_stroke_color(kwargs.get('outline'))
        self.set_fill_color(kwargs.get('fill', 'none'))
        self.set_style(kwargs.get('style'))

        x = box[0]
        y = box[1]
        width = box[2] - box[0]
        height = box[3] - box[1]

        if kwargs.get('fill') == 'none':
            self.canvas.rect(x, y, width, height, fill=0)
        else:
            self.canvas.rect(x, y, width, height, fill=1)

    def label(self, box, string, **kwargs):
        lines = TextFolder(box, string, adjustBaseline=True, **kwargs)

        self.rectangle(lines.outlineBox(), fill='white', outline='black')
        self.textarea(box, string, **kwargs)

    def text(self, xy, string, **kwargs):
        self.set_fill_color(kwargs.get('fill'))
        fontname = kwargs.get('font')
        fontsize = kwargs.get('fontsize')

        fontname = "HeiseiKakuGo-W5"  # or "HeiseiMin-W3"
        pdfmetrics.registerFont(UnicodeCIDFont(fontname))
        self.canvas.setFont(fontname, fontsize)
        self.canvas.drawString(xy[0], xy[1], string)

    def textarea(self, box, string, **kwargs):
        lines = TextFolder(box, string, adjustBaseline=True, **kwargs)
        for string, xy in lines.each_line():
            self.text(xy, string, **kwargs)

    def line(self, xy, **kwargs):
        self.set_stroke_color(kwargs.get('fill', 'none'))
        self.set_style(kwargs.get('style'))

        p1 = xy[0]
        for p2 in xy[1:]:
            self.canvas.line(p1.x, p1.y, p2.x, p2.y)
            p1 = p2

    def arc(self, xy, start, end, **kwargs):
        self.set_stroke_color(kwargs.get('outline'))
        self.set_fill_color(kwargs.get('fill', 'none'))
        self.set_style(kwargs.get('style'))

        w = (xy[2] - xy[0]) / 2
        h = (xy[3] - xy[1]) / 2
        pt1 = XY(xy[0], xy[1] + w)
        pt2 = XY(xy[2], xy[3] - w)

        r = (360 + end - start) % 360
        self.canvas.arc(xy[0], xy[1], xy[2], xy[3], start, r)

    def ellipse(self, xy, **kwargs):
        self.set_stroke_color(kwargs.get('outline'))
        self.set_fill_color(kwargs.get('fill'))
        self.set_style(kwargs.get('style'))

        w = (xy[2] - xy[0]) / 2
        h = (xy[3] - xy[1]) / 2
        pt = XY(xy[0] + w, xy[1] + h)

        if kwargs.get('fill') == 'none':
            self.canvas.ellipse(xy[0], xy[1], xy[2], xy[3], stroke=1, fill=0)
        else:
            self.canvas.ellipse(xy[0], xy[1], xy[2], xy[3], stroke=1, fill=1)

    def polygon(self, xy, **kwargs):
        self.set_stroke_color(kwargs.get('outline'))
        self.set_fill_color(kwargs.get('fill'))
        self.set_style(kwargs.get('style'))

        pd = self.canvas.beginPath()
        pd.moveTo(xy[0][0], xy[0][1])
        for p in xy[1:]:
            pd.lineTo(p[0], p[1])

        if kwargs.get('fill') == 'none':
            self.canvas.drawPath(pd, stroke=1, fill=0)
        else:
            self.canvas.drawPath(pd, stroke=1, fill=1)

    def loadImage(self, filename, box):
        x = box[0]
        y = box[1]
        w = box[2] - box[0]
        h = box[3] - box[1]

        self.canvas.drawImage(filename, x, y, w, h, mask='auto',
                              preserveAspectRatio=True)

    def save(self, filename, size, format):
        # Ignore size and format parameter; compatibility for ImageDrawEx.

        self.canvas.showPage()
        self.canvas.save()
