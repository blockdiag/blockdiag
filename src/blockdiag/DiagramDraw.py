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
import math
from utils.XY import XY
import noderenderer
import imagedraw
from imagedraw.filters.linejump import LineJumpDrawFilter


class DiagramDraw(object):
    MetrixClass = None

    @classmethod
    def set_metrix_class(cls, MetrixClass):
        cls.MetrixClass = MetrixClass

    def __init__(self, format, diagram, filename=None, **kwargs):
        self.format = format.upper()
        self.diagram = diagram
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.badgeFill = kwargs.get('badgeFill', 'pink')
        self.font = kwargs.get('font')
        self.filename = filename

        if self.format == 'PNG' and kwargs.get('antialias'):
            self.scale_ratio = 2
        else:
            self.scale_ratio = 1
        self.metrix = self.MetrixClass(kwargs.get('basediagram', diagram),
                                       scale_ratio=self.scale_ratio, **kwargs)

        kwargs = dict(font=self.font,
                      nodoctype=kwargs.get('nodoctype'),
                      scale_ratio=self.scale_ratio)

        if self.format == 'PNG':
            self.shadow = kwargs.get('shadow', (64, 64, 64))
        else:
            self.shadow = kwargs.get('shadow', (0, 0, 0))

        drawer = imagedraw.create(self.format, self.filename,
                                  self.pagesize(), **kwargs)
        self.drawer = LineJumpDrawFilter(drawer, self.metrix.cellSize / 2)

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
        for edge in (e for e in self.diagram.edges  if e.style != 'none'):
            yield edge

        for group in self.groups:
            for edge in (e for e in group.edges  if e.style != 'none'):
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
            self.drawer.resizeCanvas(pagesize)

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
                    if self.diagram.edge_layout == 'flowchart':
                        r = range(edge.node1.xy.y, edge.node2.xy.y)
                        for y in r:
                            xy = (edge.node1.xy.x, y + 1)
                            nodes = [x for x in self.nodes if x.xy == xy]
                            if len(nodes) > 0:
                                edge.skipped = 1
                    else:
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
                    if self.diagram.edge_layout == 'flowchart':
                        r = range(edge.node1.xy.x, edge.node2.xy.x)
                        for x in r:
                            xy = (x + 1, edge.node1.xy.y)
                            nodes = [x for x in self.nodes if x.xy == xy]
                            if len(nodes) > 0:
                                edge.skipped = 1
                    else:
                        r = range(edge.node1.xy.y + 1, edge.node2.xy.y)
                        for y in r:
                            xy = (edge.node2.xy.x, y)
                            nodes = [x for x in self.nodes if x.xy == xy]
                            if len(nodes) > 0:
                                edge.skipped = 1

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
            if node.color != 'none':
                r = noderenderer.get(node.shape)

                shape = r(node, metrix)
                shape.render(self.drawer, self.format,
                             fill=self.shadow, shadow=True)

        # Smoothing back-ground images.
        if self.format == 'PNG':
            self.drawer.smoothCanvas()

    def node(self, node, **kwargs):
        r = noderenderer.get(node.shape)
        shape = r(node, self.metrix)
        shape.render(self.drawer, self.format,
                     fill=self.fill, outline=self.diagram.linecolor,
                     font=self.font, badgeFill=self.badgeFill)

    def group_label(self, group):
        m = self.metrix.cell(group)

        if self.format == 'SVG' and group.href:
            drawer = self.drawer.link(group.href)
        else:
            drawer = self.drawer

        if group.label and not group.separated:
            drawer.textarea(m.groupLabelBox(), group.label,
                            fill=group.textcolor, font=self.font,
                            fontsize=self.metrix.fontSize)
        elif group.label:
            drawer.textarea(m.coreBox(), group.label, fill=group.textcolor,
                            font=self.font, fontsize=self.metrix.fontSize)

    def edge(self, edge):
        metrix = self.metrix.edge(edge)

        for line in metrix.shaft().polylines:
            self.drawer.line(line, fill=edge.color,
                             style=edge.style, jump=True)

        for head in metrix.heads():
            if edge.hstyle in ('generalization', 'aggregation'):
                self.drawer.polygon(head, outline=edge.color, fill='white')
            else:
                self.drawer.polygon(head, outline=edge.color, fill=edge.color)

    def edge_label(self, edge):
        metrix = self.metrix.edge(edge)

        if edge.label:
            self.drawer.label(metrix.labelbox(), edge.label,
                              fill=edge.textcolor, font=self.font,
                              fontsize=self.metrix.fontSize)

    def save(self, filename=None, size=None):
        if filename:
            self.filename = filename

            msg = "WARNING: DiagramDraw.save(filename) was deprecated.\n"
            sys.stderr.write(msg)

        return self.drawer.save(self.filename, size, self.format)


from DiagramMetrix import DiagramMetrix
DiagramDraw.set_metrix_class(DiagramMetrix)
