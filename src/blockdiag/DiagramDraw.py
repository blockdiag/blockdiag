#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import Image
import ImageDraw
import ImageFilter
from DiagramMetrix import DiagramMetrix


class ImageDrawEx(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None):
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

    def text(self, box, string, **kwargs):
        ttfont = kwargs.get('font')
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
            ImageDraw.ImageDraw.text(self, draw_xy, string,
                                     fill=self.fill, font=ttfont)

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
        self.metrix = DiagramMetrix(**kwargs)
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.shadow = kwargs.get('shadow', (128, 128, 128))

    def draw(self, screen, **kwargs):
        ttfont = kwargs.get('font')
        self.screen = screen

        paperSize = self.metrix.pageSize(screen.nodes)
        self.image = Image.new('RGB', paperSize, (256, 256, 256))
        self.imageDraw = ImageDrawEx(self.image, self.mode)

        self._prepareEdges()
        self._drawBackground()

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
        # Draw node groups.
        for node in (x for x in self.screen.nodes if x.drawable == 0):
            metrix = self.metrix.node(node)
            self.imageDraw.rectangle(metrix.marginBox(), fill=node.color)

        # Drop node shadows.
        for node in (x for x in self.screen.nodes if x.drawable):
            metrix = self.metrix.node(node)
            self.imageDraw.rectangle(metrix.shadowBox(), fill=self.shadow)

        # Smoothing back-ground images.
        for i in range(15):
            self.image = self.image.filter(ImageFilter.SMOOTH_MORE)

        self.imageDraw = ImageDrawEx(self.image, self.mode)

    def screennode(self, node, **kwargs):
        ttfont = kwargs.get('font')

        m = self.metrix.node(node)
        self.imageDraw.thick_rectangle(m.box(), outline=self.fill, fill=node.color)

        self.imageDraw.text(m.coreBox(), node.label,
                            font=ttfont, lineSpacing=self.metrix.lineSpacing)

    def edge(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        shaft = metrix.shaft()
        self.imageDraw.line(shaft, fill=color)

        for head in metrix.heads():
            self.imageDraw.polygon(head, outline=color, fill=color)

    def save(self, filename, format):
        self.image.save(filename, format)
