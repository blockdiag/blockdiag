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
from DiagramMetrics import AutoScaler
from imagedraw.filters.linejump import LineJumpDrawFilter


class DiagramDraw(object):
    MetricsClass = None

    @classmethod
    def set_metrics_class(cls, MetricsClass):
        cls.MetricsClass = MetricsClass

    def __init__(self, format, diagram, filename=None, **kwargs):
        self.format = format.upper()
        self.diagram = diagram
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.badgeFill = kwargs.get('badgeFill', 'pink')
        self.font = kwargs.get('font')
        self.filename = filename
        self.scale_ratio = 1

        basediagram = kwargs.get('basediagram', diagram)
        self.metrics = self.MetricsClass(basediagram, **kwargs)

        if self.format == 'PNG':
            if kwargs.get('antialias'):
                self.scale_ratio = ratio = 2
                self.metrics = AutoScaler(self.metrics, scale_ratio=ratio)
            self.shadow = kwargs.get('shadow', (64, 64, 64))
        else:
            self.shadow = kwargs.get('shadow', (0, 0, 0))

        kwargs = dict(font=self.font,
                      nodoctype=kwargs.get('nodoctype'),
                      scale_ratio=self.scale_ratio)
        drawer = imagedraw.create(self.format, self.filename,
                                  self.pagesize(), **kwargs)
        self.drawer = LineJumpDrawFilter(drawer, self.metrics.cellsize / 2)

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
            metrics = self.metrics
        else:
            metrics = self.metrics.originalMetrics()

        width = self.diagram.colwidth
        height = self.diagram.colheight
        return metrics.pagesize(width, height)

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
        metrics = self.metrics.originalMetrics()

        # Draw node groups.
        for group in self.groups:
            box = metrics.group(group).marginbox
            self.drawer.rectangle(box, fill=group.color, filter='blur')

        # Drop node shadows.
        for node in self.nodes:
            if node.color != 'none':
                r = noderenderer.get(node.shape)

                shape = r(node, metrics)
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
        shape = r(node, self.metrics)
        shape.render(self.drawer, self.format,
                     fill=self.fill, outline=self.diagram.linecolor,
                     font=self.font, badgeFill=self.badgeFill)

    def group_label(self, group):
        m = self.metrics.group(group)

        if group.label and not group.separated:
            self.drawer.textarea(m.grouplabelbox, group.label,
                                 fill=group.textcolor, font=self.font,
                                 fontsize=self.metrics.fontsize)
        elif group.label:
            self.drawer.textarea(m.corebox, group.label,
                                 fill=group.textcolor, font=self.font,
                                 fontsize=self.metrics.fontsize)

    def edge(self, edge):
        metrics = self.metrics.edge(edge)

        for line in metrics.shaft().polylines:
            self.drawer.line(line, fill=edge.color,
                             style=edge.style, jump=True)

        for head in metrics.heads():
            if edge.hstyle in ('generalization', 'aggregation'):
                self.drawer.polygon(head, outline=edge.color, fill='white')
            else:
                self.drawer.polygon(head, outline=edge.color, fill=edge.color)

        if edge.label:
            self.drawer.textarea(metrics.labelbox(), edge.label,
                                 fill=edge.textcolor, outline=self.fill,
                                 font=self.font,
                                 fontsize=self.metrics.fontsize)

    def save(self, size=None):
        return self.drawer.save(self.filename, size, self.format)


from DiagramMetrics import DiagramMetrics
DiagramDraw.set_metrics_class(DiagramMetrics)
