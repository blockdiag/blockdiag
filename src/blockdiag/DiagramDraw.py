#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from utils.XY import XY
import ImageDrawEx
import SVGImageDraw
from DiagramMetrix import DiagramMetrix
from PngDiagramMetrix import PngDiagramMetrix


class DiagramDraw(object):
    def __init__(self, format, diagram, **kwargs):
        self.format = format.upper()
        self.diagram = diagram
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.badgeFill = kwargs.get('badgeFill', 'pink')
        self.font = kwargs.get('font')

        if self.format == 'SVG':
            self.shadow = kwargs.get('shadow', (0, 0, 0))
            self.scale_ratio = 1
            self.metrix = DiagramMetrix(diagram, **kwargs)
            self.imageDraw = SVGImageDraw.SVGImageDraw(self.pageSize())
        else:
            self.shadow = kwargs.get('shadow', (64, 64, 64))
            if kwargs.get('antialias') or kwargs.get('scale') > 1:
                self.scale_ratio = 2
            else:
                self.scale_ratio = 1

            self.metrix = PngDiagramMetrix(diagram, scale=self.scale_ratio,
                                           **kwargs)
            self.imageDraw = ImageDrawEx.ImageDrawEx(self.pageSize(),
                                                     self.scale_ratio)

    def pageSize(self, scaled=False):
        if scaled:
            metrix = self.metrix
        else:
            metrix = self.metrix.originalMetrix()

        return metrix.pageSize(self.diagram.nodes)

    def draw(self, **kwargs):
        self._prepareEdges()
        self._drawBackground()

        if self.scale_ratio > 1:
            pageSize = self.pageSize(scaled=True)
            self.imageDraw = self.imageDraw.resizeCanvas(pageSize)

        for node in (x for x in self.diagram.nodes if x.drawable):
            self.node(node, **kwargs)

        for edge in self.diagram.edges:
            self.edge(edge)

        for edge in (x for x in self.diagram.edges if x.label):
            self.edge_label(edge)

    def _prepareEdges(self):
        for edge in self.diagram.edges:
            m = self.metrix.edge(edge)
            dir = m.direction()
            if dir == 'right':
                r = range(edge.node1.xy.x + 1, edge.node2.xy.x)
                for x in r:
                    xy = (x, edge.node1.xy.y)
                    nodes = [x for x in self.diagram.nodes if x.xy == xy]
                    if len(nodes) > 0:
                        edge.skipped = 1
            elif dir == 'right-down':
                r = range(edge.node1.xy.x + 1, edge.node2.xy.x)
                for x in r:
                    xy = (x, edge.node2.xy.y)
                    nodes = [x for x in self.diagram.nodes if x.xy == xy]
                    if len(nodes) > 0:
                        edge.skipped = 1
            elif dir in ('left-down', 'down'):
                r = range(edge.node1.xy.y + 1, edge.node2.xy.y)
                for y in r:
                    xy = (edge.node1.xy.x, y)
                    nodes = [x for x in self.diagram.nodes if x.xy == xy]
                    if len(nodes) > 0:
                        edge.skipped = 1
            elif dir == 'up':
                r = range(edge.node2.xy.y + 1, edge.node1.xy.y)
                for y in r:
                    xy = (edge.node1.xy.x, y)
                    nodes = [x for x in self.diagram.nodes if x.xy == xy]
                    if len(nodes) > 0:
                        edge.skipped = 1

        # Search crosspoints
        from bisect import insort, bisect_left, bisect_right

        lines = [(ed, ln) for ed in self.diagram.edges
                          for ln in self.metrix.edge(ed).shaft().lines()]
        ytree = []
        for i, (_, (st, ed)) in enumerate(lines):
            if st.y == ed.y:  # horizonal line
                insort(ytree, (st.y, 0, i))
            else:             # vertical line
                insort(ytree, (max(st.y, ed.y), -1, i))
                insort(ytree, (min(st.y, ed.y), +1, i))

        cross = []
        xtree = []
        for y, _, i in ytree:
            edge, ((x1, y1), (x2, y2)) = lines[i]
            if (x2 < x1):
                x1, x2 = x2, x1
            if (y2 < y1):
                y1, y2 = y2, y1

            if (y == y1):
                insort(xtree, x1)

            if (y == y2):
                del xtree[bisect_left(xtree, x1)]
                for x in xtree[bisect_right(xtree, x1):bisect_left(xtree, x2)]:
                    if XY(x, y) not in edge.crosspoints:
                        edge.crosspoints.append(XY(x, y))

    def _drawBackground(self):
        metrix = self.metrix.originalMetrix()

        # Draw node groups.
        for node in (x for x in self.diagram.nodes if x.drawable == 0):
            marginBox = metrix.node(node).marginBox()
            self.imageDraw.rectangle(marginBox, fill=node.color,
                                     filter='blur')

        # Drop node shadows.
        for node in (x for x in self.diagram.nodes if x.drawable):
            shadowBox = metrix.node(node).shadowBox()
            self.imageDraw.rectangle(shadowBox, fill=self.shadow,
                                     filter='transp-blur')

        # Smoothing back-ground images.
        if self.format == 'PNG':
            self.imageDraw = self.imageDraw.smoothCanvas()

    def node(self, node, **kwargs):
        m = self.metrix.node(node)

        if node.background:
            self.imageDraw.rectangle(m.box(), fill=node.color)
            self.imageDraw.loadImage(node.background, m.box())
            self.imageDraw.rectangle(m.box(), outline=self.fill,
                                     style=node.style)
        else:
            self.imageDraw.rectangle(m.box(), outline=self.fill,
                                     fill=node.color, style=node.style)

        self.imageDraw.textarea(m.coreBox(), node.label, fill=self.fill,
                                font=self.font, fontsize=self.metrix.fontSize,
                                lineSpacing=self.metrix.lineSpacing)

        if node.numbered != None:
            xy = m.topLeft()
            r = self.metrix.cellSize

            box = [xy.x - r, xy.y - r, xy.x + r, xy.y + r]
            self.imageDraw.ellipse(box, outline=self.fill, fill=self.badgeFill)
            self.imageDraw.textarea(box, node.numbered,
                                    fill=self.fill, font=self.font,
                                    fontsize=self.metrix.fontSize)

    def edge(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        for line in metrix.shaft().polylines:
            self.imageDraw.line(line, fill=color, style=edge.style)

        for head in metrix.heads():
            self.imageDraw.polygon(head, outline=color, fill=color)

        r = self.metrix.cellSize / 2
        for jump in metrix.jumps():
            box = (jump.x - r, jump.y - r, jump.x + r, jump.y + r)
            self.imageDraw.arc(box, 180, 0, fill=color, style=edge.style)

    def edge_label(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.label:
            self.imageDraw.label(metrix.labelbox(), edge.label,
                                 fill=self.fill, font=self.font,
                                 fontsize=self.metrix.fontSize)

    def save(self, filename, size=None):
        if size is None and self.format == 'PNG':
            x = int(self.imageDraw.image.size[0] / self.scale_ratio)
            y = int(self.imageDraw.image.size[1] / self.scale_ratio)
            size = (x, y)

        self.imageDraw.save(filename, size, self.format)
