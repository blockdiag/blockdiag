#!/usr/bin/python
# -*- encoding: utf-8 -*-

import Image
import ImageDraw
import ImageFilter
from DiagramMetrix import DiagramMetrix


class FoldedTextDraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None):
        ImageDraw.ImageDraw.__init__(self, im, mode)

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
        self.lineSpacing = kwargs.get('lineSpacing', 2)
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.shadow = kwargs.get('shadow', (128, 128, 128))

    def getPaperSize(self, root):
        return self.metrix.pageSize(root)

    def screennode(self, node, **kwargs):
        ttfont = kwargs.get('font')

        m = self.metrix.node(node)
        self.imageDraw.rectangle(m.box(), outline=self.fill, fill=node.color)

        draw = FoldedTextDraw(self.image)
        draw.text(m.coreBox(), node.label, font=ttfont, lineSpacing=self.lineSpacing)

    def dropshadow(self, node, **kwargs):
        metrix = self.metrix.node(node)
        self.imageDraw.rectangle(metrix.shadowBox(), fill=self.shadow)

    def screennodelist(self, nodelist, **kwargs):
        self.image = Image.new(
            'RGB', self.getPaperSize(nodelist), (256, 256, 256))
        self.imageDraw = ImageDraw.ImageDraw(self.image, self.mode)

        for node in (x for x in nodelist if x.drawable == 0):  # == ScreenGroup
            metrix = self.metrix.node(node)
            self.imageDraw.rectangle(metrix.marginBox(), fill=node.color)

        for node in (x for x in nodelist if x.drawable):
            self.dropshadow(node, **kwargs)
        for i in range(15):
            self.image = self.image.filter(ImageFilter.SMOOTH_MORE)

        self.imageDraw = ImageDraw.ImageDraw(self.image, self.mode)
        for node in (x for x in nodelist if x.drawable):
            self.screennode(node, **kwargs)

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

    def edgelist(self, edgelist, **kwargs):
        for edge in edgelist:
            self.edge(edge)

    def save(self, filename, format):
        self.image.save(filename, format)
