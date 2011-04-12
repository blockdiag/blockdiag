# -*- coding: utf-8 -*-

import math
import unicodedata
from XY import XY


def is_zenkaku(char):
    char_width = unicodedata.east_asian_width(char)
    return char_width in u"WFA"


def zenkaku_len(string):
    return len([x for x in string  if is_zenkaku(x)])


def hankaku_len(string):
    return len([x for x in string  if not is_zenkaku(x)])


def string_width(string):
    width = 0
    for c in string:
        char_width = unicodedata.east_asian_width(c)
        if char_width in u"WFA":
            width += 2
        else:
            width += 1

    return width


class TextFolder:
    def __init__(self, box, string, **kwargs):
        self.box = box
        self.string = string
        self.scale = 1
        self.halign = kwargs.get('halign', 'center')
        self.valign = kwargs.get('valign', 'center')
        self.fontsize = kwargs.get('fontsize', 11)
        self.padding = kwargs.get('padding', 12)
        self.lineSpacing = kwargs.get('lineSpacing', 2)

        if kwargs.get('adjustBaseline'):
            self.adjustBaseline = True
        else:
            self.adjustBaseline = False

        self._result = self._lines()

    def textsize(self, string):
        width = zenkaku_len(string) * self.fontsize + \
                hankaku_len(string) * self.fontsize * 0.55
        return (int(math.ceil(width)), self.fontsize)

    def height(self):
        height = 0
        for string in self._result:
            height += self.textsize(string)[1]

        if len(self._result) > 1:
            height += (len(self._result) - 1) * self.lineSpacing

        return height

    def each_line(self):
        size = XY(self.box[2] - self.box[0], self.box[3] - self.box[1])

        if self.valign == 'top':
            height = 0
        elif self.valign == 'bottom':
            height = size.y - self.height()
        else:
            height = int(math.ceil((size.y - self.height()) / 2.0))
        base_xy = XY(self.box[0], self.box[1])

        for string in self._result:
            textsize = self.textsize(string)

            halign = size.x - textsize[0] * self.scale
            if self.halign == 'left':
                x = self.padding
            elif self.halign == 'right':
                x = halign - self.padding
            else:
                x = int(math.ceil(halign / 2.0))

            if self.adjustBaseline:
                height += textsize[1]
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

        if corners:
            margin = 2  # this is MAGIC number
            box = (min(p.x for p in corners) - margin,
                   min(p.y for p in corners) - margin,
                   max(p.x for p in corners) + margin,
                   max(p.y for p in corners) + margin)
        else:
            box = self.box

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
        if len(lines) == 0:
            pass
        elif truncated:
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
