#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import Image
import ImageDraw
import ImageFont
import ImageFilter
from DiagramMetrix import DiagramMetrix, XY


class ImageDrawEx(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None):
        self.image = im
        self.mode = mode
        ImageDraw.ImageDraw.__init__(self, im, mode)

    def thick_rectangle(self, box, thick=1, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        if thick == 1:
            d = 0
        else:
            d = math.ceil(thick / 2.0)

        x1, y1, x2, y2 = box
        self.rectangle(box, fill=fill)
        self.line(((x1, y1 - d), (x1, y2 + d)), fill=outline, width=thick)
        self.line(((x2, y1 - d), (x2, y2 + d)), fill=outline, width=thick)
        self.line(((x1, y1), (x2, y1)), fill=outline, width=thick)
        self.line(((x1, y2), (x2, y2)), fill=outline, width=thick)

    def setupFont(self, font, fontsize):
        if font:
            ttfont = ImageFont.truetype(font, fontsize)
        else:
            ttfont = None

        return ttfont

    def truetypeText(self, xy, string, **kwargs):
        scale_bias = 4
        fill = kwargs.get('fill')
        font = kwargs.get('font')
        fontsize = kwargs.get('fontsize', 11)

        if font is None:
            ttfont = self.setupFont(font, fontsize)
            ImageDraw.ImageDraw.text(self, xy, string,
                                     fill=fill, font=ttfont)
        else:
            ttfont = self.setupFont(font, fontsize * scale_bias)

            size = self.textsize(string, font=ttfont)
            image = Image.new('RGBA', size)
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), string, fill=fill, font=ttfont)
            del draw

            basesize = (size[0] / scale_bias, size[1] / scale_bias)
            text_image = image.resize(basesize, Image.ANTIALIAS)

            self.image.paste(text_image, xy, text_image)
            ImageDraw.ImageDraw.__init__(self, self.image, self.mode)

    def text(self, box, string, **kwargs):
        font = kwargs.get('font')
        fontsize = kwargs.get('fontsize', 11)
        fill = kwargs.get('fill')
        ttfont = self.setupFont(font, fontsize)

        lineSpacing = kwargs.get('lineSpacing', 2)
        size = (box[2] - box[0], box[3] - box[1])

        lines = self._getFoldedText(size, string,
                                    font=ttfont, lineSpacing=lineSpacing)

        height = 0
        for string in lines:
            height += self.textsize(string, font=ttfont)[1] + lineSpacing

        height = (size[1] - (height - lineSpacing)) / 2
        xy = (box[0], box[1])
        for string in lines:
            textsize = self.textsize(string, font=ttfont)
            x = (size[0] - textsize[0]) / 2

            draw_xy = (xy[0] + x, xy[1] + height)
            self.truetypeText(draw_xy, string, fill=fill, font=font, fontsize=fontsize)

            height += textsize[1] + lineSpacing

    def _getFoldedText(self, size, string, **kwargs):
        ttfont = kwargs.get('font')
        lineSpacing = kwargs.get('lineSpacing', 2)
        lines = []

        height = 0
        truncated = 0
        for line in string.splitlines():
            while line:
                string = string.strip()
                for i in range(0, len(string)):
                    length = len(string) - i
                    metrics = self.textsize(string[0:length], font=ttfont)

                    if metrics[0] <= size[0]:
                        break

                if size[1] < height + metrics[1]:
                    truncated = 1
                    break

                lines.append(line[0:length])
                line = line[length:]

                height += metrics[1] + lineSpacing

        # truncate last line.
        if truncated:
            string = lines.pop()
            for i in range(0, len(string)):
                if i == 0:
                    truncated = string + ' ...'
                else:
                    truncated = string[0:-i] + ' ...'

                size = self.textsize(truncated, font=ttfont)
                if size[0] <= size[0]:
                    lines.append(truncated)
                    break

        return lines


class DiagramDraw(object):
    def __init__(self, mode=None, **kwargs):
        self.mode = None
        self.image = None
        self.imageDraw = None
        self._scale = kwargs.get('scale', 1)
        self.metrix = DiagramMetrix(**kwargs)
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.shadow = kwargs.get('shadow', (128, 128, 128))
        self.font = kwargs.get('font')
        self.fontsize = kwargs.get('fontsize', 11)

    def scale(self, value):
        if isinstance(value, XY):
            ret = XY(value.x * self._scale, value.y * self._scale)
        elif isinstance(value, tuple):
            ret = tuple([self.scale(x) for x in value])
        elif isinstance(value, list):
            ret = [self.scale(x) for x in value]
        elif isinstance(value, int):
            ret = value * self._scale
        else:
            ret = value

        return ret

    def draw(self, screen, **kwargs):
        self.screen = screen

        paperSize = self.metrix.pageSize(screen.nodes)
        self.image = Image.new('RGB', paperSize, (256, 256, 256))
        self.imageDraw = ImageDrawEx(self.image, self.mode)

        self._prepareEdges()
        self._drawBackground()

        if self._scale > 1:
            self.image = self.image.resize(self.scale(paperSize),
                                           Image.ANTIALIAS)
            self.imageDraw = ImageDrawEx(self.image, self.mode)

        for node in (x for x in self.screen.nodes if x.drawable):
            self.screennode(node, **kwargs)

        for edge in self.screen.edges:
            self.edge(edge)

    def _prepareEdges(self):
        for edge in self.screen.edges:
            m = self.metrix.edge(edge)
            if m.direction() == 'right':
                r = range(edge.node1.xy[0] + 1, edge.node2.xy[0])
                for x in r:
                    xy = (x, edge.node1.xy[1])
                    nodes = [x for x in self.screen.nodes if x.xy == xy]
                    if len(nodes) > 0:
                        edge.skipped = 1

    def _drawBackground(self):
        originalScale = self._scale
        self._scale = 1

        # Draw node groups.
        for node in (x for x in self.screen.nodes if x.drawable == 0):
            marginBox = self.metrix.node(node).marginBox()
            self.imageDraw.rectangle(self.scale(marginBox), fill=node.color)

        # Drop node shadows.
        for node in (x for x in self.screen.nodes if x.drawable):
            shadowBox = self.metrix.node(node).shadowBox()
            self.imageDraw.rectangle(self.scale(shadowBox), fill=self.shadow)

        # Smoothing back-ground images.
        for i in range(15):
            self.image = self.image.filter(ImageFilter.SMOOTH_MORE)

        self.imageDraw = ImageDrawEx(self.image, self.mode)
        self._scale = originalScale

    def screennode(self, node, **kwargs):
        m = self.metrix.node(node)
        self.imageDraw.thick_rectangle(self.scale(m.box()), outline=self.fill,
                                       fill=node.color)

        fontsize = self.scale(self.fontsize)
        lineSpacing = self.scale(self.metrix.lineSpacing)
        self.imageDraw.text(self.scale(m.coreBox()), node.label, fill=self.fill,
                            font=self.font, fontsize=fontsize,
                            lineSpacing=lineSpacing)

    def edge(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        shaft = metrix.shaft()
        self.imageDraw.line(self.scale(shaft), fill=color)

        for head in metrix.heads():
            self.imageDraw.polygon(self.scale(head), outline=color, fill=color)

    def save(self, filename, format, size=None):
        if size:
            x, y = size
        else:
            x, y = self.image.size
            x = int(x / self._scale)
            y = int(y / self._scale)

        self.image.thumbnail((x, y), Image.ANTIALIAS)
        self.image.save(filename, format)
