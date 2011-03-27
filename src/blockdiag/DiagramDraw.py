#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from utils.XY import XY
import noderenderer
from DiagramMetrix import DiagramMetrix


class DiagramDraw(object):
    def __init__(self, format, diagram, filename=None, **kwargs):
        self.format = format.upper()
        self.diagram = diagram
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.badgeFill = kwargs.get('badgeFill', 'pink')
        self.font = kwargs.get('font')
        self.filename = filename
        base_diagram = kwargs.get('basediagram', diagram)

        if self.format == 'PNG' and kwargs.get('antialias'):
            self.scale_ratio = 2
        else:
            self.scale_ratio = 1
        self.metrix = DiagramMetrix(base_diagram,
                                    scale_ratio=self.scale_ratio, **kwargs)

        if self.format == 'SVG':
            import SVGImageDraw

            self.shadow = kwargs.get('shadow', (0, 0, 0))
            self.drawer = SVGImageDraw.SVGImageDraw(self.pagesize())
        elif self.format == 'PDF':
            import PDFImageDraw

            self.shadow = kwargs.get('shadow', (0, 0, 0))
            self.drawer = PDFImageDraw.PDFImageDraw(self.filename,
                                                    self.pagesize())
        else:
            import ImageDrawEx

            self.shadow = kwargs.get('shadow', (64, 64, 64))
            self.drawer = ImageDrawEx.ImageDrawEx(self.pagesize(),
                                                  self.scale_ratio)

    @property
    def nodes(self):
        if self.diagram.separated:
            seq = self.diagram.nodes
        else:
            seq = self.diagram.traverse_nodes()

        for node in seq:
            if node.drawable:
                yield node

    @property
    def groups(self):
        if self.diagram.separated:
            seq = self.diagram.nodes
        else:
            seq = self.diagram.traverse_groups(preorder=True)

        for group in seq:
            if not group.drawable:
                yield group

    @property
    def edges(self):
        for edge in self.diagram.edges:
            yield edge

        for group in self.groups:
            for edge in group.edges:
                yield edge

    def pagesize(self, scaled=False):
        if scaled:
            metrix = self.metrix
        else:
            metrix = self.metrix.originalMetrix()

        if self.diagram.separated:
            width = max(n.xy.x + n.width for n in self.diagram.nodes)
            height = max(n.xy.y + n.height for n in self.diagram.nodes)
        else:
            width = self.diagram.width
            height = self.diagram.height

        return metrix.pageSize(width, height)

    def draw(self, **kwargs):
        self._prepare_edges()
        self._draw_background()

        if self.scale_ratio > 1:
            pagesize = self.pagesize(scaled=True)
            self.drawer = self.drawer.resizeCanvas(pagesize)

        for node in self.nodes:
            self.node(node, **kwargs)

        for node in self.groups:
            self.group_label(node, **kwargs)

        for edge in self.edges:
            self.edge(edge)

        for edge in (x for x in self.edges if x.label):
            self.edge_label(edge)

    def _prepare_edges(self):
        for edge in self.edges:
            m = self.metrix.edge(edge)
            dir = m.direction()

            if edge.node1.group.orientation == 'landscape':
                if dir == 'right':
                    r = range(edge.node1.xy.x + 1, edge.node2.xy.x)
                    for x in r:
                        xy = (x, edge.node1.xy.y)
                        nodes = [x for x in self.nodes if x.xy == xy]
                        if len(nodes) > 0:
                            edge.skipped = 1
                elif dir == 'right-up':
                    r = range(edge.node1.xy.x + 1, edge.node2.xy.x)
                    for x in r:
                        xy = (x, edge.node1.xy.y)
                        nodes = [x for x in self.nodes if x.xy == xy]
                        if len(nodes) > 0:
                            edge.skipped = 1
                elif dir == 'right-down':
                    r = range(edge.node1.xy.x + 1, edge.node2.xy.x)
                    for x in r:
                        xy = (x, edge.node2.xy.y)
                        nodes = [x for x in self.nodes if x.xy == xy]
                        if len(nodes) > 0:
                            edge.skipped = 1
                elif dir in ('left-down', 'down'):
                    r = range(edge.node1.xy.y + 1, edge.node2.xy.y)
                    for y in r:
                        xy = (edge.node1.xy.x, y)
                        nodes = [x for x in self.nodes if x.xy == xy]
                        if len(nodes) > 0:
                            edge.skipped = 1
                elif dir == 'up':
                    r = range(edge.node2.xy.y + 1, edge.node1.xy.y)
                    for y in r:
                        xy = (edge.node1.xy.x, y)
                        nodes = [x for x in self.nodes if x.xy == xy]
                        if len(nodes) > 0:
                            edge.skipped = 1
            else:
                if dir == 'right':
                    r = range(edge.node1.xy.x + 1, edge.node2.xy.x)
                    for x in r:
                        xy = (x, edge.node1.xy.y)
                        nodes = [x for x in self.nodes if x.xy == xy]
                        if len(nodes) > 0:
                            edge.skipped = 1
                elif dir in ('left-down', 'down'):
                    r = range(edge.node1.xy.y + 1, edge.node2.xy.y)
                    for y in r:
                        xy = (edge.node1.xy.x, y)
                        nodes = [x for x in self.nodes if x.xy == xy]
                        if len(nodes) > 0:
                            edge.skipped = 1
                elif dir == 'right-down':
                    r = range(edge.node1.xy.y + 1, edge.node2.xy.y)
                    for y in r:
                        xy = (edge.node2.xy.x, y)
                        nodes = [x for x in self.nodes if x.xy == xy]
                        if len(nodes) > 0:
                            edge.skipped = 1

        # Search crosspoints
        from bisect import insort, bisect_left, bisect_right

        lines = [(ed, ln) for ed in self.edges
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

    def _draw_background(self):
        metrix = self.metrix.originalMetrix()

        # Draw node groups.
        for node in self.groups:
            box = metrix.cell(node).marginBox()
            if self.format == 'SVG' and node.href:
                drawer = self.drawer.link(node.href)
                drawer.rectangle(box, fill=node.color, filter='blur')
            else:
                self.drawer.rectangle(box, fill=node.color, filter='blur')

        # Drop node shadows.
        for node in self.nodes:
            r = noderenderer.get(node.shape)

            shape = r(node, metrix)
            shape.render(self.drawer, self.format,
                         fill=self.shadow, shadow=True)

        # Smoothing back-ground images.
        if self.format == 'PNG':
            self.drawer = self.drawer.smoothCanvas()

    def node(self, node, **kwargs):
        r = noderenderer.get(node.shape)
        shape = r(node, self.metrix)
        shape.render(self.drawer, self.format,
                     fill=self.fill, outline=self.fill,
                     font=self.font, badgeFill=self.badgeFill)

    def group_label(self, group):
        m = self.metrix.cell(group)

        if self.format == 'SVG' and group.href:
            drawer = self.drawer.link(group.href)
        else:
            drawer = self.drawer

        if group.label and not group.separated:
            drawer.textarea(m.groupLabelBox(), group.label, fill=self.fill,
                            font=self.font, fontsize=self.metrix.fontSize)
        elif group.label:
            drawer.textarea(m.coreBox(), group.label, fill=self.fill,
                            font=self.font, fontsize=self.metrix.fontSize)

    def edge(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.color:
            color = edge.color
        else:
            color = self.fill

        for line in metrix.shaft().polylines:
            self.drawer.line(line, fill=color, style=edge.style)

        for head in metrix.heads():
            if edge.hstyle in ('generalization', 'aggregation'):
                self.drawer.polygon(head, outline=color, fill='white')
            else:
                self.drawer.polygon(head, outline=color, fill=color)

        r = self.metrix.cellSize / 2
        for jump in metrix.jumps():
            box = (jump.x - r, jump.y - r, jump.x + r, jump.y + r)
            self.drawer.arc(box, 180, 0, fill=color, style=edge.style)

    def edge_label(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.label:
            self.drawer.label(metrix.labelbox(), edge.label, fill=self.fill,
                              font=self.font, fontsize=self.metrix.fontSize)

    def save(self, filename=None, size=None):
        if size is None and self.format == 'PNG':
            x = int(self.drawer.image.size[0] / self.scale_ratio)
            y = int(self.drawer.image.size[1] / self.scale_ratio)
            size = (x, y)

        if filename:
            self.filename = filename

        return self.drawer.save(self.filename, size, self.format)
