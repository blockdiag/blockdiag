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

import sys
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from blockdiag.utils.XY import XY
from blockdiag.utils import urlutil
from blockdiag.utils.PDFTextFolder import PDFTextFolder as TextFolder


class PDFImageDraw(object):
    def __init__(self, filename, size, **kwargs):
        self.canvas = canvas.Canvas(filename, pagesize=size)
        self.size = size
        self.fonts = {}

        if kwargs.get('font') is None:
            msg = "Could not detect fonts, use --font opiton\n"
            raise RuntimeError(msg)

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
            if color != 'none':
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
        y = self.size[1] - box[3]
        width = box[2] - box[0]
        height = box[3] - box[1]

        params = self.set_render_params(**kwargs)
        self.canvas.rect(x, y, width, height, **params)

    def text(self, xy, string, **kwargs):
        self.set_fill_color(kwargs.get('fill'))
        self.set_font(kwargs.get('font'), kwargs.get('fontsize', 11))
        self.canvas.drawString(xy[0], self.size[1] - xy[1], string)

    def textarea(self, box, string, **kwargs):
        self.set_font(kwargs.get('font'), kwargs.get('fontsize', 11))
        lines = TextFolder(box, string, adjustBaseline=True,
                           canvas=self.canvas, **kwargs)

        if kwargs.get('outline'):
            outline = kwargs.get('outline')
            self.rectangle(lines.outlineBox(), fill='white', outline=outline)

        for string, xy in lines.each_line():
            self.text(xy, string, **kwargs)

    def line(self, xy, **kwargs):
        self.set_stroke_color(kwargs.get('fill', 'none'))
        self.set_style(kwargs.get('style'))

        p1 = xy[0]
        y = self.size[1]
        for p2 in xy[1:]:
            self.canvas.line(p1.x, y - p1.y, p2.x, y - p2.y)
            p1 = p2

    def arc(self, xy, start, end, **kwargs):
        start, end = 360 - end, 360 - start
        r = (360 + end - start) % 360

        params = self.set_render_params(**kwargs)
        y = self.size[1]
        self.canvas.arc(xy[0], y - xy[3], xy[2], y - xy[1], start, r)

    def ellipse(self, xy, **kwargs):
        params = self.set_render_params(**kwargs)
        y = self.size[1]
        self.canvas.ellipse(xy[0], y - xy[3], xy[2], y - xy[1], **params)

    def polygon(self, xy, **kwargs):
        pd = self.canvas.beginPath()
        y = self.size[1]
        pd.moveTo(xy[0][0], y - xy[0][1])
        for p in xy[1:]:
            pd.lineTo(p[0], y - p[1])

        params = self.set_render_params(**kwargs)
        self.canvas.drawPath(pd, **params)

    def loadImage(self, filename, box):
        x = box[0]
        y = self.size[1] - box[3]
        w = box[2] - box[0]
        h = box[3] - box[1]

        if urlutil.isurl(filename):
            from reportlab.lib.utils import ImageReader
            try:
                filename = ImageReader(filename)
            except:
                msg = "WARNING: Could not retrieve: %s\n" % filename
                sys.stderr.write(msg)
                return
        self.canvas.drawImage(filename, x, y, w, h, mask='auto',
                                  preserveAspectRatio=True)

    def save(self, filename, size, format):
        # Ignore size and format parameter; compatibility for ImageDrawEx.

        self.canvas.showPage()
        self.canvas.save()
