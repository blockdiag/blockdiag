#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from utils.XY import XY
from utils.PDFTextFolder import PDFTextFolder as TextFolder


class PDFImageDraw:
    def __init__(self, filename, size):
        self.canvas = canvas.Canvas(filename, bottomup=0, pagesize=size)
        self.fonts = {}

    def set_font(self, fontpath, fontsize):
        if fontpath not in self.fonts:
            ttfont = TTFont(fontpath, fontpath)
            pdfmetrics.registerFont(ttfont)

            self.fonts[fontpath] = ttfont

        self.canvas.setFont(fontpath, fontsize)

    def set_render_params(self, **kwargs):
        self.set_stroke_color(kwargs.get('outline'))
        self.set_fill_color(kwargs.get('fill', 'none'))
        self.set_style(kwargs.get('style'))

        params = {}
        if kwargs.get('fill', 'none') == 'none':
            params['fill'] = 0
        else:
            params['fill'] = 1

        if kwargs.get('outline') is None:
            params['stroke'] = 0
        else:
            params['stroke'] = 1

        return params

    def set_style(self, style):
        if style == 'dotted':
            self.canvas.setDash([2, 2])
        elif style == 'dashed':
            self.canvas.setDash([4, 4])
        else:
            self.canvas.setDash()

    def set_stroke_color(self, color="black"):
        if isinstance(color, basestring):
            self.canvas.setStrokeColor(color)
        elif color:
            rgb = (color[0] / 256.0, color[1] / 256.0, color[2] / 256.0)
            self.canvas.setStrokeColorRGB(*rgb)
        else:
            self.set_stroke_color()

    def set_fill_color(self, color="white"):
        if isinstance(color, basestring):
            self.canvas.setFillColor(color)
        elif color:
            rgb = (color[0] / 256.0, color[1] / 256.0, color[2] / 256.0)
            self.canvas.setFillColorRGB(*rgb)
        else:
            self.set_fill_color()

    def path(self, pd, **kwargs):
        params = self.set_render_params(**kwargs)
        self.canvas.drawPath(pd, **params)

    def rectangle(self, box, **kwargs):
        x = box[0]
        y = box[1]
        width = box[2] - box[0]
        height = box[3] - box[1]

        params = self.set_render_params(**kwargs)
        self.canvas.rect(x, y, width, height, **params)

    def label(self, box, string, **kwargs):
        self.set_font(kwargs.get('font'), kwargs.get('fontsize', 11))
        lines = TextFolder(box, string, adjustBaseline=True,
                           canvas=self.canvas, **kwargs)

        self.rectangle(lines.outlineBox(), fill='white', outline='black')
        self.textarea(box, string, **kwargs)

    def text(self, xy, string, **kwargs):
        self.set_fill_color(kwargs.get('fill'))
        self.set_font(kwargs.get('font'), kwargs.get('fontsize', 11))
        self.canvas.drawString(xy[0], xy[1], string)

    def textarea(self, box, string, **kwargs):
        self.set_font(kwargs.get('font'), kwargs.get('fontsize', 11))
        lines = TextFolder(box, string, adjustBaseline=True,
                           canvas=self.canvas, **kwargs)

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
        r = (360 + end - start) % 360

        params = self.set_render_params(**kwargs)
        self.canvas.arc(xy[0], xy[1], xy[2], xy[3], start, r)

    def ellipse(self, xy, **kwargs):
        params = self.set_render_params(**kwargs)
        self.canvas.ellipse(xy[0], xy[1], xy[2], xy[3], **params)

    def polygon(self, xy, **kwargs):
        pd = self.canvas.beginPath()
        pd.moveTo(xy[0][0], xy[0][1])
        for p in xy[1:]:
            pd.lineTo(p[0], p[1])

        params = self.set_render_params(**kwargs)
        self.canvas.drawPath(pd, **params)

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
