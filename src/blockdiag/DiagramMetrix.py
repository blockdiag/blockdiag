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

from utils.XY import XY
import noderenderer
from utils.namedtuple import namedtuple


class EdgeLines(object):
    def __init__(self, metrix):
        self.xy = None
        self.cellSize = metrix.cellSize
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
        Dummy = namedtuple('DummyMetrix', 'cellSize')

        ret = EdgeLines(Dummy(value.cellSize))
        ret.polylines = scale(value.polylines, ratio)
    elif isinstance(value, int):
        ret = value * ratio
    else:
        ret = value

    return ret


class DiagramMetrix(dict):
    def __init__(self, diagram, **kwargs):
        for key in kwargs:
            self[key] = kwargs[key]

        self.setdefault('scale_ratio', 1)
        self.setdefault('cellSize', 8)
        self.setdefault('nodePadding', 4)
        self.setdefault('lineSpacing', 2)
        self.setdefault('shadowOffsetX', 3)
        self.setdefault('shadowOffsetY', 6)
        self.setdefault('edge_layout', diagram.edge_layout)

        cellsize = self.cellSize / self.scale_ratio
        if diagram.node_width is not None:
            self.setdefault('nodeWidth', diagram.node_width)
        else:
            self.setdefault('nodeWidth', cellsize * 16)

        if diagram.node_height is not None:
            self.setdefault('nodeHeight', diagram.node_height)
        else:
            self.setdefault('nodeHeight', cellsize * 5)

        if diagram.span_width is not None:
            self.setdefault('spanWidth', diagram.span_width)
        else:
            self.setdefault('spanWidth', cellsize * 8)

        if diagram.span_height is not None:
            self.setdefault('spanHeight', diagram.span_height)
        else:
            self.setdefault('spanHeight', cellsize * 5)

        if diagram.fontsize is not None:
            self.setdefault('fontSize', diagram.fontsize)
        else:
            self.setdefault('fontSize', 11)

        if diagram.page_padding is not None:
            self.setdefault('pagePadding', diagram.page_padding)
        else:
            self.setdefault('pagePadding', [0, 0, 0, 0])

        pageMarginX = cellsize * 3
        if pageMarginX < self.spanWidth / self.scale_ratio:
            pageMarginX = self.spanWidth / self.scale_ratio

        pageMarginY = cellsize * 3
        if pageMarginY < self.spanHeight / self.scale_ratio:
            pageMarginY = self.spanHeight / self.scale_ratio + cellsize

        self.setdefault('pageMargin', XY(pageMarginX, pageMarginY))

    def __getattr__(self, name):
        if name == 'scale_ratio':
            return self[name]
        elif name in self:
            return scale(self[name], self['scale_ratio'])

    def originalMetrix(self):
        kwargs = {}
        for key in self:
            kwargs[key] = self[key]
        kwargs['scale_ratio'] = 1

        return self.__class__(self, **kwargs)

    def shiftedMetrix(self, top, right, bottom, left):
        kwargs = {}
        for key in self:
            kwargs[key] = self[key]
        padding = self['pagePadding']
        kwargs['pagePadding'] = [padding[0] + top, padding[1] + right,
                                 padding[2] + bottom, padding[3] + left]

        return self.__class__(self, **kwargs)

    def node(self, node):
        renderer = noderenderer.get(node.shape)

        if hasattr(renderer, 'render'):
            return renderer(node, self)
        else:
            return NodeMetrix(node, self)

    def cell(self, node):
        return NodeMetrix(node, self)

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
        DummyNode = namedtuple('DummyNode', 'width height xy')

        node = DummyNode(width, height, XY(0, 0))
        xy = NodeMetrix(node, self).bottomRight()
        padding = self.pagePadding
        return XY(xy.x + self.pageMargin.x + padding[1],
                  xy.y + self.pageMargin.y + padding[2])


class NodeMetrix(object):
    def __init__(self, node, metrix):
        self.metrix = metrix
        self.width = node.width
        self.height = node.height

        self.x = metrix.pageMargin.x + metrix.pagePadding[3] + \
                 node.xy.x * (metrix.nodeWidth + metrix.spanWidth)
        self.y = metrix.pageMargin.y + metrix.pagePadding[0] + \
                 node.xy.y * (metrix.nodeHeight + metrix.spanHeight)

    def box(self):
        m = self.metrix
        topLeft = self.topLeft()
        bottomRight = self.bottomRight()

        return (topLeft.x, topLeft.y, bottomRight.x, bottomRight.y)

    def marginBox(self):
        m = self.metrix
        topLeft = self.topLeft()
        bottomRight = self.bottomRight()

        return (topLeft.x - m.spanWidth / 8,
                topLeft.y - m.spanHeight / 4,
                bottomRight.x + m.spanWidth / 8,
                bottomRight.y + m.spanHeight / 4)

    def coreBox(self):
        m = self.metrix
        topLeft = self.topLeft()
        bottomRight = self.bottomRight()

        return (topLeft.x + m.nodePadding,
                topLeft.y + m.nodePadding,
                bottomRight.x - m.nodePadding * 2,
                bottomRight.y - m.nodePadding * 2)

    def groupLabelBox(self):
        m = self.metrix
        topLeft = self.topLeft()
        topRight = self.topRight()

        return (topLeft.x,
                topLeft.y - m.spanHeight / 2,
                topRight.x,
                topRight.y)

    def _nodeWidth(self):
        m = self.metrix
        return self.width * m.nodeWidth + (self.width - 1) * m.spanWidth

    def _nodeHeight(self):
        m = self.metrix
        return self.height * m.nodeHeight + (self.height - 1) * m.spanHeight

    def topLeft(self):
        return XY(self.x, self.y)

    def topCenter(self):
        return XY(self.x + self._nodeWidth() / 2, self.y)

    def topRight(self):
        return XY(self.x + self._nodeWidth(), self.y)

    def bottomLeft(self):
        return XY(self.x, self.y + self._nodeHeight())

    def bottomCenter(self):
        return XY(self.x + self._nodeWidth() / 2, self.y + self._nodeHeight())

    def bottomRight(self):
        return XY(self.x + self._nodeWidth(), self.y + self._nodeHeight())

    def leftCenter(self):
        return XY(self.x, self.y + self._nodeHeight() / 2)

    def rightCenter(self):
        return XY(self.x + self._nodeWidth(), self.y + self._nodeHeight() / 2)

    def center(self):
        return XY(self.x + self._nodeWidth() / 2,
                  self.y + self._nodeHeight() / 2)

    # method aliases
    top = topCenter
    bottom = bottomCenter
    right = rightCenter
    left = leftCenter


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

        shaft = EdgeLines(self.metrix)
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

        shaft = EdgeLines(self.metrix)
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

            shaft = EdgeLines(self.metrix)
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

            shaft = EdgeLines(self.metrix)
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
