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
        fill = kwargs.get('fill')
        font = kwargs.get('font')
        fontsize = kwargs.get('fontsize', 11)
        ttfont = self.setupFont(font, fontsize)

        if font is None:
            ImageDraw.ImageDraw.text(self, xy, string,
                                     fill=fill, font=ttfont)
        else:
            size = self.textsize(string, font=ttfont)

            # Generate mask to support BDF(bitmap font)
            mask = Image.new('1', size)
            draw = ImageDraw.Draw(mask)
            draw.text((0, 0), string, fill='white', font=ttfont)

            # Rendering text
            filler = Image.new('RGB', size, fill)
            self.image.paste(filler, xy, mask)

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
            x = int(math.ceil((size[0] - textsize[0]) / 2.0))

            draw_xy = (xy[0] + x, xy[1] + height)
            self.truetypeText(draw_xy, string, fill=fill,
                              font=font, fontsize=fontsize)

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

    def loadImage(self, filename, box, scale):
        box_width = box[2] - box[0]
        box_height = box[3] - box[1]

        # resize image.
        image = Image.open(filename)
        w = min([box_width, image.size[0] * scale])
        h = min([box_height, image.size[1] * scale])
        image.thumbnail((w, h), Image.ANTIALIAS)

        # centering image.
        w, h = image.size
        if box_width > w:
            x = box[0] + (box_width - w) / 2
        else:
            x = box[0]

        if box_height > h:
            y = box[1] + (box_height - h) / 2
        else:
            y = box[1]

        self.image.paste(image, (x, y))
        ImageDraw.ImageDraw.__init__(self, self.image, self.mode)


class DiagramDraw(object):
    def __init__(self, screen=None, mode=None, **kwargs):
        self.mode = None
        self.screen = screen
        self.image = None
        self.imageDraw = None
        self._scale = kwargs.get('scale', 1)
        self.metrix = DiagramMetrix(**kwargs)
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.badgeFill = kwargs.get('badgeFill', 'pink')
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

    def draw(self, screen=None, **kwargs):
        if screen:
            self.screen = screen

        paperSize = self.metrix.pageSize(self.screen.nodes)
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
            dir = m.direction()
            if dir == 'right':
                r = range(edge.node1.xy[0] + 1, edge.node2.xy[0])
                for x in r:
                    xy = (x, edge.node1.xy[1])
                    nodes = [x for x in self.screen.nodes if x.xy == xy]
                    if len(nodes) > 0:
                        edge.skipped = 1
            elif dir == 'right-down':
                r = range(edge.node1.xy[0] + 1, edge.node2.xy[0])
                for x in r:
                    xy = (x, edge.node2.xy[1])
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

        if node.background:
            self.imageDraw.thick_rectangle(self.scale(m.box()),
                                           outline=self.fill, fill=node.color)
            self.imageDraw.loadImage(node.background, self.scale(m.box()),
                                     scale=self._scale)
            self.imageDraw.thick_rectangle(self.scale(m.box()),
                                           outline=self.fill)
        else:
            self.imageDraw.thick_rectangle(self.scale(m.box()),
                                           outline=self.fill, fill=node.color)

        fontsize = self.scale(self.fontsize)
        lineSpacing = self.scale(self.metrix.lineSpacing)
        self.imageDraw.text(self.scale(m.coreBox()), node.label,
                            fill=self.fill, font=self.font, fontsize=fontsize,
                            lineSpacing=lineSpacing)

        if node.numbered != None:
            xy = self.scale(m.topLeft())
            r = self.scale(self.metrix.cellSize)

            box = [xy.x - r, xy.y - r, xy.x + r, xy.y + r]
            self.imageDraw.ellipse(box, outline=self.fill, fill=self.badgeFill)
            self.imageDraw.text(box, node.numbered, fill=self.fill,
                                font=self.font, fontsize=fontsize)

    def edge(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        for line in metrix.shaft().polylines:
            self.imageDraw.line(self.scale(line), fill=color)

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
