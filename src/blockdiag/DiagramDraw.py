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
        for node in self.diagram.traverse_nodes():
            if node.drawable:
                yield node

    @property
    def groups(self):
        for group in self.diagram.traverse_groups(preorder=True):
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

        width = self.diagram.width
        height = self.diagram.height
        return metrix.pageSize(width, height)

    def draw(self, **kwargs):
        self._draw_background()

        # Smoothing back-ground images.
        if self.format == 'PNG':
            self.drawer.smoothCanvas()

        if self.scale_ratio > 1:
            pagesize = self.pagesize(scaled=True)
            self.drawer.resizeCanvas(pagesize)

        self._draw_elements(**kwargs)

    def _draw_background(self):
        metrix = self.metrix.originalMetrix()

        # Draw node groups.
        for node in self.groups:
            box = metrix.cell(node).marginBox()
            self.drawer.rectangle(box, fill=node.color, filter='blur')

        # Drop node shadows.
        for node in self.nodes:
            if node.color != 'none':
                r = noderenderer.get(node.shape)

                shape = r(node, metrix)
                shape.render(self.drawer, self.format,
                             fill=self.shadow, shadow=True)

    def _draw_elements(self, **kwargs):
        for node in self.nodes:
            self.node(node, **kwargs)

        for node in self.groups:
            self.group_label(node, **kwargs)

        for edge in self.edges:
            self.edge(edge)

        # FIXME: edge_label() is obsoleted
        if hasattr(self, 'edge_label'):
            for edge in (x for x in self.edges if x.label):
                self.edge_label(edge)

    def node(self, node, **kwargs):
        r = noderenderer.get(node.shape)
        shape = r(node, self.metrix)
        shape.render(self.drawer, self.format,
                     fill=self.fill, outline=self.diagram.linecolor,
                     font=self.font, badgeFill=self.badgeFill)

    def group_label(self, group):
        m = self.metrix.cell(group)

        if group.label and not group.separated:
            self.drawer.textarea(m.groupLabelBox(), group.label,
                                 fill=group.textcolor, font=self.font,
                                 fontsize=self.metrix.fontSize)
        elif group.label:
            self.drawer.textarea(m.coreBox(), group.label,
                                 fill=group.textcolor, font=self.font,
                                 fontsize=self.metrix.fontSize)

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

        if edge.label:
            self.drawer.textarea(metrix.labelbox(), edge.label,
                                 fill=edge.textcolor, outline=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize)

    def save(self, size=None):
        return self.drawer.save(self.filename, size, self.format)


from DiagramMetrix import DiagramMetrix
DiagramDraw.set_metrix_class(DiagramMetrix)
