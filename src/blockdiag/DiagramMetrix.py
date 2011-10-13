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


def scale(value, ratio):
    if ratio == 1:
        return value

    if isinstance(value, XY):
        ret = XY(value.x * ratio, value.y * ratio)
    elif isinstance(value, tuple):
        ret = tuple([scale(x, ratio) for x in value])
    elif isinstance(value, list):
        ret = [scale(x, ratio) for x in value]
    elif isinstance(value, EdgeLines):
        ret = EdgeLines()
        ret.polylines = scale(value.polylines, ratio)
    elif isinstance(value, int):
        ret = value * ratio
    else:
        ret = value

    return ret


class AutoScaler(object):
    def __init__(self, subject, scale_ratio):
        self.subject = subject
        self.scale_ratio = scale_ratio

    def __getattr__(self, name):
        ratio = self.scale_ratio
        attr = getattr(self.subject, name)

        if not callable(attr):
            return scale(attr, ratio)
        else:
            def _(*args, **kwargs):
                ret = attr(*args, **kwargs)

                if ratio == 1:
                    pass
                elif isinstance(ret, (NodeMetrix,)):
                    ret = AutoScaler(ret, ratio)
                elif isinstance(ret, (int, XY, tuple, list, EdgeLines)):
                    ret = scale(ret, ratio)
                else:
                    ret = AutoScaler(ret, ratio)

                return ret

            return _

    def originalMetrix(self):
        return self.subject


class DiagramMetrix(object):
    cellSize = cellsize
    edge_layout = 'normal'
    nodePadding = 4
    lineSpacing = 2
    shadowOffsetX = 3
    shadowOffsetY = 6
    fontSize = 11
    pagePadding = [0, 0, 0, 0]
    nodeWidth = cellsize * 16
    nodeHeight = cellsize * 5
    spanWidth = cellsize * 8
    spanHeight = cellsize * 5

    def __init__(self, diagram, **kwargs):
        if diagram.node_width is not None:
            self.nodeWidth = diagram.node_width

        if diagram.node_height is not None:
            self.nodeHeight = diagram.node_height

        if diagram.span_width is not None:
            self.spanWidth = diagram.span_width

        if diagram.span_height is not None:
            self.spanHeight = diagram.span_height

        if diagram.fontsize is not None:
            self.fontSize = diagram.fontsize

        if diagram.page_padding is not None:
            self.pagePadding = diagram.page_padding

        if diagram.edge_layout is not None:
            self.edge_layout = diagram.edge_layout

        pageMarginX = cellsize * 3
        if pageMarginX < self.spanWidth:
            pageMarginX = self.spanWidth

        pageMarginY = cellsize * 3
        if pageMarginY < self.spanHeight:
            pageMarginY = self.spanHeight + cellsize

        self.pageMargin = XY(pageMarginX, pageMarginY)

        # setup spreadsheet
        sheet = self.spreadsheet = SpreadSheetMetrix(self)
        nodes = [n for n in diagram.nodes if isinstance(n, DiagramNode)]

        node_width = self.nodeWidth
        for x in range(diagram.colwidth):
            widths = [n.width for n in nodes if n.xy.x == x]
            if widths:
                width = max(n or node_width for n in widths)
                sheet.set_node_width(x, width)

        node_height = self.nodeHeight
        for y in range(diagram.colheight):
            heights = [n.height for n in nodes if n.xy.y == y]
            if heights:
                height = max(n or node_height for n in heights)
                sheet.set_node_width(y, height)

    def originalMetrix(self):
        return self

    def shiftedMetrix(self, top, right, bottom, left):
        metrix = copy.copy(self)

        padding = metrix.pagePadding
        metrix.pagePadding = [padding[0] + top, padding[1] + right,
                              padding[2] + bottom, padding[3] + left]

        return metrix

    def node(self, node):
        renderer = noderenderer.get(node.shape)

        if hasattr(renderer, 'render'):
            return renderer(node, self)
        else:
            return self.cell(node)

    def cell(self, node):
        return self.spreadsheet.node(node)

    def group(self, group):
        return NodeMetrix(group, self)

    def edge(self, edge):
        if self.edge_layout == 'flowchart':
            if edge.node1.group.orientation == 'landscape':
                return FlowchartLandscapeEdgeMetrix(edge, self)
            else:
                return FlowchartPortraitEdgeMetrix(edge, self)
        else:
            if edge.node1.group.orientation == 'landscape':
                return LandscapeEdgeMetrix(edge, self)
            else:
                return PortraitEdgeMetrix(edge, self)

    def pageSize(self, width, height):
        return self.spreadsheet.pagesize(width, height)


class SpreadSheetMetrix(object):
    def __init__(self, metrix):
        self.metrix = metrix
        self.node_width = defaultdict(lambda: metrix.nodeWidth)
        self.node_height = defaultdict(lambda: metrix.nodeHeight)
        self.span_width = defaultdict(lambda: metrix.spanWidth)
        self.span_height = defaultdict(lambda: metrix.spanHeight)

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

    def node(self, node):
        x, y = node.xy
        x1, y1 = self._node_topleft(node)
        x2, y2 = self._node_bottomright(node)

        return NodeMetrix(self.metrix, x1, y1, x2, y2)

    def _node_topleft(self, node, centering=True):
        m = self.metrix
        x, y = node.xy
        margin = m.pageMargin
        padding = m.pagePadding

        node_width = sum(self.node_width[i] for i in range(x))
        node_height = sum(self.node_height[i] for i in range(y))
        span_width = sum(self.span_width[i] for i in range(x))
        span_height = sum(self.span_height[i] for i in range(y))

        if centering:
            xdiff = (self.node_width[x] - (node.width or m.nodeWidth)) / 2
            ydiff = (self.node_height[y] - (node.height or m.nodeHeight)) / 2
        else:
            xdiff = 0
            ydiff = 0

        x1 = margin.x + padding[3] + node_width + span_width + xdiff
        y1 = margin.y + padding[0] + node_height + span_height + ydiff

        return XY(x1, y1)

    def _node_bottomright(self, node, centering=True):
        m = self.metrix
        x = node.xy.x + node.colwidth - 1
        y = node.xy.y + node.colheight - 1
        margin = m.pageMargin
        padding = m.pagePadding

        node_width = sum(self.node_width[i] for i in range(x + 1))
        node_height = sum(self.node_height[i] for i in range(y + 1))
        span_width = sum(self.span_width[i] for i in range(x))
        span_height = sum(self.span_height[i] for i in range(y))

        if centering:
            xdiff = (self.node_width[x] - (node.width or m.nodeWidth)) / 2
            ydiff = (self.node_height[y] - (node.height or m.nodeHeight)) / 2
        else:
            xdiff = 0
            ydiff = 0

        x2 = margin.x + padding[3] + node_width + span_width - xdiff
        y2 = margin.y + padding[0] + node_height + span_height - ydiff

        return XY(x2, y2)

    def pagesize(self, width, height):
        margin = self.metrix.pageMargin
        padding = self.metrix.pagePadding

        dummy = DiagramNode(None)
        dummy.xy = XY(width - 1, height - 1)
        x, y = self._node_bottomright(dummy, centering=False)
        return XY(x + margin.x + padding[1], y + margin.y + padding[2])


class NodeMetrix(Box):
    def __init__(self, metrix, x1, y1, x2, y2):
        self.metrix = metrix
        super(NodeMetrix, self).__init__(x1, y1, x2, y2)

    def box(self):
        return Box(self.x1, self.y1, self.x2, self.y2)

    def marginBox(self):
        return Box(self.x1 - self.metrix.spanWidth / 8,
                   self.y1 - self.metrix.spanHeight / 4,
                   self.x2 + self.metrix.spanWidth / 8,
                   self.y2 + self.metrix.spanHeight / 4)

    def coreBox(self):
        return Box(self.x1 + self.metrix.nodePadding,
                   self.y1 + self.metrix.nodePadding,
                   self.x2 - self.metrix.nodePadding * 2,
                   self.y2 - self.metrix.nodePadding * 2)

    def groupLabelBox(self):
        return Box(self.x1, self.y1 - self.metrix.spanHeight / 2,
                   self.x2, self.y1)

    def topLeft(self):
        return XY(self.x1, self.y1)

    def top(self):
        return XY(self.x1 + self.width / 2, self.y1)

    def topRight(self):
        return XY(self.x2, self.y1)

    def bottomLeft(self):
        return XY(self.x1, self.y2)

    def bottom(self):
        return XY(self.x1 + self.width / 2, self.y1 + self.height / 2)

    def bottomRight(self):
        return XY(self.x2, self.y2)

    def left(self):
        return XY(self.x1, self.y1 + self.height / 2)

    def right(self):
        return XY(self.x2, self.y1 + self.height / 2)

    def center(self):
        return XY(self.x1 + self.width / 2, self.y1 + self.height / 2)


class EdgeMetrix(object):
    def __init__(self, edge, metrix):
        self.metrix = metrix
        self.edge = edge

    def heads(self):
        pass

    def _head(self, node, direct):
        head = []
        cell = self.metrix.cellSize
        node = self.metrix.node(node)

        if direct == 'up':
            xy = node.bottom()
            head.append(xy)
            head.append(XY(xy.x - cell / 2, xy.y + cell))
            head.append(XY(xy.x, xy.y + cell * 2))
            head.append(XY(xy.x + cell / 2, xy.y + cell))
            head.append(xy)
        elif direct == 'down':
            xy = node.top()
            head.append(xy)
            head.append(XY(xy.x - cell / 2, xy.y - cell))
            head.append(XY(xy.x, xy.y - cell * 2))
            head.append(XY(xy.x + cell / 2, xy.y - cell))
            head.append(xy)
        elif direct == 'right':
            xy = node.left()
            head.append(xy)
            head.append(XY(xy.x - cell, xy.y - cell / 2))
            head.append(XY(xy.x - cell * 2, xy.y))
            head.append(XY(xy.x - cell, xy.y + cell / 2))
            head.append(xy)
        elif direct == 'left':
            xy = node.right()
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


class LandscapeEdgeMetrix(EdgeMetrix):
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
        span = XY(self.metrix.spanWidth, self.metrix.spanHeight)
        dir = self.edge.direction

        node1 = self.metrix.node(self.edge.node1)
        cell1 = self.metrix.cell(self.edge.node1)
        node2 = self.metrix.node(self.edge.node2)
        cell2 = self.metrix.cell(self.edge.node2)

        shaft = EdgeLines()
        if dir == 'right':
            shaft.moveTo(node1.right())

            if self.edge.skipped:
                shaft.lineTo(cell1.right().x + span.x / 2, cell1.right().y)
                shaft.lineTo(cell1.right().x + span.x / 2,
                             cell1.bottomRight().y + span.y / 2)
                shaft.lineTo(cell2.left().x - span.x / 4,
                             cell2.bottomRight().y + span.y / 2)
                shaft.lineTo(cell2.left().x - span.x / 4, cell2.left().y)

            shaft.lineTo(node2.left())

        elif dir == 'right-up':
            shaft.moveTo(node1.right())

            if self.edge.skipped:
                shaft.lineTo(cell1.right().x + span.x / 2, cell1.right().y)
                shaft.lineTo(cell1.right().x + span.x / 2,
                             cell2.bottomLeft().y + span.y / 2)
                shaft.lineTo(cell2.left().x - span.x / 4,
                             cell2.bottomLeft().y + span.y / 2)
                shaft.lineTo(cell2.left().x - span.x / 4, cell2.left().y)
            else:
                shaft.lineTo(cell2.left().x - span.x / 4, cell1.right().y)
                shaft.lineTo(cell2.left().x - span.x / 4, cell2.left().y)

            shaft.lineTo(node2.left())

        elif dir == 'right-down':
            shaft.moveTo(node1.right())
            shaft.lineTo(cell1.right().x + span.x / 2, cell1.right().y)

            if self.edge.skipped:
                shaft.lineTo(cell1.right().x + span.x / 2,
                             cell2.topLeft().y - span.y / 2)
                shaft.lineTo(cell2.left().x - span.x / 4,
                             cell2.topLeft().y - span.y / 2)
                shaft.lineTo(cell2.left().x - span.x / 4, cell2.left().y)
            else:
                shaft.lineTo(cell1.right().x + span.x / 2, cell2.left().y)

            shaft.lineTo(node2.left())

        elif dir == 'up':
            if self.edge.skipped:
                shaft.moveTo(node1.right())
                shaft.lineTo(cell1.right().x + span.x / 4,
                             cell1.right().y)
                shaft.lineTo(cell1.right().x + span.x / 4,
                             cell2.bottom().y + span.y / 2)
                shaft.lineTo(cell2.bottom().x, cell2.bottom().y + span.y / 2)
            else:
                shaft.moveTo(node1.top())

            shaft.lineTo(node2.bottom())

        elif dir in ('left-up', 'left', 'same'):
            shaft.moveTo(node1.right())
            shaft.lineTo(cell1.right().x + span.x / 4,
                         cell1.right().y)
            shaft.lineTo(cell1.right().x + span.x / 4,
                         cell2.top().y - span.y / 2 + span.y / 8)
            shaft.lineTo(cell2.top().x,
                         cell2.top().y - span.y / 2 + span.y / 8)
            shaft.lineTo(node2.top())

        elif dir == 'left-down':
            if self.edge.skipped:
                shaft.moveTo(node1.right())
                shaft.lineTo(cell1.right().x + span.x / 2,
                             cell1.right().y)
                shaft.lineTo(cell1.right().x + span.x / 2,
                             cell2.top().y - span.y / 2)
                shaft.lineTo(cell2.top().x, cell2.top().y - span.y / 2)
            else:
                shaft.moveTo(node1.bottom())
                shaft.lineTo(cell1.bottom().x,
                             cell2.top().y - span.y / 2)
                shaft.lineTo(cell2.top().x, cell2.top().y - span.y / 2)

            shaft.lineTo(node2.top())

        elif dir == 'down':
            if self.edge.skipped:
                shaft.moveTo(node1.right())
                shaft.lineTo(cell1.right().x + span.x / 2,
                             cell1.right().y)
                shaft.lineTo(cell1.right().x + span.x / 2,
                             cell2.top().y - span.y / 2 + span.y / 8)
                shaft.lineTo(cell2.top().x,
                             cell2.top().y - span.y / 2 + span.y / 8)
            else:
                shaft.moveTo(node1.bottom())

            shaft.lineTo(node2.top())

        return shaft

    def labelbox(self):
        span = XY(self.metrix.spanWidth, self.metrix.spanHeight)
        node = XY(self.metrix.nodeWidth, self.metrix.nodeHeight)

        dir = self.edge.direction
        node1 = self.metrix.cell(self.edge.node1)
        node2 = self.metrix.cell(self.edge.node2)

        if dir == 'right':
            if self.edge.skipped:
                box = (node1.bottomRight().x + span.x,
                       node1.bottomRight().y,
                       node2.bottomLeft().x - span.x,
                       node2.bottomLeft().y + span.y / 2)
            else:
                box = (node1.topRight().x,
                       node1.topRight().y - span.y / 8,
                       node2.left().x,
                       node2.left().y - span.y / 8)

        elif dir == 'right-up':
            box = (node2.left().x - span.x,
                   node1.top().y - node.y / 2,
                   node2.bottomLeft().x,
                   node1.top().y)

        elif dir == 'right-down':
            box = (node1.right().x,
                   node2.topLeft().y - span.y / 8,
                   node1.right().x + span.x,
                   node2.left().y - span.y / 8)

        elif dir in ('up', 'left-up', 'left', 'same'):
            if self.edge.node2.xy.y < self.edge.node1.xy.y:
                box = (node1.topRight().x - span.x / 2 + span.x / 4,
                       node1.topRight().y - span.y / 2,
                       node1.topRight().x + span.x / 2 + span.x / 4,
                       node1.topRight().y)
            else:
                box = (node1.top().x + span.x / 4,
                       node1.top().y - span.y,
                       node1.topRight().x + span.x / 4,
                       node1.topRight().y - span.y / 2)

        elif dir in ('left-down', 'down'):
            box = (node2.top().x + span.x / 4,
                   node2.top().y - span.y,
                   node2.topRight().x + span.x / 4,
                   node2.topRight().y - span.y / 2)

        # shrink box
        box = (box[0] + span.x / 8, box[1],
               box[2] - span.x / 8, box[3])

        return box


class PortraitEdgeMetrix(EdgeMetrix):
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
        span = XY(self.metrix.spanWidth, self.metrix.spanHeight)
        dir = self.edge.direction

        node1 = self.metrix.node(self.edge.node1)
        cell1 = self.metrix.cell(self.edge.node1)
        node2 = self.metrix.node(self.edge.node2)
        cell2 = self.metrix.cell(self.edge.node2)

        shaft = EdgeLines()
        if dir in ('up', 'right-up', 'same', 'right'):
            if dir == 'right' and not self.edge.skipped:
                shaft.moveTo(node1.right())
                shaft.lineTo(node2.left())
            else:
                shaft.moveTo(node1.bottom())
                shaft.lineTo(cell1.bottom().x, cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell2.right().x + span.x / 4,
                             cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell2.right().x + span.x / 4,
                             cell2.top().y - span.y / 2 + span.y / 8)
                shaft.lineTo(cell2.top().x,
                             cell2.top().y - span.y / 2 + span.y / 8)
                shaft.lineTo(node2.top())

        elif dir == 'right-down':
            shaft.moveTo(node1.bottom())
            shaft.lineTo(cell1.bottom().x, cell1.bottom().y + span.y / 2)

            if self.edge.skipped:
                shaft.lineTo(cell2.left().x - span.x / 2,
                             cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell2.topLeft().x - span.x / 2,
                             cell2.topLeft().y - span.y / 2)
                shaft.lineTo(cell2.top().x, cell2.top().y - span.y / 2)
            else:
                shaft.lineTo(cell2.top().x, cell1.bottom().y + span.y / 2)

            shaft.lineTo(node2.top())

        elif dir in ('left-up', 'left', 'same'):
            shaft.moveTo(node1.right())
            shaft.lineTo(cell1.right().x + span.x / 4,
                         cell1.right().y)
            shaft.lineTo(cell1.right().x + span.x / 4,
                         cell2.top().y - span.y / 2 + span.y / 8)
            shaft.lineTo(cell2.top().x,
                         cell2.top().y - span.y / 2 + span.y / 8)
            shaft.lineTo(node2.top())

        elif dir == 'left-down':
            shaft.moveTo(node1.bottom())

            if self.edge.skipped:
                shaft.lineTo(cell1.bottom().x, cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell2.right().x + span.x / 2,
                             cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell2.right().x + span.x / 2,
                             cell2.top().y - span.y / 2)
            else:
                shaft.lineTo(cell1.bottom().x, cell2.top().y - span.y / 2)

            shaft.lineTo(cell2.top().x, cell2.top().y - span.y / 2)
            shaft.lineTo(node2.top())

        elif dir == 'down':
            shaft.moveTo(node1.bottom())

            if self.edge.skipped:
                shaft.lineTo(cell1.bottom().x, cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell1.right().x + span.x / 2,
                             cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell2.right().x + span.x / 2,
                             cell2.top().y - span.y / 2)
                shaft.lineTo(cell2.top().x, cell2.top().y - span.y / 2)

            shaft.lineTo(node2.top())

        return shaft

    def labelbox(self):
        span = XY(self.metrix.spanWidth, self.metrix.spanHeight)

        dir = self.edge.direction
        node1 = self.metrix.cell(self.edge.node1)
        node2 = self.metrix.cell(self.edge.node2)

        if dir == 'right':
            if self.edge.skipped:
                box = (node1.bottomRight().x + span.x,
                       node1.bottomRight().y,
                       node2.bottomLeft().x - span.x,
                       node2.bottomLeft().y + span.y / 2)
            else:
                box = (node1.topRight().x,
                       node1.topRight().y - span.y / 8,
                       node2.left().x,
                       node2.left().y - span.y / 8)

        elif dir == 'right-up':
            box = (node2.left().x - span.x,
                   node2.left().y,
                   node2.bottomLeft().x,
                   node2.bottomLeft().y)

        elif dir == 'right-down':
            box = (node2.topLeft().x,
                   node2.topLeft().y - span.y / 2,
                   node2.top().x,
                   node2.top().y)

        elif dir in ('up', 'left-up', 'left', 'same'):
            if self.edge.node2.xy.y < self.edge.node1.xy.y:
                box = (node1.topRight().x - span.x / 2 + span.x / 4,
                       node1.topRight().y - span.y / 2,
                       node1.topRight().x + span.x / 2 + span.x / 4,
                       node1.topRight().y)
            else:
                box = (node1.top().x + span.x / 4,
                       node1.top().y - span.y,
                       node1.topRight().x + span.x / 4,
                       node1.topRight().y - span.y / 2)

        elif dir == 'down':
            box = (node2.top().x + span.x / 4,
                   node2.top().y - span.y / 2,
                   node2.topRight().x + span.x / 4,
                   node2.topRight().y)

        elif dir == 'left-down':
            box = (node1.bottomLeft().x,
                   node1.bottomLeft().y,
                   node1.bottom().x,
                   node1.bottom().y + span.y / 2)

        # shrink box
        box = (box[0] + span.x / 8, box[1],
               box[2] - span.x / 8, box[3])

        return box


class FlowchartLandscapeEdgeMetrix(LandscapeEdgeMetrix):
    def heads(self):
        heads = []

        if self.edge.direction == 'right-down':
            if self.edge.dir in ('back', 'both'):
                heads.append(self._head(self.edge.node1, 'up'))

            if self.edge.dir in ('forward', 'both'):
                heads.append(self._head(self.edge.node2, 'right'))
        else:
            heads = super(FlowchartLandscapeEdgeMetrix, self).heads()

        return heads

    def shaft(self):
        if self.edge.direction == 'right-down':
            span = XY(self.metrix.spanWidth, self.metrix.spanHeight)
            node1 = self.metrix.node(self.edge.node1)
            cell1 = self.metrix.cell(self.edge.node1)
            node2 = self.metrix.node(self.edge.node2)
            cell2 = self.metrix.cell(self.edge.node2)

            shaft = EdgeLines()
            shaft.moveTo(node1.bottom())

            if self.edge.skipped:
                shaft.lineTo(cell1.bottom().x,
                             cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell2.left().x - span.x / 4,
                             cell1.bottom().y + span.y / 2)
                shaft.lineTo(cell2.left().x - span.x / 4, cell2.left().y)
            else:
                shaft.lineTo(cell1.bottom().x, cell2.left().y)

            shaft.lineTo(node2.left())
        else:
            shaft = super(FlowchartLandscapeEdgeMetrix, self).shaft()

        return shaft

    def labelbox(self):
        dir = self.edge.direction
        if dir == 'right':
            span = XY(self.metrix.spanWidth, self.metrix.spanHeight)
            node1 = self.metrix.node(self.edge.node1)
            cell1 = self.metrix.cell(self.edge.node1)
            node2 = self.metrix.node(self.edge.node2)
            cell2 = self.metrix.cell(self.edge.node2)

            if self.edge.skipped:
                box = (cell1.bottom().x,
                       cell1.bottom().y,
                       cell1.bottomRight().x,
                       cell1.bottomRight().y + span.y / 2)
            else:
                box = (cell1.bottom().x,
                       cell2.left().y - span.y / 2,
                       cell1.bottom().x,
                       cell2.left().y)
        else:
            box = super(FlowchartLandscapeEdgeMetrix, self).labelbox()

        return box


class FlowchartPortraitEdgeMetrix(PortraitEdgeMetrix):
    def heads(self):
        heads = []

        if self.edge.direction == 'right-down':
            if self.edge.dir in ('back', 'both'):
                heads.append(self._head(self.edge.node1, 'left'))

            if self.edge.dir in ('forward', 'both'):
                heads.append(self._head(self.edge.node2, 'down'))
        else:
            heads = super(FlowchartPortraitEdgeMetrix, self).heads()

        return heads

    def shaft(self):
        if self.edge.direction == 'right-down':
            span = XY(self.metrix.spanWidth, self.metrix.spanHeight)
            node1 = self.metrix.node(self.edge.node1)
            cell1 = self.metrix.cell(self.edge.node1)
            node2 = self.metrix.node(self.edge.node2)
            cell2 = self.metrix.cell(self.edge.node2)

            shaft = EdgeLines()
            shaft.moveTo(node1.right())

            if self.edge.skipped:
                shaft.lineTo(cell1.right().x + span.x * 3 / 4,
                             cell1.right().y)
                shaft.lineTo(cell1.right().x + span.x * 3 / 4,
                             cell2.topLeft().y - span.y / 2)
                shaft.lineTo(cell2.top().x,
                             cell2.top().y - span.y / 2)
            else:
                shaft.lineTo(cell2.top().x, cell1.right().y)

            shaft.lineTo(node2.top())
        else:
            shaft = super(FlowchartPortraitEdgeMetrix, self).shaft()

        return shaft

    def labelbox(self):
        dir = self.edge.direction
        if dir == 'right':
            span = XY(self.metrix.spanWidth, self.metrix.spanHeight)
            node1 = self.metrix.node(self.edge.node1)
            cell1 = self.metrix.cell(self.edge.node1)
            node2 = self.metrix.node(self.edge.node2)
            cell2 = self.metrix.cell(self.edge.node2)

            if self.edge.skipped:
                box = (cell1.bottom().x,
                       cell1.bottom().y,
                       cell1.bottomRight().x,
                       cell1.bottomRight().y + span.y / 2)
            else:
                box = (cell1.bottom().x,
                       cell2.left().y - span.y / 2,
                       cell1.bottom().x,
                       cell2.left().y)
        else:
            box = super(FlowchartPortraitEdgeMetrix, self).labelbox()

        return box
