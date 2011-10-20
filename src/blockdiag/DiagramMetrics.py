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

import copy
from utils.XY import XY
from elements import DiagramNode
import noderenderer
from utils import Box
from utils.collections import defaultdict, namedtuple

cellsize = 8


class EdgeLines(object):
    def __init__(self):
        self.xy = None
        self.stroking = False
        self.polylines = []

    def moveTo(self, x, y=None):
        self.stroking = False
        if y is None:
            self.xy = x
        else:
            self.xy = XY(x, y)

    def lineTo(self, x, y=None):
        if y is None:
            elem = x
        else:
            elem = XY(x, y)

        if self.stroking == False:
            self.stroking = True
            polyline = []
            if self.xy:
                polyline.append(self.xy)
            self.polylines.append(polyline)

        if len(self.polylines[-1]) > 0:
            if self.polylines[-1][-1] == elem:
                return

        self.polylines[-1].append(elem)

    def lines(self):
        lines = []
        for line in self.polylines:
            start = line[0]
            for elem in list(line[1:]):
                lines.append((start, elem))
                start = elem

        return lines


class AutoScaler(object):
    def __init__(self, subject, scale_ratio):
        self.subject = subject
        self.scale_ratio = scale_ratio

    def __getattr__(self, name):
        ratio = self.scale_ratio
        attr = getattr(self.subject, name)

        if not callable(attr):
            return self.scale(attr, ratio)
        else:
            def _(*args, **kwargs):
                ret = attr(*args, **kwargs)
                return self.scale(ret, ratio)

            return _

    @classmethod
    def scale(cls, value, ratio):
        if ratio == 1:
            return value

        klass = value.__class__
        if klass == XY:
            ret = XY(value.x * ratio, value.y * ratio)
        elif klass == Box:
            ret = Box(value[0] * ratio, value[1] * ratio,
                      value[2] * ratio, value[3] * ratio)
        elif klass == tuple:
            ret = tuple([cls.scale(x, ratio) for x in value])
        elif klass == list:
            ret = [cls.scale(x, ratio) for x in value]
        elif klass == EdgeLines:
            ret = EdgeLines()
            ret.polylines = cls.scale(value.polylines, ratio)
        elif klass == int:
            ret = value * ratio
        else:
            ret = cls(value, ratio)

        return ret

    def originalMetrics(self):
        return self.subject


class DiagramMetrics(object):
    cellsize = cellsize
    edge_layout = 'normal'
    node_padding = 4
    line_spacing = 2
    shadow_offset = XY(3, 6)
    font = 11
    fontsize = 11
    page_padding = [0, 0, 0, 0]
    node_width = cellsize * 16
    node_height = cellsize * 5
    span_width = cellsize * 8
    span_height = cellsize * 5

    def __init__(self, diagram, **kwargs):
        if diagram.node_width is not None:
            self.node_width = diagram.node_width

        if diagram.node_height is not None:
            self.node_height = diagram.node_height

        if diagram.span_width is not None:
            self.span_width = diagram.span_width

        if diagram.span_height is not None:
            self.span_height = diagram.span_height

        fontname = kwargs.get('font')
        if fontname is not None:
            self.font = fontname

        if diagram.fontsize is not None:
            self.fontsize = diagram.fontsize

        if diagram.page_padding is not None:
            self.page_padding = diagram.page_padding

        if diagram.edge_layout is not None:
            self.edge_layout = diagram.edge_layout

        page_margin_x = cellsize * 3
        if page_margin_x < self.span_width:
            page_margin_x = self.span_width

        page_margin_y = cellsize * 3
        if page_margin_y < self.span_height:
            page_margin_y = self.span_height + cellsize

        self.page_margin = XY(page_margin_x, page_margin_y)

        # setup spreadsheet
        sheet = self.spreadsheet = SpreadSheetMetrics(self)
        nodes = [n for n in diagram.traverse_nodes() if n.drawable]

        node_width = self.node_width
        for x in range(diagram.colwidth):
            widths = [n.width for n in nodes if n.xy.x == x]
            if widths:
                width = max(n or node_width for n in widths)
                sheet.set_node_width(x, width)

        node_height = self.node_height
        for y in range(diagram.colheight):
            heights = [n.height for n in nodes if n.xy.y == y]
            if heights:
                height = max(n or node_height for n in heights)
                sheet.set_node_height(y, height)

    def originalMetrics(self):
        return self

    def shiftedMetrics(self, top, right, bottom, left):
        metrics = copy.copy(self)
        metrics.spreadsheet = copy.copy(self.spreadsheet)
        metrics.spreadsheet.metrics = metrics

        padding = metrics.page_padding
        metrics.page_padding = [padding[0] + top, padding[1] + right,
                               padding[2] + bottom, padding[3] + left]

        return metrics

    def node(self, node):
        renderer = noderenderer.get(node.shape)

        if hasattr(renderer, 'render'):
            return renderer(node, self)
        else:
            return self.cell(node)

    def cell(self, node, use_padding=True):
        return self.spreadsheet.node(node, use_padding)

    def group(self, group):
        return self.spreadsheet.node(group, use_padding=False)

    def edge(self, edge):
        if self.edge_layout == 'flowchart':
            if edge.node1.group.orientation == 'landscape':
                return FlowchartLandscapeEdgeMetrics(edge, self)
            else:
                return FlowchartPortraitEdgeMetrics(edge, self)
        else:
            if edge.node1.group.orientation == 'landscape':
                return LandscapeEdgeMetrics(edge, self)
            else:
                return PortraitEdgeMetrics(edge, self)

    def pagesize(self, width, height):
        return self.spreadsheet.pagesize(width, height)


class SpreadSheetMetrics(object):
    def __init__(self, metrics):
        self.metrics = metrics
        self.node_width = defaultdict(lambda: metrics.node_width)
        self.node_height = defaultdict(lambda: metrics.node_height)
        self.span_width = defaultdict(lambda: metrics.span_width)
        self.span_height = defaultdict(lambda: metrics.span_height)

    def set_node_width(self, x, width):
        if width is not None and 0 < width and \
           (x not in self.node_width or self.node_width[x] < width):
            self.node_width[x] = width

    def set_node_height(self, y, height):
        if height is not None and 0 < height and \
           (y not in self.node_height or self.node_height[y] < height):
            self.node_height[y] = height

    def set_span_width(self, x, width):
        if width is not None and 0 < width and \
           (x not in self.span_width or self.span_width[x] < width):
            self.span_width[x] = width

    def set_span_height(self, y, height):
        if height is not None and 0 < height and \
           (y not in self.span_height or self.span_height[y] < height):
            self.span_height[y] = height

    def node(self, node, use_padding=True):
        x, y = node.xy
        x1, y1 = self._node_topleft(node, use_padding)
        x2, y2 = self._node_bottomright(node, use_padding)

        return NodeMetrics(self.metrics, x1, y1, x2, y2)

    def _node_topleft(self, node, use_padding=True):
        m = self.metrics
        x, y = node.xy
        margin = m.page_margin
        padding = m.page_padding

        node_width = sum(self.node_width[i] for i in range(x))
        node_height = sum(self.node_height[i] for i in range(y))
        span_width = sum(self.span_width[i] for i in range(x))
        span_height = sum(self.span_height[i] for i in range(y))

        if use_padding:
            xdiff = (self.node_width[x] - (node.width or m.node_width)) / 2
            ydiff = (self.node_height[y] - (node.height or m.node_height)) / 2
        else:
            xdiff = 0
            ydiff = 0

        x1 = margin.x + padding[3] + node_width + span_width + xdiff
        y1 = margin.y + padding[0] + node_height + span_height + ydiff

        return XY(x1, y1)

    def _node_bottomright(self, node, use_padding=True):
        m = self.metrics
        x = node.xy.x + node.colwidth - 1
        y = node.xy.y + node.colheight - 1
        margin = m.page_margin
        padding = m.page_padding

        node_width = sum(self.node_width[i] for i in range(x + 1))
        node_height = sum(self.node_height[i] for i in range(y + 1))
        span_width = sum(self.span_width[i] for i in range(x))
        span_height = sum(self.span_height[i] for i in range(y))

        if use_padding:
            xdiff = (self.node_width[x] - (node.width or m.node_width)) / 2
            ydiff = (self.node_height[y] - (node.height or m.node_height)) / 2
        else:
            xdiff = 0
            ydiff = 0

        x2 = margin.x + padding[3] + node_width + span_width - xdiff
        y2 = margin.y + padding[0] + node_height + span_height - ydiff

        return XY(x2, y2)

    def pagesize(self, width, height):
        margin = self.metrics.page_margin
        padding = self.metrics.page_padding

        dummy = DiagramNode(None)
        dummy.xy = XY(width - 1, height - 1)
        x, y = self._node_bottomright(dummy, use_padding=False)
        return XY(x + margin.x + padding[1], y + margin.y + padding[2])


class NodeMetrics(Box):
    def __init__(self, metrics, x1, y1, x2, y2):
        self.metrics = metrics
        super(NodeMetrics, self).__init__(x1, y1, x2, y2)

    @property
    def box(self):
        return Box(self.x1, self.y1, self.x2, self.y2)

    @property
    def marginbox(self):
        return Box(self.x1 - self.metrics.span_width / 8,
                   self.y1 - self.metrics.span_height / 4,
                   self.x2 + self.metrics.span_width / 8,
                   self.y2 + self.metrics.span_height / 4)

    @property
    def corebox(self):
        return Box(self.x1 + self.metrics.node_padding,
                   self.y1 + self.metrics.node_padding,
                   self.x2 - self.metrics.node_padding * 2,
                   self.y2 - self.metrics.node_padding * 2)

    @property
    def grouplabelbox(self):
        return Box(self.x1, self.y1 - self.metrics.span_height / 2,
                   self.x2, self.y1)

    @property
    def topleft(self):
        return XY(self.x1, self.y1)

    @property
    def top(self):
        return XY(self.x1 + self.width / 2, self.y1)

    @property
    def topright(self):
        return XY(self.x2, self.y1)

    @property
    def bottomleft(self):
        return XY(self.x1, self.y2)

    @property
    def bottom(self):
        return XY(self.x1 + self.width / 2, self.y2)

    @property
    def bottomright(self):
        return XY(self.x2, self.y2)

    @property
    def left(self):
        return XY(self.x1, self.y1 + self.height / 2)

    @property
    def right(self):
        return XY(self.x2, self.y1 + self.height / 2)

    @property
    def center(self):
        return XY(self.x1 + self.width / 2, self.y1 + self.height / 2)


class EdgeMetrics(object):
    def __init__(self, edge, metrics):
        self.metrics = metrics
        self.edge = edge

    def heads(self):
        pass

    def _head(self, node, direct):
        head = []
        cell = self.metrics.cellsize
        node = self.metrics.node(node)

        if direct == 'up':
            xy = node.bottom
            head.append(xy)
            head.append(XY(xy.x - cell / 2, xy.y + cell))
            head.append(XY(xy.x, xy.y + cell * 2))
            head.append(XY(xy.x + cell / 2, xy.y + cell))
            head.append(xy)
        elif direct == 'down':
            xy = node.top
            head.append(xy)
            head.append(XY(xy.x - cell / 2, xy.y - cell))
            head.append(XY(xy.x, xy.y - cell * 2))
            head.append(XY(xy.x + cell / 2, xy.y - cell))
            head.append(xy)
        elif direct == 'right':
            xy = node.left
            head.append(xy)
            head.append(XY(xy.x - cell, xy.y - cell / 2))
            head.append(XY(xy.x - cell * 2, xy.y))
            head.append(XY(xy.x - cell, xy.y + cell / 2))
            head.append(xy)
        elif direct == 'left':
            xy = node.right
            head.append(xy)
            head.append(XY(xy.x + cell, xy.y - cell / 2))
            head.append(XY(xy.x + cell * 2, xy.y))
            head.append(XY(xy.x + cell, xy.y + cell / 2))
            head.append(xy)

        if self.edge.hstyle not in ('composition', 'aggregation'):
            head.pop(2)

        return head

    def shaft(self):
        pass

    def labelbox(self):
        pass


class LandscapeEdgeMetrics(EdgeMetrics):
    def heads(self):
        heads = []
        dir = self.edge.direction

        if self.edge.dir in ('back', 'both'):
            if dir in ('left-up', 'left', 'same',
                       'right-up', 'right', 'right-down'):
                heads.append(self._head(self.edge.node1, 'left'))
            elif dir == 'up':
                if self.edge.skipped:
                    heads.append(self._head(self.edge.node1, 'left'))
                else:
                    heads.append(self._head(self.edge.node1, 'down'))
            elif dir in ('left-down', 'down'):
                if self.edge.skipped:
                    heads.append(self._head(self.edge.node1, 'left'))
                else:
                    heads.append(self._head(self.edge.node1, 'up'))

        if self.edge.dir in ('forward', 'both'):
            if dir in ('right-up', 'right', 'right-down'):
                heads.append(self._head(self.edge.node2, 'right'))
            elif dir == 'up':
                heads.append(self._head(self.edge.node2, 'up'))
            elif dir in ('left-up', 'left', 'left-down', 'down', 'same'):
                heads.append(self._head(self.edge.node2, 'down'))

        return heads

    def shaft(self):
        span = XY(self.metrics.span_width, self.metrics.span_height)
        dir = self.edge.direction

        node1 = self.metrics.node(self.edge.node1)
        cell1 = self.metrics.cell(self.edge.node1, use_padding=False)
        node2 = self.metrics.node(self.edge.node2)
        cell2 = self.metrics.cell(self.edge.node2, use_padding=False)

        shaft = EdgeLines()
        if dir == 'right':
            shaft.moveTo(node1.right)

            if self.edge.skipped:
                shaft.lineTo(cell1.right.x + span.x / 2, cell1.right.y)
                shaft.lineTo(cell1.right.x + span.x / 2,
                             cell1.bottomright.y + span.y / 2)
                shaft.lineTo(cell2.left.x - span.x / 4,
                             cell2.bottomright.y + span.y / 2)
                shaft.lineTo(cell2.left.x - span.x / 4, cell2.left.y)

            shaft.lineTo(node2.left)

        elif dir == 'right-up':
            shaft.moveTo(node1.right)

            if self.edge.skipped:
                shaft.lineTo(cell1.right.x + span.x / 2, cell1.right.y)
                shaft.lineTo(cell1.right.x + span.x / 2,
                             cell2.bottomleft.y + span.y / 2)
                shaft.lineTo(cell2.left.x - span.x / 4,
                             cell2.bottomleft.y + span.y / 2)
                shaft.lineTo(cell2.left.x - span.x / 4, cell2.left.y)
            else:
                shaft.lineTo(cell2.left.x - span.x / 4, cell1.right.y)
                shaft.lineTo(cell2.left.x - span.x / 4, cell2.left.y)

            shaft.lineTo(node2.left)

        elif dir == 'right-down':
            shaft.moveTo(node1.right)
            shaft.lineTo(cell1.right.x + span.x / 2, cell1.right.y)

            if self.edge.skipped:
                shaft.lineTo(cell1.right.x + span.x / 2,
                             cell2.topleft.y - span.y / 2)
                shaft.lineTo(cell2.left.x - span.x / 4,
                             cell2.topleft.y - span.y / 2)
                shaft.lineTo(cell2.left.x - span.x / 4, cell2.left.y)
            else:
                shaft.lineTo(cell1.right.x + span.x / 2, cell2.left.y)

            shaft.lineTo(node2.left)

        elif dir == 'up':
            if self.edge.skipped:
                shaft.moveTo(node1.right)
                shaft.lineTo(cell1.right.x + span.x / 4, cell1.right.y)
                shaft.lineTo(cell1.right.x + span.x / 4,
                             cell2.bottom.y + span.y / 2)
                shaft.lineTo(cell2.bottom.x, cell2.bottom.y + span.y / 2)
            else:
                shaft.moveTo(node1.top)

            shaft.lineTo(node2.bottom)

        elif dir in ('left-up', 'left', 'same'):
            shaft.moveTo(node1.right)
            shaft.lineTo(cell1.right.x + span.x / 4, cell1.right.y)
            shaft.lineTo(cell1.right.x + span.x / 4,
                         cell2.top.y - span.y / 2 + span.y / 8)
            shaft.lineTo(cell2.top.x,
                         cell2.top.y - span.y / 2 + span.y / 8)
            shaft.lineTo(node2.top)

        elif dir == 'left-down':
            if self.edge.skipped:
                shaft.moveTo(node1.right)
                shaft.lineTo(cell1.right.x + span.x / 2, cell1.right.y)
                shaft.lineTo(cell1.right.x + span.x / 2,
                             cell2.top.y - span.y / 2)
                shaft.lineTo(cell2.top.x, cell2.top.y - span.y / 2)
            else:
                shaft.moveTo(node1.bottom)
                shaft.lineTo(cell1.bottom.x,
                             cell2.top.y - span.y / 2)
                shaft.lineTo(cell2.top.x, cell2.top.y - span.y / 2)

            shaft.lineTo(node2.top)

        elif dir == 'down':
            if self.edge.skipped:
                shaft.moveTo(node1.right)
                shaft.lineTo(cell1.right.x + span.x / 2, cell1.right.y)
                shaft.lineTo(cell1.right.x + span.x / 2,
                             cell2.top.y - span.y / 2 + span.y / 8)
                shaft.lineTo(cell2.top.x,
                             cell2.top.y - span.y / 2 + span.y / 8)
            else:
                shaft.moveTo(node1.bottom)

            shaft.lineTo(node2.top)

        return shaft

    def labelbox(self):
        span = XY(self.metrics.span_width, self.metrics.span_height)
        node = XY(self.metrics.node_width, self.metrics.node_height)

        dir = self.edge.direction
        node1 = self.metrics.cell(self.edge.node1, use_padding=False)
        node2 = self.metrics.cell(self.edge.node2, use_padding=False)

        if dir == 'right':
            if self.edge.skipped:
                box = (node1.bottomright.x + span.x,
                       node1.bottomright.y,
                       node2.bottomleft.x - span.x,
                       node2.bottomleft.y + span.y / 2)
            else:
                box = (node1.topright.x, node1.topright.y - span.y / 8,
                       node2.left.x, node2.left.y - span.y / 8)

        elif dir == 'right-up':
            box = (node2.left.x - span.x, node1.top.y - node.y / 2,
                   node2.bottomleft.x, node1.top.y)

        elif dir == 'right-down':
            box = (node1.right.x, node2.topleft.y - span.y / 8,
                   node1.right.x + span.x, node2.left.y - span.y / 8)

        elif dir in ('up', 'left-up', 'left', 'same'):
            if self.edge.node2.xy.y < self.edge.node1.xy.y:
                box = (node1.topright.x - span.x / 2 + span.x / 4,
                       node1.topright.y - span.y / 2,
                       node1.topright.x + span.x / 2 + span.x / 4,
                       node1.topright.y)
            else:
                box = (node1.top.x + span.x / 4,
                       node1.top.y - span.y,
                       node1.topright.x + span.x / 4,
                       node1.topright.y - span.y / 2)

        elif dir in ('left-down', 'down'):
            box = (node2.top.x + span.x / 4,
                   node2.top.y - span.y,
                   node2.topright.x + span.x / 4,
                   node2.topright.y - span.y / 2)

        # shrink box
        box = (box[0] + span.x / 8, box[1],
               box[2] - span.x / 8, box[3])

        return box


class PortraitEdgeMetrics(EdgeMetrics):
    def heads(self):
        heads = []
        dir = self.edge.direction

        if self.edge.dir in ('back', 'both'):
            if dir == 'right':
                if self.edge.skipped:
                    heads.append(self._head(self.edge.node1, 'up'))
                else:
                    heads.append(self._head(self.edge.node1, 'left'))
            elif dir in ('up', 'right-up', 'same'):
                heads.append(self._head(self.edge.node1, 'up'))
            elif dir in ('left-up', 'left'):
                heads.append(self._head(self.edge.node1, 'left'))
            elif dir in ('left-down', 'down', 'right-down'):
                if self.edge.skipped:
                    heads.append(self._head(self.edge.node1, 'left'))
                else:
                    heads.append(self._head(self.edge.node1, 'up'))

        if self.edge.dir in ('forward', 'both'):
            if dir == 'right':
                if self.edge.skipped:
                    heads.append(self._head(self.edge.node2, 'down'))
                else:
                    heads.append(self._head(self.edge.node2, 'right'))
            elif dir in ('up', 'right-up', 'same'):
                heads.append(self._head(self.edge.node2, 'down'))
            elif dir in ('left-up', 'left', 'left-down', 'down', 'right-down'):
                heads.append(self._head(self.edge.node2, 'down'))

        return heads

    def shaft(self):
        span = XY(self.metrics.span_width, self.metrics.span_height)
        dir = self.edge.direction

        node1 = self.metrics.node(self.edge.node1)
        cell1 = self.metrics.cell(self.edge.node1, use_padding=False)
        node2 = self.metrics.node(self.edge.node2)
        cell2 = self.metrics.cell(self.edge.node2, use_padding=False)

        shaft = EdgeLines()
        if dir in ('up', 'right-up', 'same', 'right'):
            if dir == 'right' and not self.edge.skipped:
                shaft.moveTo(node1.right)
                shaft.lineTo(node2.left)
            else:
                shaft.moveTo(node1.bottom)
                shaft.lineTo(cell1.bottom.x, cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell2.right.x + span.x / 4,
                             cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell2.right.x + span.x / 4,
                             cell2.top.y - span.y / 2 + span.y / 8)
                shaft.lineTo(cell2.top.x,
                             cell2.top.y - span.y / 2 + span.y / 8)
                shaft.lineTo(node2.top)

        elif dir == 'right-down':
            shaft.moveTo(node1.bottom)
            shaft.lineTo(cell1.bottom.x, cell1.bottom.y + span.y / 2)

            if self.edge.skipped:
                shaft.lineTo(cell2.left.x - span.x / 2,
                             cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell2.topleft.x - span.x / 2,
                             cell2.topleft.y - span.y / 2)
                shaft.lineTo(cell2.top.x, cell2.top.y - span.y / 2)
            else:
                shaft.lineTo(cell2.top.x, cell1.bottom.y + span.y / 2)

            shaft.lineTo(node2.top)

        elif dir in ('left-up', 'left', 'same'):
            shaft.moveTo(node1.right)
            shaft.lineTo(cell1.right.x + span.x / 4, cell1.right.y)
            shaft.lineTo(cell1.right.x + span.x / 4,
                         cell2.top.y - span.y / 2 + span.y / 8)
            shaft.lineTo(cell2.top.x,
                         cell2.top.y - span.y / 2 + span.y / 8)
            shaft.lineTo(node2.top)

        elif dir == 'left-down':
            shaft.moveTo(node1.bottom)

            if self.edge.skipped:
                shaft.lineTo(cell1.bottom.x, cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell2.right.x + span.x / 2,
                             cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell2.right.x + span.x / 2,
                             cell2.top.y - span.y / 2)
            else:
                shaft.lineTo(cell1.bottom.x, cell2.top.y - span.y / 2)

            shaft.lineTo(cell2.top.x, cell2.top.y - span.y / 2)
            shaft.lineTo(node2.top)

        elif dir == 'down':
            shaft.moveTo(node1.bottom)

            if self.edge.skipped:
                shaft.lineTo(cell1.bottom.x, cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell1.right.x + span.x / 2,
                             cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell2.right.x + span.x / 2,
                             cell2.top.y - span.y / 2)
                shaft.lineTo(cell2.top.x, cell2.top.y - span.y / 2)

            shaft.lineTo(node2.top)

        return shaft

    def labelbox(self):
        span = XY(self.metrics.span_width, self.metrics.span_height)

        dir = self.edge.direction
        node1 = self.metrics.cell(self.edge.node1, use_padding=False)
        node2 = self.metrics.cell(self.edge.node2, use_padding=False)

        if dir == 'right':
            if self.edge.skipped:
                box = (node1.bottomright.x + span.x,
                       node1.bottomright.y,
                       node2.bottomleft.x - span.x,
                       node2.bottomleft.y + span.y / 2)
            else:
                box = (node1.topright.x, node1.topright.y - span.y / 8,
                       node2.left.x, node2.left.y - span.y / 8)

        elif dir == 'right-up':
            box = (node2.left.x - span.x, node2.left.y,
                   node2.bottomleft.x, node2.bottomleft.y)

        elif dir == 'right-down':
            box = (node2.topleft.x, node2.topleft.y - span.y / 2,
                   node2.top.x, node2.top.y)

        elif dir in ('up', 'left-up', 'left', 'same'):
            if self.edge.node2.xy.y < self.edge.node1.xy.y:
                box = (node1.topright.x - span.x / 2 + span.x / 4,
                       node1.topright.y - span.y / 2,
                       node1.topright.x + span.x / 2 + span.x / 4,
                       node1.topright.y)
            else:
                box = (node1.top.x + span.x / 4,
                       node1.top.y - span.y,
                       node1.topright.x + span.x / 4,
                       node1.topright.y - span.y / 2)

        elif dir == 'down':
            box = (node2.top.x + span.x / 4,
                   node2.top.y - span.y / 2,
                   node2.topright.x + span.x / 4,
                   node2.topright.y)

        elif dir == 'left-down':
            box = (node1.bottomleft.x, node1.bottomleft.y,
                   node1.bottom.x, node1.bottom.y + span.y / 2)

        # shrink box
        box = (box[0] + span.x / 8, box[1],
               box[2] - span.x / 8, box[3])

        return box


class FlowchartLandscapeEdgeMetrics(LandscapeEdgeMetrics):
    def heads(self):
        heads = []

        if self.edge.direction == 'right-down':
            if self.edge.dir in ('back', 'both'):
                heads.append(self._head(self.edge.node1, 'up'))

            if self.edge.dir in ('forward', 'both'):
                heads.append(self._head(self.edge.node2, 'right'))
        else:
            heads = super(FlowchartLandscapeEdgeMetrics, self).heads()

        return heads

    def shaft(self):
        if self.edge.direction == 'right-down':
            span = XY(self.metrics.span_width, self.metrics.span_height)
            node1 = self.metrics.node(self.edge.node1)
            cell1 = self.metrics.cell(self.edge.node1, use_padding=False)
            node2 = self.metrics.node(self.edge.node2)
            cell2 = self.metrics.cell(self.edge.node2, use_padding=False)

            shaft = EdgeLines()
            shaft.moveTo(node1.bottom)

            if self.edge.skipped:
                shaft.lineTo(cell1.bottom.x, cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell2.left.x - span.x / 4,
                             cell1.bottom.y + span.y / 2)
                shaft.lineTo(cell2.left.x - span.x / 4, cell2.left.y)
            else:
                shaft.lineTo(cell1.bottom.x, cell2.left.y)

            shaft.lineTo(node2.left)
        else:
            shaft = super(FlowchartLandscapeEdgeMetrics, self).shaft()

        return shaft

    def labelbox(self):
        dir = self.edge.direction
        if dir == 'right':
            span = XY(self.metrics.span_width, self.metrics.span_height)
            node1 = self.metrics.node(self.edge.node1)
            cell1 = self.metrics.cell(self.edge.node1, use_padding=False)
            node2 = self.metrics.node(self.edge.node2)
            cell2 = self.metrics.cell(self.edge.node2, use_padding=False)

            if self.edge.skipped:
                box = (cell1.bottom.x, cell1.bottom.y,
                       cell1.bottomright.x, cell1.bottomright.y + span.y / 2)
            else:
                box = (cell1.bottom.x, cell2.left.y - span.y / 2,
                       cell1.bottom.x, cell2.left.y)
        else:
            box = super(FlowchartLandscapeEdgeMetrics, self).labelbox()

        return box


class FlowchartPortraitEdgeMetrics(PortraitEdgeMetrics):
    def heads(self):
        heads = []

        if self.edge.direction == 'right-down':
            if self.edge.dir in ('back', 'both'):
                heads.append(self._head(self.edge.node1, 'left'))

            if self.edge.dir in ('forward', 'both'):
                heads.append(self._head(self.edge.node2, 'down'))
        else:
            heads = super(FlowchartPortraitEdgeMetrics, self).heads()

        return heads

    def shaft(self):
        if self.edge.direction == 'right-down':
            span = XY(self.metrics.span_width, self.metrics.span_height)
            node1 = self.metrics.node(self.edge.node1)
            cell1 = self.metrics.cell(self.edge.node1, use_padding=False)
            node2 = self.metrics.node(self.edge.node2)
            cell2 = self.metrics.cell(self.edge.node2, use_padding=False)

            shaft = EdgeLines()
            shaft.moveTo(node1.right)

            if self.edge.skipped:
                shaft.lineTo(cell1.right.x + span.x * 3 / 4, cell1.right.y)
                shaft.lineTo(cell1.right.x + span.x * 3 / 4,
                             cell2.topleft.y - span.y / 2)
                shaft.lineTo(cell2.top.x, cell2.top.y - span.y / 2)
            else:
                shaft.lineTo(cell2.top.x, cell1.right.y)

            shaft.lineTo(node2.top)
        else:
            shaft = super(FlowchartPortraitEdgeMetrics, self).shaft()

        return shaft

    def labelbox(self):
        dir = self.edge.direction
        if dir == 'right':
            span = XY(self.metrics.span_width, self.metrics.span_height)
            node1 = self.metrics.node(self.edge.node1)
            cell1 = self.metrics.cell(self.edge.node1, use_padding=False)
            node2 = self.metrics.node(self.edge.node2)
            cell2 = self.metrics.cell(self.edge.node2, use_padding=False)

            if self.edge.skipped:
                box = (cell1.bottom.x, cell1.bottom.y,
                       cell1.bottomright.x, cell1.bottomright.y + span.y / 2)
            else:
                box = (cell1.bottom.x, cell2.left.y - span.y / 2,
                       cell1.bottom.x, cell2.left.y)
        else:
            box = super(FlowchartPortraitEdgeMetrics, self).labelbox()

        return box
