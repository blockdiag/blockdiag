#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import Image
import ImageFilter
from utils.XY import XY
import ImageDrawEx
import SVGImageDraw
from DiagramMetrix import DiagramMetrix
from PngDiagramMetrix import PngDiagramMetrix


class DiagramDraw(object):
    def __init__(self, format, screen=None, **kwargs):
        self.format = format.upper()
        self.screen = screen
        self.image = None
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.badgeFill = kwargs.get('badgeFill', 'pink')
        self.shadow = kwargs.get('shadow', (128, 128, 128))
        self.font = kwargs.get('font')

        if self.format == 'SVG':
            self.scale_ratio = 1
            self.imageDraw = SVGImageDraw.SVGImageDraw()
            self.metrix = DiagramMetrix(**kwargs)
        else:
            if kwargs.get('antialias') or kwargs.get('scale') > 1:
                self.scale_ratio = 2
            else:
                self.scale_ratio = 1

            self.metrix = PngDiagramMetrix(scale=self.scale_ratio, **kwargs)

        self.resetCanvas()

    def resetCanvas(self):
        if self.screen is None:
            return

        if self.format == 'SVG':
            if self.imageDraw.svg is None:
                metrix = self.metrix.originalMetrix()
                pageSize = metrix.pageSize(self.screen.nodes)
                self.imageDraw.resetCanvas(pageSize)
            return

        if self.image is None:
            metrix = self.metrix.originalMetrix()
            pageSize = metrix.pageSize(self.screen.nodes)
            self.image = Image.new('RGB', pageSize, (256, 256, 256))

        self.imageDraw = ImageDrawEx.ImageDrawEx(self.image, self.scale_ratio)

    def draw(self, screen=None, **kwargs):
        if screen:
            self.screen = screen
            self.resetCanvas()

        self._prepareEdges()
        self._drawBackground()

        if self.scale_ratio > 1:
            pageSize = self.metrix.pageSize(self.screen.nodes)
            self.image = self.image.resize(pageSize, Image.ANTIALIAS)
            self.resetCanvas()

        for node in (x for x in self.screen.nodes if x.drawable):
            self.screennode(node, **kwargs)

        for edge in self.screen.edges:
            self.edge(edge)

    def _prepareEdges(self):
        for edge in self.screen.edges:
            m = self.metrix.edge(edge)
            dir = m.direction()
            if dir == 'right':
                r = range(edge.node1.xy.x + 1, edge.node2.xy.x)
                for x in r:
                    xy = (x, edge.node1.xy.y)
                    nodes = [x for x in self.screen.nodes if x.xy == xy]
                    if len(nodes) > 0:
                        edge.skipped = 1
            elif dir == 'right-down':
                r = range(edge.node1.xy.x + 1, edge.node2.xy.x)
                for x in r:
                    xy = (x, edge.node2.xy.y)
                    nodes = [x for x in self.screen.nodes if x.xy == xy]
                    if len(nodes) > 0:
                        edge.skipped = 1

    def _drawBackground(self):
        metrix = self.metrix.originalMetrix()

        # Draw node groups.
        for node in (x for x in self.screen.nodes if x.drawable == 0):
            marginBox = metrix.node(node).marginBox()
            self.imageDraw.rectangle(marginBox, fill=node.color)

        # Drop node shadows.
        for node in (x for x in self.screen.nodes if x.drawable):
            shadowBox = metrix.node(node).shadowBox()
            self.imageDraw.rectangle(shadowBox, fill=self.shadow)

        # Smoothing back-ground images.
        if self.format == 'PNG':
            for i in range(15):
                self.image = self.image.filter(ImageFilter.SMOOTH_MORE)

        self.resetCanvas()

    def screennode(self, node, **kwargs):
        m = self.metrix.node(node)

        if node.background:
            self.imageDraw.rectangle(m.box(), fill=node.color)
            self.imageDraw.loadImage(node.background, m.box())
            self.imageDraw.rectangle(m.box(), outline=self.fill)
        else:
            self.imageDraw.rectangle(m.box(), outline=self.fill,
                                     fill=node.color)

        self.imageDraw.text(m.coreBox(), node.label, fill=self.fill,
                            font=self.font, fontsize=self.metrix.fontSize,
                            lineSpacing=self.metrix.lineSpacing)

        if node.numbered != None:
            xy = m.topLeft()
            r = self.metrix.cellSize

            box = [xy.x - r, xy.y - r, xy.x + r, xy.y + r]
            self.imageDraw.ellipse(box, outline=self.fill, fill=self.badgeFill)
            self.imageDraw.text(box, node.numbered, fill=self.fill,
                                font=self.font, fontsize=self.metrix.fontSize)

    def edge(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        for line in metrix.shaft().polylines:
            self.imageDraw.line(line, fill=color)

        for head in metrix.heads():
            self.imageDraw.polygon(head, outline=color, fill=color)

    def save(self, filename, format=None, size=None):
        if format:
            self.format = format

        if size:
            x, y = size
        elif self.format == 'PNG':
            x, y = self.image.size
            x = int(x / self.scale_ratio)
            y = int(y / self.scale_ratio)

        if self.format == 'SVG':
            self.imageDraw.save(filename)
        else:
            self.image.thumbnail((x, y), Image.ANTIALIAS)
            self.image.save(filename, self.format)
