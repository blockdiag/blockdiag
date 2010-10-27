# -*- coding: utf-8 -*-

import math
import Image
import ImageDraw
import ImageFont
from XY import XY


class TextFolder:
    def __init__(self, box, string, **kwargs):
        font = kwargs.get('font')
        if font:
            fontsize = kwargs.get('fontsize', 11)
            self.ttfont = ImageFont.truetype(font, fontsize)
            self.scale = 1
        else:
            self.ttfont = None
            self.scale = kwargs.get('scale', 1)

        if kwargs.get('adjustBaseline'):
            self.adjustBaseline = True
        else:
            self.adjustBaseline = False

        self.box = box
        self.string = string
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.image = Image.new('1', (1, 1))
        self.draw = ImageDraw.Draw(self.image)

        self._result = self._lines()

    def textsize(self, string):
        return self.draw.textsize(string, font=self.ttfont)

    def height(self):
        height = 0
        for string in self._result:
            height += self.textsize(string)[1]

        if len(self._result) > 1:
            height += (len(self._result) - 1) * self.lineSpacing

        return height

    def each_line(self):
        size = XY(self.box[2] - self.box[0], self.box[3] - self.box[1])

        height = int(math.ceil((size.y - self.height()) / 2.0))
        base_xy = XY(self.box[0], self.box[1])

        for string in self._result:
            textsize = self.textsize(string)
            halign = size.x - textsize[0] * self.scale

            if self.adjustBaseline:
                height += textsize[1]

            x = int(math.ceil(halign / 2.0))
            draw_xy = XY(base_xy.x + x, base_xy.y + height)

            yield string, draw_xy

            if self.adjustBaseline:
                height += self.lineSpacing
            else:
                height += textsize[1] + self.lineSpacing

    def outlineBox(self):
        corners = []
        for string, xy in self.each_line():
            textsize = self.textsize(string)
            width = textsize[0] * self.scale
            height = textsize[1] * self.scale

            if self.adjustBaseline:
                xy = XY(xy.x, xy.y - textsize[1])

            corners.append(xy)
            corners.append(XY(xy.x + width, xy.y + height))

        margin = 2  # this is MAGIC number
        box = (min(p.x for p in corners) - margin,
               min(p.y for p in corners) - margin,
               max(p.x for p in corners) + margin,
               max(p.y for p in corners) + margin)

        return box

    def _lines(self):
        lines = []
        size = (self.box[2] - self.box[0], self.box[3] - self.box[1])

        def splitlines(string):
            for line in string.splitlines():
                for subline in line.split("\\n"):
                    yield subline

        height = 0
        truncated = 0
        for line in splitlines(self.string):
            while line:
                string = line.strip()
                for i in range(0, len(string)):
                    length = len(string) - i
                    metrics = self.textsize(string[0:length])

                    if metrics[0] <= size[0]:
                        break

                if size[1] < height + metrics[1]:
                    truncated = 1
                    break

                lines.append(string[0:length])
                line = string[length:]

                height += metrics[1] + self.lineSpacing

        # truncate last line.
        if truncated:
            string = lines.pop()
            for i in range(0, len(string)):
                if i == 0:
                    truncated = string + ' ...'
                else:
                    truncated = string[0:-i] + ' ...'

                metrics = self.textsize(truncated)
                if metrics[0] <= size[0]:
                    lines.append(truncated)
                    break

        return lines
